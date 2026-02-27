# RasbyBOT
How to create your own chatbot with a Raspberry Pi 4, using a Gemini API
For this you need:
- Raspberry Pi 4 (works for Pi 5)
- USB or SD card with at least 4 GB of RAM
- An audio device (speakers)
- A USB microphone
# Install Raspberry software
For this we need to install the Raspberry Pi software so we can download the OS to an SD card or USB drive
https://www.raspberrypi.com/software/

1) Connect your USB or SD card to your PC or laptop, open the Raspbian software, select your Raspberry Pi model, then select "Raspberry Pi 4 Lite (64-bit)". This is very useful if you have a low-power Raspbian.

2) Select your USB or SD card, then go to user configuration. For this, just give it an easy-to-remember name (for example, "rasby"). Add your password (important!), select your location, time zone, and keyboard.

3) To configure Wi-Fi, you must add your Wi-Fi name exactly as it appears, including spaces, capital letters, etc. Enter the password twice, then enable the SSH option (important!) and select "Connect via password." Optionally, you can enable Raspberry Pi Connect.

# Programs
I am using 3 external programs to carry out the project:

**MobaXterm** (SSH connection)
https://mobaxterm.mobatek.net/download.html

**IP Advanced Scanner** (to locate the Raspbian IP address)
https://www.advanced-ip-scanner.com/es/download/

**RealVNC** (virtual interface)
https://www.realvnc.com/es/?lai_vid=krB6gaW5kHqzD&lai_sr=0-4&lai_sl=l

# Steps to follow

1) After connecting the USB or SD card to your Raspberry Pi, turn it on and wait a few minutes. Then open the command prompt (cmd) and type "ipconfig". You need to know your IPv4 address, so open "IP Advanced Scanner". In the search field, enter the first three octets of your IPv4 address. For example, if your IP address is "192.168.0.10", you should enter "192.168.0.0-254". Then click "Scan". The name of our Raspberry Pi manufacturer must appear, for example "Raspberry Pi Trading Ltd" so we know which one it is.

2) After finding out the IP address of our Raspberry Pi, we must open "mobaxterm". Create a new SSH session and enter only the Raspberry Pi's IP address. It will then start and ask for "login as:" Enter the name we assigned, for example, "rasby", and then it will ask for the password. Once entered, it should start and exit, for example, "rasby@raspberrypi:~$"

3) Once inside the interface, we need to enter these commands:
```
sudo apt update
sudo apt upgrade
```
(it will then ask you to accept, you must use Y)

**Install a Firewall for the Raspberry Pi**
```
sudo apt install ufw
sudo ufw allow ssh
sudo ufw enable
```
**Install Python and Pip**
(Create Python Virtual Environment in the home directory) 
```
sudo apt install python3 python3-pip python3-venv
python3 -m venv .venv
```
**Create a Project Folder**
```
mkdir projects
cd projects
mkdir va
cd va 
```
**Activate Python Virtual Environment**
```
source ~/.venv/bin/activate
```
**Install Python Packages**
```
pip install speechrecognition sounddevice pyaudio
pip install -q -U google-generativeai
pip install gtts pygame gpiozero lgpio
```

**Run the Python Code**
```
python rasby.py
```
Press "Ctrl + C" on your keyboard to exit from a running Python program.




