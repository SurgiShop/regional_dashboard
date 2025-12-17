app_name = "regional_dashboard"
app_title = "Regional Dashboard"
app_publisher = "SurgiShop"
app_email = "gary.starr@surgishop.com"
app_description = "Regional Dashboard"
app_license = "MIT"

# Ensure the report exists and stays runnable on managed environments where
# server scripts run in safe_exec (imports blocked) and modules.txt is kept empty.
after_migrate = ["regional_dashboard.install.after_migrate"]