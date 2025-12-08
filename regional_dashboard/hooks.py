app_name = "regional_dashboard"
app_title = "Regional Dashboard"
app_publisher = "SurgiShop"
app_email = "gary.starr@surgishop.com"
app_description = "Regional Dashboard"
app_license = "MIT"
# The default module for this app, which is also the module under which
# the report will be created in the UI.
app_include_js = "/assets/regional_dashboard/js/regional_dashboard.js"
app_include_css = "/assets/regional_dashboard/css/regional_dashboard.css"

# Reports
# -------
# Hook to define required reports (optional, but good practice for custom apps)
# This assumes the report is linked to the "Selling" Module in the ERPNext UI.
required_reports = [
    {
        "name": "Sales Target Achievement",
        "doctype": "Sales Person",
        "is_standard": "Yes", # Links to the script files
        "module": "Regional Dashboard",
        "report_type": "Script Report"
    }
]
