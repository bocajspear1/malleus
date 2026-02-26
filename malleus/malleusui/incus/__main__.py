from pprint import pprint

from incus.client import IncusClient

if __name__ == '__main__':
    import sys
    host = sys.argv[1]
    cert = tuple(sys.argv[2].split(","))

    client = IncusClient(host, cert, verify=False)


    pprint(client.get_projects())
    def_project = client.get_project("default")
    print(def_project.get_instances())

    print(def_project.get_instance("kali1"))
    # # print(client.get_user('hp-laptop'))
    # client.create_user("test3")
    