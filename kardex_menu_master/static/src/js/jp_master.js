/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { usePopover } from "@web/core/popover/popover_hook";
import { useService } from "@web/core/utils/hooks";
import { localization } from "@web/core/l10n/localization";
import { parseDate, formatDate } from "@web/core/l10n/dates";

import { formatMonetary } from "@web/views/fields/formatters";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";


export class KardexJPPRO extends Component {
    static props = { ...standardFieldProps };

    setup() {
        const position = localization.direction === "rtl" ? "bottom" : "left";
        this.orm = useService("orm");
        this.action = useService("action");
        this.rpc = useService("rpc");
    }

    getInfo() {
        const info = this.props.record.data[this.props.name] || {};
        return info;
    }
    async onInfoClick(ev){
        this.action.doAction({            
            type: 'ir.actions.act_window',
            name: _t('Entradas'),
            target: 'new',
            res_model: 'account.move',
            views: [[false, 'tree'],[false, 'form']],});
    }
}
KardexJPPRO.template = "kardex_menu_master.KardexMasterPro";

export const cKardexJPPRO = {
    component: KardexJPPRO,
    supportedTypes: ["char"],
};

registry.category("fields").add("KardexJPPRO", cKardexJPPRO);

