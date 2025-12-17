app_name = "regional_dashboard"
app_title = "Regional Dashboard"
app_publisher = "SurgiShop"
app_email = "gary.starr@surgishop.com"
app_description = "Regional Dashboard"
app_license = "MIT"

# Ship the report via fixtures so it is created on the site even if modules.txt
# is intentionally kept empty (common on managed/cloud setups).
fixtures = [
	{"dt": "Report", "filters": [["name", "=", "Regional Dashboard"]]},
]