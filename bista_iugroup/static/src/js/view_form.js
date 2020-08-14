openerp.bista_iugroup.form = function (instance) {
var _t = instance.web._t,
   _lt = instance.web._lt;
var QWeb = instance.web.qweb;

/** @namespace */
instance.web.form = {};

/**
 * FieldTextHtml2 Widget
 * Intended for FieldText widgets meant to display HTML content. This
 * widget will instantiate the CLEditor (see cleditor in static/src/lib)
 * To find more information about CLEditor configutation: go to
 * http://premiumsoftware.net/cleditor/docs/GettingStarted.html
 */
instance.bista_iugroup.form.FieldTextHtml2 = instance.web.form.AbstractField.extend(instance.web.form.ReinitializeFieldMixin, {
    template: 'FieldTextHtml2',
    init: function() {
        this._super.apply(this, arguments);
    },
    initialize_content: function() {
        var self = this;
        if (! this.get("effective_readonly")) {
            self._updating_editor = false;
            this.$textarea = this.$el.find('textarea');
            var width = ((this.node.attrs || {}).editor_width || '100%');
            var height = ((this.node.attrs || {}).editor_height || 250);
            this.$textarea.cleditor({
                width:      width, // width not including margins, borders or padding
                height:     height, // height not including margins, borders or padding
                controls:   // controls to add to the toolbar
                            "bold italic underline strikethrough " +
                            "|color removeformat | bullets numbering | outdent " +
                            "indent | link unlink | source",
		colors: // colors in the color popup
                    "FFF FCC FC9 FF9 FFC 9F9 9FF CFF CCF FCF " +
                    "CCC F66 F96 FF6 FF3 6F9 3FF 6FF 99F F9F " +
                    "BBB F00 F90 FC6 FF0 3F3 6CC 3CF 66C C6C " +
                    "999 C00 F60 FC3 FC0 3C0 0CC 36F 63F C3C " +
                    "666 900 C60 C93 990 090 399 33F 60C 939 " +
                    "333 600 930 963 660 060 366 009 339 636 " +
                    "000 300 630 633 330 030 033 006 309 303",
                bodyStyle:  // style to assign to document body contained within the editor
                            "margin:4px; color:#4c4c4c; font-size:13px; font-family:'Lucida Grande',Helvetica,Verdana,Arial,sans-serif; cursor:text"
            });
            this.$cleditor = this.$textarea.cleditor()[0];
            this.$cleditor.change(function() {
                if (! self._updating_editor) {
                    self.$cleditor.updateTextArea();
                    self.internal_set_value(self.$textarea.val());
                }
            });
            if (this.field.translate) {
                var $img = $('<img class="oe_field_translate oe_input_icon" src="/web/static/src/img/icons/terp-translate.png" width="16" height="16" border="0"/>')
                    .click(this.on_translate);
                this.$cleditor.$toolbar.append($img);
            }
        }
    },
    render_value: function() {
        if (! this.get("effective_readonly")) {
            this.$textarea.val(this.get('value') || '');
            this._updating_editor = true;
            this.$cleditor.updateFrame();
            this._updating_editor = false;
        } else {
            this.$el.html(this.get('value'));
        }
    }
});
instance.bista_iugroup.form.widgets.add('html2', 'instance.bista_iugroup.form.FieldTextHtml2');
//instance.bista_iugroup.form.widgets = new instance.web.Registry({
//    'char' : 'instance.web.form.FieldChar',
//    'id' : 'instance.web.form.FieldID',
//    'email' : 'instance.web.form.FieldEmail',
//    'url' : 'instance.web.form.FieldUrl',
//    'text' : 'instance.web.form.FieldText',
//    'html' : 'instance.web.form.FieldTextHtml',
//    'html2' : 'instance.web.form.FieldTextHtml2',
//    'date' : 'instance.web.form.FieldDate',
//    'datetime' : 'instance.web.form.FieldDatetime',
//    'selection' : 'instance.web.form.FieldSelection',
//    'many2one' : 'instance.web.form.FieldMany2One',
//    'many2onebutton' : 'instance.web.form.Many2OneButton',
//    'many2many' : 'instance.web.form.FieldMany2Many',
//    'many2many_tags' : 'instance.web.form.FieldMany2ManyTags',
//    'many2many_kanban' : 'instance.web.form.FieldMany2ManyKanban',
//    'one2many' : 'instance.web.form.FieldOne2Many',
//    'one2many_list' : 'instance.web.form.FieldOne2Many',
//    'reference' : 'instance.web.form.FieldReference',
//    'boolean' : 'instance.web.form.FieldBoolean',
//    'float' : 'instance.web.form.FieldFloat',
//    'integer': 'instance.web.form.FieldFloat',
//    'float_time': 'instance.web.form.FieldFloat',
//    'progressbar': 'instance.web.form.FieldProgressBar',
//    'image': 'instance.web.form.FieldBinaryImage',
//    'binary': 'instance.web.form.FieldBinaryFile',
//    'many2many_binary': 'instance.web.form.FieldMany2ManyBinaryMultiFiles',
//    'statusbar': 'instance.web.form.FieldStatus',
//    'monetary': 'instance.web.form.FieldMonetary',
//});

/**
 * Registry of widgets usable in the form view that can substitute to any possible
 * tags defined in OpenERP's form views.
 *
 * Every referenced class should extend FormWidget.
 */
//instance.bista_iugroup.form.tags = new instance.web.Registry({
//    'button' : 'instance.web.form.WidgetButton',
//});
//
//instance.bista_iugroup.form.custom_widgets = new instance.web.Registry({
//});

};

// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
