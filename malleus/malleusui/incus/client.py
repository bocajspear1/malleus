import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import websockets.sync.client as websocket_client
import ssl

from .project import IncusProject
from .user import IncusUser

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
    
    def put(self, path, json_data=None):
        return self._session.put(f"https://{self._host}:{self._port}{path}", verify=self._verify, json=json_data)
    
    def patch(self, path, json_data=None):
        return self._session.patch(f"https://{self._host}:{self._port}{path}", verify=self._verify, json=json_data)
    
    def delete(self, path):
        return self._session.delete(f"https://{self._host}:{self._port}{path}", verify=self._verify)
    
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
        
    def create_project(self, project_name, description, isolate_images=True, isolate_networks=False, isolate_storage=True, isolate_profiles=True, restricted=True, proxy=False, snapshots=False):
        proj = IncusProject.new(self, project_name, description, isolate_images=isolate_images, 
                                isolate_networks=isolate_networks, isolate_storage=isolate_storage, isolate_profiles=isolate_profiles, restricted=restricted, proxy=proxy, snapshots=snapshots)
        return proj
    
    def get_operation(self, operation_id):
        resp = self.get(f"/1.0/operations/{operation_id}")
        if resp.status_code == 200:
            return resp.json()['metadata']
        else:
            return None
        
    def await_operation(self, operation_id):
        resp = self.get(f"/1.0/operations/{operation_id}/wait?timeout=-1")

    def get_user(self, username):
        user = IncusUser(self, username)
        ok = user.load()
        if ok:
            return user
        else:
            return None

    def create_user_cert(self, username, projects=None):
        return IncusUser.new(self, username, projects=projects)
    
    def get_websocket(self, socket_id, socket_secret):

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.load_cert_chain(self._session.cert[0], self._session.cert[1])


        target_url = f"wss://{self._host}:{self._port}/1.0/operations/{socket_id}/websocket?secret={socket_secret}"
        return websocket_client.connect(target_url, 
                    max_size=2097152,
                    ping_interval=None,
                    ssl=ssl_context)
