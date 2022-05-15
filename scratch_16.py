R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'   # white
Y = '\033[33m'  # yellow

import getpass
import platform
import psutil
import wmi
import socket
import requests

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
computer = wmi.WMI()
computer_info = computer.Win32_ComputerSystem()[0]
os_info = computer.Win32_OperatingSystem()[0]
proc_info = computer.Win32_Processor()[0]
gpu_info = computer.Win32_VideoController()[0]
ip = requests.get('https://ip.42.pl/json').text
# os_name = os_info.Name.encode('utf-8').split(b'|')[0]
# os_version = ' '.join([os_info.Version, os_info.BuildNumber])
# system_ram = float(os_info.TotalVisibleMemorySize) / 1048576  # KB to GB
'''try:
    print('User:', computer_info.UserName)
except:
    print('User:', getpass.getuser())
try:
    print(f'Primary Owner Email: {computer_info.PrimaryOwnerName}')
    print(f'Manufacturer: {computer_info.Manufacturer}')
    print(f'Model PC: {computer_info.Model}')
except:
    pass
try:
    print('Model:', os_info.Name.replace('|C:\WINDOWS|\Device\Harddisk0\Partition3', ''))
except:
    print('Model:', platform.system(), platform.release())
print('Distro:', platform.version(), platform.machine())
try:
    print(f'CPU: {proc_info.Name}')
    print(f'GPU: {gpu_info.Name}')
except:
    print(f'CPU: {platform.processor()}')
    with open('/proc/cpuinfo') as f:
        print(f'GPU: {f.read()}')
print(f'RAM: {get_size (svmem.available)}/{get_size(svmem.total)}')
print(f'Disk: {get_size(partition_usage.free)}/{get_size(partition_usage.total)}')
print('LAN_IP:')
print('WAN_IP:')'''
# print(computer_info)
model_os = os_info.Name.replace('|C:\WINDOWS|\Device\Harddisk0\Partition3', '')
'''print({R}            
                                                User: {computer_info.UserName}  
                                                Primary Owner Email: {computer_info.PrimaryOwnerName}                   
`7MM"""Yb.     .g8""8q.    .M"""bgd  .M"""bgd   Manufacturer: {computer_info.Manufacturer}    
  MM    `Yb. .dP'    `YM. ,MI    "Y ,MI    "Y   Model PC: {computer_info.Model}
  MM     `Mb dM'      `MM `MMb.     `MMb.       Model OS: {model_os}
  MM      MM MM        MM   `YMMNq.   `YMMNq.   Distro: {platform.version()} {platform.machine()}
  MM     ,MP MM.      ,MP .     `MM .     `MM   CPU: {proc_info.Name}
  MM    ,dP' `Mb.    ,dP' Mb     dM Mb     dM   GPU: {gpu_info.Name}
.JMMmmmdP'     `"bmmd"'   P"Ybmmd"  P"Ybmmd"    RAM: {get_size (svmem.available)}/{get_size(svmem.total)}
                                                Disk: {get_size(partition_usage.free)}/{get_size(partition_usage.total)}
                                                LAN_IP: {local_ip}

)'''

print(f'''{R}
                                    User: {computer_info.UserName}  
                                    Primary Owner Email: {computer_info.PrimaryOwnerName}          
                                    Manufacturer: {computer_info.Manufacturer}   
██████╗░░█████╗░░██████╗░██████╗    Model PC: {computer_info.Model}
██╔══██╗██╔══██╗██╔════╝██╔════╝    Model OS: {model_os}    
██║░░██║██║░░██║╚█████╗░╚█████╗░    Distro: {platform.version()} {platform.machine()}
██║░░██║██║░░██║░╚═══██╗░╚═══██╗    CPU: {proc_info.Name}
██████╔╝╚█████╔╝██████╔╝██████╔╝    GPU: {gpu_info.Name}
╚═════╝░░╚════╝░╚═════╝░╚═════╝░    RAM: {get_size (svmem.available)}/{get_size(svmem.total)}
                                    Disk: {get_size(partition_usage.free)}/{get_size(partition_usage.total)}
                                    LAN_IP: {local_ip}
                                    WAN_IP: {ip}
''')
