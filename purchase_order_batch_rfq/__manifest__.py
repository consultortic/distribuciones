{
    "name": "Batch Request for Quotation",
    "summary": """Adds the functionality to create
    requests for quotation in batches
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
    "depends": ["base", "purchase"],
    "data": ["security/ir.model.access.csv", "wizards/purchase_order_batch.xml"],
}
