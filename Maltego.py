
#
# Updated Maltego Python library
# 2013/03/30
# See TRX documentation
#
# RT

import sys
from xml.dom import minidom

BOOKMARK_COLOR_NONE="-1"
BOOKMARK_COLOR_BLUE="0"
BOOKMARK_COLOR_GREEN="1"
BOOKMARK_COLOR_YELLOW="2"
BOOKMARK_COLOR_ORANGE="3"
BOOKMARK_COLOR_RED="4"

LINK_STYLE_NORMAL="0"
LINK_STYLE_DASHED="1"
LINK_STYLE_DOTTED="2"
LINK_STYLE_DASHDOT="3"

UIM_FATAL='FatalError'
UIM_PARTIAL='PartialError'
UIM_INFORM='Inform'
UIM_DEBUG='Debug'


class MaltegoEntity(object):
	value = ""
	weight = 100
	displayInformation = []
	additionalFields = []
	iconURL = ""
	entityType = "Phrase"
	

                	
	def __init__(self,eT=None,v=None):
		if (eT is not None):
			self.entityType = eT
		if (v is not None):
			self.value = v
		self.additionalFields = None
		self.additionalFields = []
		self.weight = 100
		self.displayInformation = []
		self.iconURL = ""
		
	def setType(self,eT=None):
		if (eT is not None):
			self.entityType = eT
	
	def setValue(self,eV=None):
		if (eV is not None):
			self.value = eV
		
	def setWeight(self,w=None):
		if (w is not None):
			self.weight = w
	
	def addDisplayInformation(self,di=None,dl='Info'):
		if (di is not None):
			self.displayInformation.append([dl,di])		
			
	def addProperty(self,fieldName=None,displayName=None,matchingRule=False,value=None):
		self.additionalFields.append([fieldName,displayName,matchingRule,value])
	
	def setIconURL(self,iU=None):
		if (iU is not None):
			self.iconURL = iU
			
        def setLinkColor(self,color):
            self.addProperty('link#maltego.link.color','LinkColor','',color)
            
        def setLinkStyle(self,style):
            self.addProperty('link#maltego.link.style','LinkStyle','',style)
            
        def setLinkThickness(self,thick):
            self.addProperty('link#maltego.link.thickness','Thickness','',str(thick))

        def setLinkLabel(self,label):
            self.addProperty('link#maltego.link.label','Label','',label)            

        def setBookmark(self,bookmark):
            self.addProperty('bookmark#','Bookmark','',bookmark)         

        def setNote(self,note):
            self.addProperty('notes#','Notes','',note)                     
        
	def returnEntity(self):
	        r=''
		r+= "<Entity Type=\"" + str(self.entityType) + "\">"
		r+= "<Value>" + str(self.value) + "</Value>"
		r+= "<Weight>" + str(self.weight) + "</Weight>"
		if (len(self.displayInformation) > 0):
			r+= "<DisplayInformation>"
			for i in range(len(self.displayInformation)):
			    r+='<Label Name=\"'+self.displayInformation[i][0]+'\" Type=\"text/html\"><![CDATA[' + str(self.displayInformation[i][1]) + ']]></Label>'
			r+='</DisplayInformation>'
		if (len(self.additionalFields) > 0):
			r+= "<AdditionalFields>"
			for i in range(len(self.additionalFields)):
				if (str(self.additionalFields[i][2]) <> "strict"):
					r+= "<Field Name=\"" + str(self.additionalFields[i][0]) + "\" DisplayName=\"" + str(self.additionalFields[i][1]) + "\">" + str(self.additionalFields[i][3]) + "</Field>"
				else:
					r+= "<Field MatchingRule=\"" + str(self.additionalFields[i][2]) + "\" Name=\"" + str(self.additionalFields[i][0]) + "\" DisplayName=\"" + str(self.additionalFields[i][1]) + "\">" + str(self.additionalFields[i][3]) + "</Field>"
			r+= "</AdditionalFields>"
		if (len(self.iconURL) > 0):
			r+= "<IconURL>" + self.iconURL + "</IconURL>"
		r+= "</Entity>"
                return r	





