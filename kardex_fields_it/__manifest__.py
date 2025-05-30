# -*- encoding: utf-8 -*-
{
	'name': 'Kardex Fields',
	'category': 'Kardex',
	'author': 'ITGRUPO-KARDEX-JP',
	'depends': ['analytic','stock','kardex_menu_master'],
	'version': '1.0',
	'description':"""
	 Campos Base para Odoo17 BO Kardex
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/ir.model.access.csv',
			'views/stock_picking.xml'
		],
	'installable': True
}
