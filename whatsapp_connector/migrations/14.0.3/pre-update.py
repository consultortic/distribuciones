# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.warning("\n**** Pre update whatsapp_connector from version %s to 14.0.3 ****" % version)

    ''' acrux.chat.message event selection '''
    cr.execute('''ALTER TABLE acrux_chat_message ADD temporary_event character varying''')
    cr.execute('''UPDATE acrux_chat_message SET temporary_event = event''')
    cr.execute('''UPDATE acrux_chat_message SET temporary_event = REPLACE(temporary_event, 'new_conv', 'to_new')''')
    cr.execute('''UPDATE acrux_chat_message SET temporary_event = REPLACE(temporary_event, 'rel_conv', 'to_done')''')
    cr.execute('''UPDATE acrux_chat_message SET temporary_event = REPLACE(temporary_event, 'res_conv', 'to_curr')''')
