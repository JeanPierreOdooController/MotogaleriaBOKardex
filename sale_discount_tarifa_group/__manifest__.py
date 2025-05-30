# -*- coding: utf-8 -*-
{
    'name' : 'NO MODIFICAR DESCUENTOS Y LISTA DE PRECIOS DE VENTA',
    'version': '1.0',
    'author': 'ITGRUPO',
    'website': '',
    'category': 'sale',
    'description':
        """
        Restringe la aplicacion de descuento a nivel de linea de producto\n
        GRUPOS:\n
            Restringe Descuentos en linea de Ventas\n
            Permite Modificar Lista de Precio en Ventas\n
        """,
    'depends' : [
        'sale'
    ],
    'data': [
        'security/group_discount_tarifa.xml',
    ],
    'auto_install': False,
    'installable': True
}
