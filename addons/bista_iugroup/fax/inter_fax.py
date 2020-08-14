from odoo import models, fields,_,api
import client
from odoo.exceptions import UserError, RedirectWarning, ValidationError

import logging
_logger = logging.getLogger(__name__)

class outbound_interfax(models.Model):
    _name='outbound.interfax'

    @api.model
    def get_login_info(self):
        username,password = False,False
        config = self.env['interfax.config.settings']
        config_ids = config.search([('active','=',True)])
        if not config_ids:
            raise UserError(_('No Interfax Account Configured.\n If configured, \
                                                    make sure the Active boolean is checked .'))
        for id in config_ids:
            username,password = id.username,id.password
        return (username,password)

    @api.model
    def create_client(self):
        username,password = self.get_login_info()
        c = client.InterFaxClient(username,password)
        return c

    @api.model
    def send_fax(self,fax_numbers=[],reciever_names=[],filenames=[]):
        key, des = False, False
        c= self.create_client()
        result = c.sendFaxEx2( fax_numbers, reciever_names, filenames) # Enter the destination fax number here.
        _logger.info('   Fax was sent with result code: %d',result) 
        if result < 0:
            stat = self.env['status.description']
            stat_ids = stat.search([('name','=',result)])
            if stat_ids:
                des = stat_ids[0].status
            raise UserError(_('%s.'%des))
        status = self.get_status(result)
        # The loop will iterate only once
        for each in status:
            key = each
        if status:
            return {'transmission_id':key , 'status':status[key]['status'],'description':status[key]['description']}
        else: return

    @api.model
    def get_status(self, trans_id=999999998, number=1):
        """ Pass the number of transmission ids status you need to check which are lesser than trans_id.
                trans_id=999999999 gives the status of all the transactions ids lesser than trans_id """
        des = False
        trans_id += 1
#        print "trans id+++++++=",trans_id
        c= self.create_client()
        try:
            result = c.faxStatus(trans_id, number)
        except:
            raise UserError(_('Cant retrieve Fax Status.'))
        _logger.info('   FaxStatus returned with code %d and %d items',result[0], len(result[1]))
        if result and result[0] < 0:
            stat = self.env['status.description']
            stat_ids = stat.search([('name','=',result)])
            if stat_ids:
                des = stat_ids[0].status
            raise UserError(_('%s.'%des))
        # Print details for each item.
        for currItem in result[1]:
            _logger.info("\ntxId: %d\nsubmitTime: %s\npostponeTime:%s\ncompletionTime:%s\ndestinationFax%s\nremoteCSID:%s\npagesSent:%s\nstatus: %d\nduration: %d\nsubject: %s\npagesSubmitted: %d",currItem)
        # Creating a dictionary of txid and status
        status_dict = dict([(each_trans[0],each_trans[7]) for each_trans in result[1]])

        status = self.get_status_description(status_dict)
        return status

    @api.model
    def get_status_description(self,trans_status_dict):
        """ trans_status_dict is a dict of type {'trans_id':'status_code'} """
        status_dict, des = {}, False
#        print "dict+++++++",trans_status_dict
        stat = self.env['status.description']
        for each in trans_status_dict:
#            print "key++++++++++",each
            code = trans_status_dict[each]
            if code < 0:
                if code == -22:
                    status = 'Out of credit, awaiting topup'
                else:
                    status = 'Processing'
            if code == 0:
                status = 'Successful'
            if code > 0:
                status = 'Failed'
            status_dict[each]={}
            stat_ids = stat.search([('name','=',code)])
            if stat_ids and stat_ids[0]:
                des = stat_ids[0].status
            status_dict[each] = {'status':status,'description': des}
        return status_dict


