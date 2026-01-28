import paramiko
from scp import SCPClient
import os

def deploy():
    host = "villa.local"
    user = "villa"
    password = "villa03"
    remote_dir = "/home/villa/preddit"
    
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
                "server.py", "preddit.py", "README.md"
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
        print("Installing dependencies on remote...")
        ssh.exec_command("sudo apt-get update && sudo apt-get install -y python3-pip python3-yaml python3-requests python3-bs4 python3-flask")
        
        # Setup systemd
        print("Setting up systemd service...")
        commands = [
            f"sudo cp {remote_dir}/systemd/preddit.service /etc/systemd/system/",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable preddit",
            "sudo systemctl restart preddit"
        ]
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
            # Handle sudo password if prompted (though usually villa is in sudoers with nopass or we can try)
            stdin.write(password + "\n")
            stdin.flush()
            print(f"Executed: {cmd}")
            # print(stdout.read().decode())

        print("\nDeployment complete!")
        print(f"Preddit is now running on port 9191 on {host}")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
