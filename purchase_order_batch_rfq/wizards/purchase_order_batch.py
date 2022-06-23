from odoo import api, fields, models


class BatchRFQ(models.TransientModel):
    _name = "purchase.order.batch.rfq"
    _inherit = "purchase.order"
    _description = "Create rfq in batch"

    partner_id = fields.Many2one("res.partner", string="Vendor")
    partner_ids = fields.Many2many("res.partner", string="Vendors")
    order_line = fields.One2many(
        "purchase.order.batch.rfq.lines",
        "order_id",
        string="Order Lines",
        states={"cancel": [("readonly", True)], "done": [("readonly", True)]},
        copy=True,
    )

    @api.model
    def create(self, vals):
        partner_ids = vals.get("partner_ids")[0][2]
        orders = []
        vals_aux = vals
        del vals_aux["partner_ids"]

        for partner in partner_ids:
            if "name" in vals_aux:
                del vals_aux["name"]
            vals_order = vals_aux
            vals_order.update({"partner_id": partner})
            orders.append(vals_order)
            purchase_order = self.env["purchase.order"]
            purchase_order.create(vals_order)

        res = super().create(vals)

        return res

    def action_close_dialog(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        return action

    def unlink(self):
        for order in self:
            order.state = "cancel"
        return super(BatchRFQ, self).unlink()


class BatchRFQLines(models.TransientModel):
    _name = "purchase.order.batch.rfq.lines"
    _inherit = "purchase.order.line"
    _description = "Create rfq lines"

    order_id = fields.Many2one(
        "purchase.order.batch.rfq",
        string="Order Reference",
        index=True,
        required=True,
        ondelete="cascade",
    )
