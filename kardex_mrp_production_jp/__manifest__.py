# -*- encoding: utf-8 -*-
{
	'name': 'Kardex Mrp Production',
	'category': 'Kardex',
	'author': 'ITGRUPO-MRP-KARDEX-JP',
	'depends': ['kardex_valorado_it', 'mrp','mrp_kardex', 'stock_balance_report','product_add_brand','kardex_fields_it'],
	'version': '1.0',
	'description':"""
	Modulo para añadir lineas de OP's en Kardex Fisico
	""",
	'auto_install': False,
	'demo': [],
	'data':	['wizard/make_kardex_view.xml'],
	'installable': True
}
