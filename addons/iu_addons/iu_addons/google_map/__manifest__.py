
{
    'name': 'Google Maps',
    'version': '1.0',
    'category': 'Customer Relationship Management',
    'description': """This module adds a Map button on the partner’s form in order to open its address directly in the Google Maps view""",
    'author': '',
    'website': '',
    'depends': ['base'],
    'init_xml': [],
    'images': ['static/description/banner.png','images/google_map.png','images/map.png','images/earth.png','static/src/img/gtk-zoom-in.png'],
    'data': [
            'views/google_map_view.xml',
            ],
	'css':['static/src/css/description.css'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: