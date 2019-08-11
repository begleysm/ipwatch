# ipwatch

## Description
This program gets for your external IP address, checks it against your "saved" IP address and, if a difference is found, emails you the new IP. This is useful for servers at residential locations whose IP address may change periodically due to actions #by the ISP.

## Usage Examples
[config] = path to an IPWatch configuration file

1. `python3 ipwatch.py [config]`
2. `./ipwatch.py [config]`
3. `python3 ipwatch.py config.txt`
4. `./ipwatch.py config.txt`

## Installation
ipwatch requires Python to run.  On Debian based systems you can install python3 by running

```bash
sudo apt install python3
```

## Config File
ipwatch uses a config file to define how to send an email.  An example and description is below.  A similar config file is in the repo as example_config.txt.  You should copy it by running something like `sudo cp example_config.txt config.txt` and then modify `config.txt`. It is recommended that you adjust the permissions of your config file so that no one but you and/or root can read it since it will contain the sender email password.

```bash
sender=Bob Sender                   #this is the name of the email sender
sender_email=bobsender@gmail.com    #this is the email address the email will be sent from
sender_username=bobsender           #this is the username (in this example gmail username) of the sender
sender_password=password1           #this is the password (in this example gmail password) of the sender
receiver=Tom Receiver               #this is the name of the recipient
receiver_email=tomreceive@gmail.com #this is the email address of the recipient
subject_line=My IP Has Changed!     #this is the subject line of the sent email
machine=Test_Machine                #this is the name of the machine sending the email
smtp_addr=smtp.gmail.com:587        #this is the SMTP address for the sending email server (in this case gmail)
save_ip_path=/opt/ipwatch/oldip.txt #this is the location where the saved ip address will be stored
try_count=10                        #this defines how many times the system will try to find the current IP before exiting
ip_blacklist=192.168.0.255,192.168.0.1,192.168.1.255,192.168.1.1  #this is a list of IP address to ignore if received
```

## Cronjob
ipwatch works best when setup as a cronjob.  It assumes that you've cloned the ipwatch repo into `/opt/ipwatch` and that your config file is in the same location.  You can access root's crontab by running

```bash
sudo su
crontab -e
```
Below is an example crontab entry to run ipwatch once per hour.

```bash
00 * * * * /opt/ipwatch/ipwatch.py /opt/ipwatch/config.txt
```

If you want to/need to run the cronjob as an unprivileged use you'll have to ensure that your user has execution privileges for `ipwatch.py` and can write to the `save_ip_path` file defined in your config file.

## Gmail
If you use Gmail as your sending email service then you'll have to enable **Less secure app access** to allow ipwatch to send emails. You can read more about this at https://support.google.com/accounts/answer/6010255?hl=en.  You can enable **Less secure app access** by visiting https://myaccount.google.com/lesssecureapps.  Chances are you'll also be blocked, by Gmail, the first time you try try to send an email and will receive a **Critical security alert** saying that a **Sign-in attempt was blocked for your linked Google Account** at your recovery email/phone #.  You'll have to click the **Check activity** button and say **Yes that was me** in order to whitelist your system.

## References
The original ipgetter.py code came from https://github.com/phoemur/ipgetter.  However that repo is gone now.  This repo contains a copy of ipgetter.py file for those who need it.  I've since updated ipgetter.py to remove reference to ip servers that no longer work.

## Author
Sean Begley
begleysm@gmail.com
2019-08-10
