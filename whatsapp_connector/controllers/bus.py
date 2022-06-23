# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.bus.controllers.main import BusController


class BusControllerInherit(BusController):

    def _poll(self, dbname, channels, last, options):
        user_id = request.session.uid
        if user_id:
            cids = request.httprequest.cookies.get('cids', str(request.env.company.id))
            cids = [int(cid) for cid in cids.split(',')]
            company_id = cids[0]
            channels = list(channels)
            channels.append((request.db, 'acrux.chat.conversation', company_id))
            channels.append((request.db, 'acrux.chat.conversation', company_id, user_id))
        return super(BusControllerInherit, self)._poll(dbname, channels, last, options)
