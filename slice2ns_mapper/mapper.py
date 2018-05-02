#!/usr/bin/python

import os, sys, requests, json, logging, uuid
import database.database as db


#################################### Sonata SP information #####################################
def get_base_url():
    ip_address=db.settings.get('SLICE_MGR','SONATA_SP_IP')
    base_url = 'http://'+ip_address+':32001/api/v2'
    
    return base_url

def use_sonata():    
    return db.settings.get('SLICE_MGR','USE_SONATA')

########################################## /sessions ##########################################
#POST /sessions to create a session and get the token
def create_sonata_session():
    # prepares the parameters for the POST request
    url = get_base_url() + '/sessions'
    data = '{"username":"' + db.settings.get('SLICE_MGR','SONATA_SP_USER') + '","password":"' + db.settings.get('SLICE_MGR','SONATA_SP_PWD') + '"}'
    
    #SONATA SP or EMULATED Connection 
    if use_sonata() == "True":
      #sends the request to the Sonata Gatekeeper API
      response = requests.post(url, data).json()

      # looks for the token value generated by Sonata for the session
      token_array = response['token']
      for item_token in token_array:
          token = token_array['access_token']
          
      return token
           
    else:
      print ("SONATA EMULATED TOKEN REQUEST --> URL: " +url+ ",DATA: " +data)

#DELETE /sessions to delete a session and get the token
def delete_sonata_session(token):
    # prepares the parameters for the POST request
    url = get_base_url() + '/sessions'
    headers = {"authorization":"bearer " + str(token)}
    
    #SONATA SP or EMULATED Connection 
    if use_sonata() == "True": 
      #sends the request to the Sonata Gatekeeper API
      response = requests.delete(url, headers)
      jsonresponse = json.dumps(response, indent=4, sort_keys=True)
      
      return jsonresponse
      
    else:
      print ("SONATA EMULATED DELETE NST --> URL: " +url+ ",HEADERS: " +str(headers))


########################################## /requests ##########################################
#POST /requests to INSTANTIATE Network Service instance
def net_serv_instantiate(token, service_uuid):
    # prepares the parameters for the POST request
    url = get_base_url() + '/requests'
    headers_instantiation = {"authorization":"bearer " + str(token)}
    data_instantiation = '{"service_uuid":"' + service_uuid + '", "ingresses":[], "egresses":[]}'

    #SONATA SP or EMULATED Connection 
    if use_sonata() == "True":
      #sends the request to the Sonata Gatekeeper API
      response = requests.post(url, headers=headers_instantiation, data=data_instantiation)
      jsonresponse = json.loads(response.text)
      
      return jsonresponse
    
    else:
      print ("SONATA EMULATED INSTANTIATION NSI --> URL: " +url+ ",HEADERS: " +str(headers_instantiation)+ ",DATA: " +str(data_instantiation))
      #Generates a RANDOM (uuid4) UUID for this emulated NSI
      uuident = uuid.uuid4()
      jsonresponse = json.loads('{"service_instance_uuid":"'+str(uuident)+'"}')
      return jsonresponse

#POST /requests to TERMINATE Network Service instance
def net_serv_terminate(token, servInstance_uuid):
    # prepares the parameters for the POST request
    url = get_base_url() + "/requests"
    headers_termination = {"authorization":"bearer " + str(token)}
    data_termination = '{"service_instance_uuid":'+ servInstance_uuid + ', "request_type":"TERMINATE"}'

    #SONATA SP or EMULATED Connection 
    if use_sonata() == "True":
      # sends the request to the Sonata Gatekeeper API
      response = requests.post(url, headers=headers_termination, data=data_termination)
      jsonresponse = json.loads(response.text)

      return jsonresponse
    
    else:
      print ("SONATA EMULATED TERMINATE NSI --> URL: " +url+ ",HEADERS: " +str(headers_termination)+ ",DATA: " +str(data_termination))

#GET /requests to pull the information of all Network Services INSTANCES
def getAllNetServInstances(token):
    # prepares the parameters for the POST request
    url = get_base_url() + "/requests"
    headers_getAll = {"authorization":"bearer " + str(token)}

    #SONATA SP or EMULATED Connection 
    if use_sonata() == "True":
      # sends the request to the Sonata Gatekeeper API
      response = requests.get(url, headers=headers_getAll)
      jsonresponse = json.dumps(response, indent=4, sort_keys=True)

      return jsonresponse
    
    else:
      print ("SONATA EMULATED GET ALL NSI --> URL: " +url+ ",HEADERS: " +str(headers_getAll))

#GET /requests/<request_uuid> to pull the information of a single Network Service INSTANCE
def getNetServInstance(token, request_uuid):
    # prepares the parameters for the POST request
    url = get_base_url() + "/requests/" + str(request_uuid)
    headers_get = {"authorization":"bearer " + str(token)}

    #SONATA SP or EMULATED Connection 
    if use_sonata() == "True":
      # sends the request to the Sonata Gatekeeper API
      response = requests.get(url, headers=headers_get)
      jsonresponse = json.dumps(response, indent=4, sort_keys=True)

      return jsonresponse.text
    
    else:
      print ("SONATA EMULATED GET NSI --> URL: " +url+ ",HEADERS: " +str(headers_get))

   
########################################## /services ##########################################
#GET /services to pull all Network Services information
def getListNetServices(token):
    #cleans the current nsInfo_list to have the information updated
    del db.nsInfo_list[:]
    
    # prepares the parameters for the POST request
    url = get_base_url() + "/services"
    headers_NetServices = {"authorization": "bearer " + str(token)}

    #SONATA SP or EMULATED Connection 
    if use_sonata() == "True":
      # sends the request to the Sonata Gatekeeper API
      response = requests.get(url, headers=headers_NetServices)
      services_array = json.loads(response.text)
    
      for service_item in services_array:
        #Each element of the list is a dictionary   
        dict_ns = {}
        dict_ns["name"] = service_item['nsd']['name']
        dict_ns["uuid"] = service_item['uuid']
        dict_ns["decription"] = service_item['nsd']['description']
        dict_ns["version"] = service_item['nsd']['version']
        dict_ns["vendor"] = service_item['nsd']['vendor']
        dict_ns["md5"] = service_item['md5']
        dict_ns["author"] = service_item['nsd']['author']
        dict_ns["created"] = service_item['created_at']
        dict_ns["status"] = service_item['status']
        dict_ns["updated"] = service_item['updated_at']
  
        #adds the dictionary element into the list
        db.nsInfo_list.append(dict_ns)
              
      return db.nsInfo_list
      
    else:
      print ("SONATA EMULATED GET SERVICES --> URL: " +url+ ",HEADERS: " + str(headers_NetServices))

################################ /records/nsir/ns-instances #####################################