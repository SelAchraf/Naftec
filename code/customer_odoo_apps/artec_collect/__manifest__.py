{
    'name': 'Artec Collect',
    'version': '16.1.0',
    'description': 'Artec Collect',
    'author': 'SARL ARTEC-INT',
    'website': 'www.artec-int.com',
    'license': 'LGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/artec_strapping_sequence.xml',
        'views/artec_tank_views.xml',
        'views/artec_product_views.xml',
        'views/artec_strapping_views.xml',
        'views/artec_gauging_views.xml',
        'views/artec_astm_views.xml',
        'views/artec_expedition_views.xml',
        'views/menus.xml',
    ],
    'depends':[
        'base'
    ],
    'auto_install': True,
    'application': True,
}