class MaltegoTransform(object):
# We were lazy to use a proper XML library to generate
# our XML. Thus - encode data before you insert!
# ..Sorry - RT 

	entities = []
	exceptions = []
	UIMessages = []
	
	def __init__(self):
	    self.entities=[]
	    self.exceptions = []
	    self.UIMessages = []
	    self=None

	    
	def addEntity(self,enType=None,enValue=None):
		me = MaltegoEntity(enType,enValue)
		self.entities.append(me)
		return me
	
		
	def addUIMessage(self,message,messageType="Inform"):
		self.UIMessages.append([messageType,message])
	
	def addException(self,exceptionString):
		self.exceptions.append(exceptionString)
		
	def throwExceptions(self):
	        r=''
		r+= "<MaltegoMessage>"
		r+= "<MaltegoTransformExceptionMessage>"
		r+= "<Exceptions>"
		
		for i in range(len(self.exceptions)):
			r+= "<Exception>" + self.exceptions[i] + "</Exceptions>"
		r+= "</Exceptions>"	
		r+= "</MaltegoTransformExceptionMessage>"
		r+= "</MaltegoMessage>"
		return r
		
	def returnOutput(self):
		r=''
		r+= "<MaltegoMessage>"
		r+= "<MaltegoTransformResponseMessage>"
						
		r+= "<Entities>"
		for i in range(len(self.entities)):
			r+=self.entities[i].returnEntity()
		r+= "</Entities>"
						
		r+= "<UIMessages>"
		for i in range(len(self.UIMessages)):
			r+= "<UIMessage MessageType=\"" + self.UIMessages[i][0] + "\">" + self.UIMessages[i][1] + "</UIMessage>"
		r+= "</UIMessages>"
			
		r+= "</MaltegoTransformResponseMessage>"
		r+= "</MaltegoMessage>"
		return r
		



class MaltegoMsg:

 def __init__(self,MaltegoXML=""):

    xmldoc = minidom.parseString(MaltegoXML)

    #read the easy stuff like value, limits etc
    self.Value = self.i_getNodeValue(xmldoc,"Value")
    self.Weight = self.i_getNodeValue(xmldoc,"Weight")
    self.Slider = int(self.i_getNodeAttributeValue(xmldoc,"Limits","SoftLimit"))
    self.Type = self.i_getNodeAttributeValue(xmldoc,"Entity","Type")
    
    
    #read additional fields
    Properties = {}
    try:
    	AFNodes= xmldoc.getElementsByTagName("AdditionalFields")[0]
    	Settings = AFNodes.getElementsByTagName("Field")
    	for node in Settings:
    		AFName = node.attributes["Name"].value
    		AFValue = self.i_getText(node.childNodes)
    		Properties[AFName] = AFValue
    except:  
        #sure this is not the right way...;)
    	dontcare=1
     

    #parse transform settings
    TransformSettings = {}
    try:
    	TSNodes= xmldoc.getElementsByTagName("TransformFields")[0]
    	Settings = TSNodes.getElementsByTagName("Field")
    	for node in Settings:
    		TSName = node.attributes["Name"].value
    		TSValue = self.i_getText(node.childNodes)
        	TransformSettings[TSName] = TSValue
    except:
    	dontcare=1  
                        
    #load back into object
    self.Properties = Properties
    self.TransformSettings = TransformSettings

 def i_getText(self,nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


 def i_getNodeValue(self,node,Tag):
    return self.i_getText(node.getElementsByTagName(Tag)[0].childNodes)

 def i_getNodeAttributeValue(self,node,Tag,Attribute):
    return node.getElementsByTagName(Tag)[0].attributes[Attribute].value


 def getProperty(self,skey):
     if skey in self.Properties.keys():
         return self.Properties[skey]
     else:
          return None
          
 def getTransformSetting(self,skey):
     if skey in self.TransformSettings.keys():
         return self.TransformSettings[skey]
     else:
          return None
           


