$(document).ready(function () {
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;
        $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change', function (ev) {
            var session = new openerp.Session();
            this.pav_model = new openerp.Model(session, "product.attribute.value");
            this.pav_model.call('pyth_met', [], {
                'prod_id': this.prod_id,
                'value_id': this.value
            }).done(function (result) {
                this.ingredients = result['ingredients'];
                $(".ingred_string").text(result['ingredients']);
            });
        });
    });
});
