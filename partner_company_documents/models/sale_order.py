from odoo import _, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for record in self:
            partner_docs = record.partner_id.reviewed

            if partner_docs:
                res = super(SaleOrder, record).action_confirm()
            else:
                raise ValidationError(
                    _("The associate partner documents have " "not yet been reviewed")
                )

        return res
