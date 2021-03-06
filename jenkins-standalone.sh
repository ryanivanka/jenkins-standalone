#!/bin/bash
set -e

# $JENKINS_VERSION should be an LTS release
JENKINS_VERSION="1.580.2"

# List of Jenkins plugins, in the format "${PLUGIN_NAME}/${PLUGIN_VERSION}"
JENKINS_PLUGINS=(
)

JENKINS_WAR_MIRROR="http://mirrors.jenkins-ci.org/war-stable"
JENKINS_PLUGINS_MIRROR="http://mirrors.jenkins-ci.org/plugins"

# Ensure we have an accessible wget
command -v wget > /dev/null
if [[ $? != 0 ]]; then
    echo "Error: wget not found in \$PATH"
    echo
    exit 1
fi

# Accept ZooKeeper paths on the command line
if [[ ! $# > 3 ]]; then
    echo "Usage: $0 -z zk://10.132.188.212:2181[, ... ]/mesos -r redis.example.com"
    echo
    exit 1
fi

while [[ $# > 1 ]]; do
    key="$1"
    shift
    case $key in
        -z|--zookeeper)
            ZOOKEEPER_PATHS="$1"
            echo "Get zookeeper=$1"
            shift
            ;;
        -r|--redis-host)
            REDIS_HOST="$1"
            echo "Get redis_host=$1"
            shift
            ;;
        -dbg|--debug)
            JVM_DEBUG="$1"
            echo "Get jvm_debug_options=$1"
            shift
            ;;
        *)
            echo "Unknown option: ${key}"
            exit 1
            ;;
    esac
done

# Jenkins WAR file
if [[ ! -f "jenkins${JENKINS_VERSION}.war" ]]; then
    echo "start wget jenkins.war..."
    wget -nc "${JENKINS_WAR_MIRROR}/${JENKINS_VERSION}/jenkins.war"
    echo "finish wget jenkins.war"
fi

# Jenkins plugins
echo "jenkins plugin is in plugin folder by default"
#[[ ! -d "plugins" ]] && mkdir "plugins"
#for plugin in ${JENKINS_PLUGINS[@]}; do
#    IFS='/' read -a plugin_info <<< "${plugin}"
#    plugin_path="${plugin_info[0]}/${plugin_info[1]}/${plugin_info[0]}.hpi"
#    wget -nc -P plugins "${JENKINS_PLUGINS_MIRROR}/${plugin_path}"
#done

# Jenkins config files
sed -i "s!_MAGIC_ZOOKEEPER_PATHS!${ZOOKEEPER_PATHS}!" config.xml
sed -i "s!_MAGIC_REDIS_HOST!${REDIS_HOST}!" jenkins.plugins.logstash.LogstashInstallation.xml
sed -i "s!_MAGIC_JENKINS_URL!http://${HOST}:${PORT}!" jenkins.model.JenkinsLocationConfiguration.xml

# Start the master
export JENKINS_HOME="$(pwd)"
if [[ -z "$JVM_DEBUG" ]]; then
    echo "Start Jenkins"
    java -jar jenkins"${JENKINS_VERSION}".war \
        -Djava.awt.headless=true \
        --webroot=war \
        --httpPort=${PORT} \
        --ajp13Port=-1 \
        --httpListenAddress=0.0.0.0 \
        --ajp13ListenAddress=127.0.0.1 \
        --preferredClassLoader=java.net.URLClassLoader \
        --logfile=../jenkins.log
else
    echo "Start Jenkins in debug mode, -Xdebug -Xrunjdwp: "
    echo "$JVM_DEBUG"
    java -jar jenkins"${JENKINS_VERSION}".war \
        -Djava.awt.headless=true \
        --webroot=war \
        --httpPort=${PORT} \
        --ajp13Port=-1 \
        --httpListenAddress=0.0.0.0 \
        --ajp13ListenAddress=127.0.0.1 \
        --preferredClassLoader=java.net.URLClassLoader \
        --logfile=../jenkins.log \
        -Xdebug \
        -Xrunjdwp:"$JVM_DEBUG"

fi
echo "Jenkins is running"