import getpass
import platform
import psutil
import socket
import requests

R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'   # white
Y = '\033[33m'  # yellow
import psutil
partitions = psutil.disk_partitions()
for partition in partitions:
    try:
        partition_usage = psutil.disk_usage(partition.mountpoint)
    except PermissionError:
        continue
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

hostname = socket. gethostname()
local_ip = socket. gethostbyname(hostname)
svmem = psutil.virtual_memory()
swap = psutil.swap_memory()
ip = requests.get('https://ip.42.pl/json').text

print(f'''{R}
                                        User: {getpass.getuser()}
    ██████╗░░█████╗░░██████╗░██████╗    Model OS: {platform.system()} {platform.release()}    
    ██╔══██╗██╔══██╗██╔════╝██╔════╝    Distro: {platform.version()} {platform.machine()}
    ██║░░██║██║░░██║╚█████╗░╚█████╗░    CPU: {platform.processor()}
    ██║░░██║██║░░██║░╚═══██╗░╚═══██╗    RAM: {get_size(svmem.available)}/{get_size(svmem.total)}
    ██████╔╝╚█████╔╝██████╔╝██████╔╝    Disk: {get_size(partition_usage.free)}/{get_size(partition_usage.total)}
    ╚═════╝░░╚════╝░╚═════╝░╚═════╝░    LAN_IP: {local_ip}
                                        WAN_IP: {ip}                                
''')
