# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    ''' Elimina campo acrux_chat_connector.sale_report_id '''
    _logger.warning("\n**** Pre update whatsapp_connector_sale from version %s to 14.0.2 ****" % version)
    cr.execute('ALTER TABLE "{0}" DROP COLUMN "{1}"'.format('acrux_chat_connector', 'sale_report_id'))
