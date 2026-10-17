---
icon: lucide/users
---

Malleus is mainly intended for small labs on limited hardware (like a laptop). Thus, is doesn't have complex user management and leans on Django's tool for managing users.


!!! warning

    Malleus is currently not designed to live on untrusted networks like the internet. 

## Creating a Super-user

When you first install Malleus, you'll need to create a super-user/admin. This user, as well as any other admin users, will have access to a special "Resources" page that appears in the main navigation bar.

```shell
python manage.py createsuperuser
```

## Managing Users

Users are allowed to self-register to gain access to labs. If a user needs to change their password, you'll have to do it manually with the Django `manage.py`:

```shell
python manage.py changepassword <USER>
```

## Cleaning Up Labs

After a workshop or event, you'll have a bunch of labs initialized and running on the Malleus system. To quickly remove labs, you can cleanup by user:

```shell
python manage.py cleanup --user <USER>
```

or all of the labs with:

```shell
python manage.py cleanup --all
```

## Adding Files for Student Access

In the "File" page, you can provide students with quick downloads for tools they need to access labs or data for the labs. Files should go in `malleus/malleusui/static/files/`. This will be available to ALL logged in users.


## Monitoring Resources

In the web UI, if your user is an admin, you have access to the "Resources" page. It will appears as an extra navigation button on the top navigation bar.

This page gives you a snapshot of what resources are being used on the system. 

!!! note

    The page refreshes every 10 seconds.