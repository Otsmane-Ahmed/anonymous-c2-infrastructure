from flask import Flask, request, Response
import requests
import argparse

app = Flask(__name__)

TARGET_C2 = None
TOR_PORT = 9050

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    global TARGET_C2
    if not TARGET_C2:
        return "Proxy not configured", 500
    
    url = f"{TARGET_C2}/{path}"
    
    proxies = {
        'http': f'socks5h://127.0.0.1:{TOR_PORT}',
        'https': f'socks5h://127.0.0.1:{TOR_PORT}'
    }
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            proxies=proxies
        )
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, headers)
        return response
    except Exception as e:
        return f"Proxy Error: {e}", 502

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', help='Target C2 Onion Address (e.g., http://xyz.onion)', required=True)
    parser.add_argument('--port', help='Local port to listen on', default=8080, type=int)
    parser.add_argument('--tor-port', help='Tor SOCKS port', default=9050, type=int)
    args = parser.parse_args()
    
    TARGET_C2 = args.target
    TOR_PORT = args.tor_port
    
    print(f"[*] Proxy starting on port {args.port}")
    print(f"[*] Forwarding to {TARGET_C2} via Tor port {TOR_PORT}")
    
    app.run(host='0.0.0.0', port=args.port)
