# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class SaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_configurator_variant.sale_order_1")
        cls.line_with_variant = cls.env.ref(
            "sale_configurator_variant.sale_order_line_1"
        )
        cls.line_variant_1 = cls.env.ref(
            "sale_configurator_variant.sale_order_line_variant_1"
        )
        cls.line_variant_2 = cls.env.ref(
            "sale_configurator_variant.sale_order_line_variant_2"
        )
        cls.line_variant_3 = cls.env.ref(
            "sale_configurator_variant.sale_order_line_variant_3"
        )
        cls.product_with_variant = cls.env.ref(
            "product.product_product_4_product_template"
        )
        cls.product_with_variant.is_configurable_opt = True
        cls.product_variant_1 = cls.env.ref("product.product_product_4")
        cls.product_variant_2 = cls.env.ref("product.product_product_4b")
        cls.product_variant_3 = cls.env.ref("product.product_product_4c")
        cls.product_variant_4 = cls.env.ref("product.product_product_4d")
        cls.product_variant_5 = cls.env.ref("sale.product_product_4e")
        cls.product_variant_6 = cls.env.ref("sale.product_product_4f")
        cls.pricelist = cls.env.ref("product.list0")

    def _conf_product_add_variants(self, sale_line):
        default_variants = [
            self.product_variant_1,
            self.product_variant_2,
            self.product_variant_3,
            self.product_variant_4,
            self.product_variant_5,
            self.product_variant_6,
        ]
        for prod in default_variants:
            vrt_vals = {
                "order_id": sale_line.order_id.id,
                "product_id": prod.id,
                "product_uom": prod.uom_id.id,
                "product_uom_qty": 1,
                "parent_variant_id": sale_line.id,
                "price_unit": prod.list_price,
            }
            new_vrt = sale_line.create(vrt_vals)
            new_vrt.product_id_change()
            new_vrt.product_uom_change()

    def create_sale_line_parent(self, product_tmpl):
        sale_line = self.env["sale.order.line"].create(
            {
                "name": product_tmpl.name,
                "product_tmpl_id": product_tmpl.id,
                "product_id": product_tmpl.product_variant_id.id,
                "price_unit": product_tmpl.list_price,
                "order_id": self.sale.id,
            }
        )
        return sale_line

    def test_is_configurable(self):
        new_line = self.create_sale_line_parent(self.product_with_variant)
        new_line.product_tmpl_id_change()
        self._conf_product_add_variants(new_line)
        for line in new_line.variant_ids:
            self.assertFalse(line.is_configurable)
        self.assertTrue(new_line.is_configurable)

    def test_total_amount(self):
        self.assertEqual(self.sale.amount_total, 6850.80)
        self.assertEqual(self.sale.amount_untaxed, 6850.80)
        self.assertEqual(self.sale.amount_tax, 0)

    def test_conf_total_amount_price(self):
        self.assertEqual(self.line_with_variant.price_config_subtotal, 6850.80)
        self.assertEqual(self.line_with_variant.price_config_total, 6850.80)
        self.assertEqual(self.line_variant_1.price_config_total, 0)
        self.assertEqual(self.line_variant_2.price_config_total, 0)
        self.assertEqual(self.line_variant_3.price_config_total, 0)

    def test_conf_product_variant_qty(self):
        new_line = self.create_sale_line_parent(self.product_with_variant)
        new_line.product_tmpl_id_change()
        self._conf_product_add_variants(new_line)
        self.assertEqual(new_line.product_uom_qty, 6)
        new_line.variant_ids[0].product_uom_qty = 3
        self.assertEqual(new_line.product_uom_qty, 8)

    def test_conf_product_variant_price_global_qty(self):
        # Check if qty of one variant change price of other variant change
        new_line = self.create_sale_line_parent(self.product_with_variant)
        new_line.product_tmpl_id_change()
        self._conf_product_add_variants(new_line)
        line_product_variant_1 = new_line.variant_ids.filtered(
            lambda l: l.product_id == self.product_variant_1
        )
        self.assertEqual(line_product_variant_1.price_unit, 750)
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": self.product_with_variant.id,
                "compute_price": "percentage",
                "percent_price": 20,
                "min_quantity": 10,
            }
        )
        line_product_variant_2 = new_line.variant_ids.filtered(
            lambda l: l.product_id == self.product_variant_2
        )
        line_product_variant_2.product_uom_qty = 6
        self.assertEqual(line_product_variant_1.price_unit, 600)

    def test_update_price(self):
        self.sale.update_prices()
        self.assertEqual(self.sale.amount_total, 6850.80)
        self.assertEqual(self.sale.amount_untaxed, 6850.80)
        self.assertEqual(self.sale.amount_tax, 0)
