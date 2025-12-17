import frappe


REPORT_NAME = "Regional Dashboard"

# NOTE: This script is executed via frappe.utils.safe_exec.safe_exec, where imports are blocked
# (builtins.__import__ is removed). So: NO "import frappe" inside the script.
SAFE_EXEC_REPORT_SCRIPT = r"""
def _flt(val):
    try:
        return float(val or 0)
    except Exception:
        return 0.0


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters) or []
    return columns, data


def get_columns():
    return [
        {"fieldname": "sales_person", "label": "REP", "fieldtype": "Link", "options": "Sales Person", "width": 180},
        {"fieldname": "total_sales", "label": "Current Account Rev", "fieldtype": "Currency", "width": 150},
        {"fieldname": "sales_goal", "label": "Account Goal", "fieldtype": "Currency", "width": 130},
        {"fieldname": "current_sil", "label": "Current SIL", "fieldtype": "Currency", "width": 130},
        {"fieldname": "sil_goal", "label": "Goal SIL", "fieldtype": "Currency", "width": 130},
        {"fieldname": "sales_goal_percent", "label": "REV Goal", "fieldtype": "Data", "width": 120},
        {"fieldname": "sil_goal_percent", "label": "SIL Goal", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
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
        sales_person_name = sp.get("name") if isinstance(sp, dict) else getattr(sp, "name", sp)

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

        sales_goal = _flt(targets[0].get("sales_goal")) if targets else 0
        sil_goal = _flt(targets[0].get("sil_goal")) if targets else 0

        total_sales = get_sales_for_person(sales_person_name, filters)
        current_sil = get_sil_sales_for_person(sales_person_name, filters)

        sales_goal_percent = f"{round((_flt(total_sales) / _flt(sales_goal) * 100), 2)}%" if sales_goal > 0 else "0%"
        sil_goal_percent = f"{round((_flt(current_sil) / _flt(sil_goal) * 100), 2)}%" if sil_goal > 0 else "0%"

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
    conditions = []
    values = {"sales_person": sales_person}

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = ("AND " + " AND ".join(conditions)) if conditions else ""

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

    return _flt(result[0].get("total")) if result else 0


def get_sil_sales_for_person(sales_person, filters):
    conditions = []
    values = {"sales_person": sales_person}

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    where_clause = ("AND " + " AND ".join(conditions)) if conditions else ""

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

    return _flt(result[0].get("total")) if result else 0
"""


def _upsert_report():
    if frappe.db.exists("Report", REPORT_NAME):
        report = frappe.get_doc("Report", REPORT_NAME)
    else:
        report = frappe.new_doc("Report")
        # Doctype Report uses report_name as its name in most setups.
        report.report_name = REPORT_NAME

    report.report_type = "Script Report"
    report.ref_doctype = "Sales Person"

    # Keep as custom (non-standard) so it doesn't depend on modules.txt / module_app mapping.
    report.is_standard = "No"
    report.module = "Selling"

    # Critical: avoid imports inside safe_exec by shipping a script without import statements.
    report.report_script = SAFE_EXEC_REPORT_SCRIPT.strip()
    report.javascript = ""
    report.disabled = 0

    # Roles: only include roles that exist on ERPNext by default.
    report.set("roles", [])
    for role in ("Sales User", "Sales Manager"):
        report.append("roles", {"role": role})

    report.save(ignore_permissions=True)


def after_migrate():
    # Keep it safe on fresh installs where ERPNext might not be ready.
    try:
        _upsert_report()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "regional_dashboard: failed to upsert Regional Dashboard report")


