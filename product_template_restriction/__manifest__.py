# -*- coding: utf-8 -*-
{
    'name' : 'BLOQUEO DE PRODUCTOS POR PERMISOS',
    'version': '1.0',
    'author': 'ITGRUPO',
    'website': '',
    'category': 'stock',
    'description':
        """
        Restringe la Creación-Modificación-Eliminación de productos por grupo.\n
        GRUPOS: \n
            Permite Creacion de Productos \n
        """,
    'depends' : ['stock','base','product','purchase'],
    #,'fxo_sale_order_approve'
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv'
    ],
    'auto_install': False,
    'installable': True
}