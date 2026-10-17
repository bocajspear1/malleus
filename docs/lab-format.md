---
icon: lucide/flask-conical
---

## Lab Structure Overview

Malleus uses a file-based lab file structure to make sharing and collaborating labs easy. It makes it easy to host labs in git repositories and easies for users to understand.

By default Malleus looks at the `../labs`, relative to the `malleus` directory with the `manage.py` file. 

A lab directory follows these rules:

  - Each lab is a single directory
  - The directory must at least contain a `lab.json` file. This contains the definition of lab, lab metadata, how the systems are connected, what types of access students have and more.
  - The `docs` subdirectory contains documentation for students.
    - Each subdirectory in the `<LAB>/docs` directory either matches the name of a system defined in the `lab.json` file or `_main` which indicates this is the primary overarching documentation for the lab. 
    - Documentation is one or more Markdown files. Malleus loads them as multiple pages either adjacent to the system's console or lab's Documentation section.
  - The `images` directory contains the files to build the lab's system images.


## `lab.json` Format

- `id`: The unique ID of the lab
- `name`: The name displayed for the lab
- `description`: The description displayed for the lab
- `display`: Can be either `diagram`, which displays systems in a network diagram, or `list`, which simply lists all hosts.
- `hosts`: List of host objects:
    - `template`: The template/image to use as the systems base
    - `hostname`: The system's hostname
    - `description`: The description displayed for the host.
    - `networks`: A list containing strings matching the different networks mapped in the root `networks` object. (See below)
    - `port_forwards`: A list containing strings that indicate ports to forwarded from a randomized host port to a port on that system. Format is:
    ```
    [tcp|udp]:<ADDRESS>:<INTERNAL_PORT>
    ```
    - `console`: Boolean indicating if students should be allowed to console to the host in the web UI.
    - `hide_ip`: Boolean indicating if the IP address should be hidden when viewing the system in the web UI.
- `networks`: The root network object, maps network names to configurations.
    - `<NETWORK_NAME>`
        - `private`: Is a private network (doesn't connect to an external network). Should be `true`.