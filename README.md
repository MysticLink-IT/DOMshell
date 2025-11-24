<img width="627" height="166" alt="image" src="https://github.com/user-attachments/assets/ea24f881-4387-4a68-8a0c-c5eb24a66265" />

                                                                 
# DOMshell
A Web Interface for managing Windows Servers, based on Django

D-ocument
O-bject
M-odel
SHELL

A better "Windows Admin Center" than "Windows Admin Center"

Project Status:
For now this is a hobby project of mine but anyone is welcome to test and contribute.
If this becomes more serious I will add proper release versions and documentation
<h2>Required Software</h2>
Python3
Django
PyWinrm https://github.com/diyan/pywinrm

<h2>Installation</h2>
<h3>Linux</h3>
Clone/Download the repo and run "domshell-install.sh"

<h3>Windows</h3>
Coming soon...

<h2>Set Up</h2>
The script will install the required software
You will prompted to choose an admin username and password for DB administration and user settings

<h2>Usage</h2>
1. From the DOMshell folder run:
python manage.py runserver
2. Open a web browser then go to http://localhost:8000/computers

<h2>Connecting to Remote Servers</h2>
You can enter a hostname manually from the home screen or choose one from your contact list

To save a hostname to the list using the Django DB admin, go to http://127.0.0.1:8000/admin/. Then enter the admin user and password you entered during setup. (You can reset the admin password by running "python manage.py createsuperuser" from the DOMshell folder). Under "Computers" choose 'Add' then enter the OS and hostname




Max
