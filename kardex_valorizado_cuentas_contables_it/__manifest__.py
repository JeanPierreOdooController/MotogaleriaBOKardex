# -*- encoding: utf-8 -*-
{
    'name': 'Kardex Valorizado Cuentas Contables',
    'version': '1.0',
    'author': 'ITGRUPO-KARDEX-JP',
    'website': '',
    'category': 'Kardex',
    'depends': ['kardex_valorado_it','kardex_fields_it'],
    'description': """KARDEX""",
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/make_kardex_view.xml',
    ],
    'auto_install': False,
    'installable': True
}
