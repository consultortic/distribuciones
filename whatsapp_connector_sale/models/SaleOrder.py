# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    conversation_id = fields.Many2one('acrux.chat.conversation', 'ChatRoom', ondelete='set null', copy=False)

    def get_chatroom_report(self):
        self.ensure_one()
        Attachment = self.env['ir.attachment']
        report_id = self.env.ref('sale.action_report_saleorder')
        pdf = report_id._render_qweb_pdf(self.id)
        b64_pdf = base64.b64encode(pdf[0])
        name = ((self.state in ('draft', 'sent') and _('Quotation - %s') % self.name) or
                _('Order - %s') % self.name)
        name = '%s.pdf' % name
        attac_id = Attachment.create({'name': name,
                                      'type': 'binary',
                                      'datas': b64_pdf,
                                      # 'store_fname': name,
                                      'access_token': Attachment._generate_access_token(),
                                      'res_model': 'acrux.chat.message',
                                      'res_id': 0,
                                      'delete_old': True, })
        return attac_id
