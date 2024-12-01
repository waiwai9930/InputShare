import socket
import subprocess
from adb_controller import get_adb_client
from server import scrcpy_receiver, reporter_receiver
from utils.config_manager import get_config
from utils.logger import LOGGER, LogType

def deploy_scrcpy_server() -> tuple[subprocess.Popen, socket.socket] | Exception:
    adb_client = get_adb_client()
    device_list = adb_client.device_list()
    if len(device_list) == 0:
        return scrcpy_receiver.ADBConnectionError()

    primary_device = device_list[0]
    scrcpy_receiver.push_server(primary_device)
    primary_device.forward(f"tcp:{scrcpy_receiver.SERVER_PORT}", "localabstract:scrcpy")

    server_process = scrcpy_receiver.server_process_factory()
    if isinstance(server_process, Exception):
        return server_process

    client_socket = scrcpy_receiver.try_connect_server("localhost")
    if isinstance(client_socket, Exception):
        return client_socket

    return server_process, client_socket

def deploy_reporter_server() -> Exception | None:
    adb_client = get_adb_client()
    device_list = adb_client.device_list()
    if len(device_list) == 0:
        return scrcpy_receiver.ADBConnectionError()

    primary_device = device_list[0]
    primary_device.forward(f"tcp:{reporter_receiver.SERVER_PORT}", f"tcp:{reporter_receiver.SERVER_PORT}")

    package_path    = primary_device.shell("pm path " + reporter_receiver.PACKAGE_NAME)
    package_version = primary_device.shell(f"dumpsys package {reporter_receiver.PACKAGE_NAME} | grep versionName")
    assert type(package_path) == str and type(package_version) == str
    parsed_version = package_version.split("=")[1] if package_version else ""
    not_installed  = len(package_path) == 0
    is_outdated    = parsed_version != reporter_receiver.PACKAGE_VERSION
    if not_installed or is_outdated:
        if not_installed: LOGGER.write(LogType.Server, "Reporter not installed, installing...")
        elif is_outdated: LOGGER.write(LogType.Server, "Reporter outdated, updating...")
        if (res := reporter_receiver.install_server(primary_device)) is not None:
            return res

    return reporter_receiver.start_server(primary_device)
