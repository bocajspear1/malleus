import hashlib
import logging

logger = logging.getLogger('IncusNetwork')

class IncusNetwork():

    @classmethod
    def get_list(cls, client, project):
        resp = client.get(f"/1.0/networks?project={project}")

    @classmethod
    def new(cls, client, network_name, description, project, network_type="bridge", ipv4_addr=None, ipv4_nat=True, ipv6_addr=None, ipv6_nat=True):

        net_hash = hashlib.sha256((project + "--" + network_name).encode()).hexdigest()[:15]
        net_config = {
            "config": {

            },
            "description": description,
            "name": net_hash,
            "type": network_type
        }
        
        if ipv4_addr is not None:
            net_config['config']['ipv4.address'] = ipv4_addr
            net_config['config']["ipv4.nat"] = ipv4_nat
        else:
            net_config['config']['ipv4.address'] = 'none'
            if network_type == "ovn":
                net_config['config']['network'] = 'none'

        if ipv6_addr is not None:
            net_config['config']['ipv6.address'] = ipv4_addr
            net_config['config']["ipv6.nat"] = ipv6_nat
        else:
            net_config['config']['ipv6.address'] = 'none'
        
        resp = None
        if network_type != "ovn":
            resp = client.post(f"/1.0/networks", json_data=net_config)
        else:
            resp = client.post(f"/1.0/networks?project={project}", json_data=net_config)

        if resp.status_code == 200 or resp.status_code == 201:
            logger.info("Created network %s with internal name %s", network_name, net_hash)
            ret_inst = cls(client, network_name, project)
            ret_inst.load()
            return ret_inst
        else:
            logger.info("Creating network failed with code %d: %s", resp.status_code, str(resp.json()))
            return None

        


    def __init__(self, client, network_name, project):
        self._client = client
        self._name = network_name
        self._data = {}
        self._project = project
        self._internal_name = hashlib.sha256((project + "--" + network_name).encode()).hexdigest()[:15]

    @property
    def name(self):
        return self._name
    
    @property
    def internal_name(self):
        return self._internal_name

    def load(self):
        resp = self._client.get(f"/1.0/networks/{self._internal_name}")
        if resp.status_code == 200:
            self._data = resp.json()['metadata']
            return True
        else:
            return False
        
    def delete(self):
        resp = self._client.delete(f"/1.0/networks/{self._internal_name}")
        if resp.status_code == 200:
            self._data = resp.json()['metadata']
            return True
        else:
            return False