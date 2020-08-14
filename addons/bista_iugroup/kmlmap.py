# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields,api
from odoo.tools.translate import _
import pygmaps
import webbrowser
import urllib, random
import csv
import time
import urllib
import urlparse
import xml.dom.minidom
GMAPS_API_KEY = 'AIzaSyBoZc-_7KabQcUo9nHTL-xCED6k2_Gj9BM'
try:
    from pygeocoder import Geocoder
except Exception , e:
     raise osv.except_osv(_('Warning!'),_('Please install pygeocoder - pip install pygeocoder'))


import subprocess
import sys
import multiprocessing.managers

host = "72.11.224.244"
port = 8049
password = "IUgroup11199"
commands = ["echo %USERPROFILE%", "dir \\", "echo $HOME", "ls /", "non_existing_command"]

def write_file(file_name, file_contents):
    fh = None
    try:
        fh = open(file_name, "wb")
        fh.write(file_contents)
        return True
    except:
        return False
    finally:
	if fh is not None:
	    fh.close()

class RemoteManager(multiprocessing.managers.BaseManager):
    pass

RemoteManager.register("write_file", write_file)

def start_server(port, password):
    print "Listening for incoming connections..."
    mgr = RemoteManager(address=('', port), authkey=password)
    server = mgr.get_server()
    server.serve_forever()

def write_file_remote(host, port, password, file_name_remote, file_contents):
    print "write_file_remote..........."
    mgr = RemoteManager(address=(host, port), authkey=password)
    mgr.connect()
    print mgr.write_file(file_name_remote, file_contents)._getvalue()
    print

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        start_server(port, password)
    elif len(sys.argv) > 3 and sys.argv[1] == "--client":
	fh = None
	try:
	    fh = open(sys.argv[2], "rb")
	    file_contents = fh.read()
	finally:
	    if fh is not None:
		fh.close()
        file_name_remote = sys.argv[3]
        write_file_remote(host, port, password, file_name_remote, file_contents)
#    else:
#        print "usage: python " + sys.argv[0] + " [ --server | --client <local_file_name> <remote_file_name>]




class Element(xml.dom.minidom.Element):
    
    def writexml(self , writer, indent="", addindent="", newl=""):
        # indent = current indentation
        # addindent = indentation to add to higher levels
        # newl = newline string
        writer.write(indent+"<" + self.tagName)
        print "self.tagName.........",self.tagName
        attrs = self._get_attributes()
        a_names = attrs.keys()
        a_names.sort()

        for a_name in a_names:
            writer.write(" %s=\"" % a_name)
            xml.dom.minidom._write_data(writer, attrs[a_name].value)
            writer.write("\"")
        if self.childNodes:
            newl2 = newl
            if len(self.childNodes) == 1 and \
                self.childNodes[0].nodeType == xml.dom.minidom.Node.TEXT_NODE:
                indent, addindent, newl = "", "", ""
            writer.write(">%s"%(newl))
            for node in self.childNodes:
                node.writexml(writer,indent+addindent,addindent,newl)
            writer.write("%s</%s>%s" % (indent,self.tagName,newl2))
        else:
            writer.write("/>%s"%(newl))

# Monkey patch Element class to use our subclass instead.
xml.dom.minidom.Element = Element

def create_document(title, description=''):
    print "create_document -title...description.......",title,description
    """Create the overall KML document."""
    doc = xml.dom.minidom.Document()
    kml = doc.createElement("kml")
    kml.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
    doc.appendChild(kml)
    document = doc.createElement('Document')
    kml.appendChild(document)
    docName = doc.createElement('name')
    document.appendChild(docName)
    docName_text = doc.createTextNode(title)
    docName.appendChild(docName_text)
    docDesc = doc.createElement('description')
    document.appendChild(docDesc)
    docDesc_text = doc.createTextNode(description)
    docDesc.appendChild(docDesc_text)
    return doc

def create_style(style_id, icon_href):
    print "create_style.........."
    """Create a new style for different placemark icons."""
    doc = xml.dom.minidom.Document()
    style = doc.createElement('Style')
    style.setAttribute('id', style_id)
    doc.appendChild(style)
    icon_style = doc.createElement('IconStyle')
    style.appendChild(icon_style)
    icon = doc.createElement('Icon')
    icon_style.appendChild(icon)
    href = doc.createElement('href')
    icon.appendChild(href)
    href_text = doc.createTextNode(icon_href)
    href.appendChild(href_text)
    return doc

