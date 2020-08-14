odoo.define('bista_logs.Chatter', function (require) {
"use strict";


var Chatter = require('mail.Chatter');
var MailThread = require('mail.ChatThread');
var core = require('web.core');
var ORDER = {
    ASC: 1,
    DESC: -1,
};
var QWeb = core.qweb;

Chatter.include({

    events: {
        "click .o_chatter_show_logs" :"on_show_logs_click",
        "click .o_chatter_button_new_message": "on_open_composer_new_message",
        "click .o_chatter_button_log_note": "on_open_composer_log_note",
    },


    on_show_logs_click: function () {
        var anchor=$('.o_chatter.o_form_field.oe_chatter').find('.o_chatter_show_logs');
        var table = $('.o_chatter.o_form_field.oe_chatter').find('.o_mail_thread')  // tbody containing all the rows
        if (anchor[0].innerHTML === 'Show Logs') {
                                 anchor[0].innerHTML='Hide Logs';
                                 table.toggle();
                        }
        else {
                                anchor[0].innerHTML='Show Logs';
                                table.toggle();
                        }
    },

});

MailThread.include({


//    render: function (messages, options) {
//        this._super();
//        var table = jQuery('.o_chatter.o_form_field.oe_chatter').find('.o_mail_thread');  // tbody containing all the rows
//    },

    render: function (messages, options) {
        var self = this;
        this._super();
        var msgs = _.map(messages, this._preprocess_message.bind(this));
        if (this.options.display_order === ORDER.DESC) {
            msgs.reverse();
        }
        options = _.extend({}, this.options, options);

        // Hide avatar and info of a message if that message and the previous
        // one are both comments wrote by the same author at the same minute
        // and in the same document (users can now post message in documents
        // directly from a channel that follows it)
        var prev_msg;
        _.each(msgs, function (msg) {
            if (!prev_msg || (Math.abs(msg.date.diff(prev_msg.date)) > 60000) ||
                prev_msg.message_type !== 'comment' || msg.message_type !== 'comment' ||
                (prev_msg.author_id[0] !== msg.author_id[0]) || prev_msg.model !== msg.model ||
                prev_msg.res_id !== msg.res_id) {
                msg.display_author = true;
            } else {
                msg.display_author = !options.squash_close_messages;
            }
            prev_msg = msg;
        });

        this.$el.html(QWeb.render('mail.ChatThread', {
            messages: msgs,
            options: options,
            ORDER: ORDER,
        }));

        _.each(msgs, function(msg) {
            var $msg = self.$('.o_thread_message[data-message-id="'+ msg.id +'"]');
            $msg.find('.o_mail_timestamp').data('date', msg.date);

            self.insert_read_more($msg);
        });

        if (!this.update_timestamps_interval) {
            this.update_timestamps_interval = setInterval(function() {
                self.update_timestamps();
            }, 1000*60);
        }

        var table = jQuery('.o_chatter.o_form_field.oe_chatter').find('.o_mail_thread');  // tbody containing all the rows
        table.hide();
    },
});
})
