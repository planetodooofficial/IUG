//openerp.web_printscreen_record = function(instance, m) {
//
//    var _t = instance.web._t,
//    QWeb = instance.web.qweb;
//
//    instance.web.ListView.include({
//        load_list: function () {
//            var self = this;
//            this._super.apply(this, arguments);
//            self.$pager.find(".oe_list_button_import_excel").unbind('click').click(function(event){self.export_to_excel("excel")})
//            self.$pager.find(".oe_list_button_import_pdf").unbind('click').click(function(event){self.export_to_excel("pdf")})
//        },
//        export_to_excel: function(export_type) {
//            var self = this
//            var export_type = export_type
//            view = this.getParent()
//            // Find Header Element
//            header_eles = self.$el.find('.oe_list_header_columns')
//            header_name_list = []
//            $.each(header_eles,function(){
//                $header_ele = $(this)
//                header_td_elements = $header_ele.find('th')
//                $.each(header_td_elements,function(){
//                    $header_td = $(this)
//                    text = $header_td.text().trim() || ""
//                    data_id = $header_td.attr('data-id')
//                    if (text && !data_id){
//                        data_id = 'group_name'
//                    }
//                    header_name_list.push({'header_name': text.trim(), 'header_data_id': data_id})
//                   // }
//                });
//            });
//
//            //Find Data Element
//            data_eles = self.$el.find('.oe_list_content > tbody > tr')
//            export_data = []
//            $.each(data_eles,function(){
//                data = []
//                $data_ele = $(this)
//                is_analysis = false
//                if ($data_ele.text().trim()){
//                //Find group name
//	                group_th_eles = $data_ele.find('th')
//	                $.each(group_th_eles,function(){
//	                    $group_th_ele = $(this)
//	                    text = $group_th_ele.text()
//	                    is_analysis = true
//	                    data.push({'data': text, 'bold': true})
//	                });
//	                data_td_eles = $data_ele.find('td')
//	                $.each(data_td_eles,function(){
//	                    $data_td_ele = $(this)
//	                    text = $data_td_ele.text().trim() || ""
//	                    if ($data_td_ele && $data_td_ele[0].classList.contains('oe_number') && !$data_td_ele[0].classList.contains('oe_list_field_float_time')){
//	                        text = text.replace('%', '')
//	                        text = instance.web.parse_value(text, { type:"float" })
//	                        data.push({'data': text || "", 'number': true})
//	                    }
//	                    else{
//	                        data.push({'data': text})
//	                    }
//	                });
//	                export_data.push(data)
//                }
//            });
//
//            //Find Footer Element
//
//            footer_eles = self.$el.find('.oe_list_content > tfoot> tr')
//            $.each(footer_eles,function(){
//                data = []
//                $footer_ele = $(this)
//                footer_td_eles = $footer_ele.find('td')
//                $.each(footer_td_eles,function(){
//                    $footer_td_ele = $(this)
//                    text = $footer_td_ele.text().trim() || ""
//                    if ($footer_td_ele && $footer_td_ele[0].classList.contains('oe_number')){
//                        text = instance.web.parse_value(text, { type:"float" })
//                        data.push({'data': text || "", 'bold': true, 'number': true})
//                    }
//                    else{
//                        data.push({'data': text, 'bold': true})
//                    }
//                });
//                export_data.push(data)
//            });
//
//            //Export to excel
//            $.blockUI();
//            if (export_type === 'excel'){
//                 view.session.get_file({
//                     url: '/web/export/record_excel_export',
//                     data: {data: JSON.stringify({
//                            model : view.model,
//                            headers : header_name_list,
//                            rows : export_data,
//                     })},
//                     complete: $.unblockUI
//                 });
//             }
//             else{
//                console.log(view)
//                new instance.web.Model("res.users").get_func("read")(this.session.uid, ["company_id"]).then(function(res) {
//                    new instance.web.Model("res.company").get_func("read")(res['company_id'][0], ["name"]).then(function(result) {
//                        view.session.get_file({
//                             url: '/web/export/record_pdf_export',
//                             data: {data: JSON.stringify({
//                                    uid: view.session.uid,
//                                    model : view.model,
//                                    headers : header_name_list,
//                                    rows : export_data,
//                                    company_name: result['name']
//                             })},
//                             complete: $.unblockUI
//                         });
//                    });
//                });
//             }
//        },
//    });
//};

