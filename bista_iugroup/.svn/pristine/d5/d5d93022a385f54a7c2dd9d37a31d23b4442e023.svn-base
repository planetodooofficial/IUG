import math
###########################################################
## Google map python wrapper V0.1
## 
############################################################

class maps:

	def __init__(self, centerLat, centerLng, zoom ):
		self.center = (float(centerLat),float(centerLng))
		self.zoom = int(zoom)
		self.grids = None
		self.paths = []
		self.points = []
		self.radpoints = []
		self.gridsetting = None
		#self.coloricon = 'http://maps.google.com/mapfiles/kml/paddle/blu-blank.png'
		self.coloricon = 'http://chart.apis.google.com/chart?cht=mm&chs=25x34&chco=FFFFFF,XXXXXX,000000&ext=.png'

	def setgrids(self,slat,elat,latin,slng,elng,lngin):
		self.gridsetting = [slat,elat,latin,slng,elng,lngin]

	def addpoint(self, lat, lng, color = '#FF0000',name= '', address = ''):
		self.points.append((lat , lng, color[1:], name , address))

	#def addpointcoord(self, coord):
	#	self.points.append((coord[0],coord[1]))

	def addradpoint(self, lat,lng,rad,color = '#0000FF'):
		self.radpoints.append((lat,lng,rad,color))

	def addpath(self,path,color = '#FF0000'):
		path.append(color)
		self.paths.append(path)
	
	#create the html file which inlcude one google map and all points and paths
	def draw(self, htmlfile):
		f = open(htmlfile,'w')
		f.write('<html>\n')
		f.write('<head>\n')
		#f.write('<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n')
		#f.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>\n')
		f.write('<title>Search Results for Interpreters </title>\n')
		f.write('<script src="http://code.jquery.com/jquery.min.js"></script>\n')
		f.write('<script type="text/javascript">\n')
		f.write('\tjQuery.noConflict();\n')
		f.write('</script>\n')
		f.write('<style>\n')
		f.write('\t#map_wrapper {\n')
		f.write('\t\theight: 400px;\n')
		f.write('\t}\n')
		f.write('\t#map_canvas {\n')
		f.write('\t\twidth: 100%;\n')
		f.write('\t\theight: 100%;\n')
		f.write('\t}\n')
		f.write('</style>\n')
		f.write('<script>\n')
		f.write('\tjQuery(function($) {\n')
		f.write('\t\tvar script = document.createElement("script");\n')
		f.write('\t\tscript.src = "http://maps.googleapis.com/maps/api/js?sensor=false&callback=initialize";\n')
		f.write('\t\tdocument.body.appendChild(script);\n')
		f.write('\t});\n')


		f.write('\tfunction initialize() {\n')
		self.drawmap(f)
		#self.drawgrids(f)
                
		self.getmarkers(f)
		f.write('\t];\n')
		f.write('\tvar infoWindowContent = [\n')
		self.getinfos(f)
		f.write('\t\t];\n')
		#self.drawpoints(f)
		#self.drawradpoints(f)
		#self.drawpaths(f,self.paths)
		#f.write('\t}\n')
		f.write('\tvar infoWindow = new google.maps.InfoWindow(), marker, i;\n')
		f.write('\tfor ( i = 0; i < markers.length; i++ ) {\n')
		f.write('\t\tvar position = new google.maps.LatLng(markers[i][1], markers[i][2]);\n')
		f.write('\t\tbounds.extend(position);\n')
		f.write('\t\tmarker = new google.maps.Marker({\n')
		f.write('\t\t\tposition: position,\n')
		f.write('\t\t\tmap: map,\n')
		f.write('\t\t\ttitle: markers[i][0]\n')
		f.write('\t\t});\n')
		f.write('\t\tgoogle.maps.event.addListener(marker, "click", (function(marker, i) {\n')
		f.write('\t\t\treturn function() {\n')
		f.write('\t\t\t\tinfoWindow.setContent(infoWindowContent[i][0]);\n')
		f.write('\t\t\t\tinfoWindow.open(map, marker);\n')
		f.write('\t\t}\n')
		f.write('\t\t})(marker, i));\n')
		f.write('\t\tmap.fitBounds(bounds);\n')
		f.write('\t}\n')
		f.write('\t\tvar boundsListener = google.maps.event.addListener((map), "bounds_changed", function(event) {\n')
		f.write('\t\t\tthis.setZoom(14);\n')
		f.write('\t\t\tgoogle.maps.event.removeListener(boundsListener);\n')
		f.write('\t\t});\n')
		f.write('\t}\n')
                
		f.write('</script>\n')
		f.write('</head>\n')
		f.write('<body>\n')
		f.write('\t<div id="map_wrapper">\n')
		f.write('\t\t<div id="map_canvas" class="mapping"></div>\n')
		f.write('\t</div>\n')
		f.write('</body>\n')
		f.write('</html>\n')
		f.close()

	def drawgrids(self, f):
		if self.gridsetting == None:
			return
		slat = self.gridsetting[0]
		elat = self.gridsetting[1]
		latin = self.gridsetting[2]
		slng = self.gridsetting[3]
		elng = self.gridsetting[4]
		lngin = self.gridsetting[5]
		self.grids = []

		r = [slat+float(x)*latin for x in range(0, int((elat-slat)/latin))]
		for lat in r:
			self.grids.append([(lat+latin/2.0,slng+lngin/2.0),(lat+latin/2.0,elng+lngin/2.0)])

		r = [slng+float(x)*lngin for x in range(0, int((elng-slng)/lngin))]
		for lng in r:
			self.grids.append([(slat+latin/2.0,lng+lngin/2.0),(elat+latin/2.0,lng+lngin/2.0)])
		
		for line in self.grids:
			self.drawPolyline(f,line,strokeColor = "#000000")
		def getmarkers(self,f):
			for point in  self.points:
				self.getmarker(f,point[0],point[1],point[2],point[3],point[4])
		def getinfos(self,f):
			for point in  self.points:
				self.getinfo(f,point[0],point[1],point[2],point[3],point[4])
                        
	def drawpoints(self,f):
		for point in  self.points:
			self.drawpoint(f,point[0],point[1],point[2],point[3],point[4])

	def drawradpoints(self, f):
		for rpoint in self.radpoints:
			path = self.getcycle(rpoint[0:3])
			self.drawPolygon(f,path,strokeColor = rpoint[3])

	def getcycle(self,rpoint):
		cycle = []
		lat = rpoint[0]
		lng = rpoint[1]
		rad = rpoint[2] #unit: meter
		d = (rad/1000.0)/6378.8;
		lat1 = (math.pi/180.0)* lat
		lng1 = (math.pi/180.0)* lng

		r = [x*30 for x in range(12)]
		for a in r:
			tc = (math.pi/180.0)*a;
			y = math.asin(math.sin(lat1)*math.cos(d)+math.cos(lat1)*math.sin(d)*math.cos(tc))
			dlng = math.atan2(math.sin(tc)*math.sin(d)*math.cos(lat1),math.cos(d)-math.sin(lat1)*math.sin(y))
			x = ((lng1-dlng+math.pi) % (2.0*math.pi)) - math.pi 
			cycle.append( ( float(y*(180.0/math.pi)),float(x*(180.0/math.pi)) ) )
		return cycle

	def drawpaths(self, f, paths):
		for path in paths:
			#print path
			self.drawPolyline(f,path[:-1], strokeColor = path[-1])

	#############################################
	# # # # # # Low level Map Drawing # # # # # # 
	#############################################
	def drawmap(self, f):
		f.write('\t\tvar map; \n')
		f.write('\t\tvar bounds = new google.maps.LatLngBounds();\n')
		f.write('\t\tvar mapOptions = {\n')
		f.write('\t\t\tmapTypeId: "roadmap"\n')
		f.write('\t\t};\n')
		f.write('\t\tmap = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);\n')
		f.write('\t\tmap.setTilt(45);\n')
		f.write('\n')
		f.write('\t\tvar markers = [\n')

	def getinfo(self,f,lat,lon,color ,name , address):
            
			f.write("""\t\t['<div class="info_content">' + \n""")
			f.write("\t\t\t '<h3>%s</h3>' +\n" %(name))
			f.write("\t\t\t '<p>%s</p>' +\n" %(address))
			f.write("\t\t'<div>'],")
			f.write('\n')
                
	def getmarker(self ,f ,lat ,lon ,color ,name , address):

		f.write('\t\t[\'%s\',' % (name))
		f.write('\t\t %f, %f],\n' %(lat,lon))
		f.write('\n')
                
	def drawpoint(self ,f ,lat ,lon ,color ,name , address):
		f.write('\t\tvar latlng = new google.maps.LatLng(%f, %f);\n'%(lat,lon))
		f.write('\t\tvar img = new google.maps.MarkerImage(\'%s\');\n' % (self.coloricon.replace('XXXXXX',color)))
		f.write('\t\tvar marker = new google.maps.Marker({\n')
		f.write('\t\ttitle: "%s",\n' %(name))
		f.write('\t\ticon: img,\n')
		f.write('\t\tposition: latlng\n')
		f.write('\t\t});\n')
		f.write('\t\tmarker.setMap(map);\n')
		f.write('\n')
		
	def drawPolyline(self,f,path,\
			clickable = False, \
			geodesic = True,\
			strokeColor = "#FF0000",\
			strokeOpacity = 1.0,\
			strokeWeight = 2
			):
		f.write('var PolylineCoordinates = [\n')
		for coordinate in path:
			f.write('new google.maps.LatLng(%f, %f),\n' % (coordinate[0],coordinate[1]))
		f.write('];\n')
		f.write('\n')

		f.write('var Path = new google.maps.Polyline({\n')
		f.write('clickable: %s,\n' % (str(clickable).lower()))
		f.write('geodesic: %s,\n' % (str(geodesic).lower()))
		f.write('path: PolylineCoordinates,\n')
		f.write('strokeColor: "%s",\n' %(strokeColor))
		f.write('strokeOpacity: %f,\n' % (strokeOpacity))
		f.write('strokeWeight: %d\n' % (strokeWeight))
		f.write('});\n')
		f.write('\n')
		f.write('Path.setMap(map);\n')
		f.write('\n\n')

	def drawPolygon(self,f,path,\
			clickable = False, \
			geodesic = True,\
			fillColor = "#000000",\
			fillOpacity = 0.0,\
			strokeColor = "#FF0000",\
			strokeOpacity = 1.0,\
			strokeWeight = 1
			):
		f.write('var coords = [\n')
		for coordinate in path:
			f.write('new google.maps.LatLng(%f, %f),\n' % (coordinate[0],coordinate[1]))
		f.write('];\n')
		f.write('\n')

		f.write('var polygon = new google.maps.Polygon({\n')
		f.write('clickable: %s,\n' % (str(clickable).lower()))
		f.write('geodesic: %s,\n' % (str(geodesic).lower()))
		f.write('fillColor: "%s",\n' %(fillColor))
		f.write('fillOpacity: %f,\n' % (fillOpacity))
		f.write('paths: coords,\n')
		f.write('strokeColor: "%s",\n' %(strokeColor))
		f.write('strokeOpacity: %f,\n' % (strokeOpacity))
		f.write('strokeWeight: %d\n' % (strokeWeight))
		f.write('});\n')
		f.write('\n')
		f.write('polygon.setMap(map);\n')
		f.write('\n\n')

