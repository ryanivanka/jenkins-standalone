#Change Jenkins master url for new APP
#Update backup location
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import os
import sys
import paramiko
import socket

rootPath="/JenkinsBackups"
app=sys.argv[1]

HOST=sys.argv[2]
USERNAME=sys.argv[3]
PASSWD=sys.argv[4]
PORT=22

#change backup location for new App
def modifyBackupPath(path):
    tree=ET.parse("thinBackup.xml")
    root=tree.getroot()
    backupPath=root.find('backupPath')
    print "old backup path is: "+backupPath.text

    backupPath.text=path
    tree.write('tmp.xml', encoding='utf-8', xml_declaration=True)
    os.remove('thinBackup.xml')
    os.rename('tmp.xml', 'thinBackup.xml')
    print "new backup path is: "+path

# notify to update ha proxy and get port info.
def notifyUpdateHaproxy():
    try:
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=HOST, username=USERNAME, password=PASSWD, port=PORT)
        stdin, stdout, stderr = ssh.exec_command('/data/haproxy/haproxy_marathon_bridge logged refresh_system_haproxy localhost:8080')
        stdin,stdout,sterr=ssh.exec_command('cat /etc/haproxy/haproxy.cfg')

    #    appPort=10000
        outs=stdout.readlines()
        for line in outs:
            line=line.strip()
            if line.find("listen "+app+"-" ) > -1:
                print line
                ports=line.split('-')
                appPort=ports[-1]
                break
        ssh.close()
        return appPort
    except paramiko.SSHException, e:
        print "Password is invalid:" , e
    except paramiko.AuthenticationException:
        print "Authentication failed for some reason"
    except socket.error, e:
        print "Socket connection failed:", e


#update master url info
def modifyMasterURL(HOST, appPort):
    tree=ET.parse("jenkins.model.JenkinsLocationConfiguration.xml")
    root=tree.getroot()
    jenkinsURL=root.find('jenkinsUrl')
    print "old jenkins URL is :"+ jenkinsURL.text

    jenkinsURL.text="http://"+str(HOST)+":"+str(appPort)+"/"
    tree.write('tmp.xml', encoding='utf-8', xml_declaration=True)
    os.remove('jenkins.model.JenkinsLocationConfiguration.xml')
    os.rename('tmp.xml','jenkins.model.JenkinsLocationConfiguration.xml')
    print "new jenkins URL is :"+ jenkinsURL.text

def main():
    modifyBackupPath("%s/%s" %(rootPath,app))
    appPort= notifyUpdateHaproxy()
    modifyMasterURL(HOST, appPort)

if __name__=='__main__':
    main()

