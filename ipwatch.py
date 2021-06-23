#!//usr/bin/env python3

#USAGE: python3 ipwatch.py [config]
#USAGE: ./ipwatch.py [config]
#
#[config] = path to an IPWatch configuration file
#
#Sean Begley
#2021-06-23
# v0.8
#
#This program gets for your external IP address
#checks it against your "saved" IP address and,
#if a difference is found, emails you the new IP.
#This is useful for servers at residential locations
#whose IP address may change periodically due to actions
#by the ISP.

#REFERENCES
#https://github.com/phoemur/ipgetter

import sys
from pathlib import Path
import re
import smtplib
import ipgetter


################
### CLASSES ####
################

#container for config file information
class ConfigInfo:
    "This class contains all of the information from the config file"
    sender = ""
    sender_email = ""
    sender_username = ""
    sender_password = ""
    receiver = []
    receiver_email = []
    subject_line = ""
    machine = ""
    smtp_addr = ""
    save_ip_path = ""
    try_count = ""

    def __init__(self):
        self.sender = ""
        self.sender_email = ""
        self.sender_username = ""
        self.sender_password = ""
        self.receiver = []
        self.receiver_email = []
        self.subject_line = ""
        self.machine = ""
        self.smtp_addr = ""
        self.save_ip_path = ""
        self.try_count = ""


################
## FUNCTIONS ###
################

#help message print
def printhelp():
    "Function to print out the help message"
    print("""\r\nIPWatch v0.5 by Sean Begley (begleysm@gmail.com)

IPWatch is a tool to check your current external IP address against a saved, previous, external IP address.  It should be run as a scheduled task/cronjob periodically.  If a difference in the new vs old IP address is found it will dispatch an email describing the change.

USAGE: python3 ipwatch.py [config]
USAGE: ./ipwatch.py [config]

[config] = path to an IPWatch configuration file

EXAMPLE USAGE: ./ipwatch.py /home/bob/ipwatch/config.txt
""")
    return

#read config file
def readconfig(filepath,  configObj):
    "Function to read a config file with email information"
    #check if the configfile exists
    if Path(filepath).is_file():
        #open configfile
        configfile = open(filepath, "r")

        #read out the contents
        lines = configfile.readlines()

        #parse the contents
        for line in lines:
            #ignore comments and blank lines
            if (line[:1] != "#" and line.strip()):
                #remove trailing whitespace and newline chars
                line = line.rstrip()
                param = line.rpartition('=')[0]
                value = line.rpartition('=')[2]
                #print ("param = %s\t\tvalue = %s" % (param, value))

                #save parameters in configObj
                if (param == "sender"):
                    configObj.sender = value
                elif (param == "sender_email"):
                    configObj.sender_email = value
                elif (param == "sender_username"):
                    configObj.sender_username = value
                elif (param == "sender_password"):
                    configObj.sender_password = value
                elif (param == "receiver"):
                    #get string of receivers, split into a list, strip leading spaces if present
                    configObj.receiver = value.split(",")
                    for i, item in enumerate(configObj.receiver):
                        configObj.receiver[i] = item.lstrip()
                elif (param == "receiver_email"):
                    #get string of receiver emails, split into a list, strip leading spaces if present
                    configObj.receiver_email = value.split(",")
                    for i, item in enumerate(configObj.receiver_email):
                        configObj.receiver_email[i] = item.lstrip()
                elif (param == "subject_line"):
                    configObj.subject_line = value
                elif (param == "machine"):
                    configObj.machine = value
                elif (param == "smtp_addr"):
                    configObj.smtp_addr = value
                elif (param == "save_ip_path"):
                    configObj.save_ip_path = value
                elif (param == "try_count"):
                    configObj.try_count = value
                elif (param == "ip_blacklist"):
                    configObj.ip_blacklist = value.split(',')
                else:
                    print ("ERROR: unexpected line found in config file: %s" % line)
                    configfile.close()
                    return "badline"

        #print (configObj.sender)
        #print (configObj.sender_email)
        #print (configObj.sender_username)
        #print (configObj.sender_password)
        #print (configObj.receiver)
        #print (configObj.receiver_email)
        #print (configObj.subject_line)
        #print (configObj.machine)
        #print (configObj.smtp_addr)
        #print (configObj.save_ip_path)
        #print (configObj.try_count)
        #print (configObj.ip_blacklist)

        #close the file
        configfile.close()
        return 0

    else:
        print ("ERROR: config file not found")
        return "nofile"