if __name__ == "__main__":

	########## CONSTRUCTOR: pygmaps(latitude, longitude, zoom) ##############################
	# DESC:		initialize a map  with latitude and longitude of center point  
	#		and map zoom level "15"
	# PARAMETER1:	latitude (float) latittude of map center point
	# PARAMETER2:	longitude (float) latittude of map center point
	# PARAMETER3:	zoom (int)  map zoom level 0~20
	# RETURN:	the instant of pygmaps
	#========================================================================================
	mymap = pygmaps(37.428, -122.145, 16)


	########## FUNCTION: setgrids(start-Lat, end-Lat, Lat-interval, start-Lng, end-Lng, Lng-interval) ######
	# DESC:		set grids on map  
	# PARAMETER1:	start-Lat (float), start (minimum) latittude of the grids
	# PARAMETER2:	end-Lat (float), end (maximum) latittude of the grids
	# PARAMETER3:	Lat-interval (float)  grid size in latitude 
	# PARAMETER4:	start-Lng (float), start (minimum) longitude of the grids
	# PARAMETER5:	end-Lng (float), end (maximum) longitude of the grids
	# PARAMETER6:	Lng-interval (float)  grid size in longitude 
	# RETURN:	no returns
	#========================================================================================
	mymap.setgrids(37.42, 37.43, 0.001, -122.15, -122.14, 0.001)


	########## FUNCTION:  addpoint(latitude, longitude, [color])#############################
	# DESC:		add a point into a map and dispaly it, color is optional default is red
	# PARAMETER1:	latitude (float) latitude of the point
	# PARAMETER2:	longitude (float) longitude of the point
	# PARAMETER3:	color (string) color of the point showed in map, using HTML color code
	#		HTML COLOR CODE:  http://www.computerhope.com/htmcolor.htm
	#		e.g. red "#FF0000", Blue "#0000FF", Green "#00FF00"
	# RETURN:	no return
	#========================================================================================
	mymap.addpoint(37.427, -122.145, "#0000FF")


	########## FUNCTION:  addradpoint(latitude, longitude, radius, [color])##################
	# DESC: 	add a point with a radius (Meter) - Draw cycle
	# PARAMETER1:	latitude (float) latitude of the point
	# PARAMETER2:	longitude (float) longitude of the point
	# PARAMETER3:	radius (float), radius  in meter 
	# PARAMETER4:	color (string) color of the point showed in map, using HTML color code
	#		HTML COLOR CODE:  http://www.computerhope.com/htmcolor.htm
	#		e.g. red "#FF0000", Blue "#0000FF", Green "#00FF00"
	# RETURN:	no return 
	#========================================================================================
	mymap.addradpoint(37.429, -122.145, 95, "#FF0000")


	########## FUNCTION:  addpath(path,[color])##############################################
	# DESC:		add a path into map, the data struceture of Path is a list of points
	# PARAMETER1:	path (list of coordinates) e.g. [(lat1,lng1),(lat2,lng2),...]
	# PARAMETER2:	color (string) color of the point showed in map, using HTML color code
	#		HTML COLOR CODE:  http://www.computerhope.com/htmcolor.htm
	#		e.g. red "#FF0000", Blue "#0000FF", Green "#00FF00"
	# RETURN:	no return
	#========================================================================================
	path = [(37.429, -122.145),(37.428, -122.145),(37.427, -122.145),(37.427, -122.146),(37.427, -122.146)]
	mymap.addpath(path,"#00FF00")

	########## FUNCTION:  addpath(file)######################################################
	# DESC:		create the html map file (.html)
	# PARAMETER1:	file (string) the map path and file
	# RETURN:	no return, generate html file in specified directory
	#========================================================================================
	mymap.draw('./mymap.html')
	
		
