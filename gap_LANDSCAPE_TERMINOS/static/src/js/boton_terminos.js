odoo.define('gap_LANDSCAPE_TERMINOS.javascript', function(require) {
    'use strict'
    console.log('holaaaaaaaa');

    var core = require('web.core');
    var config = require('web.config');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('website_sale.VariantMixin');

    console.log('CHECKBOX: '+ checkbox.checked);


   publicWidget.registry.WebsiteSale = publicWidget.Widget.extend(VariantMixin, {
    selector: '.oe_website_sale',
    events: _.extend({}, VariantMixin.events || {}, {
        'change #checkbox_terminos': '_onChangeNext',
    }),

    _onChangeNext: function () {

        if ($(ev.currentTarget).is(":checked")){
            $(ev.currentTarget).hasClass('.a-submit').addClass('disabled').attr('disabled', 'disabled');
            console.log('CHECKEADO');
        }else{
            $('.a-submit').removeClass('disabled').removeAttr('disabled');
            console.log('NO CHECKEADO');
        }

    }
});
});