# msterhuj.ctfd

Ansible role that deploys and configures [CTFd](https://ctfd.io/) as a production-ready systemd service.

CTFd is installed from its official GitHub release archive, runs inside a Python virtualenv under a dedicated `ctfd` system user, and is served by Gunicorn with the `gevent` worker. A reverse proxy (nginx or similar) is expected in front of it.

**Supported platforms:** Ubuntu 20.04 (focal), 22.04 (jammy), 24.04 (noble)

## Requirements

Before running this role you need:

- A database server (MySQL/MariaDB or PostgreSQL) reachable from the target host
- A Redis server reachable from the target host
- A reverse proxy (e.g. nginx) to terminate TLS and forward traffic to `ctfd_bind_address`

## Role Variables

All variables are documented in [`meta/argument_specs.yml`](meta/argument_specs.yml).

CTFd `config.ini` values are grouped under the `ctfd_config` dict. The role deep-merges it with its internal defaults, so you only need to set the keys you want to override. The only **required** key is `ctfd_config.secret_key`.

| Variable | Default | Description |
|---|---|---|
| `ctfd_version` | `3.8.4` | CTFd release to install |
| `ctfd_venv_path` | `/opt/ctfd/venv` | Path to the Python virtualenv |
| `ctfd_bind_address` | `127.0.0.1:4000` | Gunicorn bind address |
| `ctfd_gunicorn_workers` | `3` | Number of Gunicorn worker processes |
| `ctfd_plugins` | see defaults | List of plugins to clone (`name`, `repo`, optional `version`) |
| `ctfd_config.secret_key` | — | **Required.** Random static string used to sign sessions |
| `ctfd_config.database_url` | `""` | Database URI (e.g. `mysql+pymysql://user:pass@host/ctfd`) |
| `ctfd_config.redis_url` | `""` | Redis URI (e.g. `redis://localhost:6379`) |
| `ctfd_config.log_folder` | `/var/log/ctfd` | Directory for access/error logs |
| `ctfd_config.upload_folder` | `/opt/ctfd_uploads` | Directory for uploaded files |
| `ctfd_config.upload_provider` | `filesystem` | Upload backend: `filesystem` or `s3` |
| `ctfd_config.reverse_proxy` | `false` | Set to `true` (or a proxy-fix tuple) when behind a proxy |

Full list of supported `ctfd_config` keys: [`meta/argument_specs.yml`](meta/argument_specs.yml)

## Example Playbook

Minimal setup with a local SQLite database (development/testing only):

```yaml
- hosts: ctfd
  roles:
    - role: msterhuj.ctfd
      vars:
        ctfd_config:
          secret_key: "change-me-to-a-random-string"
```

Production setup with MySQL and Redis:

```yaml
- hosts: ctfd
  roles:
    - role: msterhuj.ctfd
      vars:
        ctfd_bind_address: "127.0.0.1:4000"
        ctfd_gunicorn_workers: 4
        ctfd_config:
          secret_key: "{{ vault_ctfd_secret_key }}"
          database_url: "mysql+pymysql://ctfd:{{ vault_db_password }}@localhost/ctfd"
          redis_url: "redis://localhost:6379"
          reverse_proxy: true
```

## Development

Requires Docker (for Molecule) and Python 3.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

| Command | Description |
|---|---|
| `ansible-lint -v .` | Lint the role |
| `molecule test` | Full test cycle (lint → converge → verify → destroy) |
| `molecule converge` | Provision only (keeps containers running) |
| `molecule verify` | Run testinfra suite against running containers |
| `molecule verify -- -k test_name` | Run a single testinfra test |

> The repository directory must be named `msterhuj.ctfd` for Molecule to resolve the role correctly.

## License

GNU GPLv3

## Author

[msterhuj](https://github.com/msterhuj) — gabin.lanore@gmail.com
