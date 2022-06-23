odoo.define("whatsapp_connector_chatter.Chatter", (function(require) {
    "use strict";
    var Widget = require("web.Widget"), AcruxChatAction = require("whatsapp_connector.acrux_chat").AcruxChatAction, chat = require("whatsapp_connector.chat_classes"), core = require("web.core"), QWeb = core.qweb, Chatter = Widget.extend({
        events: {
            "click .o_acrux_chat_item": "selectConversation",
            "click button.acrux_load_more": "loadMoreMessage"
        },
        init: function(parent, options) {
            this._super.apply(this, arguments), this.partner_id = null, this.conv_ids = [], 
            this.selected_conversation = null, this.whatsapp_limit = 20, this.currency_id = null, 
            this.props = this.getParent().props, this.promise_render = null, this.is_chatroom_installed = !0, 
            this.setPartner();
        },
        destroy: function() {
            this.selected_conversation = null, this._super.apply(this, arguments);
        },
        update: function(props) {
            let prom = [];
            if (this.needUpdate(props)) {
                if (this.props = props, this.setPartner(), this.props.isWhatsappTalkVisible && prom.push(this.queryConversation()), 
                this.currency_id || prom.push(AcruxChatAction.prototype.getCurrency.apply(this)), 
                !this.product_used_fields) {
                    let tmpModel = this.model;
                    this.model = "acrux.chat.conversation";
                    let promTmp = AcruxChatAction.prototype.getProductUsedFields.apply(this);
                    promTmp.finally((() => {
                        this.model = tmpModel;
                    })), prom.push(promTmp);
                }
            } else this.props = props;
            return Promise.all(prom);
        },
        render: function() {
            let out;
            return this.promise_render ? out = Promise.resolve() : (this.props.isWhatsappTalkVisible ? out = this.renderWhatsapp() : (this.do_hide(), 
            out = Promise.resolve()), this.promise_render = out.then((() => this.promise_render = null))), 
            out;
        },
        needUpdate: function(props) {
            let flag = !1;
            return this.props.recId == props.recId ? "res.partner" === this.props.modelName ? (this.partner_id || props.recId) && (flag = !this.partner_id || !props.recId || this.partner_id != props.recId) : (this.partner_id || props.originalState.data[props.fieldName]) && (flag = !this.partner_id || !props.originalState.data[props.fieldName] || this.partner_id != props.originalState.data[props.fieldName].data.id) : flag = !0, 
            flag;
        },
        clearData: function() {
            this.selected_conversation = null, this.conv_ids && (this.conv_ids.forEach((x => x.destroy())), 
            this.conv_ids = []);
        },
        renderWhatsapp: function() {
            let $conv = $(QWeb.render("chatter.WhatsappConversation")), $el = $conv.find(".o_current_chats"), promises = [];
            return this.conv_ids.forEach((x => promises.push(x.appendTo($el)))), Promise.all(promises).then((() => {
                if (this.renderElement(), $conv.appendTo(this.$el), this.$chat_message = this.$("div.o_chat_thread"), 
                this.selected_conversation) return this.renderConversation();
            }));
        },
        setPartner: function() {
            this.props.recId > 0 ? "res.partner" === this.props.modelName ? this.partner_id = this.props.recId : this.props.originalState.data[this.props.fieldName] ? this.partner_id = this.props.originalState.data[this.props.fieldName].data.id : this.partner_id = null : this.partner_id = null, 
            this.clearData();
        },
        queryConversation: function() {
            let out = Promise.resolve();
            return this.partner_id ? out = this._rpc({
                model: "acrux.chat.conversation",
                method: "search_conversation_by_partner",
                args: [ this.partner_id, this.whatsapp_limit ]
            }).then((conv_ids => {
                this.clearData(), this.conv_ids = conv_ids.map((conv => new chat.Conversation(this, conv))), 
                this.selected_conversation = this.conv_ids[0];
            })) : this.clearData(), out;
        },
        selectConversation: function(event) {
            let id = $(event.currentTarget).data("id"), conv_id = this.conv_ids.find((x => x.id == id));
            if (conv_id && (null == this.selected_conversation || this.selected_conversation.id != conv_id.id)) return this.selected_conversation = conv_id, 
            this.renderConversation();
        },
        renderConversation: function() {
            let $conv = this.$(`div.o_acrux_chat_item[data-id="${this.selected_conversation.id}"]`);
            return this.$(".o_acrux_chat_item").removeClass("active"), $conv.addClass("active"), 
            this.renderMessage().then((() => {
                let $message = this.$chat_message[0];
                $message.scrollTop = $message.scrollHeight - $message.clientHeight;
            }));
        },
        renderMessage: function() {
            let out;
            if (this.$chat_message.empty(), this.selected_conversation.messages.length) {
                let messages = this.selected_conversation.messages;
                out = this.selected_conversation._syncLoop(0, messages, -1, this.$chat_message);
            } else out = Promise.resolve();
            return out.then((() => this.renderLoadBtn()));
        },
        renderLoadBtn: function() {
            if (this.$chat_message.find(".acrux_load_more").remove(), this.selected_conversation && this.selected_conversation.messages.length % this.whatsapp_limit == 0 && this.selected_conversation.messages.length) {
                var btn = QWeb.render("whatsapp.connector.load_more_btn");
                this.$chat_message.prepend(btn);
            }
        },
        loadMoreMessage: function() {
            let out = Promise.resolve();
            if (this.selected_conversation.messages.length >= this.whatsapp_limit) {
                var select = this.selected_conversation;
                out = this._rpc({
                    model: "acrux.chat.conversation",
                    method: "build_dict",
                    args: [ [ select.id ], this.whatsapp_limit, select.messages.length ]
                }).then((async result => {
                    if (result[0].messages) return select.addExtraClientMessage(result[0].messages).then((() => this.renderLoadBtn()));
                }));
            }
            return out;
        },
        format_monetary: function(val) {
            return AcruxChatAction.prototype.format_monetary.apply(this, arguments);
        }
    });
    return core.action_registry.add("acrux.chat.hide_chatter_whatsapp_tag", (function(_self, _action, _options) {
        let el = document.querySelector(".o_ChatterTopbar_whatsapp");
        return el && el.classList.contains("o-active") && el.click(), {
            type: "ir.actions.act_window_close"
        };
    })), Chatter;
})), odoo.define("whatsapp_connector_chatter/static/src/js/component/view_conv/chatter.js", (function(require) {
    "use strict";
    const ChatterTopbarWhatsapp = require("whatsapp_connector_chatter/static/src/js/component/view_conv/chatter_topbar.js"), WhatsappConversation = require("whatsapp_connector_chatter/static/src/js/component/view_conv/whatsapp_conversation.js"), Chatter = require("mail/static/src/components/chatter/chatter.js"), WhatsappChatter = require("whatsapp_connector_chatter.Chatter"), {useState} = owl.hooks, {useRef} = owl.hooks;
    class ChatterWhatsapp extends Chatter {
        constructor(...args) {
            super(...args);
            let state = this.state || {};
            Object.assign(state, {
                isWhatsappTalkVisible: !1
            }), this.state = useState(state), this._whatsappConversationRef = useRef("whatsappConversationRef"), 
            this.widgetComponents || (this.widgetComponents = {}), Object.assign(this.widgetComponents, {
                WhatsappChatter
            });
        }
        showWhatsappTalk() {
            this.state.isWhatsappTalkVisible = !0;
        }
        hideWhatsappTalk() {
            this.state.isWhatsappTalkVisible = !1;
        }
        async _onClickWhatsappTalk() {
            this.state.isWhatsappTalkVisible ? this.state.isWhatsappTalkVisible = !1 : this._whatsappConversationRef.comp && (await this._whatsappConversationRef.comp.queryConversations(), 
            this.state.isWhatsappTalkVisible = !0, this.chatter.update({
                isComposerVisible: !1
            }));
        }
    }
    return Object.assign(ChatterWhatsapp.components, {
        WhatsappConversation,
        ChatterTopbar: ChatterTopbarWhatsapp
    }), Object.assign(ChatterWhatsapp.props, {
        originalState: Object,
        isChatroomInstalled: Boolean,
        isInAcruxChatRoom: Boolean
    }), ChatterWhatsapp;
})), odoo.define("whatsapp_connector_chatter/static/src/js/component/view_conv/chatter_container.js", (function(require) {
    "use strict";
    const ChatterContainer = require("mail/static/src/components/chatter_container/chatter_container.js"), ChatterWhatsapp = require("whatsapp_connector_chatter/static/src/js/component/view_conv/chatter.js");
    return Object.assign(ChatterContainer.components, {
        Chatter: ChatterWhatsapp
    }), Object.assign(ChatterContainer.props, {
        originalState: Object
    }), ChatterContainer;
})), odoo.define("whatsapp_connector_chatter/static/src/js/component/view_conv/chatter_model.js", (function(require) {
    "use strict";
    require("mail/static/src/models/chatter/chatter.js");
    const {registry} = require("mail/static/src/model/model_core.js");
    var factoryBak = registry["mail.chatter"].factory;
    registry["mail.chatter"].factory = dependencies => {
        let outClass = factoryBak(dependencies);
        class Chatter extends outClass {
            create(vals) {
                let data = {};
                return Object.assign(data, vals), data.originalState && delete data.originalState, 
                super.create(data);
            }
            update(vals) {
                let data = {};
                return Object.assign(data, vals), data.originalState && delete data.originalState, 
                super.update(data);
            }
        }
        return Object.assign(Chatter, outClass), Chatter;
    };
})), odoo.define("whatsapp_connector_chatter/static/src/js/component/view_conv/chatter_topbar.js", (function(require) {
    "use strict";
    const WhatsappTopbarButton = require("whatsapp_connector_chatter/static/src/js/component/view_conv/whatsapp_topbar_button.js"), ChatterTopbar = require("mail/static/src/components/chatter_topbar/chatter_topbar.js");
    class ChatterTopbarWhatsapp extends ChatterTopbar {
        _onClickLogNote(ev) {
            super._onClickLogNote(ev), this.__owl__.parent.hideWhatsappTalk();
        }
        _onClickSendMessage(ev) {
            super._onClickSendMessage(ev), this.__owl__.parent.hideWhatsappTalk();
        }
        _onClickWhatsappTalk() {
            return this.__owl__.parent._onClickWhatsappTalk();
        }
    }
    return Object.assign(ChatterTopbarWhatsapp.props, {
        isWhatsappTalkVisible: Boolean,
        isChatroomInstalled: Boolean,
        isInAcruxChatRoom: Boolean
    }), Object.assign(ChatterTopbarWhatsapp.components, {
        WhatsappTopbarButton
    }), ChatterTopbarWhatsapp;
})), odoo.define("whatsapp_connector_chatter.FormRenderer", (function(require) {
    "use strict";
    require("mail/static/src/widgets/form_renderer/form_renderer.js"), require("web.FormRenderer").include({
        _makeChatterContainerProps() {
            let out = this._super.apply(this, arguments);
            return out.originalState = this.state, out;
        }
    });
})), odoo.define("whatsapp_connector_chatter/static/src/js/component/view_conv/whatsapp_conversation.js", (function(require) {
    "use strict";
    var Chatter = require("mail/static/src/components/chatter/chatter.js");
    const {ComponentAdapter} = require("web.OwlCompatibility");
    class WhatsappConversation extends ComponentAdapter {
        renderWidget() {
            return this.widget.render();
        }
        updateWidget(nextProps) {
            return this.widget.update(nextProps);
        }
        async queryConversations() {
            return this.widget.queryConversation();
        }
    }
    return Object.assign(Chatter.components, {
        WhatsappConversation
    }), Object.assign(WhatsappConversation, {
        props: {
            modelName: String,
            recId: Number,
            fieldName: String,
            chatterLocalId: String,
            isWhatsappTalkVisible: Boolean,
            Component: Function,
            widgetArgs: Array,
            originalState: Object
        }
    }), WhatsappConversation;
})), odoo.define("whatsapp_connector_chatter/static/src/js/component/view_conv/whatsapp_topbar_button.js", (function(require) {
    "use strict";
    const {Component} = owl;
    class WhatsappTopbarButton extends Component {
        get chatter() {
            return this.env.models["mail.chatter"].get(this.props.chatterLocalId);
        }
        _onClickWhatsappTalk() {
            return this.__owl__.parent._onClickWhatsappTalk();
        }
    }
    return Object.assign(WhatsappTopbarButton, {
        props: {
            chatterLocalId: String,
            isWhatsappTalkVisible: Boolean
        },
        template: "whatsapp.connector.WhatsappTopbarButton"
    }), WhatsappTopbarButton;
}));