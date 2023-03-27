import BarcodeModel from stock.BarcodeModel
import { patch } from 'web.utils';

patch(BarcodeModel, 'escanear_productos', {

    async _processBarcode(barcode) {
        
        console.log("hola");

    },
});