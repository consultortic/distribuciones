##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - 2020 Steigend IT Solutions (Omal Bastin)
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    "name": "Parent Account (Chart of Account Hierarchy)",
    "summary": """
        Adds Parent account and ability to open chart of account
        list view based on the date and moves""",
    "author": "Omal Bastin / O4ODOO",
    "license": "OPL-1",
    "website": "https://github.com/waalo-fenixdoo/accounting-workflow",
    "category": "Accounting",
    "version": "14.0.1.0.2",
    "depends": ["account"],
    "data": [
        "security/account_parent_security.xml",
        "security/ir.model.access.csv",
        "views/account_view.xml",
        "views/open_chart.xml",
        "data/account_type_data.xml",
        "views/account_parent_template.xml",
        "views/report_coa_hierarchy.xml",
    ],
    "demo": [],
    "qweb": [
        "static/src/xml/account_parent_backend.xml",
    ],
    "currency": "EUR",
    "price": "25.0",
    "images": ["static/description/account_parent_9.png"],
    "installable": True,
    "post_init_hook": "_assign_account_parent",
}
