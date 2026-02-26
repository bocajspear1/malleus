

class IncusNetwork():

    @classmethod
    def get_list(cls, client, project):
        resp = client.get(f"/1.0/networks?project={project}")

    @classmethod
    def new(cls, client, network_name, description, project, network_type="bridge", ipv4_addr=None, ipv4_nat=True, ipv6_addr=None, ipv6_nat=True):
        net_config = {
            "config": {

            },
            "description": description,
            "name": network_name,
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
        
        resp = client.post(f"/1.0/networks?project={project}", json_data=net_config)
        resp_json = resp.json()
        print(resp_json)
        ret_inst = cls(client, network_name, project)
        ret_inst.load()
        return ret_inst


    def __init__(self, client, network_name, project):
        self._client = client
        self._name = network_name
        self._data = {}
        self._project = project

    def load(self):
        resp = self._client.get(f"/1.0/networks/{self._name}?project={self._project}")
        if resp.status_code == 200:
            self._data = resp.json()['metadata']
            print(self._data)
            return True
        else:
            return False