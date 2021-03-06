odoo.define("account_parent.coa_hierarchy", function (require) {
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var session = require("web.session");
    var CoAWidget = require("account_parent.CoAWidget");
    var framework = require("web.framework");

    var QWeb = core.qweb;

    var coa_hierarchy = AbstractAction.extend({
        hasControlPanel: true,
        // Stores all the parameters of the action.
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.given_context = action.context;
            this.controller_url = action.context.url;
            if (action.context.context) {
                this.given_context = action.context.context;
            }
        },
        willStart: function () {
            return Promise.all([this._super.apply(this, arguments), this.get_html()]);
        },
        set_html: function () {
            var self = this;
            var def = Promise.resolve();
            if (!this.report_widget) {
                this.report_widget = new CoAWidget(this, this.given_context);
                //            Def = this.report_widget.appendTo(this.$el);
                def = this.report_widget.appendTo(this.$(".o_content"));
            }
            return def.then(function () {
                self.report_widget.$el.html(self.html);
                if (self.given_context.auto_unfold) {
                    _.each(self.$el.find(".fa-caret-right"), function (line) {
                        self.report_widget.autounfold(line);
                    });
                }
            });
        },
        start: async function () {
            this.controlPanelProps.cp_content = {$buttons: this.$buttons};
            await this._super(...arguments);
            this.set_html();
        },
        // Fetches the html and is previous report.context if any, else create it
        get_html: async function () {
            const {html} = await this._rpc({
                model: "account.open.chart",
                method: "get_html",
                args: [this.given_context],
            });
            this.html = html;
            this.renderButtons();
        },

        // Updates the control panel and render the elements that have yet to be rendered
        update_cp: function () {
            if (!this.$buttons) {
                this.renderButtons();
            }
            this.controlPanelProps.cp_content = {$buttons: this.$buttons};
            return this.updateControlPanel();
        },
        renderButtons: function () {
            var parent_self = this;
            this.$buttons = $(QWeb.render("coaReports.buttons", {}));
            this.$buttons.bind("click", function () {
                if (this.id === "export_treeview_xls") {
                    // Xls output
                    var self_1 = parent_self,
                        view = parent_self.getParent();
                    const $element = $(parent_self.$el[0]).find(
                        ".table-responsive tbody tr"
                    );
                    const dict = [];

                    $element.each(function (index) {
                        var $el = $($element[index]);
                        dict.push({
                            id: $el.data("id"),
                            name: $el.data("name"),
                            wiz_id: $el.data("wiz_id"),
                            model_id: $el.data("model_id"),
                            unfoldable: $el.data("unfold"),
                            level: $el.find("td:first").data("level") || 1,
                        });
                    });
                    framework.blockUI();
                    let url_data = parent_self.controller_url.replace(
                        "active_id",
                        parent_self.given_context.active_id
                    );
                    url_data = url_data.replace("account_parent", "account_parent_xls");
                    url_data = url_data.replace("output_format", "xls");
                    session.get_file({
                        url: url_data,
                        data: {
                            data: JSON.stringify({
                                model: view.modelName,
                                wiz_id: parent_self.given_context.active_id,
                                report_data: JSON.stringify(dict),
                            }),
                        },
                        complete: $.unblockUI,
                        // Error: c.rpc_error.bind(c)
                        error: (error) =>
                            self_1.call("crash_manager", "rpc_error", error),
                    });
                } else {
                    // Pdf output
                    const $element = $(parent_self.$el[0]).find(
                        ".table-responsive tbody tr"
                    );
                    const dict = [];

                    $element.each(function (index) {
                        var $el = $($element[index]);
                        dict.push({
                            id: $el.data("id"),
                            name: $el.data("name"),
                            wiz_id: $el.data("wiz_id"),
                            model_id: $el.data("model_id"),
                            unfoldable: $el.data("unfold"),
                            level: $el.find("td:first").data("level") || 1,
                        });
                    });
                    framework.blockUI();
                    const url_data = parent_self.controller_url.replace(
                        "active_id",
                        parent_self.given_context.active_id
                    );
                    // Self.given_context.active_id
                    //            url_data = url_data.replace('output_format', 'pdf')
                    session.get_file({
                        url: url_data.replace("output_format", "pdf"),
                        data: {data: JSON.stringify(dict)},
                        complete: framework.unblockUI,
                        // Error: crash_manager.rpc_error.bind(crash_manager),
                        error: (error) =>
                            parent_self.call("crash_manager", "rpc_error", error),
                    });
                }
            });
            return this.$buttons;
        },
        do_show: function () {
            this._super();
            this.update_cp();
        },
    });

    core.action_registry.add("coa_hierarchy", coa_hierarchy);
    return coa_hierarchy;
});
