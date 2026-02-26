import requests

from .project import IncusProject

class IncusClient():

    def __init__(self, host, cert_path, key_path, port=8443, verify=True):
        self._session = requests.Session()
        self._session.cert = (cert_path, key_path)
        self._host = host
        self._port = port
        self._verify = verify

    def get(self, path):
        return self._session.get(f"https://{self._host}:{self._port}{path}", verify=self._verify)
    
    def post(self, path, json_data=None):
        return self._session.post(f"https://{self._host}:{self._port}{path}", verify=self._verify, json=json_data)
    
    def status(self):
        return self._get("/1.0").json()
    

    def get_projects(self):
        return IncusProject.get_list(self)
    
    def get_project(self, project_name):
        proj = IncusProject(self, project_name)
        ok = proj.load()
        if ok:
            return proj
        else:
            return None
        
    def create_project(self, project_name, description, isolate_images=True, isolate_networks=False, isolate_storage=True, isolate_profiles=True, restricted=True):
        proj = IncusProject.new(self, project_name, description, isolate_images=isolate_images, isolate_networks=isolate_networks, isolate_storage=isolate_storage, isolate_profiles=isolate_profiles, restricted=restricted)
        return proj
    
    def get_user(self, username):
        res = self._get(f"/1.0/certificates?filter=name+eq+{username}&recursion=1")

        res_json = res.json()
        if len(res_json['metadata']) == 1:
            return res_json['metadata'][0]
        elif len(res_json['metadata']) > 1:
            raise ValueError("Multi users of the same name!")
        else:
            return None
        
    def create_user(self, username):
        res = self._post("/1.0/certificates", json= {
                "name": username,
            "description": f"User {username}",
            "token": True,
            "type": "client",
            "restricted": True,
            "trust_token": "",
            "certificate": "",
            "trust_token": "",
            "projects": None
        })
        print(res.json())
