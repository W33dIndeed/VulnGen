import subprocess
import os
import mysql.connector # Requires pip install
import requests # Requires pip install
import zipfile
import random
import sys
import time
import string

def generate_flag():
    flag = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    generated_flags.append(flag)
    return flag

def generate_string(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def get_user_selection(): # Define the available services and their corresponding packages
    global selections
    services = {
        "FTP (exploit)": "vsftpd-ex",
        "FTP (misconfig)": "vsftpd-mis",
        "SMTP": "postfix",
        "SMB (exploit)": "samba-ex",
        "SMB (misconfig)": "samba-mis",
        "NFS (misconfig)": "nfs-kernel-server",
        "POP3 (misconfig)": "dovecot-pop3d",
        "MySQL (misconfig)": "mysql-server"
    }

    while True:
        print("Which services would you like to install? (Choose only 1 if its the same service type)")
        for i, service in enumerate(services):
            print(f"{i+1}. {service}")
        print("Q. Quit")
        selections = input("Enter the numbers of the services you would like to install (comma-separated) or 'R' for random services: ").strip()

        if selections.upper() == "Q":
            exit()

        if selections.upper() == "R":
            num_random_services = 3
            available_services = list(services.values())

            # Ensure services are unique
            unique_selected_services = []
            for _ in range(num_random_services):
                service = random.choice(available_services)
                available_services = [s for s in available_services if not s.startswith(service.split('-')[0])]
                unique_selected_services.append(service)

            return unique_selected_services

        try:
            selected_indices = [int(i) for i in selections.split(",")]
            selected_services = []

            for index in selected_indices:
                service = services[list(services.keys())[index - 1]]
                exploit_version = service.replace("-mis", "-ex")
                if exploit_version in selected_services:
                    print("You can't select both the exploit and misconfig versions of the same service.")
                    break

                if exploit_version not in selected_services:
                    selected_services.append(service)

            else:
                return selected_services

        except (ValueError, IndexError):
            print("Invalid input. Please enter valid numbers separated by commas or 'R' for random services.")

generated_flags = []
selected_services = get_user_selection()

# Define base shell script
shell_script = """
#!/bin/bash
sudo apt update -y
sudo apt upgrade -y
sudo apt install net-tools build-essential unzip curl vim -y
"""

# Add selected services to base shell script
for service in selected_services:
    if service == "vsftpd-ex":
        # Update vsftpd_url whenever necessary (version 2.3.4)
        vsftpd_url = "https://github.com/nikdubois/vsftpd-2.3.4-infected/archive/refs/heads/vsftpd_original.zip"
        vsftpd_zip_path = "/tmp/vsftpd.zip"
        vsftpd_extract_path = "/tmp/vsftpd"
        flag1 = generate_flag()
                
        shell_script += f"""
wget -O {vsftpd_zip_path} {vsftpd_url}
unzip {vsftpd_zip_path} -d {vsftpd_extract_path}

sudo apt-get install -y libssl-dev libpam0g-dev libwrap0-dev
cd {vsftpd_extract_path}/vsftpd-2.3.4-infected-vsftpd_original
sudo chmod 777 ./
sudo chmod 777 Makefile
sudo chmod +x vsf_findlibs.sh
sudo sed -i 's|LIBS\s*=.*|LIBS = `./vsf_findlibs.sh` -lcrypt -lpam|' Makefile
sudo make
sudo cp vsftpd /usr/local/sbin/
sudo sed -i 's/#anonymous_enable=YES/anonymous_enable=YES/' vsftpd.conf
sudo sed -i 's/#local_enable=YES/local_enable=YES/' vsftpd.conf
sudo cp vsftpd.conf /etc/
sudo mkdir /usr/share/empty/
sudo mkdir /var/ftp/
sudo useradd -d /var/ftp ftp
sudo /usr/local/sbin/vsftpd &
sudo mkdir /var/ftp/98t34hutrwe9g8n
sudo chmod 777 /var/ftp/98t34hutrwe9g8n
sudo echo "Good that you checked here, but the flag is deeper somewhere else!" > /var/ftp/98t34hutrwe9g8n/flag.txt
sudo echo "FLAG:{flag1}" > /root/VSFTPDflag.txt

"""

    elif service == "vsftpd-mis":
        flag2 = generate_flag()
        
        shell_script += "\n".join([
        f"sudo apt-get install -y vsftpd",
        "sudo sed -i 's/anonymous_enable=NO/anonymous_enable=YES/g' /etc/vsftpd.conf",
        "sudo sed -i 's/#write_enable=YES/write_enable=YES/g' /etc/vsftpd.conf",
        "sudo sed -i 's/#anon_upload_enable=YES/anon_upload_enable=YES/g' /etc/vsftpd.conf",
        "sudo sed -i 's/#anon_mkdir_write_enable=YES/anon_mkdir_write_enable=YES/g' /etc/vsftpd.conf",
        "sudo chmod 755 /srv/ftp",
        "sudo echo 'local_umask=002' | sudo tee -a /etc/vsftpd.conf",
        "sudo echo 'anon_umask=002' | sudo tee -a /etc/vsftpd.conf",
        "sudo systemctl restart vsftpd.service",

        # Create a directory for uploaded scripts
        "sudo mkdir /srv/ftp/web",
        "sudo chmod 777 /srv/ftp/web",
        "sudo chown -R www-data:www-data /srv/ftp/web",
        "sudo apt-get install -y apache2",
        "sudo apt-get install -y php libapache2-mod-php",
        "sudo systemctl restart apache2",

        # Remove default site if needed
        "sudo a2dissite 000-default.conf",

        # Create a new site configuration for FTP
        "echo -e '<VirtualHost *:80>\n\tDocumentRoot /srv/ftp/web\n\t<Directory /srv/ftp/web>\n\t\tOptions +ExecCGI\n\t\tAddHandler cgi-script .cgi .pl .py .php\n\t\tAllowOverride None\n\t\tRequire all granted\n\t</Directory>\n</VirtualHost>'| sudo tee /etc/apache2/sites-available/mysite.conf",
        "sudo a2ensite mysite.conf",
        "sudo cp /var/www/html/index.html /srv/ftp/web/index.html",
        "sudo systemctl restart apache2",
        f"sudo echo 'FLAG:{flag2}' > /FTPflag.txt",
        ])
        
    elif service == "postfix":
        shell_script += "\n".join([
        "sudo debconf-set-selections <<< 'postfix postfix/mailname string coolsite.com'",
        "sudo debconf-set-selections <<< 'postfix postfix/main_mailer_type string Internet Site'",
        "sudo apt-get -y install postfix mailutils",
        "sudo service postfix restart",
        "sudo useradd administrator --shell /sbin/nologin",
        "sudo postconf -e 'smtpd_expansion_filter = expn,verify'",
        "sudo service postfix restart",
        "echo 'administrator@coolsite.com administrator' | sudo tee -a /etc/postfix/virtual",
        "sudo postmap /etc/postfix/virtual",
        "sudo service postfix restart"
        ])

    elif service == "samba-ex":
    # Update samba_url whenever necessary (version 4.5.9)
        samba_url = "https://download.samba.org/pub/samba/stable/samba-4.5.9.tar.gz"
        samba_tar_path = "/tmp/samba-4.5.9.tar.gz"
        flag3 = generate_flag()
        
        shell_script += f"""
sudo apt-get install python-dev -y
wget -O {samba_tar_path} {samba_url}
cd /tmp
sudo tar -xzf samba-4.5.9.tar.gz
cd /tmp/samba-4.5.9
sudo ./configure --without-ad-dc --without-acl-support --without-ldap --without-ads
sudo make
sudo make install
sudo cp /usr/local/samba/sbin/smbd /usr/local/samba/sbin/nmbd /usr/local/samba/sbin/winbindd /usr/sbin/
sudo mkdir -p /var/run/samba
sudo touch /etc/printcap
sudo mkdir /root/smbshare
sudo chmod 777 /root/smbshare
"""

    # Configure smb.conf for EternalRed exploit
        smb_conf = """
[global]
   map to guest = Bad User
   server min protocol = NT1
   nt pipe support = yes
   nt status support = yes
   allow trusted domains = no
   null passwords = yes
   guest account = root
   smb encrypt = disabled
   server signing = mandatory
   min protocol = NT1
   max protocol = SMB2
   ntlm auth = yes
   client lanman auth = yes
[smbshare]
    comment = SMB_SHARE
    path = /root/smbshare
    browseable = yes
    writable = yes
    guest ok = yes
"""

        shell_script += f"""
echo '{smb_conf}' | sudo tee /usr/local/samba/etc/smb.conf
sudo smbd start
sudo nmbd start
sudo echo "FLAG:{flag3}" > /root/SMBflag.txt
"""

    elif service == "samba-mis":
        flag4 = generate_flag()
        
        shell_script += "\n".join([
        "sudo apt-get install -y samba",
        "sudo cp /usr/share/samba/smb.conf /etc/samba/smb.conf",
        "sudo echo '[Anonymous]\npath = /srv/samba/anonymous\nguest ok = yes\nread only = yes\nbrowseable = yes\nforce user = nobody\nforce group = nogroup' | sudo tee -a /etc/samba/smb.conf",
        "sudo mkdir -p /srv/samba/anonymous",
        "sudo chown -R nobody:nogroup /srv/samba/anonymous/",
        "sudo chmod -R 777 /srv/samba/anonymous/",
        "sudo systemctl restart smbd.service",
        "sudo echo 'Useful information might be here like usernames and credentials' > /srv/samba/anonymous/secret.txt",
        f"sudo echo 'FLAG:{flag4}' > /srv/samba/anonymous/SMBflag.txt"
    ])

    elif service == "nfs-kernel-server":
        flag5 = generate_flag()
        
        shell_script += "\n".join([
        f"sudo apt-get install -y {service}",
        "sudo mkdir /var/nfs_share",
        "sudo chown nobody:nogroup /var/nfs_share",
        "sudo chmod 777 /var/nfs_share",
        "sudo echo '/var/nfs_share *(rw,sync,no_subtree_check,no_root_squash)' | sudo tee -a /etc/exports",
        "sudo systemctl restart nfs-kernel-server",
        "sudo echo 'Useful information might be here like usernames and credentials' > /var/nfs_share/secret.txt",
        f"sudo echo 'FLAG:{flag5}' > /var/nfs_share/NFSflag.txt"
    ])

    elif service == "dovecot-pop3d":
        username = generate_string(12)
        flag6 = generate_flag()
        
        shell_script += "\n".join([
        "sudo apt-get install -y dovecot-imapd dovecot-pop3d",
        "sudo echo 'disable_plaintext_auth = no' | sudo tee -a /etc/dovecot/conf.d/10-auth.conf",
        "sudo useradd -m admin",
        "sudo echo 'admin:princesa' | sudo chpasswd",
        f"sudo useradd -m {username}",
        f"sudo echo '{username}:password' | sudo chpasswd",
        "sudo touch /var/mail/admin",
        f"sudo -u admin echo 'From boss@bigcompany.com Mon Sep 19 14:36:14 2021\nSubject: Delete this user please\n\nWhy is there a user \"{username}\" with password as password?\n\nAdmin please delete him as soon as possible' >> /var/mail/admin",  # Add a mail
        f"sudo touch /var/mail/{username}",
        f"sudo -u {username} echo 'From hackerman@anonymous.com Mon Sep 11 19:11:15 2021\nSubject: SECRET\n\nFLAG:{flag6}' >> /var/mail/{username}",
        "sudo chown admin:mail /var/mail/admin",
        "sudo chmod 660 /var/mail/admin",
        f"sudo chown {username}:mail /var/mail/{username}",
        f"sudo chmod 660 /var/mail/{username}",
        "sudo systemctl restart dovecot.service"
        ])

    elif service == "mysql-server":
        pw = generate_string(20)
        flag7 = generate_flag()
        
        shell_script += "\n".join([
        f"sudo apt-get install -y {service}",
        "sudo sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf",
        "sudo sed -i '/^\[mysqld\]/a secure_file_priv = \"\"' /etc/mysql/mysql.conf.d/mysqld.cnf",
        "sudo systemctl restart mysql.service",
        f"""sudo tee /tmp/setup.sql <<EOF
CREATE DATABASE users;
USE users;
CREATE TABLE credentials (
    username VARCHAR(50),
    password VARCHAR(50)
    );
INSERT INTO credentials (username, password) VALUES
    ('admin', '{pw}'),
    ('Crangis', 'impractical'),
    ('Mcbasketball', 'jokers');
CREATE DATABASE hidden;
USE hidden;
CREATE TABLE secret (
    FLAG VARCHAR(50)
    );
INSERT INTO secret (FLAG) VALUES
    ('{flag7}');
CREATE USER 'admin'@'%' IDENTIFIED WITH mysql_native_password BY '{pw}';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';
GRANT SELECT ON hidden.* TO 'admin'@'%';
FLUSH PRIVILEGES;
CREATE USER ''@'%' IDENTIFIED BY '';
GRANT USAGE ON *.* TO ''@'%';
GRANT SELECT ON users.* TO ''@'%';
FLUSH PRIVILEGES;
EOF""",
        "sudo mysql < /tmp/setup.sql",
        "sudo rm /tmp/setup.sql",
        "sudo systemctl restart mysql.service"
        ])
        
    # Add a separator between each service's installation commands
    shell_script += "\n\n"

# Define the base box and CPU/Memory settings
base_box = "bento/ubuntu-18.04"
cpu_count = 2
memory_size = 2048

with open("install_services.sh", "w") as f:
    f.write(shell_script)

# Generate the Vagrantfile
vagrantfile = f"""
Vagrant.configure("2") do |config|
  
  config.vm.box = "{base_box}"

  config.vm.network "public_network"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "{memory_size}"
    vb.cpus = "{cpu_count}"
  end

  config.vm.provision "shell", path: "install_services.sh"
end
"""

# Write the Vagrantfile to disk
with open("Vagrantfile", "w") as f:
    f.write(vagrantfile)

log_file = "generation_log.txt"

print("Generating your virtual machine...(IMPORTANT: Remember to keep your Oracle VM VirtualBox Manager opened with the generated machine selected during this process)")
print("Note: For SMTP, there will be no flags for you to submit")

with open(log_file, "w") as log:
    if "R" in selections.upper() or "8" in selections:
        print("Logs piped to 'generation_log.txt' to hide services used or MySQL details")
        subprocess.run(["vagrant", "up"], stdin=subprocess.PIPE, stdout=log, stderr=log)
    else:
        subprocess.run(["vagrant", "up"], stdin=subprocess.PIPE)

# Get the IP address of eth1 from the guest machine
get_ip_command = ["vagrant", "ssh", "-c", "hostname -I | awk '{print $2}'"]
ip_output = subprocess.run(get_ip_command, capture_output=True, text=True)
ip_address = ip_output.stdout.strip()

# Print the IP address
print(f"Target machine IP address: {ip_address}")
print("Use 'vagrant destroy' to delete the generated virtual machine")

"""Uncomment the line below to see flags"""
#print(generated_flags)

# Flag submission
def validate_flag():
    while generated_flags:
        user_input = input("Submit the flag you found here one by one in any order, no need to include 'FLAG:', only the string after (type 'quit' to exit): ").strip()

        if user_input.lower() == "quit":
            confirm_quit = input("Are you sure you want to quit this program? The virtual machine will still be running. (yes/no): ").strip().lower()
            if confirm_quit == "yes":
                print("Exiting program. Use 'vagrant destroy' to delete the generated virtual machine")
                return None 
        elif user_input in generated_flags:
            print("Correct flag submitted. Good job!")
            generated_flags.remove(user_input)
        else:
            print("Incorrect flag. Please try again.")

    print("No more flags needed for submission. Use 'vagrant destroy' to delete the generated virtual machine")

validate_flag()
