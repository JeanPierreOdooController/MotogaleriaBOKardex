# -*- coding: utf-8 -*-
{
    'name' : 'kardex menu master',
    'version': '1.0',
    'author': 'BOKARDEX-JP',
    'website': '',
    'category': '',
    'description':
        """
        Kardex
        """,
    'depends' : ['stock'],
    'data': [
        'views/fabrication_model.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'kardex_menu_master/static/src/js/jp_master.js',
            'kardex_menu_master/static/src/xml/*',
            ],        
    },
    'auto_install': False,
    'installable': True
}