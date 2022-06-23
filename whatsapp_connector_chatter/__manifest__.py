# -*- coding: utf-8 -*-
# =====================================================================================
# License: OPL-1 (Odoo Proprietary License v1.0)
#
# By using or downloading this module, you agree not to make modifications that
# affect sending messages through Acruxlab or avoiding contract a Plan with Acruxlab.
# Support our work and allow us to keep improving this module and the service!
#
# Al utilizar o descargar este módulo, usted se compromete a no realizar modificaciones que
# afecten el envío de mensajes a través de Acruxlab o a evitar contratar un Plan con Acruxlab.
# Apoya nuestro trabajo y permite que sigamos mejorando este módulo y el servicio!
# =====================================================================================
{
    'name': 'ChatRoom WhatsApp Chatter. Chat history in form.',
    'summary': 'Chat history in chatter. In many views (Partner, Invoice, Sale, CRM Leads,...). ChatRoom 2.0.',
    'description': 'Chat view in chatter (Partner, Invoice, Sale, CRM Leads). WhatsApp integration. WhatsApp Connector. apichat.io. GupShup. Chat-Api. ChatApi. ChatRoom 2.0.',
    'version': '14.0.5',
    'author': 'AcruxLab',
    'live_test_url': 'https://chatroom.acruxlab.com/web/signup',
    'support': 'info@acruxlab.com',
    'price': 39.0,
    'currency': 'USD',
    'images': ['static/description/Banner_chatter_v6.gif'],
    'website': 'https://acruxlab.com/plans',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'category': 'Discuss/Sales/CRM',
    'depends': [
        'whatsapp_connector',
    ],
    'data': [
        'views/include_template.xml',
    ],
    'qweb': [
        'static/src/xml/chatter.xml',
    ],
    'post_load': '',
    'external_dependencies': {},

}
