# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.warning("\n**** Pre update whatsapp_connector from version %s to 14.0.2.2 ****" % version)

    ''' Cambia nombre de campo '''
    cr.execute('''ALTER TABLE acrux_chat_conversation ADD temporary_agent_id int''')
    cr.execute('''UPDATE acrux_chat_conversation SET temporary_agent_id = sellman_id''')
    cr.execute('''ALTER TABLE acrux_chat_conversation DROP COLUMN sellman_id''')

    ''' Elimina campo '''
    cr.execute('''ALTER TABLE acrux_chat_conversation DROP COLUMN IF EXISTS partner_sellman_id''')
