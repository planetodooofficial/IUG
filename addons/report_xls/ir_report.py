# -*- coding: utf-8 -*-

from odoo import api, models,fields,SUPERUSER_ID,tools

class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[("xls", "xls")])

    @api.model
    def render_report(self, res_ids, name, data):
        """
        Look up a report definition and render the report for the provided IDs.
        """
        report = self._lookup_report(name)
        if isinstance(report, basestring):  # Qweb report
            # The only case where a QWeb report is rendered with this method occurs when running
            # yml tests originally written for RML reports.
            if tools.config['test_enable'] and not tools.config['test_report_directory']:
                # Only generate the pdf when a destination folder has been provided.
                return self.env['report'].get_html(res_ids, report, data=data), 'html'
            else:
                return self.env['report'].get_pdf(res_ids, report, data=data), 'pdf'
        else:
            return report.create(self._cr, SUPERUSER_ID, res_ids, data, context=self._context)

