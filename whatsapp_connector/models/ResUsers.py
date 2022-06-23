# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.bus.models.bus_presence import DISCONNECTION_TIMER


class ResUsers(models.Model):
    _inherit = 'res.users'

    acrux_chat_active = fields.Boolean('Active in Chat', default=True)
    is_chatroom_group = fields.Boolean(compute='_compute_is_chat_group', compute_sudo=True, string='ChatRoom User',
                                       store=True)

    @api.depends('groups_id')
    def _compute_is_chat_group(self):
        for user in self:
            user.is_chatroom_group = user.has_group('whatsapp_connector.group_chat_basic') and not user.share

    def toggle_acrux_chat_active(self):
        for r in self:
            r.acrux_chat_active = not r.acrux_chat_active
        self.notify_status_changed()

    def set_chat_active(self, value):
        value = value.get('acrux_chat_active')
        self.sudo().acrux_chat_active = value
        self.notify_status_changed()

    def notify_status_changed(self):
        status_data = list(map(lambda r: {'agent_id': [r.id, r.name],
                                          'status': r.acrux_chat_active}, self))
        if status_data:
            data_to_send = {'change_status': status_data}
            channel = (self.env.cr.dbname, 'acrux.chat.conversation', self.env.company.id, self.id)
            self.env['bus.bus'].sendone(channel, data_to_send)

    def chatroom_active(self, check_online=False):
        self.ensure_one()
        active = self.acrux_chat_active
        if active and check_online:
            self.env.cr.execute('''
                SELECT
                    U.id as user_id,
                    CASE WHEN B.last_poll IS NULL THEN 'offline'
                         WHEN age(now() AT TIME ZONE 'UTC', B.last_poll) > interval '%s' THEN 'offline'
                         ELSE 'online'
                    END as im_status
                FROM res_users U
                    LEFT JOIN bus_presence B ON B.user_id = U.id
                WHERE U.id = %s
                    AND U.active = 't'
            ''' % ("%s seconds" % DISCONNECTION_TIMER, self.id))
            result = self.env.cr.dictfetchone()
            active = result['im_status'] == 'online'
        return active