def create_placemark(address):
    print "create_placemark........."
    """Generate the KML Placemark for a given address."""
    doc = xml.dom.minidom.Document()
    pm = doc.createElement("Placemark")
    doc.appendChild(pm)
    name = doc.createElement("name")
    pm.appendChild(name)
    name_text = doc.createTextNode('%(name)s' % address)
    name.appendChild(name_text)
    desc = doc.createElement("description")
    pm.appendChild(desc)
    desc_text = doc.createTextNode(str(address.get('phone', '')) + ' , ' + str(address.get('email', '')))
    desc.appendChild(desc_text)
    if address.get('county', ''):
        style_url = doc.createElement("styleUrl")
        pm.appendChild(style_url)
        style_url_text = doc.createTextNode('#%(county)s' % address)
        style_url.appendChild(style_url_text)
    pt = doc.createElement("Point")
    pm.appendChild(pt)
    coords = doc.createElement("coordinates")
    pt.appendChild(coords)
    coords_text = doc.createTextNode('%(longitude)s,%(latitude)s,0' % address)
    coords.appendChild(coords_text)
    return doc

def geocode( address):
    """Geocode the given address, updating the standardized address, latitude,
    and longitude."""
    qs = dict(q=address['address_string'], key=GMAPS_API_KEY, sensor='true',
              output='csv')
    qs = urllib.urlencode(qs)
    url = urlparse.urlunsplit(('http', 'maps.google.com', '/maps/geo', qs, ''))
    print "url.........",url
    f = urllib.urlopen(url)
    result = list(csv.DictReader(f, ('status', 'accurary', 'latitude', 'longitude')))[0]
    print "result........",result
    if int(result['status']) != 200:
        raise RuntimeError, 'could not geocode address %s (%s)' % \
                            (address, result['status'])
    address['latitude'] = result['latitude']
    address['longitude'] = result['longitude']
    time.sleep(1.0)

def read_addresses(filename):
    """Retrieve addresses from the given CSV filename."""
    required_fields = set(['name', 'address', 'city', 'zip'])
    reader = csv.DictReader(file(filename, 'rU'))
    for row in reader:
        #print "row......",row
        if not all(row.get(f, '').strip() for f in required_fields):
            continue
        yield row
#import smbclient
#https://www.dropbox.com/developers/core/docs/python
#https://www.dropbox.com/static/developers/dropbox-python-sdk-1.6-docs/#dropbox.client.DropboxClient.share
# Include the Dropbox SDK
#import dropbox

# Get your app key and secret from the Dropbox developer website
app_key = 'glb81i3vlwmradi'
app_secret = 'h4p76uumpf90b42'

def get_dropbox_file():
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'
    #code = raw_input("Enter the authorization code here: ").strip()

    # This will fail if the user enters an invalid authorization code
    #code = '4bt20TunjQUAAAAAAAAACfN8Q7EPmA5r2jfbGQ_w4WY'
    code = '4bt20TunjQUAAAAAAAAAFbHPER8Geq-PC_500T1o7w4'
    access_token, user_id = flow.finish(code)

    client = dropbox.client.DropboxClient(access_token)
    print 'linked account: ', client.account_info()
    #out = commands.getoutput('dropbox puburl ' + path + i)
    #paired = { "url": out, "description": i, "tags":"download" ,"replace":"no" }
    #data = urllib.urlencode(paired)
    #print "data...........",data
    f = open('/home/openerp/workspace/openerp/openerp-7.0/openerp/addons/bista_iugroup/mymap3.html', 'rb')
    response = client.put_file('/mymap3.html', f)
    print 'uploaded: ....', response
    response2 = client.share('/mymap3.html', f)
    print "response2..shared.......",response2
    f, metadata = client.get_file_and_metadata('/mymap3.html')
#    print "metadata.......",metadata
#    response2 = client.file_delete('/mymap3.html')
#    print "deleted: ....",response2
#    folder_metadata = client.metadata('/')
#    print 'metadata: ', folder_metadata

#    f, metadata = client.get_file_and_metadata('/mymap3.html')
#    out = open('magnum-opus.txt', 'wb')
#    out.write(f.read())
#    out.close()
#    print metadata
    
