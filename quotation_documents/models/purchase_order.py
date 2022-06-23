from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    definitive_attachments = fields.Many2many(
        comodel_name="ir.attachment",
        string="Attachments",
    )

    def button_confirm(self):
        for record in self:
            definitive = record.definitive_attachments

            if definitive:
                res = super(PurchaseOrder, record).button_confirm()
            else:
                raise ValidationError(
                    _(
                        "The quotation does not have the necessary supporting "
                        "document to be confirmed"
                    )
                )

        return res
