import base64
import io

import xlwt

from odoo import fields, models


class AccountCommonReportBalance(models.TransientModel):
    _name = "accounting.report.balance"
    _description = "Account Report Balance"
    _inherit = "accounting.report"

    account_level = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
        string="Nivel",
        required=True,
        default="1",
    )

    def _print_balance_sheet_excel_report(self, report_lines):
        # filename = self.account_report_id.name
        filename = "balance_general.xls"
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("Sheet 1")
        date_format = xlwt.XFStyle()
        date_format.num_format_str = "dd/mm/yyyy"
        style_header = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on,color black;"
            " align: horiz center"
        )
        worksheet.row(0).height_mismatch = True
        worksheet.row(0).height = 500
        worksheet.write_merge(0, 0, 0, 3, "Balance General", style=style_header)
        worksheet.write(2, 0, "Incluir")

        worksheet.write(
            3,
            0,
            "Todos los asientos validados"
            if self.target_move == "posted"
            else "Todos los asientos",
        )
        worksheet.write(3, 1, "Fecha de corte:")

        if self.date_to:
            worksheet.write(3, 2, self.date_to, date_format)

        worksheet.write(5, 0, "Código de Cuenta")
        worksheet.write(5, 1, "Nombre de Cuenta")
        worksheet.write(5, 2, "Saldo")
        row = 6
        col = 0
        for lines in report_lines:
            if lines.get("level") != 0:
                if lines.get("level") != 1:
                    style_line = xlwt.easyxf("font:bold off,color black;")
                else:
                    style_line = xlwt.easyxf("font:bold on,color black;")
                worksheet.write(row, col, lines.get("code"), style_line)
                worksheet.write(row, col + 1, lines.get("name"), style_line)
                worksheet.write(row, col + 2, lines.get("balance"), style_line)
                row += 1
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

    def _print_report(self, data):
        data["form"].update(
            self.read(
                [
                    "account_level",
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
            "account_balance_sheet_report.action_report_financial_balance"
        ).report_action(self, data=data, config=False)

    def check_report(self):
        res = super(AccountCommonReportBalance, self).check_report()
        if self._context.get("report_type") == "excel":
            data = res.get("data")
            obj_report = self.env[
                "report.account_balance_sheet_report.report_financial_balance"
            ]
            report_lines = obj_report.get_account_lines(data.get("form", []))
            return self._print_balance_sheet_excel_report(report_lines)
        else:
            return res
