import re

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.utils import IntegrityError
from django.conf import settings
from django.http import HttpResponseNotFound


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
            if project == f"{request.user.username}--{project}":
                lab.set_running()
        lab_dicts.append(lab.get_dict())
        
    context={'labs': lab_dicts}
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

    

    
    project_name = f"{request.user.username}--{cleaned_name}"

    print(project_name)

    project = client.get_project(project_name)
    if project is None:
        client.create_project(project_name, "", isolate_images=False, isolate_networks=True, isolate_profiles=True, isolate_storage=True, restricted=True)

    for network_name in lab_data.networks:
        print(network_name)
        network = project.get_network(network_name)
        if network is None:
            project.create_network(network_name, f"{network_name} network for lab {cleaned_name}", network_type="ovn")

    for host in lab_data.hosts:
        print(host)
        host_data = project.get_instance(host['hostname'])
        print(host_data)
        if host_data is None:
            project.create_instance(host['hostname'], host['template'], networks=host['networks'])

    

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
