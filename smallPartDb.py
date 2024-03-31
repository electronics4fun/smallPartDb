"""
Small python class for interfacing [partDb](https://github.com/Part-DB/Part-DB-server) based on request package.
Author: Albrecht Münzing <albrecht.muenzing@x-bert.de>
Created: 1st March, 2024
"""

# import
import logging
import json
import yaml
import requests
import warnings
import urllib.parse



# config the logging behavior
logging.basicConfig(filename='log.log',level=logging.DEBUG)

class Endpoint():
    base_url = ""
    attachment_types = ""
    attachment_typesId = ""
    attachment_typesIdChildren = ""
    attachments = ""
    attachmentsId = ""
    categories = ""
    categoriesId = ""
    categoriesIdChildren = ""
    info = ""
    manufacturers = ""
    manufacturersId = ""
    parts = ""
    partsId = ""
    projects = ""
    projectsId = ""
    projectsIdChildren = ""
    tokensCurrent = ""
    users = ""
    usersId = ""
    footprints = ""
    footprintsId = ""
    parameters = ""
    parametersId = ""

    def __init__(self, base_url):
        self.base_url = base_url

        self.attachment_types = base_url + "attachment_types"
        self.attachment_typesId = base_url + "attachment_types/{id}"
        self.attachment_typesIdChildren = base_url + "attachment_types/{id}/children"
        self.attachments = base_url + "attachments"
        self.attachmentsId = base_url + "attachments/{id}"
        self.categories = base_url + "categories"
        self.categoriesId = base_url + "categories/{id}"
        self.categoriesIdChildren = base_url + "categories/{id}/children"
        self.info = base_url + "info"
        self.manufacturers = base_url + "manufacturers"
        self.manufacturersId = base_url + "manufacturers/{id}"
        self.parts = base_url + "parts"
        self.partsId = base_url + "parts/{id}"
        self.projects = base_url + "projects"
        self.projectsId = base_url + "projectsId"
        self.projectsIdChildren = base_url + "projectsIdChildren"
        self.tokensCurrent = base_url + "tokens/current"
        self.users = base_url + "users"
        self.usersId = base_url + "users/{id}"
        self.footprints = base_url + "footprints"
        self.footprintsId = base_url + "footprints/{id}"
        self.parameters = base_url + "parameters"
        self.parametersId = base_url + "parameters/{id}"
  
