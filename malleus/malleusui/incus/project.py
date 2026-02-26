from .instance import IncusInstance
from .network import IncusNetwork

class IncusProject():

    @classmethod
    def get_list(cls, client):
        resp = client.get(f"/1.0/projects")
        proj_paths = resp.json()['metadata']

        ret_list = []
        for proj_path in proj_paths:
            ret_list.append(proj_path.split("/")[-1])
        return ret_list
    
    @classmethod
    def new(cls, client, project_name, description, isolate_images=True, isolate_networks=False, isolate_storage=True, isolate_profiles=True, restricted=True):

        config = {
            "config": {
                "features.images": str(isolate_images),
                "features.networks": str(isolate_networks),
                "features.networks.zones": str(isolate_networks),
                "features.profiles": str(isolate_profiles),
                "features.storage.volumes": str(isolate_storage),
                "features.storage.buckets": str(isolate_storage),
                "restricted": str(restricted)
            },
            "description": description,
            "name": project_name
        }
        resp = client.post(f"/1.0/projects", json_data=config)
        print(resp.json())
        return resp.json()['metadata']

    def __init__(self, client, project_name="default"):
        self._client = client
        self._name = project_name
        self._data = {}
        self._resources = []

    def load(self):
        resp = self._client.get(f"/1.0/projects/{self._name}")
        print(resp)
        if resp.status_code == 200:
            self._data = resp.json()['metadata']
            print(self._data)
            self._resources = self._data['used_by']
            return True
        else:
            return False
    

    def get_instances(self):
        instance_list = []
        for item in self._resources:
            if item.startswith("/1.0/instances/"):
                instance_list.append(item.split("/")[-1])
        return instance_list
    
    def get_instance(self, instance_name):
        inst = IncusInstance(self._client, instance_name, self._name)
        ok = inst.load()
        if not ok:
            return None
        return inst

    
    def create_instance(self, instance_name, template_name, vm=False, networks=None):
        return IncusInstance.new(self._client, instance_name, "", template_name, self._name, vm=vm, networks=networks)

    def get_networks(self):
        pass

    def get_network(self, network_name):
        net = IncusNetwork(self._client, network_name, self._name)
        ok =  net.load()
        print(ok)
        if not ok:
            return None
        else:
            return net
        
    def create_network(self, network_name, description, network_type="bridge", ipv4_addr=None, ipv4_nat=True):
        return IncusNetwork.new(self._client, network_name, description, self._name, network_type=network_type, ipv4_addr=ipv4_addr, ipv4_nat=ipv4_nat)
