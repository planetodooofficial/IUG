odoo.define('drag_drop_multi_attachment.drag_drop_multi_attachment', function (require) {
"use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');
    var Sidebar = require('web.Sidebar');
    var framework = require('web.framework');
    
    FormView.include({
        toggle_drag_drop: function(event){
            var self = this;
            event.preventDefault();
            self.$el.find('.o_form_sheet').removeClass('hide_window');
            self.$el.find('div.drop_window').removeClass('drop_window_show');
        },
        toggle_buttons: function() {
            var self = this;
            this._super.apply(this, arguments);
            if(this.get("actual_mode") === "view") {
                self.$el.find('div.o_form_sheet').on('dragover',function(event) {
                    event.preventDefault();
                    self.$el.find('.o_form_sheet').addClass('hide_window');
                    self.$el.find('div.drop_window').addClass('drop_window_show');
                })
                .on('drop',function(event) {
                    if(event.originalEvent.dataTransfer && event.originalEvent.dataTransfer.files.length){
                        self.toggle_drag_drop(event);
                        framework.blockUI();
                        self.upload_multi_files(event.originalEvent.dataTransfer.files);
                    }
                })
                .on('dragleave', function(event){
                    self.toggle_drag_drop(event)
                });
            } else {
                self.$el.find('div.o_form_sheet').off('dragover').off('dragleave').off('drop');
            }
        },
        upload_multi_files: function(files){
            var self = this;
            var count = 1;
            _.each(files, function(file){
                var data = new FormData();
                data.append('callback', 'oe_fileupload_temp2');
                data.append('model', self.dataset.model);
                data.append('id', self.datarecord.id);
                data.append('ufile',file);
                data.append('csrf_token', core.csrf_token);
                $.ajax({
                    type: 'POST',
                    url: '/web/binary/upload_attachment',
                    cache: false,
                    processData: false,
                    contentType: false,
                    data: data,
                    success: function(id){
                        self.load_record(self.datarecord);
                        if(files.length == count) framework.unblockUI();
                        count += 1;
                    }

                });
            });

        }
    });
    Sidebar.include({
        on_attachment_changed: function(event) {
            var $e = $(event.target);
            if ($e.val() !== '') {
                this.getParent().upload_multi_files(event.target.files);
            }
        }
    });
});