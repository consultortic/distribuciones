odoo.define("acrux_whatsapp_sale.acrux_chat", (function(require) {
    "use strict";
    var chat = require("whatsapp_connector.chat_classes"), AcruxChatAction = require("whatsapp_connector.acrux_chat").AcruxChatAction, session = require("web.session"), core = require("web.core"), _t = core._t, QWeb = core.qweb;
    return AcruxChatAction.include({
        events: _.extend({}, AcruxChatAction.prototype.events, {
            "click li#tab_lastes_sale": "tabLastesSale",
            "click li#tab_order": "tabOrder"
        }),
        _initRender: function() {
            return this._super().then((() => (this.$tab_order = this.$("li#tab_order > a"), 
            this.$tab_content_order = this.$("div#tab_content_order > div.o_group"), this.$tab_content_indicator = this.$("div#tab_content_lastes_sale > div.o_group"), 
            session.user_has_group("sales_team.group_sale_salesman").then((hasGroup => {
                hasGroup ? this.allow_sale_order = !0 : (this.$("li#tab_order").addClass("d-none"), 
                this.allow_sale_order = !1);
            })))));
        },
        getRequiredViews: function() {
            return this._super().then((() => this._rpc({
                model: "ir.model.data",
                method: "get_object_reference",
                args: [ "whatsapp_connector_sale", "acrux_whatsapp_sale_order_form_view" ]
            }).then((result => {
                this.sale_order_view_id = result[1];
            }))));
        },
        tabOrder: function(_event, data) {
            let out = Promise.reject();
            if (this.selected_conversation) if (this.selected_conversation.isMine()) {
                let sale_order_id = this.selected_conversation.sale_order_id;
                this.saveDestroyWidget("sale_order_form");
                let options = {
                    context: this.action.context,
                    sale_order: sale_order_id,
                    action_manager: this.action_manager,
                    form_name: this.sale_order_view_id,
                    searchButton: !0
                };
                this.sale_order_form = new chat.SaleOrderForm(this, options), this.$tab_content_order.empty(), 
                out = this.sale_order_form.appendTo(this.$tab_content_order);
            } else this.$tab_content_order.html(QWeb.render("acrux_empty_tab", {
                notYourConv: !0
            })); else this.$tab_content_order.html(QWeb.render("acrux_empty_tab"));
            return out.then((() => data && data.resolve && data.resolve())), out.catch((() => data && data.reject && data.reject())), 
            out;
        },
        tabLastesSale: function(_event, data) {
            let out = Promise.reject();
            if (this.selected_conversation) if (this.selected_conversation.res_partner_id[0]) {
                this.saveDestroyWidget("indicator_widget");
                let options = {
                    partner_id: this.selected_conversation.res_partner_id[0]
                };
                this.indicator_widget = new chat.Indicators(this, options), this.$tab_content_indicator.empty(), 
                out = this.indicator_widget.appendTo(this.$tab_content_indicator);
            } else this.$tab_content_indicator.html(QWeb.render("acrux_empty_tab", {
                message: _t("This conversation does not have a partner.")
            })); else this.$tab_content_indicator.html(QWeb.render("acrux_empty_tab"));
            return out.then((() => data && data.resolve && data.resolve())), out.catch((() => data && data.reject && data.reject())), 
            out;
        },
        tabsClear: function() {
            this._super(), this.saveDestroyWidget("indicator_widget"), this.saveDestroyWidget("sale_order_form");
        }
    }), AcruxChatAction;
})), odoo.define("acrux_whatsapp_sale.chat_classes", (function(require) {
    "use strict";
    var chat = require("whatsapp_connector.chat_classes");
    return _.extend(chat, {
        Indicators: require("acrux_whatsapp_sale.indicators"),
        SaleOrderForm: require("acrux_whatsapp_sale.sale_order")
    });
})), odoo.define("acrux_whatsapp_sale.conversation", (function(require) {
    "use strict";
    var Conversation = require("whatsapp_connector.conversation");
    return Conversation.include({
        init: function(parent, options) {
            this._super.apply(this, arguments), this.sale_order_id = this.options.sale_order_id || [ !1, "" ];
        }
    }), Conversation;
})), odoo.define("acrux_whatsapp_sale.indicators", (function(require) {
    "use strict";
    var Widget = require("web.Widget"), ajax = require("web.ajax"), Indicators = Widget.extend({
        jsLibs: [ "/web/static/lib/Chart/Chart.js" ],
        init: function(parent, options) {
            this._super.apply(this, arguments), this.parent = parent, this.options = _.extend({}, options), 
            this.context = _.extend({}, this.options.context), this.partner_id = this.options.partner_id, 
            this.chart = null;
        },
        willStart: function() {
            return Promise.all([ this._super(), ajax.loadLibs(this), this.getPartnerIndicator() ]);
        },
        start: function() {
            return this._super().then((() => this._initRender()));
        },
        _initRender: function() {
            return this.month_last_sale_data && this.$el.append(this.graph_6last_sale()), this.html_last_sale && this.$el.append(this.html_last_sale), 
            Promise.resolve();
        },
        getPartnerIndicator: function() {
            return this._rpc({
                model: "res.partner",
                method: "get_chat_indicators",
                args: [ [ this.partner_id ] ]
            }).then((result => {
                result["6month_last_sale_data"] && (this.month_last_sale_data = result["6month_last_sale_data"]), 
                result.html_last_sale && (this.html_last_sale = result.html_last_sale);
            }));
        },
        graph_6last_sale: function() {
            let $canvas, context, config, $out = $("<div>");
            return $out.addClass("o_graph_barchart"), this.chart = null, $canvas = $("<canvas/>"), 
            $canvas.height(150), $out.append($canvas), context = $canvas[0].getContext("2d"), 
            config = this._getBarChartConfig(), this.chart = new Chart(context, config), $out;
        },
        _getBarChartConfig: function() {
            var data = [], labels = [];
            let data_param = this.month_last_sale_data;
            return data_param[0].values.forEach((pt => {
                data.push(pt.value), labels.push(pt.label);
            })), {
                type: "bar",
                data: {
                    labels,
                    datasets: [ {
                        data,
                        fill: "start",
                        label: data_param[0].key,
                        backgroundColor: [ "#FFD8E1", "#FFE9D3", "#FFF3D6", "#D3F5F5", "#CDEBFF", "#E6D9FF" ],
                        borderColor: [ "#FF3D67", "#FF9124", "#FFD36C", "#60DCDC", "#4CB7FF", "#A577FF" ]
                    } ]
                },
                options: {
                    legend: {
                        display: !1
                    },
                    scales: {
                        yAxes: [ {
                            display: !1
                        } ]
                    },
                    maintainAspectRatio: !1,
                    tooltips: {
                        intersect: !1,
                        position: "nearest",
                        caretSize: 0,
                        callbacks: {
                            label: (tooltipItem, data) => {
                                var label = data.datasets[tooltipItem.datasetIndex].label || "";
                                return label && (label += ": "), label += this.parent.format_monetary(tooltipItem.yLabel);
                            }
                        }
                    },
                    elements: {
                        line: {
                            tension: 1e-6
                        }
                    }
                }
            };
        }
    });
    return Indicators;
})), odoo.define("whatsapp_connector_sale.product_search", (function(require) {
    "use strict";
    var ProductSearch = require("whatsapp_connector.product_search");
    return ProductSearch.include({
        events: _.extend({}, ProductSearch.prototype.events, {
            "click .acrux_product_shop": "productOptions"
        }),
        doProductOption: function(product, event) {
            let out;
            return event.target.classList.contains("acrux_product_shop") ? (this.parent.$tab_order.hasClass("active") ? this.parent.sale_order_form.addProductToOrder(product) : this.parent.$tab_order.trigger("click", {
                resolve: () => this.parent.sale_order_form.addProductToOrder(product)
            }), out = Promise.resolve()) : out = this._super(product, event), out;
        },
        searchProduct: function() {
            return this._super().then((() => {
                this.parent.allow_sale_order || this.$product_items.find("button.acrux_product_shop").addClass("d-none");
            }));
        }
    }), ProductSearch;
})), odoo.define("acrux_whatsapp_sale.sale_order", (function(require) {
    "use strict";
    var SaleOrderForm = require("whatsapp_connector.form_view").extend({
        init: function(parent, options) {
            options && (options.model = "sale.order", options.record = options.sale_order), 
            this._super.apply(this, arguments), this.parent = parent, _.defaults(this.context, {
                default_partner_id: this.parent.selected_conversation.res_partner_id[0],
                default_team_id: this.parent.selected_conversation.team_id[0]
            });
        },
        _showAcruxFormView: function() {
            this._super().then((() => {
                if (this.moveSaleOrderNode(), !this.action.context.default_partner_id) {
                    let selector = "div.o_form_sheet > .o_notebook > .o_notebook_headers";
                    selector += " > ul.nav-tabs > li", this.acrux_form_widget.$(selector).eq(1).find("a").trigger("click");
                }
                this.$(".oe_title > h1").css("font-size", "20px");
            }));
        },
        recordUpdated: function(record) {
            return this._super(record).then((() => {
                if (this.moveSaleOrderNode(), record && record.data && record.data.id) {
                    let sale_order_key, partner_key, partner_id, localData;
                    sale_order_key = this.acrux_form_widget.handle, localData = this.acrux_form_widget.model.localData, 
                    sale_order_key && (partner_key = localData[sale_order_key].data.partner_id), partner_key && (partner_id = localData[partner_key]), 
                    this.parent.setNewPartner(partner_id);
                }
            }));
        },
        recordChange: function(sale_order) {
            return Promise.all([ this._super(sale_order), this._rpc({
                model: this.parent.model,
                method: "write",
                args: [ [ this.parent.selected_conversation.id ], {
                    sale_order_id: sale_order.data.id
                } ]
            }).then((isOk => {
                if (isOk) {
                    let result = [ sale_order.data.id, sale_order.data.name ];
                    this.parent.selected_conversation.sale_order_id = result, this.record = result;
                }
            })) ]);
        },
        makeDropable: function() {
            return this._super() || !0;
        },
        acceptDrop: function(ui) {
            return this._super(ui) || this._acceptSaleDrop(ui);
        },
        _acceptSaleDrop: function(ui) {
            return ui.hasClass("o_product_record");
        },
        handlerDradDrop: function(_event, ui) {
            return this._super(_event, ui).then((() => {
                if (this._acceptSaleDrop(ui.draggable) && this.parent.selected_conversation && this.parent.selected_conversation.isMine()) {
                    let product = this.parent.product_search.find(ui.draggable.data("id"));
                    product && this.addProductToOrder(product);
                }
            }));
        },
        moveSaleOrderNode: function() {
            let main_group = this.acrux_form_widget.$("div.oe_title").next("div.o_group");
            main_group.length && main_group.prev().hasClass("oe_title") && (main_group = main_group.detach(), 
            main_group.appendTo(this.acrux_form_widget.$("div.o_form_sheet > div.o_notebook > div.tab-content > div.tab-pane").first().next()));
        },
        addProductToOrder: function(product) {
            "edit" != this.acrux_form_widget.mode ? this.acrux_form_widget._setMode("edit").then((() => {
                this.addRecord(product);
            })) : this.addRecord(product);
        },
        addRecord: function(product) {
            let sale_key, orderline, renderer, options;
            sale_key = this.acrux_form_widget.handle, renderer = this.acrux_form_widget.renderer, 
            orderline = renderer.allFieldWidgets[sale_key].find((x => "order_line" == x.name));
            let link_id = orderline.$el.parent().attr("id"), $link = this.$('a[href$="' + link_id + '"]'), wait = 0;
            $link.parent().hasClass("active") || $link.hasClass("active") || ($link.trigger("click"), 
            wait = 100), setTimeout((() => {
                if (orderline.renderer.addCreateLine) orderline.renderer.unselectRow().then((() => {
                    options = {
                        onSuccess: this.addProductToOrderLine.bind(this, product)
                    }, orderline.renderer.trigger_up("add_record", options);
                })); else {
                    const context = Object.assign({}, this.context, {
                        default_product_id: product.id
                    });
                    options = {
                        context: [ context ]
                    }, orderline.renderer.trigger_up("add_record", options);
                }
            }), wait);
        },
        addProductToOrderLine: function(product) {
            let sale_key, orderline, renderer, orderline_id, product_id;
            sale_key = this.acrux_form_widget.handle, renderer = this.acrux_form_widget.renderer, 
            orderline = renderer.allFieldWidgets[sale_key].find((x => "order_line" == x.name)), 
            orderline_id = orderline.renderer.getEditableRecordID(), orderline_id && (product_id = orderline.renderer.allFieldWidgets[orderline_id], 
            product_id = product_id.find((x => "product_id" == x.name)), product_id && product_id.reinitialize({
                id: product.id,
                display_name: product.name
            }));
        },
        _getOnSearchChatroomDomain: function() {
            let domain = this._super();
            return domain.push([ "conversation_id", "=", this.parent.selected_conversation.id ]), 
            this.parent.selected_conversation.res_partner_id && this.parent.selected_conversation.res_partner_id[0] && (domain.unshift("|"), 
            domain.push([ "partner_id", "=", this.parent.selected_conversation.res_partner_id[0] ])), 
            domain;
        }
    });
    return SaleOrderForm;
}));