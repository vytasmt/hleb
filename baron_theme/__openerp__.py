# -*- coding: utf-8 -*-
{
    'name': 'Baron theme site',
    'description': 'Theme for Baron Llc',
    'category': 'Theme',
    'version': '1.0',
    'website': 'https://itlibertas.com',
    'author': 'IT Libertas',
    'depends': [
        'website_sale',
        'baron_shop_js',
        'baron_shelf',
    ],
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
