import re
import socket
import random
import base64
import json
import os

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.utils import IntegrityError
from django.conf import settings
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseBadRequest


# Create your views here.
from django.http import HttpResponse

from .labloader import LabLoader
from .incus.client import IncusClient

STATIC_PASSWORD = "Thisisatemppassword"

@login_required
def index(request):
    loader = LabLoader("../labs")
    labs = loader.load()

    client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)

    projects = client.get_projects()

    lab_dicts = []

    for lab_name in labs:
        lab = loader.get(lab_name)
        
        for project in projects:
            print(project, f"{request.user.username}--{lab_name}")
            if project == f"{request.user.username}--{lab_name}":
                lab.set_running()
        lab_dicts.append(lab.get_dict())
        
    context={'labs': lab_dicts}
    print(context)
    return render(request, "malleusui/index.html", context)

@login_required
def create(request, project):
    loader = LabLoader("../labs")
    loader.load()

    cleaned_name = re.sub(r"[^a-zA-Z0-9_-]", "", project)

    lab_data = loader.get(cleaned_name)
    if lab_data is None:
        return HttpResponseNotFound("Lab not found")

    client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)

    
    context = {
        "operations": {

        }
    }
    
    project_name = f"{request.user.username}--{cleaned_name}"

    print(project_name)

    user = client.get_user(request.user.username)
    if user is not None:
        user.add_project(project_name)

    project = client.get_project(project_name)
    if project is None:
        project = client.create_project(project_name, "", isolate_images=False, isolate_networks=False, isolate_profiles=True, isolate_storage=True, restricted=True, proxy=True)

    for network_name in lab_data.networks:
        print(network_name)
        network = project.get_network(network_name)
        if network is None:
            project.create_network(network_name, f"{network_name} network for lab {cleaned_name}")

    for host in lab_data.hosts:
        print(host)
        host_data = project.get_instance(host['hostname'])
        print(host_data)
        if host_data is None:
            operation_id, instance = project.create_instance(host['hostname'], host['template'], networks=host['networks'])
            if 'port_forwards' in host:
                for port_forward in host['port_forwards']:
                    forward_split = port_forward.split(":")
                    proto = forward_split[0]
                    addr = forward_split[1]
                    port_num = int(forward_split[2])
                    name = f"{proto}-{port_num}"
                    if proto == "tcp" and port_num == 2:
                        name = "ssh-forward"

                    found_port = False

                    ext_port = 0
                    while not found_port:
                        ext_port = 20000 + random.randint(1, 19999)
                        try:
                            # Can we get a a race condition to this port? Yes, yes we can.
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                                sock.bind(('', ext_port))
                                found_port = True
                        except OSError:
                            pass
                    print(f"Adding proxy from {ext_port} to {port_forward}")
                    instance.add_device(name, "proxy", {
                        "connect": port_forward,
                        "listen": f"{proto}:0.0.0.0:{ext_port}"
                    })
            print(f"\nGot operation {operation_id}")
            context['operations'][operation_id] = host['hostname']

    context['lab_id'] = cleaned_name
    print(context)
    return render(request, "malleusui/building.html", context)




@login_required
def manage(request, project):
    context = {}

    loader = LabLoader("../labs")
    loader.load()

    cleaned_name = re.sub(r"[^a-zA-Z0-9_-]", "", project)

    lab_data = loader.get(cleaned_name)
    if lab_data is None:
        return HttpResponseNotFound("Lab not found")

    client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)

    project_name = f"{request.user.username}--{cleaned_name}"

    project = client.get_project(project_name)

    context['lab'] = lab_data.get_dict()
    context['project_name'] = project_name
    context['lab_id'] = cleaned_name


    for i in range(len(context['lab']['hosts'])):
        host = context['lab']['hosts'][i]
        instance = project.get_instance(host['hostname'])
        context['lab']['hosts'][i]['port_forwards'] = {}
        if not context['lab']['hosts'][i].get("hide_ip", False):
            state_data = instance.get_state()
            interface_str = ""
            for item in state_data['network']:
                if item in ("lo",):
                    continue
                for addr in state_data['network'][item]['addresses']:
                    if addr['family'] == "inet":
                        interface_str += f" {item}|{addr['address']}"
            context['lab']['hosts'][i]['ip_addr'] = interface_str.strip()
        for device in instance.devices:
            if instance.devices[device]['type'] == "proxy":
               listen_split = instance.devices[device]['listen'].split(":")
               connect_split = instance.devices[device]['connect'].split(":")
                
               context['lab']['hosts'][i]['port_forwards'][device] = {
                   "listen": f"{listen_split[0]}/{listen_split[2]}",
                   "connect_to": f"{connect_split[0]}/{connect_split[2]}"
               }

    print(context)
    return render(request, "malleusui/manage.html", context)

