$(document).ready(function () {
    var count_variants = function () {
        // build order summary string
        var result = "";
        var variant_text = "";
        var value_text = "";
        var value_name = "";
        $("label > input.js_variant_change:checked").each(function () {
            var parent_li = $(this).parents("ul.list-unstyled"); // parent element is needed to get sequence number
            variant_text = $("li[data-order=" + parent_li.data("order") + "]").children().first().text(); // get corresponding variant text
            value_text = $(this).parent().text()
            if (variant_text == 'Выберите вкус'){
                value_name = value_text
            }
            result += variant_text + ": " + value_text + "; "; // get variant value
        });
        $(".variants_result_string").text(result);
        var session = new openerp.Session();
        this.pav_model = new openerp.Model(session, "product.attribute.value");
        this.pav_model.call('pyth_met', [], {
            'prod_id': this.prod_id,
            'value_id': this.value,
            'value_name': value_name
        }).done(function (result) {
            this.ingredients = result['ingredients'];
            $(".prod_ingred").text(result['prod_ingred']);
            $(".val_ingred").text(result['val_ingred']);
        });
    }
    count_variants();
    $(".js_add_cart_variants .main-variants-nav > li").click(function () {
        // show corresponding order attributes by clickng on variant
        var order = $(this).attr("data-order");
        $(".js_add_cart_variants .main-variants-nav > li").removeClass("active_variant");
        $(this).addClass("active_variant");
        $(".js_add_cart_variants")
        .find("ul.list-unstyled")
        .css(
            {
                "visibility": "hidden",
                "position": "absolute",
            }
        );
        $("ul[data-order=" + order + "]")
        .css(
            {
                "visibility": "visible",
                "position": "relative",
            }
        );
        count_variants();
    });
    $("label > input.js_variant_change").click(function () {
        count_variants();
    });

});

$(document).scroll(function() { // show top bar on scroll
    var scroll_delta = $(this).scrollTop();
    if (scroll_delta > 45) {
        $('#header-style-1').css("visibility", "visible");
    } else {
        $('#header-style-1').css("visibility", "hidden");
    }
});