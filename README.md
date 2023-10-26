# VulnGen
A Vulnerable Virtual Machine Generator that creates a virtual machine for you to practice pen-testing it, could be helpful for your OSCP certification exam.
Only tested on Windows 10 and 11, 64-bit

## Requirements
- Python 3
- Vagrant
- Oracle VM Virtualbox

## Installation
### Python 3
Make sure you are able to run python and pip command on your terminal
1. run "pip install mysql-connector-python" and "pip install requests"
2. run "pip install mysql" if required
### Vagrant and Oracle VM Virtualbox
Download the installers from their respective official websites and install them

## Usage
- Set your attacking machine's network adapter on Oracle VM Virtualbox to be Bridged Adapter to ensure its on the same local network as the generated machine
- Run with the command "python \VulnGen.py" (or the appropriate filename)
- For the first run, select SMTP for its speed and efficiency
- If it seems stuck at "default:" portion of the log, make sure to have Oracle VM Virtualbox open and the generated machine selected/highlighted. (Refer to 2nd image in Examples)

Rest of the instructions stated in the program

Step-by-step command answer key provided

## Examples
### Main Menu
![image](https://github.com/W33dIndeed/VulnGen/assets/73786469/21b6cbac-23bd-47a4-922f-49f086bd5959)
### Might stuck here or at "/boot/initrd" portion
Make sure to select/highlight it

![image](https://github.com/W33dIndeed/VulnGen/assets/73786469/cb0ffe08-ad52-4b30-a08c-9c4094bc39e3)

## Contribute
Interested in this concept? Feel free to contribute! Add more vulnerable ports and services, generate more than 1 machines for pivoting, include Windows machines, privilege escalation, etc. The sky's the limit!