#    bigFile = open("/home/openerp/workspace/openerp/openerp-7.0/openerp/addons/bista_iugroup/mymap3.html", 'rb')
#    uploader = myclient.get_chunked_uploader(bigFile, size)
#    print "uploading: ", size
#    while uploader.offset < size:
#        try:
#            upload = uploader.upload_chunked()
#        except rest.ErrorResponse, e:
#            # perform error handling and retry logic
#    uploader.finish('/bigFile.txt')
#def _get_StringIO():
#    # we can't use cStringIO since it doesn't support Unicode strings
#    from StringIO import StringIO
#    return StringIO()
#
#def toprettyxml(self, indent="\t", newl="\n", encoding = None):
#    # indent = the indentation string to prepend, per level
#    # newl = the newline string to append
#    writer = _get_StringIO()
#    if encoding is not None:
#        import codecs
#        # Can't use codecs.getwriter to preserve 2.0 compatibility
#        writer = codecs.lookup(encoding)[3](writer)
#    if self.nodeType == Node.DOCUMENT_NODE:
#        # Can pass encoding only to document, to put it into XML header
#        self.writexml(writer, "", indent, newl, encoding)
#    else:
#        self.writexml(writer, "", indent, newl)
#    return writer.getvalue()
    
def remove_xml_tag(obj , file_str):
    #from __future__ import print_function # works on 2.x and 3.x
    from lxml import etree

    root = etree.fromstring(file_str)
    for element in root.iterfind('xml'):
        #if(element.find('.//tessellate')) is not None:
        element.remove(element)

    #print (etree.tostring(root))
    return (etree.tostring(root))

class kml_map( osv.osv):
    _name = "kml.map"
    
    
#    def update_file(self , cr ,uid ,ids , context = None):
#        a=get_dropbox_file()
#        print "a.........", a
        
    def update_file1(self , cr ,uid ,ids , context = None):
#        smb = smbclient.SambaClient(server="192.168.1.50", share="root",
#            username="root", password="IUgroup11199", domain="baz")
#        f = smb.open('/opt/openerp-7.0/addons_iu/bista_iugroup/mymap3.html')
#        data = f.read()
#        print "data..........",data
#        f.close()
#        start_server(port, password)
#
	fh = None
	try:
	    fh = "/home/openerp/workspace/openerp/openerp-7.0/openerp/addons/bista_iugroup/mymap3.html"
	    file_contents = fh.read()
	finally:
	    if fh is not None:
		fh.close()
        file_name_remote = "/opt/openerp-7.0/addons_iu/bista_iugroup/mymap3.html"
        write_file_remote(host, port, password, file_name_remote, file_contents)
        
    def kml_map(self , cr ,uid ,ids , context = None):
#        import simplekml
#        kml = simplekml.Kml()
#        kml.newpoint(name="Kirstenbosch", coords=[(18.432314,-33.988862)])
#        kml.save("botanicalgarden.kml")
        keyword = self.browse(cr ,uid ,ids[0], ).name
        print "keyword..........",keyword
        #gmaps = GoogleMaps('AIzaSyBoZc-_7KabQcUo9nHTL-xCED6k2_Gj9BM')

        customer_address = ''
        customer_obj = self.pool.get('res.partner')
        customer_ids = customer_obj.search(cr ,uid , ['|',('city','ilike',keyword),('zip','ilike',keyword)])
#        query = "select id from res_partner where upper(city) = %s or zip = %s"%( str(keyword).upper() , str(keyword))
#        cr.execute(query )
#        customer_ids = map(lambda x: x[0], cr.fetchall())
        print "customer_ids.........",customer_ids
#        results1 = Geocoder.geocode(keyword)
#        cord1 = results1[0].coordinates
#        print "cord1........",cord1
#        if len(cord1) > 1 and cord1[0] and cord1[1]:
#            lat1 = cord1[0]
#            lon1 = cord1[1]
#        mymap = pygmaps.maps(lat1, lon1, 7)
#
        kml_doc = create_document('Customer\'s',
                          'Nearby Area')
        print "kml_doc........",kml_doc
        document = kml_doc.documentElement.getElementsByTagName('Document')[0]
        style_doc = create_style('Wake', \
            'http://maps.google.com/mapfiles/kml/paddle/red-blank.png')
        document.appendChild(style_doc.documentElement)
        style_doc = create_style('Durham', \
            'http://maps.google.com/mapfiles/kml/paddle/blu-blank.png')
        document.appendChild(style_doc.documentElement)
        style_doc = create_style('Orange', \
            'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png')
        document.appendChild(style_doc.documentElement)
