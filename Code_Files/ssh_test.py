import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    print("creating connection")
    ssh.connect("137.112.203.157", username="pi", password="Armold")
    print("connected")
    ssh.exec_command("touch Armold/Code_Files/ssh_works.txt")
finally:
    print("closing connection")
    ssh.close()
    print("closed")