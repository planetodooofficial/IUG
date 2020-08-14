# -*- coding: utf-8 -*-

{
    "name": "Merging Objects",
    "version": "1.0",
    "category": "Tools",
    "description": """
Merge objects:
==============

This Module will give you the possibility to merge 2 or more objects together:
------------------------------------------------------------------------------

Example:
--------

    * IF you want to merge 2 or more products, select the Product to merge, and select which one to keep.
    * All SO, PO, Pickings, etc. of selected records will be add to the one that you keep.
""",
    "author": "Geetha",
    "website": "http://www.kastechssg.com",
    "Author": "Geetha",
    "depends": ["base"],
    "data": [
             "wizard/object_merging_view.xml",
             "views/res_config_view.xml",
             ],
    "demo": [],
    "installable": True,
    "active": False,
}
