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

    def __init__(self, config):
        self._id = config['id']
        self._config = config
        self._running = False

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


class LabLoader():

    def __init__(self, lab_dir):
        self._lab_dir = lab_dir
        self._labs = {} 

    def load(self):
        items = os.listdir(self._lab_dir)
        
        for item in items:
            if item.endswith(".json"):
                with open(os.path.join(self._lab_dir, item)) as lab_file:
                    json_data = json.load(lab_file)
                    if 'id' in json_data:
                        
                        self._labs[json_data['id']] = Lab(json_data)

        return list(self._labs.keys())
    
    def get(self, name):
        if name in self._labs:
            return self._labs[name]
        else:
            return None