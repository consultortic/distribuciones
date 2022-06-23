from odoo import _, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for record in self:
            partner_docs = record.partner_id.reviewed

            if partner_docs or record.move_type not in ["out_invoice", "out_refund"]:
                res = super(AccountMove, record).action_post()
            else:
                raise ValidationError(
                    _("The associate partner documents have " "not yet been reviewed")
                )

        return res
