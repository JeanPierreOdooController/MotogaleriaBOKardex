# -*- encoding: utf-8 -*-
{
    'name': 'IMPORTADOR DE SALDOS INICIALES C/S LOTES.',
    'category': 'stock',
    'author': 'ITGRUPO',
    'depends': ['stock','kardex_fields_it'],
    'version': '1.0',
    'description':"""
    Agrega los campos y opciones de importación de saldos iniciales en el albaran.\n
    """,
    'auto_install': False,
    'demo': [],
    'data': [
        'views.xml',
        ],
    'installable': True
}