class inbound_interfax(models.Model):
    _name='inbound.interfax'
    _username = 'bista_bista'
    _password = 'solutions'

    @api.model
    def create_client(self):
        username,password = self.env['outbound.interfax'].get_login_info()
        c = client.InterFaxClient(username,password)
        return c

    @api.model
    def get_list(self):
        """
        Makes a call to the InterFAX GetList API method to return a list of
        received faxes.
        see http://www.interfax.net/en/dev/webservice/reference/getlist

        Arguments:
             listType - One of: AllMessages, NewMessages, AccountAllMessages, AccountNewMessages
             maxItems - Maximum items to return, between 1 to 100

        Returns: a tuple of (resultCode, [] of MessageItem tuples)
                 resultCode of 0 means OK, negative number indicates an error.
                 See the list of Web Service Return Codes:
                 http://www.interfax.net/en/dev/webservice/reference/web-service-return-codes
                 Each MessageItem tuple is of the form
                 ( MessageID,
                   PhoneNumber,
                   RemoteCSID
                   MessageStatus
                   Pages
                   MessageSize
                   MessageType
                   ReceiveTime
                   CallerID
                   MessageRecordingDuration )
        """
        c = self.create_client()
        result = c.getList('AccountNewMessages', 100)
        _logger.info('   GetList returned with code %d and %d items',result[0],len(result[1]))
        if result and result[0] < 0:
            stat = self.env['status.description']
            stat_id = stat.search([('name','=',result)])
            des = stat_id[0].status
            raise UserError(_('%s.'%des))

        for currItem in result[1]:
            _logger.info("\nmessageId: %d\nphoneNumber: %s\nremoteCSID: %s\nmessageStatus: %d \
            \npages: %d\nmessageSize: %d\nmessageType: %d\nreceiveTime: %s\ncallerID: %s\nmessageRecodingDuration: %d",
            currItem[0],currItem[1],currItem[2],currItem[3],currItem[4],currItem[5],currItem[6],currItem[7],currItem[8],currItem[9])
            if currItem[0]:
                try:
                    fax_ids = self.env['incoming.fax'].search([('msg_id','=',int(currItem[0]))])
                    if fax_ids:
                        result[1].remove(currItem)
                except Exception, e:
                    _logger.info(" Error : %s ",e.args)
        return result[1]

    @api.model
    def get_fax_image(self,message_id,message_size):
        """
        Makes a call to the InterFAX GetImageChunk API method.
        see http://www.interfax.net/en/dev/webservice/reference/getimagechunk

        Arguments:
            messageId - Message ID of the transaction to download.
           markAsRead - True - mark as read. False - doesn't change the current status.
            chunkSize - Buffer size to download.
             readFrom - Starting point of the image to write to the buffer
          outfilename - Name of a local file to write the result to.

        Returns: If retrieval of fax image is successful, return value is 0.
                 In case of failure, a negative value is returned.
                 See the list of Web Service Return Codes:
                 http://www.interfax.net/en/dev/webservice/reference/web-service-return-codes
        """
#        os.path.join(tools.config['root_path'], location, '', path)
        c = self.create_client()
        result = c.getImageChunk( message_id, True, message_size, 0, r"/opt/openerp-7.0/temp_fax_in/%d.pdf" % message_id )
        _logger.info('   GetImageChunk returned with code %d', result) 
#        Didnt add Error handling as it is handled in get_fax() 'Failed List'
#        and cant raise error for each request as we fetch multiple messages
        return result

    @api.model
    def get_fax(self):
        list,result,failed,succecced,res = False,False,False,False,{} 
        # Get the list of received faxes in InterFax.
        # The get_list() method returns the [(),()...] where each tuple represents complete description
        # of each received msg respectively.
        list = self.get_list()
        
        if list:
            # Fetching image for each msg received in get_list().
            # Creating a [(msg id, msg size, result of get image),()....]
            result = [(each_tup[0], each_tup[5],self.get_fax_image(each_tup[0],each_tup[5]))for each_tup in list]
        else: return
        # Seggregation of result based on msg received either failed and succecceded
        failed = [each_tup for each_tup in result if each_tup[2]<0]
        succecced = [each_tup for each_tup in result if each_tup[2]==0]
        # Returning the whole list in received as it contains the actual description
        # 'received' can be queried ,For successful received msg id in succecced.
        res ={'received':list,
                'result':result,
                'failed':failed,
                'succecced':succecced,
                }

        return res

class status_description(models.Model):
    _name='status.description'

    name=fields.Integer('Code')
    status=fields.Text('Status')
    code_type=fields.Selection([('web_services','Web Services'),('fax','Fax Code')])



