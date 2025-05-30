# -*- coding: utf-8 -*-
{
    'name' : 'PERMISO MODIFICAR ALMACEN, TIPO OPERACION Y UBICACIONES',
    'version': '1.0',
    'author': 'ITGRUPO',
    'website': '',
    'category': 'stock',
    'description':
        """
        Crea los grupos para controlar las modificaciones en el Almacen, tipo de operacion y ubicación.\n
        GRUPOS:\n
            Permite Modificar Almacén\n
            Permite Modificar Operación\n
            Permite Modificar Ubicaciones
        """,
    'depends' : [
        'stock',
        'base'
    ],
    'data': [
        'security/res_groups.xml'
    ],
    'auto_install': False,
    'installable': True
}