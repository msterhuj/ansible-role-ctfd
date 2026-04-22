CTFD
=========

Install and configure CTFd app

Development
-----------

To run linting and Molecule locally, use a Python virtual environment:

  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements-dev.txt
  molecule test

Requirements
------------

You need to configure a database and a redis server.
You also need to configure a web server to serve the CTFd application after installation with nginx proxy.

Role Variables
--------------

Variable can be found in `meta/argument_specs.yml` and are as follows: [Click here](meta/argument_specs.yml)

Main CTFd `config.ini` values are now grouped under `ctfd_config`.
The only mandatory key is `ctfd_config.secret_key`.
The role merges `ctfd_config` with its internal defaults, so you can override only the keys you need.

Example:

    ctfd_config:
      secret_key: "change-me"
      database_url: "mysql+pymysql://root:password@localhost/ctfd"
      redis_url: "redis://localhost:6379"
      log_folder: "/var/log/ctfd"
      upload_folder: "/opt/ctfd_uploads"

Dependencies
------------

This role dosn't have any dependencies.
But you need to configure a database and a redis server.

Example Playbook
----------------

    - hosts: ctfd
      roles:
         - { role: msterhuj.ctfd }

License
-------

GNU GPLv3

Author Information
------------------

msterhuj <gabin.lanore@gmail.com>
