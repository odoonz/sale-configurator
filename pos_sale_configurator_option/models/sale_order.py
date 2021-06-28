# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_pos_option(self, option):
        return {
            "product_id": int(option["product_id"]),
            "option_unit_qty": int(option["qty"]),
            "option_qty_type": "proportional_qty",
            "product_option_id": int(option["id"]),
            "name": option.get("description"),
            "note": option.get("note"),
        }

    def _prepare_pos_line(self, line):
        vals = super()._prepare_pos_line(line)
        if line.get("config", {}).get("selected_options"):
            # Note we only support simple case in POS where the product
            # have a price unit of 0 and the price come from the option
            # the price of the option are recomputed
            vals["price_unit"] = 0
            vals["option_ids"] = []
            for option in line["config"]["selected_options"]:
                vals["option_ids"].append([0, 0, self._prepare_pos_option(option)])
        return vals

    def _get_lines_to_deliver(self):
        return super()._get_lines_to_deliver().filtered(lambda s: not s.parent_id)
