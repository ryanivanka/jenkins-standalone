<h1>How to use Haproxy</h1>
Marathon ships with a simple shell script called haproxy_marathon_bridge that turns the Marathon's REST API's list of running tasks into a config file for HAProxy, a lightweight TCP/HTTP proxy. To generate an HAProxy configuration from Marathon running at localhost:8080, use the haproxy_marathon_bridge script:

    $ bin/haproxy_marathon_bridge localhost:8080 > haproxy.cfg
To reload the HAProxy configuration without interrupting existing connections:

    $ haproxy -f haproxy.cfg -p haproxy.pid -sf $(cat haproxy.pid)
The configuration script and reload could be triggered frequently by Cron, to keep track of topology changes. If a node goes away between reloads, HAProxy's health check will catch it and stop sending traffic to that node.

To facilitate this setup, the haproxy_marathon_bridge script can be invoked in an alternate way which installs the script itself, HAProxy and a cronjob that once a minute pings one of the Marathon servers specified and refreshes HAProxy if anything has changed.

    $ install_haproxy_system localhost:8080
The list of Marathons to ping is stored one per line in /etc/haproxy_marathon_bridge/marathons The script is installed as /usr/local/bin/haproxy_marathon_bridge The cronjob is installed as /etc/cron.d/haproxy_marathon_bridge and run as root. The provided script is just a basic example. For a full list of options, check the HAProxy configuration docs.
