import getpass
import platform
import psutil
import socket
import requests
import time
import re
from subprocess import Popen, PIPE
import shutil
import distro
import cpuinfo

R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'   # white
Y = '\033[33m'  # yellow

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

def uptime():
    def includes(text: str, num: int):
        return f"{num} {text}{'' if num == 1 else 's'}"
    delta = round(time.time() - psutil.boot_time())
    hours, remainder = divmod(int(delta), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    d = includes("day", days)
    h = includes("hour", hours)
    m = includes("minute", minutes)
    s = includes("second", seconds)
    if days:
        output = f"{d}, {h}, {m} and {s}"
    elif hours:
        output = f"{h}, {m} and {s}"
    elif minutes:
        output = f"{m} and {s}"
    else:
        output = s
    return output

def powershell(command: str):
        try:
            p = Popen(["powershell"] + command.split(" "), stdout=PIPE)
        except FileNotFoundError as err:
            print("PowerShell command failed to run, make sure you're running the latest version of Windows possible.")
            _traceback = ''.join(traceback.format_tb(err.__traceback__))
            error = ('{1}{0}: {2}').format(type(err).__name__, _traceback, err)
            print(error)
            sys.exit(0)

        stdout, stderror = p.communicate()

        output = stdout.decode("UTF-8", "ignore")
        output = output.replace("\n", "").replace("  ", "").replace("\x00", "")  # Just to make sure...
        return output

def motherboard():
    mboard = powershell("Get-WmiObject win32_baseboard | Format-List Product,Manufacturer")
    find_mboard = re.compile(r"\r\rProduct: (.*?)\rManufacturer : (.*?)\r\r\r\r").search(mboard)
    if find_mboard:
        return f"{find_mboard.group(2)} ({find_mboard.group(1)})"
    else:
        return "Unknown..."

def gpu():
    ps = powershell("(Get-WMIObject win32_VideoController).name")
    return ps.split("\n")

def disk_name():
    parts = psutil.disk_partitions()
    disk_list = []
    for i in parts:
        try:
            total, used, free = shutil.disk_usage(i.device)
            percent_used = round(used / total * 100, 2)
            disk_list.append(f"{i.device[:2]} {get_size(free)} / {get_size(total)} ({percent_used}%)")
        except PermissionError:
            continue
    return str(disk_list).replace("['", "").replace("']", "").replace("'", "")

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
svmem = psutil.virtual_memory()
swap = psutil.swap_memory()
ip = requests.get('https://ip.42.pl/json').text

try:
    import wmi
    computer = wmi.WMI()
    computer_info = computer.Win32_ComputerSystem()[0]
    os_info = computer.Win32_OperatingSystem()[0]
    proc_info = computer.Win32_Processor()[0]
    cpu = powershell(" Get-WmiObject Win32_Processor | Format-list Name").split(":")[1].replace('\n', '').strip()
    gpu_info = computer.Win32_VideoController()[0]
    model_os = os_info.Name.split("|")[0].replace("Майкрософт ", "").replace("Microsoft", "")
    print(f'''{R}
                                    User: {computer_info.UserName}  
                                    Hostname: {proc_info.SystemName}
                                    Primary Owner Email: {computer_info.PrimaryOwnerName}          
                                    Manufacturer: {motherboard()}   
██████╗░░█████╗░░██████╗░██████╗    Model PC: {computer_info.Model} {platform.architecture()[1]}
██╔══██╗██╔══██╗██╔════╝██╔════╝    Model OS: {model_os}
██║░░██║██║░░██║╚═███═╗░╚═███═╗░    Distro: {platform.version()} {platform.machine()}
██║░░██║██║░░██║╚█████╗░╚█████╗░    Uptime: {uptime()}
██║░░██║██║░░██║░╚═══██╗░╚═══██╗    CPU: {cpu} @ {proc_info.CurrentClockSpeed/1000}GHz
██████╔╝╚█████╔╝██████╔╝██████╔╝    GPU: {gpu_info.Name} {int(gpu_info.MaxRefreshRate*0.1)}GB
╚═════╝░░╚════╝░╚═════╝░╚═════╝░    RAM: {get_size(svmem.available)}/{get_size(svmem.total)} ({round(svmem.used / svmem.total * 100, 2)}%)
                                    Disk: {disk_name()}
                                    LAN_IP: {local_ip}
                                    WAN_IP: {ip}
    ''')
except:
    print(f'''{R}
                                        User: {getpass.getuser()}
                                        Hostname: {hostname}
    ██████╗░░█████╗░░██████╗░██████╗    Model OS: {platform.system()} {platform.release()}    
    ██╔══██╗██╔══██╗██╔════╝██╔════╝    Distro: {distro.name()}
    ██║░░██║██║░░██║╚█████╗░╚═███═╗░    Uptime: {uptime()}
    ██║░░██║██║░░██║╚█████╗░╚█████╗░    CPU: {cpuinfo.get_cpu_info()['brand_raw']} @ { cpuinfo.get_cpu_info()['hz_actual_friendly']}
    ██║░░██║██║░░██║░╚═══██╗░╚═══██╗    RAM: {get_size(svmem.available)}/{get_size(svmem.total)} ({round(svmem.used / svmem.total * 100, 2)}%)
    ██████╔╝╚█████╔╝██████╔╝██████╔╝    Disk {disk_name()}
    ╚═════╝░░╚════╝░╚═════╝░╚═════╝░    LAN_IP: {local_ip}
                                        WAN_IP: {ip}                                
    ''')
