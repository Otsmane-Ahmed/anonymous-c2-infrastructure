import os
import shutil
from stem.control import Controller
from stem.process import launch_tor_with_config

class TorManager:
    def __init__(self, hidden_service_dir='hidden_service', tor_port=9050, ctrl_port=9051, service_port=80, target_port=5000):
        self.hidden_service_dir = os.path.abspath(hidden_service_dir)
        self.tor_port = tor_port
        self.ctrl_port = ctrl_port
        self.service_port = service_port
        self.target_port = target_port
        self.tor_process = None

    def start_tor(self):
        print("Starting Tor...")
        
        if not os.path.exists(self.hidden_service_dir):
            os.makedirs(self.hidden_service_dir, mode=0o700)
        
        
        tor_config = {
            'SocksPort': str(self.tor_port),
            'ControlPort': str(self.ctrl_port),
            'HiddenServiceDir': self.hidden_service_dir,
            'HiddenServicePort': f'{self.service_port} 127.0.0.1:{self.target_port}',
            'CookieAuthentication': '1',
            'Log': 'NOTICE stdout',
        }

        print(f"[*] Tor Config: HiddenServiceDir={self.hidden_service_dir}")

        try:
            self.tor_process = launch_tor_with_config(
                config=tor_config,
                take_ownership=True,  
                completion_percent=100
            )
            print("Tor started successfully.")
        except Exception as e:
            print(f"Error starting Tor: {e}")
            if "Process terminated" in str(e):
                print("[!] Hint: Check permissions on 'c2_hidden_service' or AppArmor logs.")
            raise

    def get_onion_address(self):
        hostname_path = os.path.join(self.hidden_service_dir, 'hostname')
        if os.path.exists(hostname_path):
            with open(hostname_path, 'r') as f:
                return f.read().strip()
        return None

    def stop_tor(self):
        if self.tor_process:
            self.tor_process.kill()
            print("Tor stopped.")
