{
    "name": "Quotation documents",
    "summary": """Validates if a quotation has a backup
    document to convert it to purchase order""",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "FenixERP",
    "website": "https://github.com/waalo-fenixdoo/custom-alutrafic",
    "author": "Joseph Armas / Ads Software",
    "maintainers": ["josarmas9416"],
    "license": "OPL-1",
    "application": False,
    "installable": True,
    "depends": ["base", "purchase"],
    "data": [
        "views/purchase_order_views.xml",
    ],
}
