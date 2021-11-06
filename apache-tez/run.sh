cp /pucrs/apache-tez/yarn-site.xml /usr/local/hadoop/etc/hadoop/
service apache2 start
# shellcheck disable=SC2164
cd /usr/local/hadoop/etc/hadoop
./hadoop-env.sh
./yarn-env.sh
./httpfs-env.sh
./kms-env.sh
./mapred-env.sh
# shellcheck disable=SC2164
cd /usr/local/hadoop/sbin
./start-all.sh
/usr/local/hadoop/sbin/yarn-daemon.sh start timelineserver
/usr/local/hadoop/bin/hadoop fs -mkdir /pucrs/
/usr/local/hadoop/bin/hadoop fs -mkdir /pucrs/data
/usr/local/hadoop/bin/hadoop fs -put /pucrs/data/mt5_database.csv /pucrs/data
/usr/local/hadoop/bin/hadoop fs -rm -r /pucrs/reduced
cp /pucrs/apache-tez/target/tez-mt5-0.9.0.jar /usr/local/tez/tez-examples/target/
/usr/local/hadoop/bin/hadoop fs -put -f /pucrs/apache-tez/target/tez-mt5-0.9.0.jar /tez/
/usr/local/hadoop/bin/hadoop jar /pucrs/apache-tez/target/tez-mt5-0.9.0.jar mt5wordcount /pucrs/data/mt5_database.csv /pucrs/reduced
rm -r /pucrs/data/reduced
/usr/local/hadoop/bin/hadoop fs -get /pucrs/reduced /pucrs/data/
