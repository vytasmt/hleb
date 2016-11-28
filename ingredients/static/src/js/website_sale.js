$(document).ready(function () {
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;
        $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change', function (ev) {
            var session = new openerp.Session();
            this.my_model = new openerp.Model(session, "product.attribute.value");
            var fff = this.my_model.call('pyth_met', []).done(function (result) {
                this.cool1 = result;
            });
        });
    });
});
