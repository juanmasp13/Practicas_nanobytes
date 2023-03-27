/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import BarcodeModel from '@stock_barcode/barcode_model';

patch(BarcodeModel.prototype, 'escanear_productos', {
    /**
     * @override
     */
    async _processBarcode(barcode) {

        console.log("Holaaaa");

    },
});