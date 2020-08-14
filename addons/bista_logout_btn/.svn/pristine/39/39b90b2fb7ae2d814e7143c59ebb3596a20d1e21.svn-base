odoo.define('bista_logout_btn.UserMenu', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var framework = require('web.framework');
var Model = require('web.Model');
var session = require('web.session');
var Widget = require('web.Widget');
var UserMenu=require('web.UserMenu')

var _t = core._t;
var QWeb = core.qweb;

UserMenu.include({
    start: function() {
        var self=this;
        jQuery( ".logout_button" ).click(function() {
				var f = self['on_menu_logout'];
				if (f) {
					f($(this));
				}
			});
		this._super();
    },



});
});

