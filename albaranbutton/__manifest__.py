{
    'name': 'Albaran agregar botón',
    'version': '1.0',
    'description': 'Boton para albanares',
    'author': 'ITGRUPO-KARDEX-JP',
    'license': 'LGPL-3',
    'category': 'Kardex',
    'auto_install': False,
    'depends': [
    #     'sale',
    #     'project',
    #     'account'
        'stock_balance_report','stock_balance_report_lote','kardex_fields_it'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/button.xml',
    ],
    'installable': True
}