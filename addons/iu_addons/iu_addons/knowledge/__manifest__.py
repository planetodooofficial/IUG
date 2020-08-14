# -*- coding: utf-8 -*-

{
    "name": "Knowledge Management System",
    "version": "10.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Knowledge",
    "license": "",
    "website": "",
    "depends": ["base"],
    "data": [
        "data/ir_module_category.xml",
        "security/knowledge_security.xml",
        "views/knowledge.xml",
        "views/res_config.xml",
    ],
    "demo": ["demo/knowledge.xml"],
    "installable": True,
    "auto_install": False,
}
