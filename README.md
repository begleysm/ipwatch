# ipwatch

Sean Begley (begleysm@gmail.com)

https://steamforge.net/wiki

https://github.com/begleysm/ipwatch

2022-04-04

## Description
This program gets your external & internal IP addresses, checks them against your "saved" IP addresses and, if a difference is found, emails you the new IP's. This is useful for servers at residential locations whose IP address may change periodically due to actions by the ISP.

## Usage Examples
[config] = path to an IPWatch configuration file

1. `python3 ipwatch.py [config]`
2. `./ipwatch.py [config]`
3. `python3 ipwatch.py config.txt`
4. `./ipwatch.py config.txt`
5. `python3 /path/to/dir/ipwatch.py /path/to/dir/config.txt`
6. `./path/to/dir/ipwatch.py /path/to/dir/config/txt`

## Installation
### Debian based Linux systems
Install python3, git, & nano by running
```bash
sudo apt install python3 git nano
```

Clone the ipwatch repo by running
```bash
sudo git clone https://github.com/begleysm/ipwatch /opt/ipwatch
```

Copy `example_config.txt` to `config.txt` by running
```bash
sudo cp /opt/ipwatch/example_config.txt /opt/ipwatch/config.txt
```

Since `config.txt` will contain an email password, make it viewable & editable by `root` only by running
```bash
sudo chmod 600 /opt/ipwatch/config.txt
```

Edit `config.txt` by running the following command and observing the instructions in the **Config File** section below.  If you're using Gmail as your sending mail service then be sure to read the **Gmail** section below.
```bash
sudo nano /opt/ipwatch/config.txt
```

You can test the setup by running
```bash
sudo python3 /opt/ipwatch/ipwatch.py /opt/ipwatch/config.txt
```
Check out the **Cronjob** section below to make this utility run on its own so that you may be quickly alerted to any IP changes on your system.

## Config File
ipwatch uses a config file to define how to send an email.  An example and description is below.  A similar config file is in the repo as example_config.txt.  You should copy it by running something like `sudo cp example_config.txt config.txt` and then modify `config.txt`. It is recommended that you adjust the permissions of your config file so that no one but you and/or root can read it since it will contain the sender email password.

```bash
sender=Bob Sender                    					#this is the name of the email sender
sender_email=bobsender@gmail.com     					#this is the email address the email will be sent from
sender_username=bobsender            					#this is the username (in this example gmail username) of the sender
sender_password=password1            					#this is the password (in this example gmail password) of the sender
receiver=Tom Receiver, Bob Receiver					#this is a comma delimited list of the names of the recipients
receiver_email=tomreceiver@gmail.com, bobreceiver@gmail.com  		#this is a comma delimited lit of the the email addresses of the recipients
subject_line=My IP Has Changed!      					#this is the subject line of the sent email
machine=Test_Machine                 					#this is the name of the machine sending the email
smtp_addr=smtp.gmail.com:587         					#this is the SMTP address for the sending email server (in this case gmail)
save_ip_path=/opt/ipwatch/oldip.txt  					#this is the location where the saved ip address will be stored
try_count=10                         					#this defines how many times the system will try to find the current IP before exiting
ip_blacklist=192.168.0.255,192.168.0.1,192.168.1.255,192.168.1.1	#this is a list of IP address to ignore if received
```

## Cronjob
ipwatch works best when setup as a cronjob.  For the following instructions I assume that you've cloned the ipwatch repo into `/opt/ipwatch` and that your config file is in the same location.  You can access root's crontab by running

```bash
sudo su
crontab -e
```
Below is an example crontab entry to run ipwatch once per hour.

```bash
00 * * * * /opt/ipwatch/ipwatch.py /opt/ipwatch/config.txt
```

If you want to/need to run the cronjob as an unprivileged user you'll have to ensure that your user has execution privileges for `ipwatch.py` and can write to the `save_ip_path` file defined in your config file.  This is probably most easily accomplished by installing *ipwatch* somewhere under your home directory.

## Gmail
### Less secure app access
If you use Gmail as your sending email service then you'll have to enable **Less secure app access** to allow ipwatch to send emails. You can read more about this at https://support.google.com/accounts/answer/6010255.  You can enable **Less secure app access** by visiting https://myaccount.google.com/lesssecureapps.
### Critical security alert
Chances are you'll also be blocked, by Gmail, the first time you try try to send an email and will receive a **Critical security alert** saying that a **Sign-in attempt was blocked for your linked Google Account** at your recovery email/phone #.  You'll have to click the **Check activity** button and say **Yes that was me** in order to whitelist the *ipwatch* machine.
### 2-Step Verification
If you use **2-Step Verification** with Gmail then you'll need configure your Gmail account to **Sign in with App Passwords** which you can learn more about by visiting https://support.google.com/accounts/answer/185833.

## Server List
The server list is hosted in this github repo as `servers.json`.  Locally, there is a cached copy kept which will be re-retrieved from github every 90 days.

## References
The original ipgetter.py code came from https://github.com/phoemur/ipgetter.  However that repo is gone now.  This repo contains an updated copy of the ipgetter.py file that has been modified to further support ipwatch.

## Thanks
1. Thanks to TheFlyingBadger for adding in support for the GitHub hosted servers.json file.
2. Thanks to pjuster for providing info on Gmail 2-Step Verification.
3. Thanks to carolmanderson for adding in support for monitoring local IP.
