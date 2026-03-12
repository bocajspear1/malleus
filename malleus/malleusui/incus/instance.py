from pprint import pprint
import json
import logging


logger = logging.getLogger('IncusInstance')

from .base import IncusBase

class IncusInstance(IncusBase):

    @classmethod
    def get_list(cls, client, project):
        resp = client.get(f"/1.0/instances?project={project}")

    @classmethod
    def new(cls, client, instance_name, description, template_name, project, vm=False, networks=None):
        inst_config = {
                "architecture": "",
                "config": {},
                "devices": {
                        "root": {
                                "path": "/",
                                "pool": "default",
                                "type": "disk"
                        }
                },
                "ephemeral": False,
                "profiles": [
                        "default"
                ],
                "stateful": False,
                "description": description,
                "name": instance_name,
                "source": {
                        "type": "image",
                        "alias": template_name
                },
                "instance_type": "",
                "type": "container",
                "start": True
        } 
        logger.debug("Creating instance with config %s", json.dumps(inst_config, indent=4))

        if vm:
            inst_config['type'] = 'vm'

        counter = 0
        for network in networks:
            iface_name = f"eth{counter}"
            inst_config['devices'][iface_name] = {
                "name": iface_name,
                "network": network,
                "type": "nic"
            }
            counter += 1
        
        resp = client.post(f"/1.0/instances?project={project}", json_data=inst_config)

        resp_json = resp.json()
        
        if resp.status_code == 202:
            logger.info("Created instance %s in project %s", instance_name, project)
            ret_inst = cls(client, instance_name, project)
            ret_inst.load()
            return resp_json['metadata']['id'], ret_inst
        else:
            logger.error("Creating instance failed with code %d: %s", resp.status_code, str(resp.json()))
            return None, None
        
        
    
    def __init__(self, client, instance_name, project):
        super().__init__(client)
        self._client = client
        self._name = instance_name
        self._data = {}
        self._devices = {}
        self._project = project
        self._state = {}


    @property
    def name(self):
        return self._name
    
    @property
    def devices(self):
        return self._devices

    def load(self):
        resp = self._client.get(f"/1.0/instances/{self._name}?project={self._project}")
        if resp.status_code == 200:
            metadata = resp.json()['metadata']
            # pprint(metadata)
            # self._data = 
            self._devices = metadata['devices']
            return True
        else:
            return False
        
    def get_state(self):
        resp = self._client.get(f"/1.0/instances/{self._name}/state?project={self._project}")
        if resp.status_code == 200:
            metadata = resp.json()['metadata']
            self._state = metadata
            # pprint(metadata)
            return self._state
        else:
            return None
        
    def _change_state(self, new_state, forced=False):
        resp = self._client.put(f"/1.0/instances/{self._name}/state?project={self._project}", json_data={
            "action": new_state,
            "force": forced,
            "timeout": 30,
            "stateful": False
        })
        # print(resp.json())
        if resp.status_code == 202:
            operation_id = resp.json()['operation'].split("/")[-1]
            return operation_id
        else:
            return False
        
    def start(self):
        return self._change_state('start')
    
    def stop(self):
        return self._change_state('stop')
    
        
    def delete(self, wait=True):
        
        self.await_operation(self.stop())

        resp = self._client.delete(f"/1.0/instances/{self._name}?project={self._project}")
        if resp.status_code == 202:
            operation_id = resp.json()['operation'].split("/")[-1]
            if wait:
                self.await_operation(operation_id)
            else:
                return operation_id
        else:
            return False
        
    def add_device(self, name, device_type, options=None):

        devices = self._devices
        devices[name] = {
            "type": device_type
        }

        for option in options:
            devices[name][option] = options[option]


        resp = self._client.patch(f"/1.0/instances/{self._name}?project={self._project}", json_data={
            "devices": devices
        })

        if resp.status_code == 200 or resp.status_code == 201:
            logger.info("Added device %s (%s) to instance %s", name, device_type, self._name)
        else:
            logger.error("Failed to add device %s: %s", name, str(resp.json()))

    def get_console(self, command=None, height=24, width=80, term="xterm"):
        if command is None:
            command = [
                "bash"
            ]
        resp = self._client.post(f"/1.0/instances/{self._name}/exec?project={self._project}", json_data={
            "environment": {
                "TERM": term
            },
            "command": command,
            "interactive": True,
            "height": int(height),
            "width": int(width),
            "wait-for-websocket": True
        })
        if resp.status_code == 202:
            logger.info("Got console for instance %s", self._name)
            return resp.json()['metadata']
        else:
            logger.error("Failed to get console for instance %s: %s", self._name, str(resp.json()))
            return False


