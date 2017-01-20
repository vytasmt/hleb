# -*- coding: utf-8 -*-
{
    'name': 'Baron Package Variant',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Baron Package Variant Price based on attributes',
    'description': '''
Baron Package Variant Price based on attributes
    ''',
    'auto_install': False,
    'application':True,
        
    'author': 'IT Libertas',
    'website': 'http://itlibertas.net',
    'depends': [
        'variant_price_system',
    ],
    'data': [ 
        'views/baron_package.xml',
        'security/ir.model.access.csv',
            ],
    'qweb': [ 
    
            ],
    'js': [ 

            ],
    'demo': [ 

            ],
    'test': [ 

            ],
    'license': 'AGPL-3',
    'images': ['static/description/main.png'],
    'update_xml': [],
    'application':True,
    'installable': True,
    'private': True,

}
