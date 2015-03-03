#Change Jenkins master url for new APP
#Change backup location for new APP

#Read APP info first.
from xml.dom import minidom
doc=minidom.parse("thinBackup.xml")
root=doc.documentElement
backupPath=root.getElementsByTagName('backupPath')
print("backup path is,", backupPath.nodeValue )