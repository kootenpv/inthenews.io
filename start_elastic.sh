wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
apt-get update
apt-get install -y elasticsearch

update-rc.d elasticsearch defaults 95 10
add-apt-repository ppa:webupd8team/java
apt-get update
apt-get install -y openjdk-7-jre

echo "network.host: 0.0.0.0" >> /etc/elasticsearch/elasticsearch.yml
echo "script.groovy.sandbox.enabled: true" >> /etc/elasticsearch/elasticsearch.yml
echo "script.inline: on" >> /etc/elasticsearch/elasticsearch.yml
echo "script.indexed: on" >> /etc/elasticsearch/elasticsearch.yml
echo "script.search: on" >> /etc/elasticsearch/elasticsearch.yml
echo "script.engine.groovy.inline.aggs: on" >> /etc/elasticsearch/elasticsearch.yml

apt-get install -y python3-pip
apt-get install -y python3-lxml

apt-get install -y curl
apt-get install -y jq
apt-get install -y vim
apt-get install -y git
apt-get install -y screen

git clone https://github.com/kootenpv/inthenews.io
cd inthenews.io

pip3 install -r requirements.txt

# /etc/init.d/elasticsearch start

#rsync -a ~/dir1 username@remote_host:destination_directory
