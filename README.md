# jenkins-standalone
Run a Jenkins master on Apache Mesos and Marathon.

<http://rogerignazio.com/blog/scaling-jenkins-mesos-marathon>.
## APP Command
```
git clone https://github.com/XiaokunHou/jenkins-standalone
&& cd jenkins-standalone && chmod 777 fetch-baks.sh 
&& ./fetch-baks.sh username password ip folder 
&& python customize.py appname haproxy_ip username password 
&& ./jenkins-standalone.sh -z $(cat /etc/mesos/zk) -r localhost
```
Copy backups from sharefolder,
```
./fetch-baks.sh folder ip username password
```
username&password: Used to access share folder.

ip: Machine ip to store backups

Do customization on new Jenkins master
```
python customize.py appname haproxy_ip username password 
```
appname: Application name

haproxy_ip: ip info for haproxy machine

username&password: used to access haproxy machine.

**Haproxy is deprecated, Mesos DNS is the new solution.**

## Usage
`jenkins-standalone.sh` takes three arguments:

  - ZooKeeper URL (-z)
  - Redis host(-r)
  - JVM remote debug option (-dbg)

Redis is used as the broker for Logstash and the Jenkins Logstash plugin.

When copying/pasting this command into Marathon, each line should be
concatenated with `&&`, so that it only proceeds if the previous command
was successful.

Example usage:
```
git clone https://github.com/rji/jenkins-standalone
cd jenkins-standalone
./jenkins-standalone.sh -z $(cat /etc/mesos/zk) -r redis.example.com -dbg transport=dt_socket,server=y,address=8000,suspend=n
```

You can also use the Marathon API to create apps. There is an example
`jenkins-standalone.json` in the `examples/` directory.

```
curl -i -H 'Content-Type: application/json' -d @jenkins-standalone.json marathon.example.com:8080/v2/apps
```
