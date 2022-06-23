# -*- coding: utf-8 -*-
import base64
from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_chatroom_report(self):
        self.ensure_one()
        Attachment = self.env['ir.attachment']
        invoice_print = self.action_invoice_print()
        report_name = (invoice_print or {}).get('report_name')
        if not report_name:
            raise ValidationError(_('Configure Reports.'))
        report_id = self.env['ir.actions.report']._get_report_from_name(report_name)
        pdf = report_id._render_qweb_pdf(self.id)
        b64_pdf = base64.b64encode(pdf[0])
        name = (self._get_report_base_filename() or self.name or 'INV').replace('/', '_') + '.pdf'
        attac_id = Attachment.create({'name': name,
                                      'type': 'binary',
                                      'datas': b64_pdf,
                                      # 'store_fname': name,
                                      'access_token': Attachment._generate_access_token(),
                                      'res_model': 'acrux.chat.message',
                                      'res_id': 0,
                                      'delete_old': True})
        return attac_id