#return the current external IP address
def getip(try_count, blacklist):
    "Function to return the current, external, IP address"
    good_ip = 0
    counter = 0
    pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    
    #try up to config.try_count servers for an IP
    while(good_ip == 0) and(counter < try_count):
        
        #get an IP
        currip,server = ipgetter.myip()
        
        #check to see that it has a ###.###.###.### format
        if pattern.match(currip) and currip not in blacklist:
            good_ip = 1
            print ("GetIP: Try %d: Good IP: %s" % (counter+1, currip))
        else:
            if currip in blacklist:
                print ("GetIP: Try %d:  Bad IP (in Blacklist): %s" % (counter+1, currip))
            else:
                print ("GetIP: Try %d:  Bad IP    (malformed): %s" % (counter+1, currip))
        
        #increment the counter
        counter = counter + 1
        
    #print ("My IP = %s\r\n" % currip)
    #print ("Server used = %s\r\n" % server)
    return currip,server

#get old IP address
def getoldip(filepath):
    "Function to get the old ip address from savefile"
    #check if the savefile exists
    if Path(filepath).is_file():
        #open savefile
        savefile = open(filepath, "r")

        #check if the content of savefile makes sense
        oldip = savefile.read(15).rstrip()
        pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        if (pattern.match(oldip)):
            savefile.close()
            return oldip
            #print ("oldip = %s\r\n" % oldip)
        else:
            savefile.close()
            return "malformed"
            #print ("malformed IP or empty file: ignoring\r\n")
    else:
        return "nofile"
        #print ("file doesn't exist\r\n")

#write the new IP address to file
def updateoldip(filepath,  newip):
    "Function to update the old ip address from savefile"
    #open savefile
    savefile = open(filepath, "w")

    #write new ip
    savefile.write(newip)
    savefile.close()

#send mail with new IP address
def sendmail(oldip,  newip,  server, sender, sender_email, receivers, receiver_emails, username, password, subject,  machine,  smtp_addr):
    "Function to send an email with the new IP address"
    
    messages = [None]*len(receiver_emails)
    error_flag = 0

    for i in range(len(receiver_emails)):
        #print(str(i) + ": receiver = " + receivers[i] + "\t\t receiver email = " + receiver_emails[i])
        
        messages[i] = ("""From: """ + sender + """ <"""+ sender_email + """>
To: """ + receivers[i] + """ <""" + receiver_emails[i] + """>
Subject: """ + subject + """
Mime-Version: 1.0
Content-Type: text/plain; charset=us-ascii
Content-Transfer-Encoding: 7bit

The IP address of """ + machine + """ has changed:
    Old IP = """ + oldip + """\r\n    New IP = """ + newip + """\r\n\r\nThe Server queried was """ + server)

        #print (messages)
        #print (smtp_addr)
        #print (username)
        #print (password)
        #print (sender)
        #print (receiver_emails)
        #print (message)
        try:
            smtpObj = smtplib.SMTP(smtp_addr)
            smtpObj.starttls()
            smtpObj.login(username, password)
            smtpObj.ehlo(name=machine)
            smtpObj.sendmail(sender_email, receiver_emails[i], messages[i])
            smtpObj.quit()
            print ("Successfully sent email " + str(i+1) + " of " + str(len(receiver_emails)) + " to " + receiver_emails[i])
        except:
            print ("ERROR: unable to send email " + str(i+1) + " of " + str(len(receiver_emails)) + " to " + receiver_emails[i])
            error_flag = 1
    
    if (error_flag == 1):
        return 1
    else:
        return 0


################
##### MAIN #####
################

#parse arguments
if (len(sys.argv) != 2):
    printhelp()
    #print ("len = %d\r\n" % len(sys.argv))
else:
    config_path = str(sys.argv[1])
    #print ("email = %s" % email)
    #print ("machine = %s" % machine)
    #print ("savefile = %s" % savefile_path)

    #parse config file
    config = ConfigInfo()
    rc_ret = readconfig(config_path, config)
    if (rc_ret == "nofile"):
        sys.exit(1)
    elif (rc_ret == "badline"):
        sys.exit(2)

    #print (config.sender)
    #print (config.sender_email)
    #print (config.sender_username)
    #print (config.sender_password)
    #print (config.receiver)
    #print (config.receiver_email)
    #print (config.subject_line)
    #print (config.machine)
    #print (config.smtp_addr)
    #print (config.save_ip_path)

    #get the old ip address
    oldip = getoldip(config.save_ip_path)
    #print ("Old IP = %s" % oldip)

    #get current, external, IP address
    currip,server = getip(int(config.try_count), config.ip_blacklist)
    #print ("Curr IP = %s" % currip)
    #print ("Server used = %s" % server)

    #check to see if the IP address has changed
    if (currip != oldip):
        #send email
        print ("Current IP differs from old IP.")
        sm_ret = sendmail(oldip,  currip,  server, config.sender, config.sender_email, config.receiver, config.receiver_email, config.sender_username, config.sender_password, config.subject_line,  config.machine,  config.smtp_addr)

        # only update the file if the email was successfully sent
        if (sm_ret == 0):
            #update file
            updateoldip(config.save_ip_path,  currip)
            print ("Saved IP address updated.")
        else:
            print ("Saved IP address NOT updated.")

    else:
        print ("Current IP = Old IP.  No need to send email.")
    
    sys.exit(0)



