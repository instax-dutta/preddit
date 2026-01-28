import paramiko
from scp import SCPClient
import os
import sys

def deploy():
    # Load from environment or prompt user
    host = os.getenv("PREDDIT_HOST") or input("Enter remote host (e.g. 192.168.1.10): ")
    user = os.getenv("PREDDIT_USER") or input("Enter SSH username: ")
    password = os.getenv("PREDDIT_PASS") or input("Enter SSH password: ")
    remote_dir = os.getenv("PREDDIT_DIR") or f"/home/{user}/preddit"
    
    if not host or not user or not password:
        print("Error: Host, user, and password are required for deployment.")
        sys.exit(1)

    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected!")
        
        # Create remote directories
        ssh.exec_command(f"mkdir -p {remote_dir}/templates {remote_dir}/systemd")
        
        # Transfer files
        with SCPClient(ssh.get_transport()) as scp:
            print("Transferring files...")
            files_to_transfer = [
                "config.yaml", "database.py", "fetcher.py", 
                "server.py", "preddit.py", "README.md", "requirements.txt"
            ]
            for f in files_to_transfer:
                if os.path.exists(f):
                    scp.put(f, f"{remote_dir}/{f}")
            
            # Transfer templates
            scp.put("templates/index.html", f"{remote_dir}/templates/index.html")
            scp.put("templates/subreddit.html", f"{remote_dir}/templates/subreddit.html")
            
            # Transfer service file
            scp.put("systemd/preddit.service", f"{remote_dir}/systemd/preddit.service")

        print("Files transferred.")
        
        # Install dependencies on remote
        print("Checking remote dependencies...")
        ssh.exec_command("sudo apt-get update && sudo apt-get install -y python3-pip python3-yaml python3-requests python3-bs4 python3-flask")
        
        # Cleanup cache
        print("Cleaning remote cache...")
        ssh.exec_command(f"find {remote_dir} -name '__pycache__' -exec rm -rf {{}} +")

        # Setup systemd
        print("Configuring systemd service...")
        commands = [
            f"sudo cp {remote_dir}/systemd/preddit.service /etc/systemd/system/",
            "sudo systemctl daemon-reload",
            "sudo systemctl stop preddit",
            "sudo pkill -f preddit.py || true",
            "sudo systemctl enable preddit",
            "sudo systemctl start preddit"
        ]
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
            # Handle sudo password if prompted
            stdin.write(password + "\n")
            stdin.flush()
            print(f"Executed: {cmd}")

        print("\nDeployment complete!")
        print(f"Preddit is now running on {host}")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
