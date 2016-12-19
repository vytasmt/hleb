# -*- coding: utf-8 -*-
{
    'name': 'Baron res_partner extras',
    'version': '1.0',
    'category': 'Category',
    'summary': 'Baron res_partner extras',
    'description': '''
    Change look of res_partner view.
    Fixed missing street2 field from kladr address block
    ''',
    'auto_install': False,
    'application':True,
    'author': 'IT Libertas, SUVIT LLC',
    'website': 'http://itlibertas.com, https://suvit.ru',
    'depends': [
        'crm',
        'sale',
        'account',
        'crm_claim',
        'project_issue',
        'project',
        'partner_kladr_address',
    ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
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
    'installable': True,
    'private_category':False,
    'external_dependencies': {
    },

}
