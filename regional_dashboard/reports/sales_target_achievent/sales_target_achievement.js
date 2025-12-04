/*
* Client-side script for the Sales Target Achievement Report.
* This file defines the report's filters and provides custom formatting.
*/

frappe.query_reports["Sales Target Achievement"] = {
    "filters": [
        {
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "reqd": 1,
            "default": frappe.defaults.get_user_default("year_start_date")
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.now_date(), -3)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.now_date()
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        }
    ],

    // Custom formatter for the percentage fields to add coloring
    "formatter": function (value, row_details, column, data) {
        if (column.fieldname === 'revenue_goal_percent' || column.fieldname === 'sil_goal_percent') {
            const percentage = parseFloat(value);
            let color = 'text-gray-700';
            
            if (percentage >= 100) {
                // Green for achieving 100% or more
                color = 'text-green-600 font-bold';
            } else if (percentage >= 75) {
                // Orange/Yellow for close to target
                color = 'text-orange-500';
            } else if (percentage > 0) {
                // Red for far below target
                color = 'text-red-500';
            }

            return `<span class="${color}">${frappe.format(value, column)}</span>`;
        }
        return value;
    }
};
