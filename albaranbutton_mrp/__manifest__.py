{
    'name': 'Albaran agregar botón mrp',
    'version': '1.0',
    'description': 'Albaran agregar botón mrp',
    'author': 'ITGRUPO-MRP-KARDEX-JP',
    'license': 'LGPL-3',
    'category': 'Kardex',
    'auto_install': False,
    'depends': [
    #     'sale',
    #     'project',
    #     'account'
        'stock_balance_report','stock_balance_report_lote','mrp','stock','albaranbutton','kardex_fields_it'
    ],
    'data': [
        'views/ir.model.access.csv',
        'views/button.xml',
    ],
    'installable': True
}