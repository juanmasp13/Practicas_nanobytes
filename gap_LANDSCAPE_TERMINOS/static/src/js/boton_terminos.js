odoo.define('gap_LANDSCAPE_TERMINOS.javascript', function(require) {
    'use strict'
    console.log('holaaaaaaaa');

    var core = require('web.core');
    var config = require('web.config');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('website_sale.VariantMixin');

   publicWidget.registry.WebsiteSale = publicWidget.Widget.extend(VariantMixin, {
    selector: '.oe_website_sale',
    events: _.extend({}, VariantMixin.events || {}, {
        'change #checkbox_terminos': '_onChangeNext',
    }),

    _onChangeNext: function () {
        if ($("#checkbox_terminos").checked){
            $('.a-submit').addClass('disabled');
            console.log('CHECKEADO');
        }else{
            $('.a-submit').removeClass('disabled');
            console.log('NO CHECKEADO');
        }

    }
});
});