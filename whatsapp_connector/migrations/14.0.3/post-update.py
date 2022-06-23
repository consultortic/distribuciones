# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.warning("\n**** Post update whatsapp_connector from version %s to 14.0.3 ****" % version)

    ''' selection acrux.chat.message event '''
    cr.execute('''UPDATE acrux_chat_message SET event = temporary_event''')
    cr.execute('''ALTER TABLE acrux_chat_message DROP COLUMN temporary_event''')
