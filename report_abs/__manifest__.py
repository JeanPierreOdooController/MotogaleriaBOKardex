# -*- coding: utf-8 -*-
{
    'name' : 'Reporte ABC',
    'versionIT': '24.0',
    'author': 'ITGRUPO-KARDEX-JP',
    'website': '',
    'category': 'sale',
    'description':
        """
        Reporte ABC
        """,
    'depends' : ['sale','stock','account','kardex_fields_it'],
    'data': [
        'views/wizard.xml',
        'security/ir.model.access.csv',
    ],
    'auto_install': False,
    'installable': True
}