# -*- encoding: utf-8 -*-
{
    'name': 'Kardex',
    'version': '1.0',
    'author': 'ITGRUPO-KARDEX-JP',
    'website': '',
    'category': 'account',
    'depends': ['kardex_valorado_it','product_expiry','kardex_fields_it'],
    'description': """KARDEX""",
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/make_kardex_view.xml',
    ],
    'auto_install': False,
    'installable': True
}
