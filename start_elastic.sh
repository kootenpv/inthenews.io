apt-get install git
git clone https://github.com/kootenpv/inthenews.io

wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
apt-get update && sudo apt-get install elasticsearch
update-rc.d elasticsearch defaults 95 10
add-apt-repository ppa:webupd8team/java
apt-get update
apt-get install oracle-java7-installer

echo "network.host: 0.0.0.0" >> /etc/elasticsearch/elasticsearch.yml
echo "script.groovy.sandbox.enabled: true" >> /etc/elasticsearch/elasticsearch.yml
echo "script.inline: on" >> /etc/elasticsearch/elasticsearch.yml
echo "script.indexed: on" >> /etc/elasticsearch/elasticsearch.yml
echo "script.search: on" >> /etc/elasticsearch/elasticsearch.yml
echo "script.engine.groovy.inline.aggs: on" >> /etc/elasticsearch/elasticsearch.yml

/etc/init.d/elasticsearch start

apt-get install python3-pip
apt-get install python3-lxml
cd inthenews.io
pip3 install -r requirements.txt

#rsync -a ~/dir1 username@remote_host:destination_directory
