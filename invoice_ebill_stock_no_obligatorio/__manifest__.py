# -*- encoding: utf-8 -*-
{
	'name': 'Invoice Ebill Stock no obligatorio',
	'category': 'account',
	'author': 'ITGRUPO-KARDEX-JP',
	'depends': ['sale_stock','account','stock','landed_cost_it','kardex_fields_it'],
	'version': '1.0',
	'description':"""
	Agregar información a la factura.
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
			'views/mrp_kardex.xml'],
	'installable': True
}
