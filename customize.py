#Change Jenkins master url for new APP
#Update backup location
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import os
import sys
import paramiko
import socket
import tempfile
import shutil

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
    temp=tempfile.NamedTemporaryFile()
    tree.write(temp.name, encoding='utf-8', xml_declaration=True)
    shutil.copy(temp.name,'thinBackup.xml')
    temp.close()
    print "new backup path is: "+path

# notify to update ha proxy and get master url port info.
# update the jnlp port for haproxy
def notifyUpdateHaproxy(app, jnlpPort):
    try:
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=HOST, username=USERNAME, password=PASSWD, port=PORT)

        # refresh haproxy config and find the new port for jenkins master
        stdin, stdout, stderr = ssh.exec_command('/data/haproxy/haproxy_marathon_bridge logged refresh_system_haproxy localhost:8080')
        stdin,stdout,sterr=ssh.exec_command('cat /etc/haproxy/haproxy.cfg')

        # find haproxy port and dest ip
        outs=stdout.readlines()
        appFound=False
        for line in outs:
            line=line.strip()
            if line.find("listen "+app+"-" ) > -1:
                print line
                ports=line.split('-')
                appPort=ports[-1]
                appFound=True
                continue
            if line.find('server ')>-1 and appFound==True:
                print line
                routeIP=line.strip().split(' ')[2].split(':')[0]
                break
        
        # generate the new jnlp haproxy config file
        ftp=ssh.open_sftp()
        ftp.get('/etc/haproxy/jnlp_haproxy.cfg', 'jnlp_haproxy_local.cfg')
        temp=tempfile.NamedTemporaryFile()
        infile=open('jnlp_haproxy_local.cfg', 'r+')
        infile.seek(0)
        file_content_list=infile.readlines()
        needAdd=True
        appFound=False
        for line in file_content_list:
            if line.strip().find('listen jnlp-'+app)>-1:
        #       print line.split(' ')[1:]
                appFound=True
                needAdd=False
                temp.write(line)
                continue
            if line.find(':')>-1 and appFound==True:
                line=line.strip('\n').split(':')[0]+':'+jnlpPort+'\n'
                temp.write(line)
                continue
            if line.find('listen ')>-1:
                appFound=False
            temp.write(line)
        if needAdd:
            temp.write('''
listen jnlp-%s
  bind 0.0.0.0:%s
  mode tcp
  option tcplog
  balance leastconn
  server %s %s:%s check
''' %(app,jnlpPort,app,routeIP,jnlpPort))
        temp.flush()
        shutil.copy(temp.name,'jnlp_haproxy_local.cfg')
        temp.close()
        ftp.put('jnlp_haproxy_local.cfg','/etc/haproxy/jnlp_haproxy.cfg')
        ftp.close()

        # refresh haproxy config and find the new port for jenkins master
        stdin, stdout, stderr = ssh.exec_command('/data/haproxy/haproxy_marathon_bridge logged refresh_system_haproxy localhost:8080')

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
    temp=tempfile.NamedTemporaryFile()
    tree.write(temp.name, encoding='utf-8', xml_declaration=True)
    shutil.copy(temp.name,'jenkins.model.JenkinsLocationConfiguration.xml')
    temp.close()
    print "new jenkins URL is :"+ jenkinsURL.text


#set a fixed JNLP port
def modifySlaveAgentPort():
    #read old port first
    tree=ET.parse("config.xml")
    root=tree.getroot()
    slaveAgentPort=root.find('slaveAgentPort')
    print "old slave agent port is: "+slaveAgentPort.text
    if slaveAgentPort.text!='0' and os.popen('netstat -apn | grep %s' % slaveAgentPort.text).read().strip()=="":
        return slaveAgentPort.text

    # need to find a free port.
    try:
        while True:
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=HOST, username=USERNAME, password=PASSWD, port=PORT)
            stdin, stdout, stderr = ssh.exec_command('python -c \'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()\'')
            port=stdout.read().strip()
            print 'available port is',port
            if(os.popen('netstat -apn | grep %s' % port).read().strip()==""):
                break

        slaveAgentPort.text=port
        temp=tempfile.NamedTemporaryFile()
        tree.write(temp.name, encoding='utf-8', xml_declaration=True)
        shutil.copy(temp.name, 'config.xml')
        temp.close()
        print "new slave agent port is: "+port
        return port
    except paramiko.SSHException, e:
        print "Password is invalid:" , e
    except paramiko.AuthenticationException:
        print "Authentication failed for some reason"
    except socket.error, e:
        print "Socket connection failed:", e

def main():
    modifyBackupPath("%s/%s" %(rootPath,app))
    jnlpPort=modifySlaveAgentPort()
    print "jnlp port should be", jnlpPort  
    appPort= notifyUpdateHaproxy(app, jnlpPort)
    modifyMasterURL(HOST, appPort)


if __name__=='__main__':
    main()
