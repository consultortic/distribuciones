import time

from odoo import _, api, models
from odoo.exceptions import UserError


class ReportFinancialBalance(models.AbstractModel):
    _name = "report.account_balance_sheet_report.report_financial_balance"

    def get_account_lines(self, data):
        obj_account = self.env["account.account"]
        lines = []
        leability_plus_equity = 0.0
        income = obj_account.search([("code", "=", "4")], limit=1)
        income = income and income.balance or 0.0
        expense = obj_account.search([("code", "=", "5")], limit=1)
        expense = expense and expense.balance or 0.0
        cost_of_revenue = obj_account.search([("code", "=", "6")], limit=1)
        cost_of_revenue = cost_of_revenue and cost_of_revenue.balance or 0.0
        profit_or_loss = income - expense - cost_of_revenue

        account_level = int(data.get("account_level", 1))
        account_root = (
            self.env["account.account"]
            .with_context(show_parent_account=True)
            .search(
                [
                    ("parent_id", "=", False),
                    ("name", "=", "PUC"),
                    ("company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
        )

        if account_root:
            income = obj_account.with_context(show_parent_account=True).search(
                [("code", "=like", "4%"), ("parent_id", "=", account_root.id)], limit=1
            )
            income = (
                income and income.with_context(data.get("used_context")).balance or 0.0
            )
            expense = obj_account.with_context(show_parent_account=True).search(
                [("code", "=like", "5%"), ("parent_id", "=", account_root.id)], limit=1
            )
            expense = (
                expense
                and expense.with_context(data.get("used_context")).balance
                or 0.0
            )
            cost_of_revenue = obj_account.with_context(show_parent_account=True).search(
                [("code", "=like", "6%"), ("parent_id", "=", account_root.id)], limit=1
            )
            cost_of_revenue = (
                cost_of_revenue
                and cost_of_revenue.with_context(data.get("used_context")).balance
                or 0.0
            )
            profit_or_loss = income + expense + cost_of_revenue

            level_one_accounts = (
                self.env["account.account"]
                .with_context(show_parent_account=True)
                .search([("parent_id", "=", account_root.id)], order="code")
            )
            for account in level_one_accounts.filtered(
                lambda acc: acc.code and acc.code[0] in ("1", "2", "3")
            ):
                vals = {
                    "code": account.code,
                    "name": account.name,
                    "balance": account.with_context(data.get("used_context")).balance,
                    "type": "account",
                    "level": 1,
                    "account_type": False,
                }
                lines.append(vals)
                if account.code[0] in ("2", "3"):
                    leability_plus_equity += vals["balance"]

                if account_level < 2:
                    continue
                level_two_accounts = (
                    self.env["account.account"]
                    .with_context(show_parent_account=True)
                    .search([("parent_id", "=", account.id)], order="code")
                )
                for account in level_two_accounts.filtered(
                    lambda acc: acc.with_context(data.get("used_context")).balance
                ):
                    vals = {
                        "code": account.code,
                        "name": account.name,
                        "balance": account.with_context(
                            data.get("used_context")
                        ).balance,
                        "type": "account",
                        "level": 2,
                        "account_type": False,
                    }
                    lines.append(vals)
                    if account_level < 3:
                        continue
                    level_three_accounts = (
                        self.env["account.account"]
                        .with_context(show_parent_account=True)
                        .search([("parent_id", "=", account.id)], order="code")
                    )
                    for account in level_three_accounts.filtered(
                        lambda acc: acc.with_context(data.get("used_context")).balance
                    ):
                        vals = {
                            "code": account.code,
                            "name": account.name,
                            "balance": account.with_context(
                                data.get("used_context")
                            ).balance,
                            "type": "account",
                            "level": 3,
                            "account_type": False,
                        }
                        lines.append(vals)
                        if account_level < 4:
                            continue
                        level_four_accounts = (
                            self.env["account.account"]
                            .with_context(show_parent_account=True)
                            .search([("parent_id", "=", account.id)], order="code")
                        )
                        for account in level_four_accounts.filtered(
                            lambda acc: acc.with_context(
                                data.get("used_context")
                            ).balance
                        ):
                            vals = {
                                "code": account.code,
                                "name": account.name,
                                "balance": account.with_context(
                                    data.get("used_context")
                                ).balance,
                                "type": "account",
                                "level": 4,
                                "account_type": False,
                            }
                            lines.append(vals)
                            if account_level < 5:
                                continue
                            level_five_accounts = (
                                self.env["account.account"]
                                .with_context(show_parent_account=True)
                                .search([("parent_id", "=", account.id)], order="code")
                            )
                            for account in level_five_accounts.filtered(
                                lambda acc: acc.with_context(
                                    data.get("used_context")
                                ).balance
                            ):
                                vals = {
                                    "code": account.code,
                                    "name": account.name,
                                    "balance": account.with_context(
                                        data.get("used_context")
                                    ).balance,
                                    "type": "account",
                                    "level": 5,
                                    "account_type": False,
                                }
                                lines.append(vals)
            vals = {
                "code": "",
                "name": "RESULTADO DEL PERIODO :",
                "balance": profit_or_loss,
                "type": "account",
                "level": 1,
                "account_type": False,
            }
            lines.append(vals)

            vals = {
                "code": "",
                "name": "TOTAL PASIVO + PATRIMONIO :",
                "balance": leability_plus_equity + profit_or_loss,
                "type": "account",
                "level": 1,
                "account_type": False,
            }
            lines.append(vals)
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

        active_model = self.env.context.get("active_model")
        docs = self.env[active_model].browse(self.env.context.get("active_id"))
        report_lines = self.get_account_lines(data.get("form"))
        return {
            "doc_ids": self.ids,
            "doc_model": active_model,
            "data": data["form"],
            "docs": docs,
            "time": time,
            "get_account_lines": report_lines,
        }
