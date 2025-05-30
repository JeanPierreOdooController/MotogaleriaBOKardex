# -*- encoding: utf-8 -*-
{
    'name': 'Kardex Formato Sunat V12',
    'version': '1.0',
    'author': 'ITGRUPO-KARDEX-JP',
    'website': '',
    'category': 'account',
    'depends': ['kardex_valorado_it','kardex_fields_it'],
    'description': """KARDEX FORMATO SUNAT V12""",
    'demo': [],
    'data': [
        'security/ir.model.access.csv', 
        'wizard/make_kardex_view.xml',
    ],
    'auto_install': False,
    'installable': True
}
