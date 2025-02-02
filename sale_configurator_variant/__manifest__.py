# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Variant",
    "summary": "Extend sale configurator to manage product variant",
    "version": "14.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sale_configurator_option"],
    "data": ["views/sale_view.xml"],
    "demo": ["demo/sale_demo.xml"],
    "qweb": [],
}
