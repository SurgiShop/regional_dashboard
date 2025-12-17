import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    """
    Execute function for Regional Dashboard Report
    Returns columns and data
    """
    columns = get_columns()
    data = get_data(filters)

    if data is None:
        data = []

    return columns, data


def get_columns():
    """
    Define report columns
    """
    return [
        {
            "fieldname": "sales_person",
            "label": _("REP"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180,
        },
        {
            "fieldname": "total_sales",
            "label": _("Current Account Rev"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "sales_goal",
            "label": _("Account Goal"),
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "current_sil",
            "label": _("Current SIL"),
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "sil_goal",
            "label": _("Goal SIL"),
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "fieldname": "sales_goal_percent",
            "label": _("REV Goal"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "sil_goal_percent",
            "label": _("SIL Goal"),
            "fieldtype": "Data",
            "width": 120,
        },
    ]


def get_data(filters):
    """
    Fetch and return report data
    """
    if not filters:
        filters = {}

    # Get all active sales persons
    sales_persons = frappe.get_all(
        "Sales Person",
        filters={"enabled": 1},
        fields=["name"],
        order_by="name asc",
    )

    if not sales_persons:
        return []

    data = []

    for sp in sales_persons:
        sales_person_name = sp.name

        # Get targets from Target Detail child table
        targets = frappe.db.sql(
            """
            SELECT
                SUM(CASE WHEN item_group = 'Products' THEN target_amount ELSE 0 END) as sales_goal,
                SUM(CASE WHEN item_group = 'SIL' THEN target_amount ELSE 0 END) as sil_goal
            FROM `tabTarget Detail`
            WHERE parent = %(sales_person)s
        """,
            {"sales_person": sales_person_name},
            as_dict=1,
        )

        sales_goal = flt(targets[0].sales_goal) if targets and targets[0].sales_goal else 0
        sil_goal = flt(targets[0].sil_goal) if targets and targets[0].sil_goal else 0

        # Get actual total sales for this sales person
        total_sales = get_sales_for_person(sales_person_name, filters)

        # Get SIL sales
        current_sil = get_sil_sales_for_person(sales_person_name, filters)

        # Calculate percentages and format with % symbol
        sales_goal_percent = (
            f"{round((flt(total_sales) / flt(sales_goal) * 100), 2)}%" if sales_goal > 0 else "0%"
        )
        sil_goal_percent = (
            f"{round((flt(current_sil) / flt(sil_goal) * 100), 2)}%" if sil_goal > 0 else "0%"
        )

        data.append(
            {
                "sales_person": sales_person_name,
                "total_sales": total_sales,
                "sales_goal": sales_goal,
                "current_sil": current_sil,
                "sil_goal": sil_goal,
                "sales_goal_percent": sales_goal_percent,
                "sil_goal_percent": sil_goal_percent,
            }
        )

    return data


def get_sales_for_person(sales_person, filters):
    """
    Get total sales for a sales person
    """
    conditions = []
    values = {"sales_person": sales_person}

    # Add date filters if provided
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = ""
    if conditions:
        where_clause = "AND " + " AND ".join(conditions)

    result = frappe.db.sql(
        f"""
        SELECT SUM(si.grand_total) as total
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Team` st ON st.parent = si.name
        WHERE si.docstatus = 1
            AND st.sales_person = %(sales_person)s
            {where_clause}
    """,
        values,
        as_dict=1,
    )

    return flt(result[0].total) if result and result[0].total else 0


def get_sil_sales_for_person(sales_person, filters):
    """
    Get SIL sales for a sales person
    """
    conditions = []
    values = {"sales_person": sales_person}

    # Add date filters if provided
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = ""
    if conditions:
        where_clause = "AND " + " AND ".join(conditions)

    result = frappe.db.sql(
        f"""
        SELECT SUM(sii.amount) as total
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Team` st ON st.parent = si.name
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN `tabItem` item ON item.name = sii.item_code
        WHERE si.docstatus = 1
            AND st.sales_person = %(sales_person)s
            AND item.item_group = 'SIL'
            {where_clause}
    """,
        values,
        as_dict=1,
    )

    return flt(result[0].total) if result and result[0].total else 0


