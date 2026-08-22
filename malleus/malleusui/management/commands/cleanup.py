from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings

from malleusui.helpers import cleaned_username
from malleusui.incus.client import IncusClient
from malleusui.labloader import LabLoader

class Command(BaseCommand):
    help = "Cleans up labs from local instance"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, nargs="+",)
        parser.add_argument("--all", action="store_true")

    def handle(self, *args, **options):

        loader = LabLoader("../labs")
        loader.load()

        if (len(loader._labs) == 0):
            raise CommandError('No labs loaded! Be sure to be in root dir of the project')
        
        if options['user'] is not None and len(options['user']) > 0 and options['all']:
            raise CommandError('Can only select users or use --all')
        
        user_list = []
        User = get_user_model()
        if options['all']:
            
            user_list = User.objects.all()
        else:
            for user in options['user']:
                
                try:
                    user_obj = User.objects.get(username=user)
                    user_list.append(user_obj)
                except User.DoesNotExist:
                    raise CommandError('User "%s" does not exist' % user)
                
        client = IncusClient(settings.INCUS_SERVER, settings.INCUS_CERT, settings.INCUS_KEY, verify=settings.INCUS_VERIFY)
        projects = client.get_projects()

        for project_name in projects:
            if project_name == "default":
                continue
            for user in user_list:
                username = cleaned_username(user.get_username())
                if project_name.startswith(f"{username}--"):
                    lab_data = loader.get(project_name.replace(f"{username}--", ""))

                    project = client.get_project(project_name)
                    if project is None:
                        self.style.ERROR("Project not found!")
                    
                    incus_user = client.get_user(cleaned_username(username))
                    if incus_user is not None:
                        incus_user.remove_project(project_name)
                    
                    for host in lab_data.hosts:
                        host_data = project.get_instance(host['hostname'])
                        if host_data is not None:
                            self.style.NOTICE(f"Deleting instance {host['hostname']}")
                            host_data.delete()
                        else:
                            self.style.ERROR(f"Instance {host['hostname']} not found in project")
                    
                    for network_name in lab_data.networks:
                        network = project.get_network(network_name)
                        if network is not None:
                            self.style.NOTICE(f"Deleting network {network_name}")
                        else:
                            self.style.ERROR(f"Network {network_name} not found in project", )

                    project.delete()
                    # self.stdout.write(str(project))
        # for poll_id in options["poll_ids"]:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)

        #     poll.opened = False
        #     poll.save()

        #     self.stdout.write(
        #         self.style.SUCCESS('Successfully closed poll "%s"' % poll_id)
        #     )