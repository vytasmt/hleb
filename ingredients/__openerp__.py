# -*- coding: utf-8 -*-
{
    'name': 'Ingredients',
    'version': '1.0',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'property_id for product.attribute.value',
    'author': 'Ilyas',
    'depends': [
        'product',
        'sale',
        'account',
    ],
    'data': [
        'views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
