/** @odoo-module **/

import { patch } from 'web.utils';
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { _t } from 'web.core';

patch(BarcodeModel.prototype, 'escanear_productos', {
    
     
    async _processBarcode(barcode) {
        let barcodeData = {};
        let currentLine = false;
        // Creates a filter if needed, which can help to get the right record
        // when multiple records have the same model and barcode.
        if (this.record.picking_type_code !== 'incoming'){
            var rpc = require('web.rpc');
            const serials_no = await rpc.query({
                model: 'stock.production.lot',
                method: 'search_read',
                args: [[['pallet_no', '=', barcode]]],
                fields: ['name','product_id','product_qty']
            });
            console.log(this)
            if (serials_no.length > 0) {
                let move_lines_to_create = [];
                for (let serial_no of serials_no){
                    let move_line = {
                        picking_id: this.params.id, 
                        product_id: serial_no.product_id[0],
                        product_uom_id: 1,
                        product_uom_qty: serial_no.product_qty,
                        qty_done: 1,
                        lot_id: serial_no.id,
                        location_dest_id: this.record.location_dest_id,
                        location_id: this.record.location_id
                    };
                    move_lines_to_create.push(move_line);
                }
                console.log(move_lines_to_create)
                // let move_lines_ids = [];
                // const move_lines = await rpc.query({
                //     model: 'stock.move.line',
                //     method: 'create',
                //     args: [move_lines_to_create],
                // }).then(function(result){
                //     for (let id of result){
                //         move_lines_ids.push(id);
                //     }
                //     console.log('result:', result);
                // }).catch(function(error) {
                //     console.log('Error al crear los registros:', error);
                // });

                // console.log(move_lines_ids);
                // this.linesToSave = move_lines_ids;
                // this.trigger('update');
                // console.log(barcodeData);
                console.log(this);
                return;
            }
        }
        const filters = {};
        if (this.selectedLine && this.selectedLine.product_id.tracking !== 'none') {
            filters['stock.production.lot'] = {
                product_id: this.selectedLine.product_id.id,
            };
        }
        try {
            barcodeData = await this._parseBarcode(barcode, filters);
            if (!barcodeData.match && filters['stock.production.lot'] &&
                !this.canCreateNewLot && this.useExistingLots) {
                // Retry to parse the barcode without filters in case it matches an existing
                // record that can't be found because of the filters
                const lot = await this.cache.getRecordByBarcode(barcode, 'stock.production.lot');
                if (lot) {
                    Object.assign(barcodeData, { lot, match: true });
                }
            }
        } catch (parseErrorMessage) {
            barcodeData.error = parseErrorMessage;
        }

        // Process each data in order, starting with non-ambiguous data type.
        if (barcodeData.action) { // As action is always a single data, call it and do nothing else.
            return await barcodeData.action();
        }

        if (barcodeData.packaging) {
            barcodeData.product = this.cache.getRecord('product.product', barcodeData.packaging.product_id);
            barcodeData.quantity = barcodeData.packaging.qty;
            barcodeData.uom = this.cache.getRecord('uom.uom', barcodeData.product.uom_id);
        }

        if (barcodeData.lot && !barcodeData.product) {
            barcodeData.product = this.cache.getRecord('product.product', barcodeData.lot.product_id);
        }

        await this._processLocation(barcodeData);
        await this._processPackage(barcodeData);
        if (barcodeData.stopped) {
            // TODO: Sometime we want to stop here instead of keeping doing thing,
            // but it's a little hacky, it could be better to don't have to do that.
            return;
        }

        if (barcodeData.weight) { // Convert the weight into quantity.
            barcodeData.quantity = barcodeData.weight.value;
        }

        // If no product found, take the one from last scanned line if possible.
        if (!barcodeData.product) {
            if (barcodeData.quantity) {
                currentLine = this.selectedLine || this.lastScannedLine;
            } else if (this.selectedLine && this.selectedLine.product_id.tracking !== 'none') {
                currentLine = this.selectedLine;
            } else if (this.lastScannedLine && this.lastScannedLine.product_id.tracking !== 'none') {
                currentLine = this.lastScannedLine;
            }
            if (currentLine) { // If we can, get the product from the previous line.
                const previousProduct = currentLine.product_id;
                // If the current product is tracked and the barcode doesn't fit
                // anything else, we assume it's a new lot/serial number.
                if (previousProduct.tracking !== 'none' &&
                    !barcodeData.match && this.canCreateNewLot) {
                    barcodeData.lotName = barcode;
                    barcodeData.product = previousProduct;
                }
                if (barcodeData.lot || barcodeData.lotName ||
                    barcodeData.quantity) {
                    barcodeData.product = previousProduct;
                }
            }
        }
        const {product} = barcodeData;
        if (!product) { // Product is mandatory, if no product, raises a warning.
            if (!barcodeData.error) {
                if (this.groups.group_tracking_lot) {
                    barcodeData.error = _t("You are expected to scan one or more products or a package available at the picking location");
                } else {
                    barcodeData.error = _t("You are expected to scan one or more products.");
                }
            }
            return this.notification.add(barcodeData.error, { type: 'danger' });
        } else if (barcodeData.lot && barcodeData.lot.product_id !== product.id) {
            delete barcodeData.lot; // The product was scanned alongside another product's lot.
        }
        if (barcodeData.weight) { // the encoded weight is based on the product's UoM
            barcodeData.uom = this.cache.getRecord('uom.uom', product.uom_id);
        }

        // Searches and selects a line if needed.
        if (!currentLine || this._shouldSearchForAnotherLine(currentLine, barcodeData)) {
            currentLine = this._findLine(barcodeData);
        }

        // Default quantity set to 1 by default if the product is untracked or
        // if there is a scanned tracking number.
        if (product.tracking === 'none' || barcodeData.lot || barcodeData.lotName || this._incrementTrackedLine()) {
            const hasUnassignedQty = currentLine && currentLine.qty_done && !currentLine.lot_id && !currentLine.lot_name;
            const isTrackingNumber = barcodeData.lot || barcodeData.lotName;
            const defaultQuantity = isTrackingNumber && hasUnassignedQty ? 0 : 1;
            barcodeData.quantity = barcodeData.quantity || defaultQuantity;
            if (product.tracking === 'serial' && barcodeData.quantity > 1 && (barcodeData.lot || barcodeData.lotName)) {
                barcodeData.quantity = 1;
                this.notification.add(
                    _t(`A product tracked by serial numbers can't have multiple quantities for the same serial number.`),
                    { type: 'danger' }
                );
            }
        }

        if ((barcodeData.lotName || barcodeData.lot) && product) {
            const lotName = barcodeData.lotName || barcodeData.lot.name;
            for (const line of this.currentState.lines) {
                if (line.product_id.tracking === 'serial' && this.getQtyDone(line) !== 0 &&
                    ((line.lot_id && line.lot_id.name) || line.lot_name) === lotName) {
                    return this.notification.add(
                        _t("The scanned serial number is already used."),
                        { type: 'danger' }
                    );
                }
            }
            // Prefills `owner_id` and `package_id` if possible.
            const prefilledOwner = (!currentLine || (currentLine && !currentLine.owner_id)) && this.groups.group_tracking_owner && !barcodeData.owner;
            const prefilledPackage = (!currentLine || (currentLine && !currentLine.package_id)) && this.groups.group_tracking_lot && !barcodeData.package;
            if (this.useExistingLots && (prefilledOwner || prefilledPackage)) {
                const lotId = (barcodeData.lot && barcodeData.lot.id) || (currentLine && currentLine.lot_id && currentLine.lot_id.id) || false;
                const res = await this.orm.call(
                    'product.product',
                    'prefilled_owner_package_stock_barcode',
                    [product.id],
                    {
                        lot_id: lotId,
                        lot_name: (!lotId && barcodeData.lotName) || false,
                    }
                );
                this.cache.setCache(res.records);
                if (prefilledPackage && res.quant && res.quant.package_id) {
                    barcodeData.package = this.cache.getRecord('stock.quant.package', res.quant.package_id);
                }
                if (prefilledOwner && res.quant && res.quant.owner_id) {
                    barcodeData.owner = this.cache.getRecord('res.partner', res.quant.owner_id);
                }
            }
        }

        // Updates or creates a line based on barcode data.
        if (currentLine) { // If line found, can it be incremented ?
            let exceedingQuantity = 0;
            if (product.tracking !== 'serial' && barcodeData.uom && barcodeData.uom.category_id == currentLine.product_uom_id.category_id) {
                // convert to current line's uom
                barcodeData.quantity = (barcodeData.quantity / barcodeData.uom.factor) * currentLine.product_uom_id.factor;
                barcodeData.uom = currentLine.product_uom_id;
            }
            if (this.canCreateNewLine) {
                // Checks the quantity doesn't exceed the line's remaining quantity.
                if (currentLine.product_uom_qty && product.tracking === 'none') {
                    const remainingQty = currentLine.product_uom_qty - currentLine.qty_done;
                    if (barcodeData.quantity > remainingQty) {
                        // In this case, lowers the increment quantity and keeps
                        // the excess quantity to create a new line.
                        exceedingQuantity = barcodeData.quantity - remainingQty;
                        barcodeData.quantity = remainingQty;
                    }
                }
            }
            if (barcodeData.quantity > 0 || barcodeData.lot || barcodeData.lotName) {
                const fieldsParams = this._convertDataToFieldsParams({
                    qty: barcodeData.quantity,
                    lotName: barcodeData.lotName,
                    lot: barcodeData.lot,
                    package: barcodeData.package,
                    owner: barcodeData.owner,
                });
                if (barcodeData.uom) {
                    fieldsParams.uom = barcodeData.uom;
                }
                await this.updateLine(currentLine, fieldsParams);
            }
            if (exceedingQuantity) { // Creates a new line for the excess quantity.
                const fieldsParams = this._convertDataToFieldsParams({
                    product,
                    qty: exceedingQuantity,
                    lotName: barcodeData.lotName,
                    lot: barcodeData.lot,
                    package: barcodeData.package,
                    owner: barcodeData.owner,
                });
                if (barcodeData.uom) {
                    fieldsParams.uom = barcodeData.uom;
                }
                currentLine = await this._createNewLine({
                    copyOf: currentLine,
                    fieldsParams,
                });
            }
        } else if (this.canCreateNewLine) { // No line found. If it's possible, creates a new line.
            const fieldsParams = this._convertDataToFieldsParams({
                product,
                qty: barcodeData.quantity,
                lotName: barcodeData.lotName,
                lot: barcodeData.lot,
                package: barcodeData.package,
                owner: barcodeData.owner,
            });
            if (barcodeData.uom) {
                fieldsParams.uom = barcodeData.uom;
            }
            currentLine = await this._createNewLine({fieldsParams});
        }

        // And finally, if the scanned barcode modified a line, selects this line.
        if (currentLine) {
            this.selectLine(currentLine);
        }
        this.trigger('update');
    }

});