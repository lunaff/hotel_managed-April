{
    "name": "Hotel Management",
    "version": "17.0.1.0.0",
    "category": "Addons",
    "summary": "Hotel is an addons for Oddo 17 to manage Hotel",
    "description": """Hotel is an addons for Oddo 17 to manage Hotel""",
    "author": "April",
    "company": "April",
    "maintainer": "April",
    "depends": ["web", "mail"],
    "application": True,
    "data": [
        # "security/library_security.xml",
        "security/ir.model.access.csv",
        "report/report_pdf.xml",
        "views/configuration.xml",
        "views/hotel_menu.xml",
        "views/reporting_excel_template.xml",
        "views/reporting_pdf_template.xml",
        "views/reporting.xml",
        "views/reservation.xml"

    ], 
    "assets": {
    },
    "installable": True,
    "auto_install": False,
    "application": True,

}