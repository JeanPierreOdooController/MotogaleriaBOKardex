# -*- encoding: utf-8 -*-
{
	'name': 'Cerrar Kardex IT',
	'category': 'account',
	'author': 'ITGRUPO-KARDEX-JP',
	'depends': ['kardex_valorado_it','stock','kardex_fields_it'],
	'version': '1.0',
	'description':"""
		Permisos para Aprobar en los modulos contables y de gestion
	""",
	'auto_install': False,
	'demo': [],
	'data':	['security/ir.model.access.csv','security/purchase_national_security.xml','account_journal_view.xml'],
	'installable': True
}
