import frappe
from frappe import _
from datetime import datetime, timedelta

def execute(filters=None):
    """
    Server-side function to fetch and process data for the Sales Target Achievement Report.
    The report calculates actual revenue and SIL sales against defined targets.
    """
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_report_data(filters)
    
    # Sort data alphabetically by Sales Person name
    data.sort(key=lambda x: x.get('sales_person', ''))

    return columns, data

def get_columns():
    """
    Defines the structure and type of columns for the report.
    These column definitions are used by the client-side JavaScript.
    """
    return [
        {
            "fieldname": "sales_person",
            "label": _("Sales Person"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 150
        },
        {
            "fieldname": "total_revenue",
            "label": _("Total Revenue"),
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "width": 140
        },
        {
            "fieldname": "revenue_goal",
            "label": _("Revenue Goal"),
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "width": 140
        },
        {
            "fieldname": "total_sil",
            "label": _("Total SIL"),
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "width": 120
        },
        {
            "fieldname": "goal_sil",
            "label": _("Goal SIL"),
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "width": 120
        },
        {
            "fieldname": "revenue_goal_percent",
            "label": _("Revenue Goal %"),
            "fieldtype": "Float",
            "width": 140,
            "precision": 2,
            "formatter": "frappe.utils.formatters.percentage"
        },
        {
            "fieldname": "sil_goal_percent",
            "label": _("SIL Goal %"),
            "fieldtype": "Float",
            "width": 140,
            "precision": 2,
            "formatter": "frappe.utils.formatters.percentage"
        },
    ]

def get_report_data(filters):
    """
    Fetches actual sales data and target data, and calculates achievements.
    NOTE: The target calculation logic (Target Distribution) is complex and requires custom
    logic not possible in a simple report. For this draft, we will assume the
    `Target Amount` on the main Sales Person Target is the amount for the *period*.
    A robust solution would query the child table `Sales Person Target Distribution`.
    """
    start_date = filters.get("from_date")
    end_date = filters.get("to_date")
    fiscal_year = filters.get("fiscal_year")
    company = filters.get("company") or frappe.defaults.get_global_default("company")
    
    if not start_date or not end_date or not fiscal_year:
        frappe.throw(_("Please select a Fiscal Year, From Date, and To Date."))

    # 1. Fetch Sales Person Target data
    # We aggregate targets grouped by Sales Person
    targets = frappe.get_all(
        "Sales Person Target",
        filters={
            "fiscal_year": fiscal_year,
            "docstatus": 0, # Active targets
        },
        fields=["sales_person", "item_group", "target_amount"],
        as_list=True
    )

    target_map = {}
    sales_persons = set()
    
    # Process targets and map them to Sales Persons
    for sp, item_group, amount in targets:
        if not sp: continue
        sales_persons.add(sp)
        if sp not in target_map:
            target_map[sp] = {"revenue_goal": 0.0, "goal_sil": 0.0}

        # The system often uses a null/empty item_group for overall revenue goal
        if item_group in ["", "All Item Groups", None]:
            target_map[sp]["revenue_goal"] += amount
        elif item_group == "SIL":
            target_map[sp]["goal_sil"] += amount
            
    # 2. Fetch Actual Sales (Total Revenue and SIL)
    
    # Get all submitted Sales Invoices within the period
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "posting_date": ["between", [start_date, end_date]],
            "docstatus": 1, # Submitted
            "company": company,
        },
        fields=["name", "base_net_total", "base_grand_total", "sales_person"]
    )
    
    invoice_names = [inv.name for inv in invoices]
    
    # Get actual sales grouped by Sales Person
    actual_map = {sp: {"total_revenue": 0.0, "total_sil": 0.0} for sp in sales_persons}

    # Total Revenue (sum of base_net_total from the invoice header)
    for inv in invoices:
        if inv.sales_person and inv.sales_person in actual_map:
            actual_map[inv.sales_person]["total_revenue"] += inv.base_net_total

    # Total SIL Sales (sum of net amount for items belonging to 'SIL' group)
    if invoice_names:
        sil_sales = frappe.db.sql("""
            SELECT 
                si.sales_person,
                SUM(sii.base_net_amount)
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON si.name = sii.parent
            JOIN `tabItem` i ON i.item_code = sii.item_code
            WHERE 
                si.name IN %(invoice_names)s AND
                si.docstatus = 1 AND
                i.item_group = 'SIL'
            GROUP BY 
                si.sales_person
        """, {"invoice_names": invoice_names}, as_dict=True)

        for row in sil_sales:
            sp = row['sales_person']
            amount = row['SUM(sii.base_net_amount)']
            if sp in actual_map:
                actual_map[sp]["total_sil"] += amount

    # 3. Compile Final Data and Calculate Percentages
    report_data = []

    for sp in sales_persons:
        goals = target_map.get(sp, {"revenue_goal": 0.0, "goal_sil": 0.0})
        actuals = actual_map.get(sp, {"total_revenue": 0.0, "total_sil": 0.0})
        
        # Calculate percentages, avoiding division by zero
        revenue_goal_p = (actuals["total_revenue"] / goals["revenue_goal"]) * 100 if goals["revenue_goal"] else 0.0
        sil_goal_p = (actuals["total_sil"] / goals["goal_sil"]) * 100 if goals["goal_sil"] else 0.0

        report_data.append({
            "sales_person": sp,
            "total_revenue": actuals["total_revenue"],
            "revenue_goal": goals["revenue_goal"],
            "total_sil": actuals["total_sil"],
            "goal_sil": goals["goal_sil"],
            "revenue_goal_percent": revenue_goal_p,
            "sil_goal_percent": sil_goal_p,
        })

    return report_data
