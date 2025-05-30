# -*- encoding: utf-8 -*-
{
	'name': 'IMPORTADOR DE TARIFA',
	'category': 'sale',
	'author': 'ITGRUPO-KARDEX-JP',
	'depends': [
    	# 'base',
     	'stock',
      	# 'account_accountant',
       	'account',
        'sale',
        # 'kardex_fields_it'
    ],
	'version': '1.0',
	'description':"""
		Permite habilitar el importador de tarifa /lista de precios en ventas.\n
		GRUPOS:\n
			Permite acceder al IMPORTADOR DE TARIFAS
	""",
	'auto_install': False,
	'data': [
		'security/ir.model.access.csv',
        'security/res_groups.xml',
        'data/attachment_sample.xml',
        'views/tarifa_import_view.xml',        
    ],
	'installable': True
}