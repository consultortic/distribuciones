# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ChatMessageWizard(models.TransientModel):
    _name = 'acrux.chat.message.wizard'
    _description = 'ChatRoom Message'

    def _domain_conversation_id(self):
        conversation_id = self.env.context.get('conversation_id') or self.env.context.get('default_conversation_id')
        if self.env.context.get('is_acrux_chat_room') and conversation_id:
            return [('id', 'in', [conversation_id])]
        partner_id = self.env['res.partner'].browse(self.env.context.get('default_partner_id', []))
        conv_ids = partner_id.contact_ids.ids + [conversation_id]
        conv_ids = list(set([x for x in conv_ids if x]))
        return [('id', 'in', conv_ids)] if conv_ids else []

    new_number = fields.Boolean('New number')
    number = fields.Char('Number')
    numbers_available = fields.Text('Available', compute='_compute_numbers_available', store=False, readonly=True)
    text = fields.Text('Message', required=True)
    partner_id = fields.Many2one('res.partner')
    conversation_id = fields.Many2one('acrux.chat.conversation', string='ChatRoom', ondelete='set null',
                                      domain=_domain_conversation_id)
    connector_id = fields.Many2one('acrux.chat.connector', string='Channel', ondelete='set null')
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', ondelete='set null')
    invisible_top = fields.Boolean()

    @api.depends('partner_id')
    def _compute_numbers_available(self):
        for rec in self:
            numbers = False
            p = rec.partner_id
            if p and p.mobile and p.phone != p.mobile:
                numbers = _('Mobile: %s\nPhone: %s') % (p.mobile, p.phone)
            rec.numbers_available = numbers

    @api.model
    def default_get_conversation(self):
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        conversation_id = self.env.context.get('conversation_id') or self.env.context.get('default_conversation_id')
        if not conversation_id and active_id and active_model \
                and 'conversation_id' in self.env[active_model]._fields:
            conversation_id = self.env[active_model].browse(active_id).conversation_id.id
        if not conversation_id and self.env.context.get('default_partner_id'):
            contact_ids = self.env['res.partner'].browse([self.env.context.get('default_partner_id')]).contact_ids
            conversation_id = contact_ids[0].id if contact_ids else False
        return conversation_id

    @api.model
    def default_get_attachment(self):
        if not self.use_template():
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
            if active_id and hasattr(self.env[active_model], 'get_chatroom_report'):
                attachment_id = self.env[active_model].browse([active_id]).get_chatroom_report()
                return attachment_id.id
        return False

    @api.model
    def default_get(self, default_fields):
        vals = super(ChatMessageWizard, self).default_get(default_fields)
        if 'conversation_id' in default_fields:
            vals['conversation_id'] = self.default_get_conversation()
        if 'attachment_id' in default_fields:
            vals['attachment_id'] = self.default_get_attachment()
        if 'invisible_top' in default_fields and 'default_invisible_top' not in self.env.context \
                and self.env.context.get('is_acrux_chat_room') and vals.get('conversation_id'):
            vals['invisible_top'] = True
        return vals

    def use_template(self):
        return False

    @api.onchange('new_number')
    def onchange_new_number(self):
        if self.partner_id:
            self.number = self.partner_id.mobile or self.partner_id.phone or False
        if self.new_number:
            self.conversation_id = False
            self.connector_id = self.env['acrux.chat.connector'].search([])[0].id
        else:
            self.connector_id = False
            if not self.conversation_id:
                self.conversation_id = self.default_get_conversation()

    def _parse_msg_data(self, conv_id):
        txt_mes = {'ttype': 'text',
                   'from_me': True,
                   'contact_id': conv_id.id,
                   'text': self.text}
        msg_datas = [txt_mes]
        attac_id = self.attachment_id
        if attac_id:
            attac_id.res_model = 'acrux.chat.message'
            att_mes = {'ttype': 'file',
                       'from_me': True,
                       'contact_id': conv_id.id,
                       'res_model': 'ir.attachment',
                       'res_id': attac_id.id,
                       'text': attac_id.name}
            if attac_id.mimetype in ['image/jpeg', 'image/png', 'image/gif']:
                att_mes.update({'ttype': 'image'})
            msg_datas.append(att_mes)
        return msg_datas

    def send_message_wizard(self):
        self.ensure_one()
        self = self.with_context(not_log_event=True, is_from_wizard=True)
        Conv = self.env['acrux.chat.conversation']
        if self.new_number:
            if not self.partner_id or not self.connector_id or not self.number:
                raise ValidationError(_('Enter required values'))
            conv_id = Conv.conversation_create(self.partner_id, self.connector_id.id, self.number)
        else:
            if not self.conversation_id:
                raise ValidationError(_('Enter required values'))
            conv_id = self.conversation_id
        back_status = conv_id.status
        conv_id.block_conversation()
        msg_datas = self._parse_msg_data(conv_id)
        loop = 1
        for msg_data in msg_datas:
            if loop < len(msg_datas):
                back = 'current'
            else:
                back = back_status
            conv_id.send_message_bus_release(msg_data, back)
            loop += 1
