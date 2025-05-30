from odoo import _, models, api
from odoo.exceptions import UserError
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    def button_validate(self):
        for move in self.move_line_ids_without_package.filtered(lambda m: m.state not in ['done', 'cancel']):
            # Recolectar las cantidades disponibles (quants) considerando package_id, owner_id y strict
            quants = self.env['stock.quant']._gather(
                move.product_id, 
                move.location_id, 
                lot_id=move.lot_id, 
                package_id=move.package_id, 
                owner_id=move.owner_id
                #strict=move.move_id.strict
            )
            # Obtener la cantidad disponible sumando las cantidades de los quants
            available_qty = sum(quants.mapped('quantity'))
            # Filtrar las líneas del mismo producto, lote, ubicación, paquete y dueño
            move_lines = self.move_line_ids_without_package.filtered(
                lambda ml: ml.product_id == move.product_id 
                           and ml.lot_id == move.lot_id 
                           and ml.location_id == move.location_id
                           and ml.package_id == move.package_id
                           and ml.owner_id == move.owner_id
            )
            # Sumar las cantidades confirmadas, convirtiendo a la unidad de medida base del producto
            cantidad_sml = sum(
                ml.product_uom_id._compute_quantity(ml.quantity, move.product_id.uom_id)
                for ml in move_lines
            )
            # Convertir la cantidad disponible de los quants a la unidad de medida base del producto
            cantidad_quant = move.product_id.uom_id._compute_quantity(available_qty, move.product_id.uom_id)
            # Calcular la cantidad efectiva disponible restando lo que ya está movido
            cantidad_restante = cantidad_quant - cantidad_sml
            # Evitar stock negativo en ubicaciones internas
            if move.location_id.usage == 'internal' and not move.location_id.allow_negative_stock and cantidad_restante < 0 and move.product_id.detailed_type == 'product':
                err = _(
                    "Has elegido evitar el stock negativo. %(product_name)s tiene %(available_qty)s piezas disponibles en la ubicación %(location_name)s. "
                    "Estás intentando validar una transferencia de %(required_qty)s piezas, lo que resultaría en stock negativo. "
                    "Por favor, ajusta tus cantidades o corrige tu stock con un ajuste de inventario."
                ) % {
                    'product_name': move.product_id.name,
                    'available_qty': available_qty,
                    'location_name': move.location_id.name,
                    'required_qty': cantidad_sml,
                }
                raise UserError(err)
        # Si todas las líneas están bien, continuar con la acción de validación
        return super(StockPicking, self).button_validate()
class stock_quant(models.Model):
    _inherit = "stock.quant"
    @api.model
    def create(self,vals):
        t = super(stock_quant,self).create(vals)
        for i in t:
            if i.quantity < 0 and i.location_id.usage == "internal" and not i.location_id.allow_negative_stock:
                raise UserError("Imposible generar un saldo negativo.Ubicacion: " +str(i.location_id.name_get()[0][1]) + ", Producto: "+str(i.product_id.name_get()[0][1]    )     )
        return t
    def write(self,vals):
        t = super(stock_quant,self).write(vals)
        if "quantity" in vals:
            for i in self:
                if i.quantity < 0 and i.location_id.usage == "internal" and not i.location_id.allow_negative_stock:
                    raise UserError("Imposible generar un saldo negativo.Ubicacion: " +str(i.location_id.name_get()[0][1]) + ", Producto: "+str(i.product_id.name_get()[0][1]    )     )
        return t
#    def _get_available_quantity(
#        self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False
#    ):
#        res = super()._get_available_quantity(
#            product_id=product_id,
#            location_id=location_id,
#            lot_id=lot_id,
#            package_id=package_id,
#            owner_id=owner_id,
#            strict=strict,
#            allow_negative=allow_negative,
#        )
#        if location_id and not location_id.allow_negative_stock and res < 0.0 and location_id.usage == "internal":
#            err = _(
#                "You have chosen to avoid negative stock. %(lot_qty)s pieces of %(product_name)s are remaining in location %(location_name)s. "
#                "Please adjust your quantities or correct your stock with an inventory adjustment."
#            ) % {
#                "lot_qty": res,
#                "product_name": product_id.name,
#                "location_name": location_id.name,
#            }
#            raise UserError(err)
#        return re
