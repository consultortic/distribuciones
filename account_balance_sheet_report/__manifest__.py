{
    "name": "Balance Sheet Report",
    "version": "14.0.1.0.1",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": """
        Balance Sheet Report.
        """,
    "author": "Antonio Silva",
    "website": "https://github.com/waalo-fenixdoo/accounting-workflow",
    "depends": ["accounting_pdf_reports", "account_parent"],
    "data": [
        "wizards/balance_sheet_wizard.xml",
        "report/report.xml",
        "report/excel_report.xml",
        "report/report_financial_balance_templates.xml",
        "report/report_financial_balance.xml",
        "security/ir.model.access.csv",
        "security/multi_company.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
