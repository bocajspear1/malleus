---
icon: lucide/package-open
---

## Installing Dependencies

Installation is fairly simple, you only need Python 3 and Incus installed.

Details on installing Incus can be found [here](https://linuxcontainers.org/incus/docs/main/installing/).


!!! note

    Ensure your Incus installation properly initialized with the daemon listening externally. 
    
    If you just installed it, you'll need to run:

    ```shell
    incus admin init
    ```

    When prompted for Incus to listen on the network, prompt to allow it.


## Installing Malleus

1. Clone the repository from [GitHub](https://github.com/bocajspear1/malleus.git)
2. Create and activate a venv: 
```shell
python3 -m venv ./venv
source ./venv/bin/activate
```
3. Install Python dependencies:
```shell
pip3 install -r requirements.txt
```
4. Generate the Incus certificates. They will be generated in `~/.config/incus` as `client.crt` and `client.key`.
```shell
incus remote generate-certificate
```
5. **As root**, configure the Incus daemon to trust the new certificates
```shell
incus config trust add-certificate <PATH TO client.crt> 
```
6. Configure Malleus by editing `malleus/malleus/settings.py` to point to these certificates. Set the following:
```python
INCUS_CERT = "<PATH TO client.crt>"
INCUS_KEY = "<PATH TO client.key"
ALLOWED_HOSTS = [
    ...
    "*"
]
```
9. Run the database migrations:
```shell
cd malleus
python manage.py migrate
```
10. Run the server:
```shell
python3 manage.py runserver 0.0.0.0:8000
```

!!! warning

    This is just running the internal Django development server. This is not intended for untrusted environments and doesn't serve TLS!

## Initializing Labs

Lab systems will still need to be built after installation so students will have those images available to them.

Default labs come with the files need to build their images in the `labs/<LAB>/images` directory. Each subdirectory contains the files for a single system. Each system directory has a `Makefile` with either `local` (Only builds to a local Incus installation) or `export` (exports the image to a `tar.gz` for moving to the Incus system) target. You must have [incus-build](https://github.com/bocajspear1/incus-build) installed. This tool allows you to use Dockerfile-like syntax to build the needed images.


!!! warning

    The default labs do have port forwarding enabled (certain ports are mapped to randomized ports on the host so students can directly access a service). If you're running Malleus on a public server (like in the cloud, which really isn't recommended currently), you'll probably want to disable this by removing the lines for `"port_forwards"` in the `lab.json` file for each lab.
