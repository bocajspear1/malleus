import logging

logger = logging.getLogger('IncusProject')

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
    def new(cls, client, project_name, description, isolate_images=True, isolate_networks=False, isolate_storage=True, isolate_profiles=True, restricted=True, proxy=False, snapshots=False):

        config = {
            "config": {
                "features.images": str(isolate_images),
                "features.networks": str(isolate_networks),
                "features.networks.zones": str(isolate_networks),
                "features.profiles": str(isolate_profiles),
                "features.storage.volumes": str(isolate_storage),
                "features.storage.buckets": str(isolate_storage),
                "restricted": str(restricted),
            },
            "description": description,
            "name": project_name
        }

        if proxy:
            config['config']['restricted.devices.proxy'] = 'allow'
        if snapshots:
            config['config']['restricted.snapshots'] = 'allow'
        resp = client.post(f"/1.0/projects", json_data=config)
        
        if resp.status_code == 201:
            logger.info("Created project %s", project_name)
            ret_inst = cls(client, project_name)
            ret_inst.load()
            return ret_inst
        else:
            logger.error("Creating project failed with code %d: %s", resp.status_code, str(resp.json()))
            return None

    def __init__(self, client, project_name="default"):
        self._client = client
        self._name = project_name
        self._description = ""
        self._config = {}
        self._resources = []
        self._loaded = False

    def load(self):
        resp = self._client.get(f"/1.0/projects/{self._name}")

        if resp.status_code == 200:
            metadata = resp.json()['metadata']
            self._description = metadata['description']
            self._config = metadata['config']

            self._resources = metadata['used_by']
            self._loaded = True
            logger.info("Loaded project %s", self._name)
            return True
        else:
            logger.error("Failed to load project %s: %s", self._name, str(resp.json()))
            return False
        
    def delete(self):
        logger.info("Deleting project %s", self._name)
        resp = self._client.delete(f"/1.0/projects/{self._name}")
        if resp.status_code == 200:
            return True
        else:
            return False
    

    def get_instances(self):
        if not self._loaded:
            raise ValueError("Project not loaded")
        instance_list = []
        for item in self._resources:
            if item.startswith("/1.0/instances/"):
                instance_list.append(item.split("/")[-1])
        return instance_list
    
    def get_instance(self, instance_name):
        if not self._loaded:
            raise ValueError("Project not loaded")
        inst = IncusInstance(self._client, instance_name, self._name)
        ok = inst.load()
        if not ok:
            return None
        return inst

    
    def create_instance(self, instance_name, template_name, vm=False, networks=None):
        if not self._loaded:
            raise ValueError("Project not loaded")
        
        internal_network_list = []
        
        for network_name in networks:
            logger.debug("Looking for network %s in project", network_name)
            network = self.get_network(network_name)
            if network is None:
                raise ValueError("Invalid network, unable to find in project")
            logger.debug("Mapped network %s to %s", network.name, network.internal_name)

            internal_network_list.append(network.internal_name)

        return IncusInstance.new(self._client, instance_name, f"Instance of {template_name} for project {self._name}", template_name, self._name, vm=vm, networks=internal_network_list)

    def get_networks(self):
        pass

    def get_network(self, network_name):
        if not self._loaded:
            raise ValueError("Project not loaded")

        net = IncusNetwork(self._client, network_name, self._name)
        ok =  net.load()
        if not ok:
            return None
        else:
            return net
        
    def create_network(self, network_name, description, network_type="bridge", ipv4_addr=None, ipv4_nat=True):
        if not self._loaded:
            raise ValueError("Project not loaded")
        if network_type == "ovn":
            return IncusNetwork.new(self._client, network_name, description, self._name, network_type=network_type, ipv4_addr=ipv4_addr, ipv4_nat=ipv4_nat)
        else:
            new_net = IncusNetwork.new(self._client, network_name, description, self._name, network_type=network_type, ipv4_addr=ipv4_addr, ipv4_nat=ipv4_nat)
            if new_net is None:
                logger.error("Failed to create network %s in project %s", network_name, self._name)
                return None

            net_list = [new_net.internal_name]
            if "restricted.networks.access" in self._config:
                net_list += self._config["restricted.networks.access"].split(",")
            self.update_config({
                "restricted.networks.access": ",".join(set(net_list))
            })
            return new_net

    def update_config(self, new_config):
        if not self._loaded:
            raise ValueError("Project not loaded")
        
        for new_key in new_config:
            self._config[new_key] = new_config[new_key]

        resp = self._client.patch(f"/1.0/projects/{self._name}", json_data={
            "config": self._config
        })
        if resp.status_code == 200:
            logger.info("Updated config for project %s", self._name)
            return True
        else:
            logger.error("Failed to update config for project %s", self._name)
            return False
