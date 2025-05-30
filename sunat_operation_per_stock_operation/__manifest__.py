# -*- encoding:utf-8 -*- 
{
    'name': 'TIPO OPERACION SUNAT POR OPERACION',
    'version': '1.0',
    'description': 'Permite habilitar en cada TIPO DE OPERACION de INVENTARIO, un campo donde indique el TIPO DE OPERACION SUNAT POR DEFECTO.',
    'author': 'ITGRUPO, Jhorel Revilla Calderon',
    'license': 'LGPL-3',
    'depends': [
        'stock'
    ],
    'data': [
        'views/stock_picking_type.xml'
    ],
    'auto_install': False,
    'application': False
}