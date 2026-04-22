import pytest


CTFD_USER = "ctfd"
CTFD_GROUP = "ctfd"
CTFD_HOME = "/opt/ctfd"
CTFD_VERSION = "/opt/CTFd-3.8.4"
CTFD_VENV = "/opt/ctfd/venv"
CTFD_CONFIG = "/opt/ctfd/CTFd/config.ini"
CTFD_SERVICE = "/etc/systemd/system/ctfd.service"
CTFD_PLUGIN = "/opt/ctfd/CTFd/plugins/containers"


@pytest.mark.parametrize(
    "package_name",
    ["python3", "python3-pip", "python3-venv", "python-is-python3", "unzip", "git"],
)
def test_required_packages_are_installed(host, package_name):
    package = host.package(package_name)
    assert package.is_installed


def test_ctfd_account_present(host):
    group = host.group(CTFD_GROUP)
    user = host.user(CTFD_USER)

    assert group.exists
    assert user.exists
    assert user.group == CTFD_GROUP
    assert user.home == CTFD_HOME
    assert user.shell == "/bin/bash"


@pytest.mark.parametrize(
    "path, owner, group, mode",
    [
        (CTFD_VERSION, CTFD_USER, CTFD_GROUP, 0o755),
        ("/opt/ctfd_uploads", CTFD_USER, CTFD_GROUP, 0o755),
        ("/var/log/ctfd", CTFD_USER, CTFD_GROUP, 0o755),
        (CTFD_PLUGIN, CTFD_USER, CTFD_GROUP, 0o755),
    ],
)
def test_ctfd_directories(host, path, owner, group, mode):
    directory = host.file(path)

    assert directory.exists
    assert directory.is_directory
    assert directory.user == owner
    assert directory.group == group
    assert directory.mode == mode


def test_ctfd_symlink_points_to_versioned_release(host):
    symlink = host.file(CTFD_HOME)

    assert symlink.exists
    assert symlink.is_symlink
    assert symlink.linked_to == CTFD_VERSION


def test_ctfd_virtualenv_contains_python_and_gunicorn(host):
    python_bin = host.file(f"{CTFD_VENV}/bin/python3")
    gunicorn_bin = host.file(f"{CTFD_VENV}/bin/gunicorn")

    assert python_bin.exists
    assert python_bin.is_file
    assert python_bin.mode == 0o755
    assert gunicorn_bin.exists
    assert gunicorn_bin.is_file
    assert gunicorn_bin.mode == 0o755


def test_ctfd_config_file_rendered(host):
    config = host.file(CTFD_CONFIG)

    assert config.exists
    assert config.is_file
    assert config.user == CTFD_USER
    assert config.group == CTFD_GROUP
    assert config.mode == 0o600
    assert "[server]" in config.content_string
    assert "SECRET_KEY=secret_key_molecule" in config.content_string
    assert "UPLOAD_FOLDER=/opt/ctfd_uploads" in config.content_string
    assert "LOG_FOLDER=/var/log/ctfd" in config.content_string
    assert "UPDATE_CHECK=True" in config.content_string


def test_ctfd_systemd_unit_rendered(host):
    service_file = host.file(CTFD_SERVICE)

    assert service_file.exists
    assert service_file.is_file
    assert service_file.user == "root"
    assert service_file.group == "root"
    assert service_file.mode == 0o644
    assert "WorkingDirectory=/opt/ctfd" in service_file.content_string
    assert f"ExecStart={CTFD_VENV}/bin/gunicorn" in service_file.content_string
    assert "--workers 3 'CTFd:create_app()'" in service_file.content_string
    assert "--bind 0.0.0.0:4000" in service_file.content_string
    assert "--access-logfile /var/log/ctfd/access.log" in service_file.content_string
    assert "--error-logfile /var/log/ctfd/error.log" in service_file.content_string


def test_ctfd_service_enabled_and_running(host):
    service = host.service("ctfd")

    assert service.is_enabled
    assert service.is_running


def test_ctfd_service_listens_on_configured_port(host):
    socket = host.socket("tcp://0.0.0.0:4000")

    assert socket.is_listening
