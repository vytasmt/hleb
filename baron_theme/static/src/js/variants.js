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
            // if (variant_text == 'Выберите вкус'){
            //     value_name = value_text
            // }
            // result += variant_text + ": " + value_text + "; "; // get variant value
            result += value_text + "; "; // get variant value
        });
        $(".variants_result_string").text(result);
        openerp.jsonRpc("/shop/properties", 'call', {
            'prod_id': this.prod_id,
            'value_id': this.value,
            'value_name': value_name
        }).then(function (result) {
            $(".prod_property_caption").text(result['prod_property_caption']);
            $(".prod_property").html(result['prod_property']);
            $(".val_property_caption").text(result['val_property_caption']);
            $(".val_property").html(result['val_property']);
            if (result['prod_property_caption'] == ''){
                 $(".prod_property_caption").hide();
            }
            else{
                $(".prod_property_caption").show();
            }
            if (result['prod_property'] == ''){
                 $(".prod_property").hide();
            }
            else{
                $(".prod_property").show();
            }
            if (result['val_property_caption'] == ''){
                 $(".val_property_caption").hide();
            }
            else{
                $(".val_property_caption").show();
            }
            if (result['val_property'] == ''){
                 $(".val_property").hide();
            }
            else{
                $(".val_property").show();
            }

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

$( document ).ready(function() {

$('#add_to_cart').on('click', function () {
        var cart = $('.fa-shopping-cart');
        var imgtodrag = $(this).parents().find('img').eq(0);
        if (imgtodrag) {
            var imgclone = imgtodrag.clone()
                .offset({
                top: imgtodrag.offset().top,
                left: imgtodrag.offset().left
            })
                .css({
                'opacity': '0.8',
                    'position': 'absolute',
                    'height': '350px',
                    'width': '350px',
                    'z-index': '100'
            })
                .appendTo($('body'))
                .animate({
                'top': cart.offset().top + 10,
                    'left': cart.offset().left + 10,
                    'width': 150,
                    'height': 150
            }, 2000, 'easeInOutExpo');
            
            imgclone.animate({
                'width': 0,
                    'height': 0
            }, function () {
                $(this).detach()
            });
        }
    });
});