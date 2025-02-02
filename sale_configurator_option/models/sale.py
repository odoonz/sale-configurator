# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_option_id = fields.Many2one("sale.order.line", string="Parent Option")
    child_type = fields.Selection(
        selection_add=[("option", "Option")],
        ondelete={"option": "set null"},
    )
    option_ids = fields.One2many(
        "sale.order.line",
        "parent_option_id",
        "Options",
        copy=False,
    )
    is_configurable_opt = fields.Boolean(
        "Is the product configurable Option ?", related="product_id.is_configurable_opt"
    )
    option_unit_qty = fields.Float(
        string="Option Unit Qty",
        digits="Product Unit of Measure",
        default=1.0,
    )
    option_qty_type = fields.Selection(
        [
            ("proportional_qty", "Proportional Qty"),
            ("independent_qty", "Independent Qty"),
        ],
        string="Option qty Type",
        compute="_compute_option_qty_type",
        store=True,
        readonly=False,
    )
    product_option_id = fields.Many2one(
        "product.configurator.option",
        "Product Option",
        ondelete="set null",
        compute="_compute_product_option_id",
    )

    # TODO in V16 the price_unit is a computed field \o/
    # so we should be able to drop this
    @api.depends("product_uom_qty")
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for record in self:
            if record.child_type == "option":
                product = record.product_id.with_context(
                    partner=record.order_id.partner_id,
                    quantity=record.product_uom_qty,
                    date=record.order_id.date_order,
                    pricelist=record.order_id.pricelist_id.id,
                    uom=record.product_uom.id,
                )
                record.price_unit = record._get_display_price(product)

    @api.depends("parent_option_id")
    def _compute_parent(self):
        for record in self:
            if record.parent_option_id:
                record.parent_id = record.parent_option_id
                record.child_type = "option"
            else:
                super(SaleOrderLine, record)._compute_parent()

    def _get_child_type_sort(self):
        res = super()._get_child_type_sort()
        res.append((20, "option"))
        return res

    def _is_line_configurable(self):
        if self.is_configurable_opt:
            return True
        else:
            return super()._is_line_configurable()

    @api.depends(
        "product_uom_qty",
        "option_unit_qty",
        "option_qty_type",
        "parent_option_id.product_uom_qty",
    )
    def _compute_product_uom_qty(self):
        super()._compute_product_uom_qty()
        for record in self:
            if record.parent_option_id:
                if record.option_qty_type == "proportional_qty":
                    record.product_uom_qty = (
                        record.option_unit_qty * record.parent_option_id.product_uom_qty
                    )
                elif record.option_qty_type == "independent_qty":
                    record.product_uom_qty = record.option_unit_qty

    @api.onchange("product_uom_qty")
    def onchange_qty_propagate_to_child(self):
        # When adding a new configurable product the qty is not propagated
        # correctly to child line with the onchange (it work when modifying)
        # seem to have a bug in odoo ORM
        for record in self:
            record.option_ids._compute_product_uom_qty()

    @api.model_create_multi
    def create(self, vals_list):
        options_list = [vals.pop("option_ids", None) for vals in vals_list]
        lines = super().create(vals_list)
        # For weird reason it seem that the product_uom_qty have been not recomputed
        # correctly. Recompute is only triggered in the onchange
        # and the onchange do not propagate the qty see the following test:
        # tests/test_sale_order.py::SaleOrderCase::test_create_sale_with_option_ids
        # Note maybe it's because the product_uom_qty have a default value
        # and so the create will add it, end then if we have a value the recompute
        # is note done
        lines._compute_product_uom_qty()

        # We ensure to write the option after all field on the main line a recomputed
        if any(options_list):
            for line, vals in zip(lines, options_list):
                if vals:
                    line.write({"option_ids": vals})

        return lines

    def _get_product_option(self):
        self.ensure_one()
        return self.parent_option_id.product_id.configurable_option_ids.filtered(
            lambda o: o.product_id == self.product_id
        )

    @api.depends("product_id")
    def _compute_product_option_id(self):
        for record in self:
            record.product_option_id = record._get_product_option()

    @api.depends("product_id")
    def _compute_option_qty_type(self):
        for record in self:
            if record.product_option_id:
                record.option_qty_type = record.product_option_id.option_qty_type

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        # Note we use here the context because we only want to add the default option
        # in odoo backend when editing a SO
        # Other module can call the method product_id_change and we do not want
        # to have weird side effect
        if self.product_id.is_configurable_opt and self._context.get(
            "add_default_option"
        ):
            self.option_ids = False
            for opt in self.product_id.configurable_option_ids:
                if opt.is_default_option:
                    option = self.new(
                        {
                            "product_id": opt.product_id.id,
                            "parent_option_id": self.id,
                            "order_id": self.order_id.id,
                            "option_unit_qty": opt.option_qty_default
                        }
                    )
                    option.product_id_change()
                    self.option_ids |= option
        return res

    def _get_parent_id_from_vals(self, vals):
        if "parent_option_id" in vals:
            return vals.get("parent_option_id")
        else:
            return super()._get_parent_id_from_vals(vals)

    @api.depends("option_ids")
    def _compute_report_line_is_empty_parent(self):
        super()._compute_report_line_is_empty_parent()

    @api.depends("option_ids.price_subtotal", "option_ids.price_total")
    def _compute_config_amount(self):
        super()._compute_config_amount()

    def get_children(self):
        return super().get_children() + self.option_ids
