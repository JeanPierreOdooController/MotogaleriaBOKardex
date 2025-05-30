# -*- encoding: utf-8 -*-
{
    'name': 'Kardex Formato Sunat Update',
    'version': '1.0',
    'author': 'ITGRUPO-KARDEX-JP',
    'website': '',
    'category': 'account',
    'depends': ['base','kardex_formato_sunat_it','kardex_fields_it'],
    'description': """KARDEX FORMATO SUNAT""",
    'demo': [],
    'data': [           
        'data/einvoice_catalog_25.xml',
        'data/existence_type.xml',       
    ],
    'auto_install': False,
    'installable': True
}
