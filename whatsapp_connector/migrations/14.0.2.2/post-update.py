# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.warning("\n**** Post update whatsapp_connector from version %s to 14.0.2.2 ****" % version)

    cr.execute('''UPDATE acrux_chat_conversation SET agent_id = temporary_agent_id''')
    cr.execute('''ALTER TABLE acrux_chat_conversation DROP COLUMN temporary_agent_id''')

