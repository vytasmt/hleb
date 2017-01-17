$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    var $shippingDifferent = $("select[name='shipping_id']", oe_website_sale);
    $shippingDifferent.change(function (event) {
        var value = +$shippingDifferent.val();
        var data = $shippingDifferent.find("option:selected").data();
        var $snipping = $(".js_shipping", oe_website_sale);
        var $inputs = $snipping.find("input");
        var $selects = $snipping.find("select");

        $snipping.toggle(!!value);
        $inputs.attr("readonly", value <= 0 ? null : "readonly" ).prop("readonly", value <= 0 ? null : "readonly" );
        $selects.attr("disabled", value <= 0 ? null : "disabled" ).prop("disabled", value <= 0 ? null : "disabled" );

        $inputs.each(function () {
            $(this).val( data[$(this).attr("name")] || "" );
        });
    });

    // change for css
    $(oe_website_sale).on('mouseup touchend', '.js_publish', function (ev) {
        $(ev.currentTarget).parents(".thumbnail").toggleClass("disabled");
    });

    $(oe_website_sale).on("click", ".js_check_product_baron", function () {
        var $input = $(this);
        if ($(this).parent().find('.product_id').length > 0){
            var $pid = $(this).parent().find('.product_id').attr('value');
            var $qty = $(this).parent().find('.js_quantity').attr('value');
            //var value = parseInt($input.val(), 10);
            //var line_id = parseInt($input.data('line-id'),10);
            if (isNaN($qty)) $qty = 0;
            openerp.jsonRpc("/shop/cart/update_baron", 'call', {
                'line_id': false,
                'product_id': $pid,
                'add_qty': $qty,
                'display':true})
                .then(function (data) {
                    if (!data.quantity) {
                        location.reload();
                        return;
                    }
                    var $q = $(".my_cart_quantity");
                    $q.parent().parent().removeClass("hidden", !data.quantity);
                    $q.html(data.cart_quantity).hide().fadeIn(600);

                    $input.val(data.quantity);
                    //$('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                    $("#cart_total").replaceWith(data['website_sale.total']);
                });
        }else{
            alert("Can't add this Product")
        }
    });

    $(oe_website_sale).on("change", ".oe_cart input.js_quantity", function () {
        var $input = $(this);
        var value = parseInt($input.val(), 10);
        var line_id = parseInt($input.data('line-id'),10);
        if (isNaN(value)) value = 0;
        openerp.jsonRpc("/shop/cart/update_json", 'call', {
            'line_id': line_id,
            'product_id': parseInt($input.data('product-id'),10),
            'set_qty': value})
            .then(function (data) {
                if (!data.quantity) {
                    location.reload();
                    return;
                }
                var $q = $(".my_cart_quantity");
                $q.parent().parent().removeClass("hidden", !data.quantity);
                $q.html(data.cart_quantity).hide().fadeIn(600);

                $input.val(data.quantity);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                $("#cart_total").replaceWith(data['website_sale.total']);
                $("#minimal_total_alert").replaceWith(data['baron_theme.minimal_total_alert']);
            });
    });

    // hack to add and rome from cart with json
    $(oe_website_sale).on('click', 'a.js_add_cart_json', function (ev) {
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $input = $link.parent().parent().find("input");
        var min = parseFloat($input.data("min") || 0);
        var max = parseFloat($input.data("max") || Infinity);
        var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val(),10);
        $input.val(quantity > min ? (quantity < max ? quantity : max) : min);
        $('input[name="' + $input.attr("name") + '"]').val(quantity > min ? (quantity < max ? quantity : max) : min);
        $input.change();
        if (quantity > 0) {
            var el = $("input.js_variant_change");
            var $ul = $(el).parents('.js_add_cart_variants:first');
            var $parent = $ul.closest('.js_product');
            var $product_id = $parent.find('input.product_id').first();
            var $price = $parent.find(".oe_price:first .oe_currency_value");
            var $price_per_one = $parent.find(".price_per_one:first");
            var $price_per_one_qty = $parent.find(".price_per_one_qty:first");
            var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
            var variant_ids = $ul.data("attribute_value_ids");
            var values = [];
            var val_pack_qty = [];
            $parent.find('input.js_variant_change:checked, sthisect.js_variant_change').each(function () {
                values.push(+$(this).val());
                if ($($(this).find(":selected")) && $($(this).find(":selected")).attr("pack")) {
                    val_pack_qty.push(+$($(this).find(":selected")).attr("pack"));
                }
                if ($(this).attr("pack")) {
                    val_pack_qty.push(+$(this).attr("pack"));
                }
            });
            $(oe_website_sale).find('span.product_pack_variant').each(function () {
                if ($(el).attr("pack")) {
                    val_pack_qty.push(+$(el).attr("pack"));
                }
            });
            $parent.find("label").removeClass("text-muted css_not_available");
            var coef = 1;
            for (var v in val_pack_qty) {
                coef = coef * val_pack_qty[v];
                break
            }
            var product_id = false;
            var uom_val = parseFloat($("input.js_variant_change:checked").siblings("span[name=attr_uom_val]").text()) || 1;
            var uom_qty = parseFloat($('#uom_qty').text());
            var uos_qty = parseFloat($('#uos_qty').text());
            var factor = parseFloat($('#factor').text());
            var uos_coeff = parseFloat($('#uos_coeff').text());
            var res_uom_qty = uom_qty;
            var res_uos_qty = uos_qty;
            res_uom_qty = uom_qty * uom_val;
            res_uos_qty = uos_qty * uom_val * uos_coeff;
            var uos_name = $("#uos_name").text();
            var uom_name = $('#uom_name').text();
            var uos_cof = parseFloat($("#uos_cof").text()) || 1;
            var basic_price = parseFloat($("#list_price").text());
            var qty = 0;
            if (res_uos_qty == res_uom_qty) {
	        qty = quantity_to_str(res_uos_qty) + " " + uos_name;
	    }
	    else {qty = quantity_to_str(res_uos_qty) + " " + uos_name  + " (" +  quantity_to_str(res_uom_qty)  + " " + uom_name + ")";}
            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                    product_id = variant_ids[k][0];
                    var result_price = parseFloat(variant_ids[k][3]);
                    var total_price = result_price * quantity;
                    $price.html(price_to_str(total_price));
                    $price_per_one.html(price_to_str(total_price / (uom_val * quantity)));
                    $price_per_one_qty.html(qty); //
                    $default_price.html(price_to_str(variant_ids[k][3]));
                    if (variant_ids[k][3] - variant_ids[k][2] > 0.2) {
                        $default_price.closest('.oe_website_sale').addClass("discount");
                    } else {
                        $default_price.closest('.oe_website_sale').removeClass("discount");
                    }
                    break;
                }
            }

            if (product_id) {
                var $img = $(el).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
                $img.attr("src", "/website/image/product.product/" + product_id + "/image");
                $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                    .data('oe-model', 'product.product').data('oe-id', product_id);
            }
            $parent.find("input.js_variant_change:radio, select.js_variant_change").each(function () {
                var $input = $(el);
                var id = +$input.val();
                var values = [id];
                $parent.find("ul:not(:has(input.js_variant_change[value='" + id + "'])) input.js_variant_change:checked, select").each(function () {
                    values.push(+$(el).val());
                });
                for (var k in variant_ids) {
                    if (!_.difference(values, variant_ids[k][1]).length) {
                        return;
                    }
                }
                $input.closest("label").addClass("css_not_available");
                $input.find("option[value='" + id + "']").addClass("css_not_available");
            });
            if (product_id) {
                $parent.removeClass("css_not_available");
                $product_id.val(product_id);
                $parent.find(".js_check_product").removeAttr("disabled");
            } else {
                $parent.addClass("css_not_available");
                $product_id.val(0);
                $parent.find(".js_check_product").attr("disabled", "disabled");
            }
            return false;
        }
    });
    // $(oe_website_sale).on('click', 'a.js_add_cart_json')
    $('.oe_website_sale .a-submit, #comment .a-submit').off('click').on('click', function () {
        $(this).closest('form').submit();
        setTimeout(update_cart_amount, 2000);

    });
    function update_cart_amount() {
        openerp.jsonRpc("/shop/get_order", 'call', {})
            .then(function (data) {
                var $q = $(".my_cart_quantity");
                $q.html(data['cart_uos_qty']).hide().fadeIn(600);
            });
    };
    $('form.js_attributes input, form.js_attributes select', oe_website_sale).on('change', function () {
        $(this).closest("form").submit();
    });

    // change price when they are variants
    $('form.js_add_cart_json label', oe_website_sale).on('mouseup touchend', function (ev) {
        var $label = $(this);
        var $price = $label.parents("form:first").find(".oe_price .oe_currency_value");
        if (!$price.data("price")) {
            $price.data("price", parseFloat($price.text()));
        }
        var value = $price.data("price") + parseFloat($label.find(".badge span").text() || 0);
        var dec = value % 1;
        $price.html(value + (dec < 0.01 ? ".00" : (dec < 1 ? "0" : "") ));
    });
    // hightlight selected color
    $('.css_attribute_color input', oe_website_sale).on('change', function (ev) {
        $('.css_attribute_color').removeClass("active");
        $('.css_attribute_color:has(input:checked)').addClass("active");
    });

    function price_to_str(price) {
        price = Math.round(price * 100) / 100;
        var dec = Math.round((price % 1) * 100);
        return price + (dec ? '' : '.0') + (dec%10 ? '' : '0');
    }
    function quantity_to_str(price) {
        price = Math.round(price * 100) / 100;
        var dec = Math.round((price % 1) * 100);
        return price;
    }

    $(oe_website_sale).on('change', 'input.js_product_change', function (ev) {
        var $parent = $(this).closest('.js_product');
        $parent.find(".oe_default_price:first .oe_currency_value").html( price_to_str(+$(this).data('lst_price')) );
        $parent.find(".oe_price:first .oe_currency_value").html(price_to_str(+$(this).data('price')) );

        var $img = $(this).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
        $img.attr("src", "/website/image/product.product/" + $(this).val() + "/image");
    });
    $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change', recalculate);
    function recalculate (ev) {
        var $ul = $(this).parents('.js_add_cart_variants:first');
        var $parent = $ul.closest('.js_product');
        var $product_id = $parent.find('input.product_id').first();
        var $price = $parent.find(".oe_price:first .oe_currency_value");
        var $price_per_one = $parent.find(".price_per_one:first");
        var $price_per_one_qty = $parent.find(".price_per_one_qty:first");
        var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
        var variant_ids = $ul.data("attribute_value_ids");
        var values = [];
        var val_pack_qty = [];
        $parent.find('input.js_variant_change:checked, sthisect.js_variant_change').each(function () {
            values.push(+$(this).val());
            if ($($(this).find(":selected")) && $($(this).find(":selected")).attr("pack")) {
                val_pack_qty.push(+$($(this).find(":selected")).attr("pack"));
            }
            if ($(this).attr("pack")) {
                val_pack_qty.push(+$(this).attr("pack"));
            }
        });

        $(oe_website_sale).find('span.product_pack_variant').each(function () {
            if ($(this).attr("pack")) {
                val_pack_qty.push(+$(this).attr("pack"));
            }
        });

        $parent.find("label").removeClass("text-muted css_not_available");

        var coef = 1;
        for (var v in val_pack_qty) {
            coef = coef * val_pack_qty[v];
            break
        }
        var product_id = false;
        var uom_val = parseFloat($("input.js_variant_change:checked").siblings("span[name=attr_uom_val]").text()) || 1;
        var uom_qty = parseFloat($('#uom_qty').text());
        var uos_qty = parseFloat($('#uos_qty').text());
        var factor = parseFloat($('#factor').text());
        var uos_coeff = parseFloat($('#uos_coeff').text());
        var res_uom_qty = uom_qty;
        var res_uos_qty = uos_qty;
        res_uom_qty = uom_qty * uom_val;
        res_uos_qty = uos_qty * uom_val * uos_coeff;
        var uos_name = $("#uos_name").text();
        var uom_name = $('#uom_name').text();
        var uos_cof = parseFloat($("#uos_cof").text()) || 1;
        var basic_price = parseFloat($("#list_price").text());
        var quantity = parseFloat($("[name='add_qty']").val());
        var qty = 0;
        if (res_uos_qty == res_uom_qty) {
            qty = quantity_to_str(res_uos_qty) + " " + uos_name;
        }
        else {
            qty = quantity_to_str(res_uos_qty) + " " + uos_name + " (" + quantity_to_str(res_uom_qty) + " " + uom_name + ")";
        }
        for (var k in variant_ids) {
            if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                product_id = variant_ids[k][0];
                var result_price = parseFloat(variant_ids[k][3]);
                var total_price = result_price * quantity;
                $price.html(price_to_str(total_price));
                $price_per_one.html(price_to_str(total_price / (uom_val * quantity)));
                $price_per_one_qty.html(qty); //
                $default_price.html(price_to_str(variant_ids[k][3]));
                if (variant_ids[k][3] - variant_ids[k][2] > 0.2) {
                    $default_price.closest('.oe_website_sale').addClass("discount");
                } else {
                    $default_price.closest('.oe_website_sale').removeClass("discount");
                }
                break;
            }
        }

        if (product_id) {
            var $img = $(this).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
            $img.attr("src", "/website/image/product.product/" + product_id + "/image");
            $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                .data('oe-model', 'product.product').data('oe-id', product_id);
        }

        $parent.find("input.js_variant_change:radio, select.js_variant_change").each(function () {
            var $input = $(this);
            var id = +$input.val();
            var values = [id];

            $parent.find("ul:not(:has(input.js_variant_change[value='" + id + "'])) input.js_variant_change:checked, select").each(function () {
                values.push(+$(this).val());
            });

            for (var k in variant_ids) {
                if (!_.difference(values, variant_ids[k][1]).length) {
                    return;
                }
            }

            $input.closest("label").addClass("css_not_available");
            $input.find("option[value='" + id + "']").addClass("css_not_available");
        });
        if (product_id) {
            $parent.removeClass("css_not_available");
            $product_id.val(product_id);
            $parent.find(".js_check_product").removeAttr("disabled");
        } else {
            $parent.addClass("css_not_available");
            $product_id.val(0);
            $parent.find(".js_check_product").attr("disabled", "disabled");
        }
        $(".finger").click();
    }
    $('.js_add_cart_variants', oe_website_sale).each(function () {
        $('input.js_variant_change, select.js_variant_change', this).first().trigger('change');
    });

    $(oe_website_sale).on('change', "select[name='country_id']", function () {
        var $select = $("select[name='state_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-country_id="+($(this).val() || 0)+"]").show().size();
        $select.parent().toggle(nb>1);
    });
    $(oe_website_sale).find("select[name='country_id']").change();

    $(oe_website_sale).on('change', "select[name='shipping_country_id']", function () {
        var $select = $("select[name='shipping_state_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-country_id="+($(this).val() || 0)+"]").show().size();
        $select.parent().toggle(nb>1);
    });
    $(oe_website_sale).find("select[name='shipping_country_id']").change();
    // $(".finger").first().css("class","active_variant");
    $("li[data-order=1]").addClass( "active_variant" );
});
});


