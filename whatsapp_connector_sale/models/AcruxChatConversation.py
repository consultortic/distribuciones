# -*- coding: utf-8 -*-
from odoo import models
from odoo import fields
from odoo import api


class AcruxChatConversation(models.Model):
    _inherit = 'acrux.chat.conversation'

    sale_order_id = fields.Many2one('sale.order', 'Sale Order', ondelete='set null')

    def get_to_done(self):
        out = super(AcruxChatConversation, self).get_to_done()
        out['sale_order_id'] = False
        return out

    def get_to_current(self):
        out = super(AcruxChatConversation, self).get_to_current()
        out['sale_order_id'] = False
        return out

    def get_to_new(self):
        out = super(AcruxChatConversation, self).get_to_new()
        out['sale_order_id'] = False
        return out

    @api.model
    def get_fields_to_read(self):
        out = super(AcruxChatConversation, self).get_fields_to_read()
        out.extend(['sale_order_id'])
        return out
