# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    ''' Campo acrux_chat_conversation.number debe contener solo números '''
    _logger.warning("\n**** Pre update whatsapp_connector from version %s to 14.0.2 ****" % version)
    cr.execute('''UPDATE acrux_chat_conversation SET number = REPLACE(REPLACE(number, '+', ''), ' ', '') ''')
