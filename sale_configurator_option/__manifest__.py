# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Option",
    "summary": "Base module for sale configurator",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sale_configurator_base"],
    "data": [
        "views/sale_view.xml",
        "views/product_template_view.xml",
        "views/product_configurator_template_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/product_demo.xml", "demo/sale_demo.xml"],
    "qweb": [],
}
