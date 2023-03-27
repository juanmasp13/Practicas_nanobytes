/** @odoo-module **/

import { patch } from 'web.utils';
import BarcodeModel from '@stock_barcode/models/barcode_model';

patch(BarcodeModel.prototype, 'escanear_productos', {
    /**
     * @override
     */
    async _processBarcode(barcode) {

        console.log("Holaaaa");

    },
});