@login_required
def console(request, project, instance_name):
    context = {}

    loader = LabLoader("../labs")
    loader.load()

    cleaned_project = re.sub(r"[^a-zA-Z0-9_-]", "", project)
    cleaned_instance = re.sub(r"[^a-zA-Z0-9_-]", "", instance_name)

    lab_data = loader.get(cleaned_project)
    if lab_data is None:
        return HttpResponseNotFound("Lab not found")

    client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)

    project_name = f"{request.user.username}--{cleaned_project}"

    project = client.get_project(project_name)

    context['lab'] = lab_data.get_dict()
    context['project_name'] = project_name
    context['lab_id'] = cleaned_project

    found = False
    for i in range(len(context['lab']['hosts'])):
        if found:
            continue
        host = context['lab']['hosts'][i]

        if host['hostname'] == cleaned_instance:
            found = True
            context['hostname'] = host['hostname']

            if host.get("console", False) == False:
                return HttpResponseBadRequest("Console not allowed for " + cleaned_instance)
        
    
    if not found:
        return HttpResponseNotFound("Instance not found")

    print(context)
    return render(request, "malleusui/console.html", context)


@login_required
def wait(request, operation_id):

    client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)
    oper_data = client.await_operation(operation_id)
    
    return JsonResponse({
        "done": True
    })



@login_required
def delete(request, project):
    loader = LabLoader("../labs")
    loader.load()

    cleaned_name = re.sub(r"[^a-zA-Z0-9_-]", "", project)

    lab_data = loader.get(cleaned_name)
    if lab_data is None:
        return HttpResponseNotFound("Lab not found")

    client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)

    project_name = f"{request.user.username}--{cleaned_name}"

    project = client.get_project(project_name)
    if project is None:
        return HttpResponseNotFound("Project for lab not found")
    
    user = client.get_user(request.user.username)
    if user is not None:
        user.remove_project(project_name)
    
    for host in lab_data.hosts:
        print(host)
        host_data = project.get_instance(host['hostname'])
        print(host_data)
        if host_data is not None:
            host_data.delete()
    
    for network_name in lab_data.networks:
        print(network_name)
        network = project.get_network(network_name)
        if network is not None:
            network.delete()

    project.delete()

    return redirect("index") 


@login_required
def access(request):
    client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)

    loader = LabLoader("../labs")
    labs = loader.load()

    projects = client.get_projects()

    user_projects = []

    for lab_name in labs:
        lab = loader.get(lab_name)
        for project in projects:
            if project == f"{request.user.username}--{lab_name}":
                user_projects.append(project)
        

    resp = client.create_user_cert(request.user.username, projects=user_projects)
    print(resp)

    # {"client_name":"testme","fingerprint":"7dfd30939b994ea79db37a1757f6ae4368a2c5f67a2f543270796ea8545dc4a5","addresses":["192.168.6.18:8443","10.20.40.1:8443","[fd42:8149:2634:c3ed::1]:8443","[fd42:60f4:19d5:811c::1]:8443"],"secret":"043784f43f6ed33c2260e9da8b46eec06fda22ebbb8abe52ad9c25b67b7b24f7","expires_at":"0001-01-01T00:00:00Z"}
    

    data_dict = {"client_name": request.user.username,
                 "fingerprint":resp['fingerprint'],
                 "addresses":resp['addresses'],
                 "secret":resp['secret'],
                 "expires_at":"0001-01-01T00:00:00Z"}
    
    data_str = base64.b64encode(json.dumps(data_dict).encode()).decode()
    
    context={'user_key': data_str}
    print(context)
    return render(request, "malleusui/access.html", context)   


@login_required
def files(request):

    static_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static", "files")

    file_list = []

    for item in os.listdir(static_path):
        file_list.append({"path": f"files/{item}", "name": item})

    context={'files': file_list}
    print(context)
    return render(request, "malleusui/files.html", context)   

def login(request):
    if request.method =='POST':
        user = authenticate(request, username=request.POST['username'], password=STATIC_PASSWORD)
        auth_login(request, user)
        return redirect("index")
    else:
        context={}
        return render(request, "malleusui/login.html", context)


def logout(request):
    auth_logout(request)
    return redirect("index")

def register(request):
    if request.method =='POST':
        try:
            user = User.objects.create_user(request.POST['username'], "nope@nope.com", STATIC_PASSWORD)
            auth_login(request, user)
            return redirect("index")
        except IntegrityError:
            context={"error": "Username already exists"}
            return render(request, "malleusui/register.html", context)
    else:
        context={}
        return render(request, "malleusui/register.html", context)
