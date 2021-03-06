{
    "name": "Trial Balance Report",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "Antonio Silva",
    "website": "https://github.com/waalo-fenixdoo/accounting-workflow",
    "depends": ["account_balance_sheet_report"],
    "data": [
        "wizards/trial_balance_wizard.xml",
        "report/report.xml",
        "report/report_financial_trial_balance_templates.xml",
        "report/report_financial_trial_balance.xml",
        "security/ir.model.access.csv",
        "security/multi-company.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
