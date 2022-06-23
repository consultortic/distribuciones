{
    "name": "Partner Company Documents",
    "summary": """create a list of documents that will be
    available for upload when creating a new contact
    """,
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "FenixERP",
    "website": "https://github.com/waalo-fenixdoo/custom-alutrafic",
    "author": "Joseph Armas / Ads Software",
    "maintainers": ["josarmas9416"],
    "license": "OPL-1",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "contacts",
        "crm",
        "sale_management",
        "chart_of_accounts_group",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/document_type_views.xml",
        "views/res_partner_views.xml",
    ],
}
