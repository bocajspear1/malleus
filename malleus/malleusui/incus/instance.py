

class IncusInstance():

    @classmethod
    def get_list(cls, client, project):
        resp = client.get(f"/1.0/instances?project={project}")

    @classmethod
    def new(cls, client, instance_name, description, template_name, project, vm=False, networks=None):
        print("hlleo")
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
        print(resp_json)
        ret_inst = cls(client, instance_name, project)
        ret_inst.load()
        return ret_inst
    
    def __init__(self, client, instance_name, project):
        self._client = client
        self._name = instance_name
        self._data = {}
        self._project = project

    def load(self):
        resp = self._client.get(f"/1.0/instances/{self._name}?project={self._project}")
        if resp.status_code == 200:
            self._data = resp.json()['metadata']
            print(self._data)
            return True
        else:
            return False