import time

from odoo import _, api, models
from odoo.exceptions import UserError


class ReportFinancialBalance(models.AbstractModel):
    _name = "report.account_trial_balance_report.report_trial_balance"
    _description = "Trial Balance Report"

    def get_account_lines(self, data):
        display_account = data.get("display_account")
        amount_context = data.get("used_context")
        if data.get("date_from"):
            amount_context.update({"show_initial_balance": True})
        lines = []

        def get_account_childs(account, level=1):
            initial_balance = account.with_context(amount_context).initial_balance
            balance = account.with_context(amount_context).balance
            vals = {
                "code": account.code,
                "name": account.name,
                "initial_balance": initial_balance,
                "debit": account.with_context(amount_context).debit,
                "credit": account.with_context(amount_context).credit,
                "balance": initial_balance + balance,
                "type": account.user_type_id.type,
                "level": level,
                "account_type": False,
            }

            currency = (
                account.currency_id
                and account.currency_id
                or account.company_id.currency_id
            )
            if display_account == "all":
                lines.append(vals)
            if display_account == "movement" and (
                not currency.is_zero(vals["debit"])
                or not currency.is_zero(vals["credit"])
            ):
                lines.append(vals)
            if display_account == "not_zero" and not currency.is_zero(balance):
                lines.append(vals)
            if display_account == "not_zero" and vals["type"] == "view":
                lines.append(vals)

            for child_account in account.with_context(show_parent_account=True).search(
                [
                    ("parent_id", "=", account.id),
                    ("company_id", "=", self.env.company.id),
                ]
            ):
                get_account_childs(child_account, level + 1)

        accounts_root = (
            self.env["account.account"]
            .with_context(show_parent_account=True)
            .search(
                [("parent_id", "=", False), ("company_id", "=", self.env.company.id)]
            )
        )
        for account_root in accounts_root:
            get_account_childs(account_root, 1)

        return lines

    @api.model
    def _get_report_values(self, docids, data=None):
        if (
            not data.get("form")
            or not self.env.context.get("active_model")
            or not self.env.context.get("active_id")
        ):
            raise UserError(
                _("Form content is missing, this report cannot be printed.")
            )

        model = self.env.context.get("active_model")
        docs = self.env[model].browse(self.env.context.get("active_id"))
        report_lines = self.get_account_lines(data.get("form"))
        sum_initial_balance = sum_debit = sum_credit = sum_balance = 0.0
        max_level = (
            max(report_lines, key=lambda l: l["level"])["level"] if report_lines else 0
        )

        for line in report_lines:
            if line["level"] < max_level and line["type"] == "view":
                continue
            sum_initial_balance = sum_initial_balance + line["initial_balance"]
            sum_debit = sum_debit + line["debit"]
            sum_credit = sum_credit + line["credit"]
            sum_balance = sum_balance + line["balance"]

        return {
            "doc_ids": self.ids,
            "doc_model": model,
            "data": data["form"],
            "docs": docs,
            "time": time,
            "get_account_lines": report_lines,
            "sum_initial_balance": sum_initial_balance,
            "sum_debit": sum_debit,
            "sum_credit": sum_credit,
            "sum_balance": sum_balance,
        }
