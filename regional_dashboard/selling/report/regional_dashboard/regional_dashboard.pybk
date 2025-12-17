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
    
    # Ensure we always return a list, even if empty
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
            "label": _("Sales Person"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180
        },
        {
            "fieldname": "total_sales",
            "label": _("Total Sales"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "sales_goal",
            "label": _("Sales Goal"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "current_sil",
            "label": _("Current SIL"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "sil_goal",
            "label": _("SIL Goal"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "sales_goal_percent",
            "label": _("Sales Goal %"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "sil_goal_percent",
            "label": _("SIL Goal %"),
            "fieldtype": "Percent",
            "width": 120
        }
    ]

def get_data(filters):
    """
    Fetch and return report data - SIMPLIFIED FOR TESTING
    """
    if not filters:
        filters = {}
    
    # Get all active sales persons
    sales_persons = frappe.get_all(
        "Sales Person",
        filters={"enabled": 1},
        fields=["name"],
        order_by="name asc"
    )
    
    # Return empty list if no sales persons found
    if not sales_persons:
        return []
    
    data = []
    
    # Just return sales person names with dummy data to test
    for sp in sales_persons:
        data.append({
            "sales_person": sp.name,
            "total_sales": 1000,
            "sales_goal": 5000,
            "current_sil": 500,
            "sil_goal": 2000,
            "sales_goal_percent": 20,
            "sil_goal_percent": 25
        })
    
    return data