class smallPartDb():
    host = None
    header = None
    headerPatch = None
    info = None
    categories = []
    projects = []
    parts = []
    manufacturers =[]
    attachments = []
    footprints = []
    attachmentTypes = []

    def __init__(self, host, token):
        self.host = host
        self.endpoint = Endpoint("http://" + self.host + "/api/")

        self.header = {'Content-Type': 'application/json', 'User-Agent':'APS-DB-Converter', 'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
        self.r = requests.Session()
        self.r.headers.update(self.header)

        self.headerPatch = {'Content-Type': 'application/merge-patch+json', 'User-Agent':'APS-DB-Converter', 'Accept': 'application/ld+json', 'Authorization': 'Bearer ' + token}
        self.rUpdate = requests.Session()
        self.rUpdate.headers.update(self.headerPatch)

        self.getInfo()
    
    def __str__(self):
        if self.info is not None:
            return "Connected to " + self.info['title'] + ", Version: " + self.info['version'] + " on " + str(self.host)
        
    def getInfo(self):
        url = self.endpoint.info.format()
        r = self.r.get(url)
        if r.status_code == 200:
            self.info = json.loads(r.text)
        else:
            self.info = None
            raise RuntimeError("unable to get info")
        return r
    
    def getCategories(self):
        url = self.endpoint.categories.format()
        p = 1
        size = 500
        junk = []
        cat = []
        while(True):
            params = { 'page': p, 'itemsPerPage': size }
            r = self.r.get(url, params=params)
            if r.status_code == 200:
                junk = json.loads(r.text)
            else:
                junk = None
                warnings.warn("getCategories status_code: " + str(r.status_code))
                return r

            if(len(junk) > 0):
                for i in junk:
                    cat.append(i)
            else:
                break
           
            p = p + 1
            junk.clear()

        self.categories = cat
        return r

    def writeParameter(self, name=None, data=None):
        myData = {}
        myData['name'] = ""

        if data==None and name==None:
            warnings.warn("writeParameter nothing to do")
            return

        if name!=None:
            myData['name'] = name

        data.update(myData)

        data = json.dumps(data)
        url = self.endpoint.parameters.format()
        r = self.r.post(url, data=data)
        return r

    def patchParameter(self, id, data=None):
        data = json.dumps(data)
        url = self.endpoint.parametersId.format(id=id)
        #print("url: " + url + ", data: " + str(data) + ", header: " + str(self.rUpdate.headers))
        r = self.rUpdate.patch(url, data=data)
        return r
        
    def writeAttachment(self, name=None, data=None):
        myData = {}
        myData['name'] = ""

        if data==None and name==None:
            warnings.warn("writeAttachment nothing to do")
            return

        if name!=None:
            myData['name'] = name

        data.update(myData)

        data = json.dumps(data)
        url = self.endpoint.attachments.format()
        r = self.r.post(url, data=data)
        return r

    def writeProject(self, name, parent=None, comment=None):
        if parent is not None:
            parent = self.lookupProject(parent) # returns the id or None

        data = { 'name': name }
        if parent != None:
            data['parent'] = '/api/projects/' + parent
        if comment != None:
            data['comment'] = comment

        data = json.dumps(data)
        url = self.endpoint.projects.format()
        r = self.r.post(url, data=data)
        return r

    def writeCategory(self, name, parent=None, comment=None):
        if parent is not None:
            parent = self.lookupCategory(parent) # returns the id or None

        data = { 'name': name }
        if parent != None:
            data['parent'] = '/api/categories/' + parent
        if comment != None:
            data['comment'] = comment

        data = json.dumps(data)
        url = self.endpoint.categories.format()
        r = self.r.post(url, data=data)
        return r
    
    def patchCategory(self, name, newName=None, parent=None, comment=None):
        data = {}
        if newName != None:
            data['name'] = newName
        if parent != None:
            data['parent'] = '/api/categories/' + parent
        if comment != None:
            data['comment'] = comment

        if newName != None and parent != None and comment != None:
            warnings.warn("patchCategory... nothing to do")
            return None

        id = self.lookupCategory(name)
    
        data = json.dumps(data)
        url = self.endpoint.categoriesId.format(id=id)
        #print("url: " + url + ", data: " + str(data) + ", header: " + str(self.rUpdate.headers))
        r = self.rUpdate.patch(url, data=data)
        return r 

    def lookupCategory(self, category):
        if self.getCategories().status_code != 200:
            #print("ERROR: while getCategories")
            return None
        categoryId = None
        if self.categories is not None and type(category) == str:
            for c in self.categories:
                if c['name'] == category:
                    categoryId = str(c['id'])
        if categoryId == None:
            warnings.warn("no parent found for >" + category + "<")
        return categoryId

    def lookupProject(self, project):
        if self.getProjects().status_code != 200:
            #print("ERROR: while getProjects")
            return None
        projectId = None
        if self.projects is not None and type(project) == str:
            for c in self.projects:
                if c['name'] == project:
                    projectId = str(c['id'])
        if projectId == None:
            warnings.warn("no parent found for >" + project + "<")
        return projectId
        
    def getProjects(self):
        url = self.endpoint.projects.format()
        p = 1
        size = 500
        junk = []
        cat = []
        while(True):
            params = { 'page': p, 'itemsPerPage': size }
            r = self.r.get(url, params=params)
            if r.status_code == 200:
                junk = json.loads(r.text)
            else:
                junk = None
                warnings.warn("getProjects status_code: " + str(r.status_code))
                return r

            if(len(junk) > 0):
                for i in junk:
                    cat.append(i)
            else:
                break
           
            p = p + 1
            junk.clear()

        self.projects = cat
        return r

    def lookupPart(self, name):
        r = self.getParts().status_code
        if r.status_code != 200:
            warnings.warn("lookupPart - getParts returned: " + str(r.status_code))
            return None
        partId = None
        if self.parts is not None and type(name) == str:
            for p in self.parts:
                if p['name'] == name:
                    partId = str(p['id'])
        if partId == None:
            warnings.warn("lookupPart - no part found for >" + name + "<")
        return partId
    
    def writePart(self, name=None, category=None, data=None, comment=None):
        categoryId = None
        myData = {}
        myData['name'] = ""
        myData['category'] = ""

        if data==None:
            if name==None and category==None:
                warnings.warn("wirtePart - no data given")
                return
            if name==None or category==None:
                warnings.warn("if name and category-name is used, both is necessary")
            data = {}

        if name!=None:
            myData['name'] = name
        if category!=None:
            categoryId = self.lookupCategory(category) # returns the id or None
            if categoryId == None:
                r = self.writeCategory(category)
                categoryId = json.loads(r.text)['id']
            myData['category'] = '/api/categories/' + str(categoryId)

        data.update(myData)
        data = json.dumps(data)
        
        url = self.endpoint.parts.format()
        if comment:
            url = url + "?_comment=" + urllib.parse.quote(comment)
        r = self.r.post(url, data=data)

        return r
    
    def writeManufacturer(self, data=None):
        myData = {}

        if data==None:
            warnings.warn("writeManufacturer - no data given")
            return

        data.update(myData)

        data = json.dumps(data)
        url = self.endpoint.manufacturers.format()
        r = self.r.post(url, data=data)
        return r

    def writeFootprint(self, data=None):
        myData = {}

        if data==None:
            warnings.warn("writeFootprint - no data given")
            return

        data.update(myData)

        data = json.dumps(data)
        url = self.endpoint.footprints.format()
        r = self.r.post(url, data=data)
        return r
        
    def patchPart(self, id, data):
        try:
            del data['addedDate']
            del data['lastModified']
            del data['id']
        except:
            pass
    
        status, part = self.getPartById(id)
        # Todo: check for status
        if "addedDate" in part:
            del part['addedDate']
        if "lastModified" in part:
            del part['lastModified']
        if "id" in part:
            del part['id']
        
        part.update(data)

        newData = json.dumps(part)
        url = self.endpoint.partsId.format(id=id)
        r = self.rUpdate.patch(url, data=newData)
        return r 
    
    def getAttachmentTypes(self):
        url = self.endpoint.attachment_types.format()
        p = 1
        size = 500
        junk = []
        part = []
        while(True):
            params = { 'page': p, 'itemsPerPage': size }
            r = self.r.get(url, params=params)
            if r.status_code == 200:
                junk = json.loads(r.text)
            else:
                junk = None
                warnings.warn("getAttachmentTypes status_code: " + str(r.status_code))
                return r

            if(len(junk) > 0):
                for i in junk:
                    part.append(i)
            else:
                break
           
            p = p + 1
            junk.clear()

        self.attachmentTypes = part
        return r

    def patchAttachment(self, id, data=None):
        data = json.dumps(data)
        url = self.endpoint.attachmentsId.format(id=id)
        r = self.rUpdate.patch(url, data=data)
        return r

    def getManufacturers(self):
        url = self.endpoint.manufacturers.format()
        p = 1
        size = 500
        junk = []
        part = []
        while(True):
            params = { 'page': p, 'itemsPerPage': size }
            r = self.r.get(url, params=params)
            if r.status_code == 200:
                junk = json.loads(r.text)
            else:
                junk = None
                warnings.warn("getManufacturers status_code: " + str(r.status_code))
                return r

            if(len(junk) > 0):
                for i in junk:
                    part.append(i)
            else:
                break
           
            p = p + 1
            junk.clear()

        self.manufacturers = part
        return r

    def getFootprints(self):
        url = self.endpoint.footprints.format()
        p = 1
        size = 500
        junk = []
        part = []
        while(True):
            params = { 'page': p, 'itemsPerPage': size }
            r = self.r.get(url, params=params)
            if r.status_code == 200:
                junk = json.loads(r.text)
            else:
                junk = None
                warnings.warn("getFootprints status_code: " + str(r.status_code))
                return r

            if(len(junk) > 0):
                for i in junk:
                    part.append(i)
            else:
                break
           
            p = p + 1
            junk.clear()

        self.footprints = part
        return r

    def lookupAttachmentType(self, name):
        r = self.getAttachmentTypes()
        if r.status_code != 200:
            warnings.warn("lookupAttachmentType - getAttachmentTypes returned: " + str(r.status_code))
            return None
        id = None
        if self.attachmentTypes is not None and type(name) == str:
            for p in self.attachmentTypes:
                if p['name'] == name:
                    id = str(p['id'])
        if id == None:
            warnings.warn("no AttachmentType found for >" + name + "<")

        return id

    def lookupFootprint(self, name):
        r = self.getFootprints()
        if r.status_code != 200:
            warnings.warn("lookupFootprint - getFootprints returned: " + str(r.status_code))
            return None
        id = None
        if self.footprints is not None and type(name) == str:
            for p in self.footprints:
                if p['name'] == name:
                    id = str(p['id'])
        if id == None:
            warnings.warn("no Footprint found for >" + name + "<")
        return id
    
    def lookupManufacturer(self, name):
        manufacturersId = None
        if self.manufacturers is not None and type(name) == str:
            for p in self.manufacturers:
                if p['name'] == name:
                    manufacturersId = str(p['id'])
        if manufacturersId == None:
            warnings.warn("no manufacturer found for >" + name + "<")
        return manufacturersId
    
    def getParts(self):
        url = self.endpoint.parts.format()
        p = 1
        size = 500
        junk = []
        part = []
        while(True):
            params = { 'page': p, 'itemsPerPage': size }
            r = self.r.get(url, params=params)
            if r.status_code == 200:
                junk = json.loads(r.text)
            else:
                junk = None
                warnings.warn("getParts status_code: " + str(r.status_code))
                return r

            if(len(junk) > 0):
                for i in junk:
                    part.append(i)
            else:
                break
           
            p = p + 1
            junk.clear()

        self.parts = part
        return r

    def getPartById(self, id):
        url = self.endpoint.partsId.format(id=id)
        r = self.r.get(url)
        if r.status_code == 200:
            part = json.loads(r.text)
        else:
            part = None
            warnings.warn("unable to get part by id (" + str(id) + "/" + str(r.status_code) + ")")
        
        return r, part

    def getAttachments(self):
        url = self.endpoint.attachments.format()
        p = 1
        size = 500
        junk = []
        attachment = []
        while(True):
            params = { 'page': p, 'itemsPerPage': size }
            r = self.r.get(url, params=params)
            if r.status_code == 200:
                junk = json.loads(r.text)
            else:
                junk = None
                warnings.warn("getAtachments status_code: " + str(r.status_code))
                return r

            if(len(junk) > 0):
                for i in junk:
                    attachment.append(i)
            else:
                break
           
            p = p + 1
            junk.clear()

        self.attachments = attachment
        return r


if __name__ == '__main__':
    
    with open("settings.yaml") as stream:
        try:
            settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise RuntimeError(exc)
    partDb = smallPartDb(settings['host'], settings['token'])

    # show info
    print(partDb)

    print("List all parts")
    status = partDb.getParts()
    if status.status_code == 200:
        for p in partDb.parts:
            print(str(p['id']) + ": " + p['name'])
