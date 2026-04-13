import os
import json

from .incus.client import IncusClient

class LabBuilder():

    def __init__(self, user, lab, client : IncusClient):
        self._user = user
        self._client : IncusClient = client
        self._lab = lab

        self._project_name = f"{self._user}--{lab.id}"

    def build(self):

        project = self._client.get_project(self._project_name)
        if project is None:
            self._client
class Lab():

    def __init__(self, config, lab_path):
        self._id = config['id']
        self._config = config
        self._running = False
        self._lab_path = lab_path

    @property
    def id(self):
        return self._id
    
    @property
    def running(self):
        return self._running
    
    @property
    def networks(self):
        return self._config['networks']
    
    @property
    def hosts(self):
        return self._config['hosts']
    
    def set_running(self):
        self._running = True

    def get_dict(self):
        ret_dict = self._config
        ret_dict['running'] = self._running
        return ret_dict
    
    def get_instance_docs(self, instance_name):
        docs_path = os.path.join(self._lab_path, "docs", instance_name)
        
        if os.path.exists(docs_path):
            doc_list = os.listdir(docs_path)
            print(doc_list)
            doc_list.sort()
            doc_data_list = []
            for doc_item in doc_list:
                full_doc_path = os.path.join(docs_path, doc_item)
                with open(full_doc_path, "r") as doc_file:
                    doc_contents = doc_file.read()
                    doc_data_list.append({
                        "content": doc_contents,
                        "haschecks": False
                    })

            return doc_data_list

        
        return []
    
    def get_main_docs(self):
        docs_path = os.path.join(self._lab_path, "docs", "_main")

        if os.path.exists(docs_path):
            doc_list = os.listdir(docs_path)
            doc_list.sort()
            doc_data_list = []
            for doc_item in doc_list:
                full_doc_path = os.path.join(docs_path, doc_item)
                with open(full_doc_path, "r") as doc_file:
                    doc_contents = doc_file.read()
                    doc_data_list.append({
                        "content": doc_contents,
                    })

            return doc_data_list

        
        return []


class LabLoader():

    def __init__(self, lab_dir):
        self._lab_dir = lab_dir
        self._labs = {} 

    def load(self):
        items = os.listdir(self._lab_dir)
        
        for item in items:
            lab_path = os.path.join(self._lab_dir, item)
            lab_file_path = os.path.join(lab_path, "lab.json")
            if os.path.exists(lab_file_path):
                with open(lab_file_path) as lab_file:
                    json_data = json.load(lab_file)
                    if 'id' in json_data:
                        
                        self._labs[json_data['id']] = Lab(json_data, lab_path)

        return list(self._labs.keys())
    
    def get(self, name):
        if name in self._labs:
            return self._labs[name]
        else:
            return None