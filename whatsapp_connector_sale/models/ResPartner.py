# -*- coding: utf-8 -*-
from odoo import models
from odoo.tools.translate import _
from datetime import date
from dateutil.relativedelta import relativedelta


class Contact(models.Model):
    _inherit = 'res.partner'

    def _query_html_latest_sales(self):
        sql = """
                SELECT product_id, order_line.name as p_name, price_unit, product_uom_qty,
                    uom.name as uom_name, date_order
                FROM uom_uom AS uom
                JOIN (
                    SELECT DISTINCT ON (product_id) product_id, line.id, name, price_unit,
                        product_uom_qty, date_order, product_uom
                    FROM sale_order_line AS line
                    JOIN(
                        SELECT date_order, id FROM sale_order WHERE partner_id=%s AND state IN ('sale', 'done')
                    )
                    AS sale_order ON sale_order.id = line.order_id LIMIT 10
                )
                AS order_line ON uom.id = order_line.product_uom
                ORDER BY date_order DESC
                """ % (self.id)
        self.env.cr.execute(sql)
        return self.env.cr.dictfetchall()

    def get_html_latest_sales(self):
        self.ensure_one()
        HTML = ("<table class='table table-condensed'><thead><tr><th>" + _('Product') +
                "</th><th>" + _('Price') + "</th><th>" + _('Qty') + "</th><th>" +
                _('Uom') + "</th><th>" + _('Date') + "</th></tr></thead><tbody>%s </tbody></table>")
        precision_sale = self.env['decimal.precision'].precision_get('Product Price')
        precision_uom = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        lang = self.env.user.lang or 'en_US'
        lang = self.env['res.lang']._lang_get(lang)
        date_format = lang.date_format
        body = """"""
        for line in self._query_html_latest_sales():
            price_unit = lang.format(percent='%.{p}f'.format(p=precision_sale), value=line['price_unit'], grouping=True)
            quantity = lang.format(percent='%.{p}f'.format(p=precision_uom), value=line['product_uom_qty'], grouping=True)
            date_order = line['date_order'].strftime(date_format).split(' ')[0]
            body += """<tr data-product_id="%s"><td>%s</td><td class="text-right">%s</td><td class="text-right">%s</td><td>%s</td><td>%s</td></tr>\n""" \
                    % (line['product_id'], line['p_name'][:50], price_unit, quantity, line['uom_name'], date_order)
        return HTML % body

    def _query_6month_last_sale_data(self, months):
        sql = """
            SELECT  TO_CHAR(date_order, 'MM-YYYY') date_order, TO_CHAR(date_order, 'YYYYMM'),
                    COALESCE(SUM(amount_total), 0) amount_total
            FROM sale_order
            WHERE state in ('done', 'sale')
              AND date_order >= CURRENT_DATE - INTERVAL '%s months'
              AND partner_id=%s
            GROUP BY TO_CHAR(date_order, 'MM-YYYY'), TO_CHAR(date_order, 'YYYYMM')
            ORDER BY TO_CHAR(date_order, 'YYYYMM')
                """ % (months, self.id)
        self.env.cr.execute(sql)
        out = self.env.cr.dictfetchall()
        if out and len(out) != months:
            exist = [x['to_char'] for x in out]
            today = date.today()
            for month in range(0, months):
                aux = today - relativedelta(months=month)
                Y, M = aux.year, str(aux.month).zfill(2)
                to_char = '%s%s' % (Y, M)
                if to_char not in exist:
                    date_order = '%s-%s' % (M, Y)
                    out.append({'date_order': date_order, 'to_char': to_char,
                                'amount_total': 0.0})
            out = sorted(out[:months], key=lambda i: i['to_char'])
        return out

    def get_6month_last_sale_data(self):
        self.ensure_one()
        values = []
        months = 6
        for line in self._query_6month_last_sale_data(months):
            values.append({'label': line['date_order'], 'value': line['amount_total']})
        if values:
            values = [{'values': values,
                       'title': _('Last %s months sales') % months,
                       'currency_id': self.currency_id.id}]
        else:
            values = False
        return values

    def get_chat_indicators(self):
        self.ensure_one()
        return {'html_last_sale': self.get_html_latest_sales(),
                '6month_last_sale_data': self.get_6month_last_sale_data()}