#        for address in read_addresses('/home/openerp/Documents/address.csv'):
#            print "address.........",address
#            address['address_string'] = \
#                '%(address)s, %(city)s, %(state)s %(zip)s' % address
#            print "address......",address
        for customer_id in customer_ids:
            customer = customer_obj.browse(cr ,uid ,customer_id)
            #address={'city': 'Apex', 'name': 'Apex - Williams Street', 'zip': '27539', 'country': 'Wake', 'phone': '919-362-6796', 'state': 'NC', 'address': '1581 East Williams Street'}
            customer_address = ''
            title= ''
            if customer.name:
                title += customer.name
            if customer.middle_name:
                title += ' ' + customer.middle_name
            if customer.last_name:
                title += ' ' + customer.last_name
            #print "title........",title
            address = {}
            address['name'] = title
            if customer.street:
                customer_address+=customer.street
                address['address'] = customer.street
            if customer.city:
                customer_address+=' '+customer.city
                address['city'] = customer.city
            if customer.state_id:
                customer_address+=' '+customer.state_id.name
                address['state'] = customer.state_id.name
            if customer.country_id:
                customer_address+=' '+customer.country_id.name
                address['country'] = customer.country_id.name
            if customer.zip:
                customer_address+=' '+customer.zip
                address['zip'] = customer.zip
            if customer.phone:
                address['phone'] = customer.phone
            if customer.email:
                address['email'] = customer.email
            address['county'] = 1
            print "address......",address
            #print "customer_address........address.",customer_address,address
#            try:
#                lat, lon = gmaps.address_to_latlng('United states')
#            except googlemaps.GoogleMapsError, e:
#                print "Oh, no! Couldn't geocode", addr
#                print e
            results = Geocoder.geocode(customer_address)
            cord = results[0].coordinates
            print "cord........",cord
            if len(cord) > 1 and cord[0] and cord[1]:
                address['latitude'] = cord[0]
                address['longitude'] = cord[1]
            #print "lat...lon.......",lat,lon
#            try:
#                geocode(address)
#            except RuntimeError, e:
#                print >> sys.stderr, e
#                print >> sys.stderr, "warning: %s skipped" % address['address_string']
#                continue
            placemark = create_placemark(address)
            document.appendChild(placemark.documentElement)
        print "Printing....kml........"
        xml_str= kml_doc.toprettyxml( )#indent="  ", encoding='UTF-8'
        print "xml_str......",xml_str
        kml_str = remove_xml_tag(kml_doc, xml_str)
        print "kml_str...........",kml_str
#        u = urllib.urlopen('http://www.datafilehost.com/get.php?file=4d421236')
#        raw_data = u.raed(a)
#        u.close()
#        file = 'https://www.dropbox.com/meta_dl/eyJzdWJfcGF0aCI6ICIiLCAidGVzdF9saW5rIjogZmFsc2UsICJzZXJ2ZXIiOiAiZGwuZHJvcGJveHVzZXJjb250ZW50LmNvbSIsICJpdGVtX2lkIjogbnVsbCwgImlzX2RpciI6IGZhbHNlLCAidGtleSI6ICJpcThwbzB2Nng3a2RjZGwifQ/AAMG__92aSsxOWK_Eb1FLRxQ0JCYjj-FDIJp9s7jbnLPoA?dl=1'
        file = 'https://www.dropbox.com/s/yehfc83rxth8i59/new3.kml?dl=1'
        app_key = 'fmaqmohgdytdkpn'
#        fh = open(file, "w")
#
#        fh.write(str(a))
#        fh.close()
#        url = 'http://maps.google.com/maps?q=' + 'http://www.datafilehost.com/get.php?file=4d421236'
        url = 'http://maps.google.com/maps?q=' + file
              
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }
        

        return True
    _columns = {
        'name': fields.char('City/Zip Code', size=128,  select=True),
    }

