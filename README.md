# jenkins-standalone
Run a Jenkins master on Apache Mesos and Marathon.

<http://rogerignazio.com/blog/scaling-jenkins-mesos-marathon>.
## APP Command
```
git clone https://github.com/XiaokunHou/jenkins-standalone&& cd jenkins-standalone && chmod 777 fetch-baks.sh && ./fetch-baks.sh username password ip folder && python customize.py appname haproxy_ip username password && ./jenkins-standalone.sh -z $(cat /etc/mesos/zk) -r localhost
```

## Usage
`jenkins-standalone.sh` takes two arguments:
  - ZooKeeper URL
  - Redis host

Redis is used as the broker for Logstash and the Jenkins Logstash plugin.

When copying/pasting this command into Marathon, each line should be
concatenated with `&&`, so that it only proceeds if the previous command
was successful.

Example usage:
```
git clone https://github.com/rji/jenkins-standalone
cd jenkins-standalone
./jenkins-standalone.sh -z $(cat /etc/mesos/zk) -r redis.example.com
```

You can also use the Marathon API to create apps. There is an example
`jenkins-standalone.json` in the `examples/` directory.

```
curl -i -H 'Content-Type: application/json' -d @jenkins-standalone.json marathon.example.com:8080/v2/apps
```
