/** @odoo-module **/

import { patch } from 'web.utils';
import BarcodeModel from '@stock_barcode/models/barcode_model';

patch(BarcodeModel.prototype, 'escanear_productos', {
    
    

    async _processBarcode(barcode) {

        let barcodeData = {};

        const filters = {};

        console.log("Holaaaa");
        barcodeData = await this._parseBarcode(barcode, filters);
        console.log(barcodeData);

        let codigo = barcodeData.barcode

        const productos = await this.messaging.rpc({
            model: 'product.product',
            method: 'search',
            args: [[['id', '=', 5]]],
            
        }, { shadow: true });


        console.log(productos);
    }
    
});