odoo.define('web_printscreen_export.Pager', function (require) {
"use strict";

var Pager=require('web.Pager');
var formats = require('web.formats');
var Model =require('web.Model');

var direction = {
    previous: -1,
    next: 1,
};

Pager.include({
    template: "Pager",

    events: {
        'click .o_pager_previous': 'previous',
        'click .o_pager_next': 'next',
        'click .o_pager_value': '_edit',
        'click .o_list_button_import_excel': function() {
            this.export_to_excel('excel');
            },
        'click .o_list_button_import_pdf': function() {
            this.export_to_excel('pdf');
            }
    },

    export_to_excel: function(export_type) {
            var self = this;
            var export_type = export_type;
            var view = this.getParent();
            console.log(view);
            // Find Header Element
            var header_eles = view.$el.find('.o_list_view');
            console.log(header_eles);
            var header_name_list = []
            $.each(header_eles,function(){
                var header_ele = $(this);
                var header_td_elements = header_ele.find('th')
                $.each(header_td_elements.slice(1),function(){
                    var header_td = $(this)
                    var text = header_td.text().trim() || ""
                    var data_id = header_td.attr('data-id')
                    if (text && !data_id){
                        data_id = 'group_name'
                    }
                    header_name_list.push({'header_name': text.trim(), 'header_data_id': data_id})


                   // }
                });
            });
            console.log(header_name_list);
            //Find Data Element
            var data_eles = view.$el.find('tbody > tr')
            var export_data = []
            $.each(data_eles,function(){
                var data = []
                var data_ele = $(this)
                var is_analysis = false
                if (data_ele.text().trim()){
                //Find group name
//	                var group_th_eles = data_ele.find('.o_list_record_selector')
//	                $.each(group_th_eles,function(){
//	                    var group_th_ele = $(this)
//	                    var text = group_th_ele.text()
//	                    is_analysis = true
//	                    data.push({'data': text, 'bold': true})
//	                });
//	                console.log('dkhgfsdjfgks',data);
	                var data_td_eles = data_ele.find('td')
	                $.each(data_td_eles.slice(1),function(){
	                    var data_td_ele = $(this)
	                    var text = data_td_ele.text().trim() || ""
	                    if (data_td_ele && data_td_ele[0].classList.contains('o_list_number')){
	                        text = text.replace(/[^\d.]/g, '');
	                        text = formats.parse_value(text, { type:"float" })
	                        data.push({'data': text || "", 'number': true})
	                    }
	                    else{
	                        data.push({'data': text})
	                    }
	                });
	                export_data.push(data)
	                console.log(data)
                }
            });

            //Find Footer Element

            var footer_eles = view.$el.find('tfoot> tr')
            $.each(footer_eles,function(){
                var data = []
                var footer_ele = $(this)
                var footer_td_eles = footer_ele.find('td')
                $.each(footer_td_eles.slice(1),function(){
                    var footer_td_ele = $(this)
                    var text = footer_td_ele.text().trim() || ""
                    if (footer_td_ele && footer_td_ele[0].classList.contains('o_list_number')){
                        text = text.replace(/[^\d.]/g, '');
                        text = formats.parse_value(text, { type:"float" })
                        data.push({'data': text || "", 'bold': true, 'number': true})
                    }
                    else{
                        data.push({'data': text, 'bold': true})
                    }
                });
                export_data.push(data)
            });

            //Export to excel
            $.blockUI();
            if (export_type === 'excel'){
                 console.log(view.session);
                 view.session.get_file({
                     url: '/web/export/record_excel_export',
                     data: {data: JSON.stringify({
                            model : view.model,
                            headers : header_name_list,
                            rows : export_data,
                     })},
                     complete: $.unblockUI
                 });
             }
             else{
                console.log(view)
                new Model("res.users").get_func("read")(view.session.uid, ["company_id"]).then(function(res) {
                    console.log(res[0]['company_id'][1]);
                    new Model("res.company").get_func("read")(res[0]['company_id'][2], ["name"]).then(function(result) {

                        view.session.get_file({
                             url: '/web/export/record_pdf_export',
                             data: {data: JSON.stringify({
                                    uid: view.session.uid,
                                    model : view.model,
                                    headers : header_name_list,
                                    rows : export_data,
                                    company_name: res[0]['company_id'][1]
                             })},
                             complete: $.unblockUI
                         });
                    });
                });
             }
        },    /**
     * The pager goes from 1 to size (included).
     * The current value is current_min if limit === 1
     *                   or the interval [current_min, current_min + limit[ if limit > 1
     * @param {Widget} [parent] the parent widget
     * @param {int} [size] the total number of elements
     * @param {int} [current_min] the first element of the current_page
     * @param {int} [limit] the number of elements per page
     * @param {boolean} [options.can_edit] editable feature of the pager
     * @param {boolean} [options.single_page_hidden] (not) to display the pager if only one page
     * @param {function} [options.validate] callback returning a Deferred to validate changes
     */


});
})