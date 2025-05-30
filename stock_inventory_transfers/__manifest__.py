# -*- coding: utf-8 -*-
{
    'name': "MANEJO DE ALBARANES EN TRANSITO",

    'summary': """""",

    'description': """
	Crea el check en la ubicacion de usar en transito, y el check en el tipo de operacion de usar en transito, esto se configura.\n
    y sirve para que cada que validas un albaran cuyo destino es una ubicacion que se usa en transito, se creara otro albaran que usara el tipo de operación que se maca usar en transito y cuya ubicacion origen es la ubicacion destino del albaran validado.
    ejemplo: validas albaran de aqp/stock a lim/transito - se creara el albaran automaticamente de lim/transito a lim/stock.
    """,

    'author': "ITGRUPO",
    'category': 'stock',
    'version': '0.1',
    'depends': ['stock','kardex_valorado_it'],
    'data': [
        'views/partner.xml',
    ],
    'demo': [],
}
