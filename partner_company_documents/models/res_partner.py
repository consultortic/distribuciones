from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DocumentType(models.Model):
    _name = "document.type"
    _description = "Document type"

    name = fields.Char("Document type")
    mandatory = fields.Boolean("Required")


class ResPartnerDocuments(models.Model):
    _name = "res.partner.documents"
    _description = "Documents required by the partner to be created"

    partner_id = fields.Many2one("res.partner", "Partner")
    doc_type = fields.Many2one("document.type", "Document Type", required=True)
    document = fields.Binary("Document", required=True)


class ResPartner(models.Model):
    _inherit = "res.partner"

    document_ids = fields.One2many("res.partner.documents", "partner_id", "Documents")
    mandatory = fields.Text(
        "Required documents",
        compute="_compute_mandatory_docs",
        default=lambda self: self._compute_mandatory_docs(),
        readonly=True,
    )
    reviewed = fields.Boolean("Documents Reviewed")

    def _compute_mandatory_docs(self):
        docs = self.env["document.type"].sudo().search([("mandatory", "=", True)])
        txt = ""
        for doc in docs:
            txt += "- " + doc.name + "\n"

        self.mandatory = txt
        return txt

    @api.model
    def create(self, vals):
        create = False

        if vals.get("company_type") == "company":
            ids = self._get_documents_type(vals)
            check = self._validate_create_docs(ids)
            if check:
                create = True
        else:
            create = True

        if create:
            return super(ResPartner, self).create(vals)

        raise ValidationError(_("You must upload all required documents"))

    def write(self, vals):
        write = False

        if "company_type" in vals:
            partner_type = vals["company_type"]
        else:
            partner_type = self.company_type

        if partner_type == "company" and "document_ids" in vals:
            docs = vals["document_ids"]

            docs_modify = []
            modify_types = []
            type_create = []
            docs_link = []
            list_types = []

            for item in docs:
                if item[0] == 0:
                    type_create.append(item[2]["doc_type"])
                elif item[0] == 1:
                    if "doc_type" in item[2]:
                        docs_modify.append({item[1]: item[2]["doc_type"]})
                    else:
                        docs_link.append(item[1])
                elif item[0] == 4:
                    docs_link.append(item[1])

            link_types = (
                self.env["res.partner.documents"]
                .search([("id", "in", docs_link)])
                .mapped("doc_type")
            )

            for item in link_types:
                list_types.append(item.id)
            for item in docs_modify:
                modify_types.append(list(item.values())[0])

            list_types = list_types + type_create + modify_types

            set_types = set(list_types)

            check = self._validate_create_docs(set_types)
            if check:
                write = True
                self.reviewed = False
        else:
            write = True

        if write:
            return super(ResPartner, self).write(vals)
        else:
            raise ValidationError(_("You must upload all required documents"))

    def _get_documents_type(self, vals):
        doc_ids = vals.get("document_ids")
        docs_list = []

        for doc_id in doc_ids:
            docs_list.append({"doc_type": doc_id[2].get("doc_type")})

        ids = {val for dic in docs_list for val in dic.values()}
        return ids

    def _validate_create_docs(self, ids):
        mandatory_ids = (
            self.env["document.type"]
            .sudo()
            .search([("mandatory", "=", True)])
            .mapped("id")
        )
        set_ids = set(mandatory_ids)

        missing_ids = set_ids - ids

        if missing_ids:
            return False

        return True
