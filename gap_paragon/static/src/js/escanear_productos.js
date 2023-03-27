/** @odoo-module **/

import { patch } from 'web.utils';
import BarcodeModel from '@stock_barcode/models/barcode_model';

patch(BarcodeModel.prototype, 'escanear_productos', {
    
     
    async _processBarcode(barcode) {

        var rpc = require('web.rpc');

        let barcodeData = {};
        const filters = {};

        console.log("Holaaaa");
        barcodeData = await this._parseBarcode(barcode, filters);
        console.log(barcodeData);
        let codigo = barcodeData.barcode
        
        const productos = await rpc.query({
            model: 'product.product',
            method: 'search_read',
            args: [[['id', '=', 5]]],
            fields: ['name','list_price']
        });


        console.log(productos);
    },

});