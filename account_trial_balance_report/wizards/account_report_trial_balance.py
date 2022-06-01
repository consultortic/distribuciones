import base64
import io

import xlwt

from odoo import fields, models


class AccountCommonReportTrialBalance(models.TransientModel):
    _name = "accounting.report.trial.balance"
    _description = "Account Report Trial Balance"
    _inherit = "accounting.report"

    display_account = fields.Selection(
        [
            ("all", "All"),
            ("movement", "With movements"),
            ("not_zero", "With balance is not equal to 0"),
        ],
        string="Display Accounts",
        required=True,
        default="movement",
    )

    def _print_trial_balance_excel_report(self, report_lines):
        # filename = self.account_report_id.name
        filename = "balance_comprobacion.xls"
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("Sheet 1")
        date_format = xlwt.XFStyle()
        date_format.num_format_str = "dd/mm/yyyy"
        style_header = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on,color black; "
            "align: horiz center"
        )
        worksheet.row(0).height_mismatch = True
        worksheet.row(0).height = 500
        worksheet.write_merge(0, 0, 0, 6, "Balance de Comprobación", style=style_header)
        worksheet.write(2, 0, "Incluir")

        worksheet.write(
            3,
            0,
            "Todos los asientos validados"
            if self.target_move == "posted"
            else "Todos los asientos",
        )
        worksheet.write(3, 2, "Desde:")
        if self.date_from:
            worksheet.write(3, 3, self.date_from, date_format)

        worksheet.write(3, 4, "Hasta:")
        if self.date_to:
            worksheet.write(3, 5, self.date_to, date_format)

        worksheet.write(5, 0, "Código de Cuenta")
        worksheet.write(5, 1, "Nombre de Cuenta")
        worksheet.write(5, 2, "Saldo Anterior")
        worksheet.write(5, 3, "Debe")
        worksheet.write(5, 4, "Haber")
        worksheet.write(5, 5, "Saldo Final")

        row = 6
        col = 0

        sum_initial_balance = sum_debit = sum_credit = sum_balance = 0.0
        max_level = (
            max(report_lines, key=lambda l: l["level"])["level"] if report_lines else 0
        )

        for line in report_lines:
            if not (line["level"] < max_level and line["type"] == "view"):
                sum_initial_balance = sum_initial_balance + line["initial_balance"]
                sum_debit = sum_debit + line["debit"]
                sum_credit = sum_credit + line["credit"]
                sum_balance = sum_balance + line["balance"]

            if line.get("level") != 0:
                if line.get("type") == "view":
                    style_line = xlwt.easyxf("font:bold off,color black;")
                else:
                    style_line = xlwt.easyxf("font:bold on,color black;")
                worksheet.write(row, col + 0, line.get("code"), style_line)
                worksheet.write(row, col + 1, line.get("name"), style_line)
                worksheet.write(row, col + 2, line.get("initial_balance"), style_line)
                worksheet.write(row, col + 3, line.get("debit"), style_line)
                worksheet.write(row, col + 4, line.get("credit"), style_line)
                worksheet.write(row, col + 5, line.get("balance"), style_line)
                row += 1

        style_line = xlwt.easyxf("font:bold on,color black;")
        row += 1
        worksheet.write(row, col + 1, "Total General:", style_line)
        worksheet.write(row, col + 2, sum_initial_balance, style_line)
        worksheet.write(row, col + 3, sum_debit, style_line)
        worksheet.write(row, col + 4, sum_credit, style_line)
        worksheet.write(row, col + 5, sum_balance, style_line)

        fp = io.BytesIO()
        workbook.save(fp)

        export_id = self.env["excel.report"].create(
            {"excel_file": base64.encodestring(fp.getvalue()), "file_name": filename}
        )
        res = {
            "view_mode": "form",
            "res_id": export_id.id,
            "res_model": "excel.report",
            "type": "ir.actions.act_window",
            "target": "new",
        }
        return res

    def check_report(self):
        res = super(AccountCommonReportTrialBalance, self).check_report()
        if self._context.get("report_type") == "excel":
            data = res.get("data")
            obj_report = self.env[
                "report.account_trial_balance_report.report_trial_balance"
            ]
            report_lines = obj_report.get_account_lines(data.get("form", []))
            return self._print_trial_balance_excel_report(report_lines)
        else:
            return res

    def _print_report(self, data):
        data["form"].update(
            self.read(
                [
                    "display_account",
                    "date_from_cmp",
                    "debit_credit",
                    "date_to_cmp",
                    "filter_cmp",
                    "account_report_id",
                    "enable_filter",
                    "label_filter",
                    "target_move",
                ]
            )[0]
        )
        return self.env.ref(
            "account_trial_balance_report.action_report_trial_balance"
        ).report_action(self, data=data, config=False)
