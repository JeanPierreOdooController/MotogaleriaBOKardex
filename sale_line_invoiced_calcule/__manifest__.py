# -*- encoding: utf-8 -*-
{
	'name': 'CORRECCION EN CALCULO DE VENTAS Y SU FACTURA',
	'category': 'account',
	'author': 'ITGRUPO',
#	'depends': ['sale','l10n_pe_edi_extended'], revisar en models comente algo una vez descargado el repositorio de 17
	'depends': ['sale','account'],
	'version': '1.0',
	'description':"""
    Corrige el campo Cantidad facturada en la venta, para considerar si se crea una nota de credito, esta le reduce la cantidad facturada a la venta.
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
			'security/security.xml',
			'views/mrp_kardex.xml'],
	'installable': True
}
