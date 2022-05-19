import cpuinfo
import ctypes
import distro
import getpass
import platform
import psutil
import re
import requests
from rich.console import Console
import shutil
import socket
from subprocess import Popen, PIPE
import time
import os

console = Console()

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

try:
    import wmi
    computer = wmi.WMI()
    computer_info = computer.Win32_ComputerSystem()[0]
    os_info = computer.Win32_OperatingSystem()[0]
    proc_info = computer.Win32_Processor()[0]
    cpu = powershell(" Get-WmiObject Win32_Processor | Format-list Name").split(":")[1].replace('\n', '').strip()
    gpu_info = computer.Win32_VideoController()[0]
    model_os = os_info.Name.split("|")[0].replace("Майкрософт ", "").replace("Microsoft", "")
    ip = powershell("Invoke-RestMethod ifconfig.me/ip")
    shell = powershell('"PowerShell v$($PSVersionTable.PSVersion)"')
    color = powershell("('{0}[0;40m{1}{0}{0}[0;40m{1}{0}{0}[0;40m{1}{0}[0;41m{1}{0}[0;41m{1}{0}[0;41m{1}{0}[0;42m{1}{0}[0;42m{1}{0}[0;42m{1}{0}[0;43m{1}{0}[0;43m{1}{0}[0;43m{1}{0}[0;44m{1}{0}[0;44m{1}{0}[0;44m{1}{0}[0;45m{1}{0}[0;45m{1}{0}[0;45m{1}{0}[0;46m{1}{0}[0;46m{1}{0}[0;46m{1}{0}[0;47m{1}{0}[0;47m{1}{0}[0;47m{1}{0}[0m') -f [char]0x1B, '   '")
    color_ = powershell("('{0}[0;100m{1}{0}{0}[0;100m{1}{0}{0}[0;100m{1}{0}[0;101m{1}{0}[0;101m{1}{0}[0;101m{1}{0}[0;102m{1}{0}[0;102m{1}{0}[0;102m{1}{0}[0;103m{1}{0}[0;103m{1}{0}[0;103m{1}{0}[0;104m{1}{0}[0;104m{1}{0}[0;104m{1}{0}[0;105m{1}{0}[0;105m{1}{0}[0;105m{1}{0}[0;106m{1}{0}[0;106m{1}{0}[0;106m{1}{0}[0;107m{1}{0}[0;107m{1}{0}[0;107m{1}{0}[0m') -f [char]0x1B, '   '")

    console.print(f'''
                                  [bold yellow]User[/bold yellow]: [white]{computer_info.UserName}[/white]
                                  [bold yellow]Hostname[/bold yellow]: [white]{proc_info.SystemName}[/white]
                                  [bold yellow]Primary Owner Email[/bold yellow]: [white]{computer_info.PrimaryOwnerName}[/white]
                                  [bold yellow]Manufacturer[/bold yellow]: [white]{motherboard()}[/white]
[red]██████╗░░█████╗░░██████╗░██████╗[/red]  [bold yellow]Model PC[/bold yellow]: [white]{computer_info.Model}[/white]
[red]██╔══██╗██╔══██╗██╔════╝██╔════╝[/red]  [bold yellow]Model OS[/bold yellow]: [white]{model_os}[/white]
[red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]Kernel[/bold yellow]: [white]{platform.version()} {platform.machine()}[/white]
[red]██║░░██║██║░░██║╚█████╗░╚█████╗░[/red]  [bold yellow]Uptime[/bold yellow]: [white]{uptime()}[/white]
[red]██║░░██║██║░░██║╚█████╗░╚█████╗░[/red]  [bold yellow]Shell[/bold yellow]: [white]{shell}[/white]
[red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]Resolution[/bold yellow]: [white]{ctypes.windll.user32.GetSystemMetrics(0)}x{ctypes.windll.user32.GetSystemMetrics(1)}[/white]
[red]██║░░██║██║░░██║░╚═══██╗░╚═══██╗[/red]  [bold yellow]CPU[/bold yellow]: [white]{cpu} @ {proc_info.CurrentClockSpeed/1000}GHz[white]
[red]██████╔╝╚█████╔╝██████╔╝██████╔╝[/red]  [bold yellow]GPU[/bold yellow]: [white]{gpu_info.Name} {int(gpu_info.MaxRefreshRate*0.1)}GB[/white]
[red]╚═════╝░░╚════╝░╚═════╝░╚═════╝░[/red]  [bold yellow]RAM[/bold yellow]: [white]{get_size(svmem.available)}/{get_size(svmem.total)} ({round(svmem.used / svmem.total * 100, 2)}%)[/white]
                                  [bold yellow]Disk[/bold yellow]: [white]{disk_name()}[/white]
                                  [bold yellow]LAN_IP[/bold yellow]: [white]{local_ip}[/white]
                                  [bold yellow]WAN_IP[/bold yellow]: [white]{ip}[/white]
''')
    print(f'''                                  {color}
                                  {color_}
''')
except:
    ip = requests.get("https://ip.42.pl/json").text
    machine = os.popen("uname -m").read().strip()
    host = os.popen("cat /sys/devices/virtual/dmi/id/product_name").read().strip()
    host_ = os.popen("cat /sys/devices/virtual/dmi/id/product_version").read().strip()
    kernel = os.popen("uname -r").read().strip()
    resolution = os.popen("xrandr -q | grep '\*'").read().strip()
    de = os.popen("echo $XDG_CURRENT_DESKTOP").read().strip()
    shell = os.popen("$SHELL --version").read().strip()
    wm = os.popen("update-alternatives --list x-window-manager").read().strip().replace("/usr/bin/", "")
    theme = os.popen("gsettings get org.gnome.desktop.wm.preferences theme").read().strip().replace("'", "")
    wm_theme = os.popen("gsettings get org.gnome.desktop.wm.preferences theme").read().strip().replace("'", "")
    icons = os.popen("gsettings get org.gnome.desktop.interface icon-theme").read().strip().replace("'", "")
    gpu = os.popen('''
    lspci -mm |                                  
                       awk -F '\"|\" \"|\\(' \
                              '/"Display|"3D|"VGA/ {
                                  a[$0] = $1 " " $3 " " ($(NF-1) ~ /^$|^Device [[:xdigit:]]+$/ ? $4 : $(NF-1))
                              }
                              END { for (i in a) {
                                  if (!seen[a[i]]++) {
                                      sub("^[^ ]+ ", "", a[i]);
                                      print a[i]
                                  }
                              }}'
    ''').read().strip()
    console.print(f'''
                                      [bold yellow]User:[/bold yellow] [white]{getpass.getuser()}[/white]
                                      [bold yellow]Host:[/bold yellow] [white]{host} {host_}[/white]
    [red]██████╗░░█████╗░░██████╗░██████╗[/red]  [bold yellow]OS:[/bold yellow] [white]{platform.system()} {platform.release()} {machine}[/white]
    [red]██╔══██╗██╔══██╗██╔════╝██╔════╝[/red]  [bold yellow]Kernel:[/bold yellow] [white]{kernel}[/white]
    [red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]Uptime:[/bold yellow] [white]{uptime()}[/white]
    [red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]Shell:[/bold yellow] [white]{shell}[/white]
    [red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]Resolution:[/bold yellow] [white]{resolution}[/white]
    [red]██║░░██║██║░░██║╚█████╗░╚█████╗░[/red]  [bold yellow]DE:[/bold yellow] [white]{de.capitalize()}[/white]
    [red]██║░░██║██║░░██║╚█████╗░╚█████╗░[/red]  [bold yellow]WM:[/bold yellow] [white]{wm}[/white]
    [red]██║░░██║██║░░██║╚█████╗░╚█████╗░[/red]  [bold yellow]WM Theme:[/bold yellow] [white]{wm_theme}[/white]
    [red]██║░░██║██║░░██║╚█████╗░╚█████╗░[/red]  [bold yellow]Theme:[/bold yellow] [white]{wm_theme}[/white]
    [red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]Icons:[/bold yellow] [white]{icons}[/white]
    [red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]CPU:[/bold yellow] [white]{cpuinfo.get_cpu_info()['brand_raw']} @ { cpuinfo.get_cpu_info()['hz_actual_friendly']}[/white]
    [red]██║░░██║██║░░██║╚═███═╗░╚═███═╗░[/red]  [bold yellow]GPU:[/bold yellow] [white]{gpu}[/white]
    [red]██║░░██║██║░░██║░╚═══██╗░╚═══██╗[/red]  [bold yellow]RAM:[/bold yellow] [white]{get_size(svmem.available)}/{get_size(svmem.total)} ({round(svmem.used / svmem.total * 100, 2)}%)[/white]
    [red]██████╔╝╚█████╔╝██████╔╝██████╔╝[/red]  [bold yellow]Disk:[/bold yellow] [white]{disk_name()}[/white]
    [red]╚═════╝░░╚════╝░╚═════╝░╚═════╝░[/red]  [bold yellow]LAN_IP:[/bold yellow] [white]{local_ip}[/white]
                                      [bold yellow]WAN_IP:[/bold yellow] [white]{ip}[/white]
    ''')
