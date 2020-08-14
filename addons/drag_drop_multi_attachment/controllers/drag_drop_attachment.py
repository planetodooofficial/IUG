
from odoo import http, _
from odoo.addons import web
import unicodedata
from odoo.http import content_disposition, dispatch_rpc, request, \
                      serialize_exception as _serialize_exception
import base64
import json
import logging
import functools
import werkzeug.utils
import werkzeug.wrappers
_logger = logging.getLogger(__name__)
from odoo.addons.web.controllers.main import Binary



class DragDropAttachment(Binary):

    def serialize_exception(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception, e:
                _logger.exception("An exception occured during an http request")
                se = _serialize_exception(e)
                error = {
                    'code': 200,
                    'message': "Odoo Server Error",
                    'data': se
                }
                return werkzeug.exceptions.InternalServerError(json.dumps(error))

        return wrap

    @http.route('/web/binary/upload_attachment', type='http', auth="user")
    @serialize_exception
    def upload_attachment(self, callback, model, id, ufile):
        Model = request.env['ir.attachment']
        out = """<script language="javascript" type="text/javascript">
                        var win = window.top.window;
                        win.jQuery(win).trigger(%s, %s);
                    </script>"""

        filename = ufile.filename
        if request.httprequest.user_agent.browser == 'safari':
            filename = unicodedata.normalize('NFD', ufile.filename).encode('UTF-8')

        try:
            attachment = Model.create({
                # 'upload_attachment_id': int(id),
                'name': filename,
                'datas': base64.encodestring(ufile.read()),
                    'datas_fname': filename,
                'res_model': model,
                'res_id': int(id),
            })

            args = {
                'filename': filename,
                'mimetype': ufile.content_type,
                'id': attachment.id
            }
            data=int(id)
            attachment.write({'upload_attachment_id': int(id)})
            request.env.cr.commit()
        except Exception:
            args = {'error': _("Something horrible happened")}
            _logger.exception("Fail to upload attachment %s" % ufile.filename)

        return out % (json.dumps(callback), json.dumps(args))


            # return super(DragDropAttachment, self).upload_attachment(callback, model, id, ufile)
