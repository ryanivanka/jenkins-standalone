#Change Jenkins master url for new APP


#Read APP info first.
import xml.etree.ElementTree as ET
import os
import sys

path=sys.argv[1]
#change backup location for new App
def modifyBackupPath(path):
    tree=ET.parse("thinBackup.xml")
    root=tree.getroot()
    backupPath=root.find('backupPath')
    print "backup path is: "+backupPath.text

    backupPath.text=path
    tree.write('tmp.xml')
    os.remove('thinBackup.xml')
    os.rename('tmp.xml', 'thinBackup.xml')

def main():
    modifyBackupPath(path)

if __name__=='__main__':
    main()
