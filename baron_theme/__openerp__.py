# -*- coding: utf-8 -*-
{
    'name': 'Baron theme site',
    'description': 'Theme for Baron Llc',
    'category': 'Theme',
    'version': '1.0',
    'website': '',
    'author': 'IT Libertas, Ilyas',
    'depends': [
        'website_sale',
        'baron_shop_js',
        'baron_shelf',
    ],
    'external_dependencies': {'python': ['bs4']},
    'data': [
        'views/theme.xml',
        'views/product_view.xml',
        'security/ir.model.access.csv',
    ],
    'images':[
        'static/description/splash_screen.png',
    ],
    'application': True,
}
