

class IncusUser():

    @classmethod
    def new(cls, client, username, projects=None):
        res = client.post("/1.0/certificates", json_data={
            "name": username,
            "description": f"User {username}",
            "token": True,
            "type": "client",
            "restricted": True,
            "trust_token": "",
            "certificate": "",
            "trust_token": "",
            "projects": projects
        })

        if res.status_code == 202:
            return res.json()['metadata']['metadata']
        else:
            print(res.status_code, res.json())
            return None
        
    def __init__(self, client, username):
        self._client = client
        self._username = username
        self._config = None
        self._loaded = False
        self._fingerprint = None

    def load(self):
        res = self._client.get(f"/1.0/certificates?filter=name+eq+{self._username}&recursion=1")

        res_json = res.json()
        if len(res_json['metadata']) == 1:
            self._config = res_json['metadata'][0]
            print(self._config)
            self._fingerprint = res_json['metadata'][0]['fingerprint']
            self._loaded = True
            return True
        elif len(res_json['metadata']) > 1:
            raise ValueError("Multi users of the same name!")
        else:
            return False

    def _update_projects(self, project_list):
        res = self._client.patch(f"/1.0/certificates/{self._fingerprint}", json_data={
            "projects": project_list
        })

        res_json = res.json()
        print(res_json)

    def remove_project(self, project_name):
        if not self._loaded:
            raise ValueError("User not loaded")
        if project_name in self._config['projects']:
            self._config['projects'].remove(project_name)
        self._update_projects(self._config['projects'])

    def add_project(self, project_name):
        if not self._loaded:
            raise ValueError("User not loaded")
        if project_name not in self._config['projects']:
            self._config['projects'].append(project_name)
        self._update_projects(self._config['projects'])
