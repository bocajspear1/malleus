Malleus is a web ui for Incus with a focus on deploying educational labs.

# Installation

Clone the repo:
```
git clone https://github.com/bocajspear1/malleus.git
```

Create a venv and install the dependencies.
```
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

Ensure Incus is set up (be sure to run `inucs admin init`) and configured to listen externally on port 8443, then with the `incus` command run the following command to generate the certificate:

```
incus remote generate-certificate
```

The keys are now generated and present in `~/.config/incus`, `client.crt` and `client.key`. You can copy these local to the repo if desired.

As **root**, configure the Incus daemon to trust the newly generated certificates:
```
su - # or run the next command with "sudo"
incus config trust add-certificate <PATH TO client.crt> 
```

Then configure `malleus/malleus/settings.py` to point to the certificates:

```
vi malleus/malleus/settings.py
```

Set:
```
INCUS_CERT = "<PATH TO client.crt>"
INCUS_KEY = "<PATH TO client.key"
```

Add the `*` to the ALLOWED_HOSTS as well.

Then run the server's migrations with:
```
cd malleus
python manage.py migrate
```

Then run the server with:
```
python3 manage.py runserver 0.0.0.0:8000
```