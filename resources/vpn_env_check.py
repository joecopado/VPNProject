import getpass
import json
import os
import platform
import shutil
import socket
import subprocess
import sys


def get_working_directory():
    return os.getcwd()


def check_identity():
    sudo_path = shutil.which("sudo")
    sudo_noninteractive_ok = False
    if sudo_path:
        sudo_noninteractive_ok = subprocess.run(
            [sudo_path, "-n", "true"], capture_output=True
        ).returncode == 0
    return {
        "euid": os.geteuid() if hasattr(os, "geteuid") else None,
        "is_root": hasattr(os, "geteuid") and os.geteuid() == 0,
        "whoami": getpass.getuser(),
        "sudo_present": sudo_path is not None,
        "sudo_noninteractive_ok": sudo_noninteractive_ok,
    }


def check_tun_device():
    result = {"path_exists": os.path.exists("/dev/net/tun")}
    if result["path_exists"]:
        try:
            fd = os.open("/dev/net/tun", os.O_RDWR)
            os.close(fd)
            result["openable"] = True
        except OSError as e:
            result["openable"] = False
            result["open_error"] = str(e)
    return result


def check_init_system():
    return {
        "systemd_managed": os.path.exists("/run/systemd/system"),
        "pid1_comm": _read_pid1_comm(),
        "systemctl_present": shutil.which("systemctl") is not None,
    }


def _read_pid1_comm():
    try:
        with open("/proc/1/comm") as f:
            return f.read().strip()
    except OSError:
        return None


def check_dbus():
    return {
        "dbus_daemon_present": shutil.which("dbus-daemon") is not None,
        "system_bus_socket": os.path.exists("/var/run/dbus/system_bus_socket")
        or os.path.exists("/run/dbus/system_bus_socket"),
    }


def check_package_managers():
    return {
        mgr: shutil.which(mgr) is not None
        for mgr in ("apt-get", "yum", "dnf", "apk")
    }


def check_vpn_tooling():
    return {
        "openvpn": shutil.which("openvpn"),
        "openvpn3": shutil.which("openvpn3"),
    }


def check_egress(host, ports):
    results = {}
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((host, port))
            results[str(port)] = "open"
        except Exception as e:
            results[str(port)] = f"closed/filtered ({e.__class__.__name__})"
        finally:
            s.close()
    return results


def run_full_env_check():
    report = {
        "cwd": get_working_directory(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "identity": check_identity(),
        "tun_device": check_tun_device(),
        "init_system": check_init_system(),
        "dbus": check_dbus(),
        "package_managers": check_package_managers(),
        "vpn_tooling": check_vpn_tooling(),
        "egress_easyvpn_openvpn_com": check_egress(
            "easyvpn.openvpn.com", [443, 943, 1194]
        ),
    }
    return json.dumps(report, indent=2)


if __name__ == "__main__":
    print(run_full_env_check())
