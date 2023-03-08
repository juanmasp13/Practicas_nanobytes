odoo.define('gap_LANDSCAPE_TERMINOS.javascript', function(require) {
    'use strict'
    console.log('holaaaaaaaa');

    var core = require('web.core');
    var config = require('web.config');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('website_sale.VariantMixin');
    publicWidget.registry.terminos = publicWidget.Widget.extend({
        selector: '.checkout_autoformat',
        start: function () {
            console.log('entro');
            var self = this;
            this.$el.find('#checkbox_terminos').on('change', function (ev) {
                var boton = self.$el.find('.btn btn-primary mb32 a-submit a-submit-disable a-submit-loading');
                if(self.$el.find('#checkbox_terminos').is(':checked')){
                    console.log('marcado');
                    console.log('MI BOTON: '+boton);
                    console.log(boton);
                    //boton.addClass('juanma');
                    boton.hide();
                }else{
                    console.log('desmarcado');
                    console.log('MI BOTON: '+boton);
                    console.log(boton);
                    //boton.removeClass('juanma');
                    boton.show();
                }

            });
            return this._super.apply(this, arguments);
     }
    });

   /*publicWidget.registry.websiteSaleCart = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change #checkbox_terminos': '_onChangeNext',
    },*/

    /*_onChangeNext: function (ev) {
        console.log("CHECKBOX: "+$(ev.currentTarget).is(":checked"));
        if ($(ev.currentTarget).is(":checked")){
            $(ev.currentTarget).hasClass('.a-submit').addClass('disabled').attr('disabled', 'disabled');
            console.log('CHECKEADO');
        }else{
            $('.a-submit').removeClass('disabled').removeAttr('disabled');
            console.log('NO CHECKEADO');
        }

    console.log('hjdgsjhf');
    }*/
});