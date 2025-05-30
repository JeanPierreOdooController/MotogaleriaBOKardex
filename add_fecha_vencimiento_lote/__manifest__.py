# -*- encoding: utf-8 -*-
{
    'name': 'IMPORTAR FECHAS DE VENCIMIENTO EN LOTES',
    'category': 'stock',
    'author': 'ITGRUPO',
    'depends': ['stock'],
    'version': '1.0',
    'description':"""
    Agrega el boton 'Importar Fechas Caducidad' que coloca las fechas agregadas en el excel a las fechas de vencimiento del lote.
    """,
    'auto_install': False,
    'depends' : ['import_nro_lotes'],
    'demo': [],

    'data': [
        'views.xml',
        ],
    'installable': True
}