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
    'name': 'ChatRoom WhatsApp Sale Order, Invoice. Real All in One',
    'summary': 'From ChatRoom main view Create & Send Sales Orders and Invoices. All in one screen. ChatRoom 2.0.',
    'description': 'Send Sales Orders, Invoices. Real All in One. Send and receive messages. Real ChatRoom. WhatsApp integration. WhatsApp Connector. apichat.io. GupShup. Chat-Api. ChatApi. Drag and Drop. ChatRoom 2.0.',
    'version': '14.0.3',
    'author': 'AcruxLab',
    'live_test_url': 'https://chatroom.acruxlab.com/web/signup',
    'support': 'info@acruxlab.com',
    'price': 59.6,
    'currency': 'USD',
    'images': ['static/description/Banner_full_v6.gif'],
    'website': 'https://acruxlab.com/plans',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'category': 'Discuss/Sales/CRM',
    'depends': [
        'whatsapp_connector',
        'sale_management',
    ],
    'data': [
        'data/data.xml',
        'views/sale_order_views.xml',
        'views/acrux_chat_conversation_views.xml',
        'reports/reports.xml',
        'views/include_template.xml',
    ],
    'qweb': [
        'static/src/xml/acrux_chat_template.xml',
    ],
}
