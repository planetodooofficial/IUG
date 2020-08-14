{
    "name": "Drag & Drop Multi Files Attachments", 
    "summary": "Drag & Drop Multi Files Attachments",
    "description": """
    Drag & Drop Multi Files Attachments : Allow user to Drag & Drop Multi Files Attachments in any of form view.
    """,

    "version": "10.0",
    "depends": ["document"],
    "category": "Extra Tools",

    'data': [
        "views/drag_drop_template.xml"
    ],

    'qweb': [
        'static/src/xml/drag_drop_multi_attachment.xml'
    ],
    "auto_install": False,
    "installable": True,
}
