package com.ang.sec;

import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer010;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;

import java.util.Properties;

public class FlinkConsumer {
    private static String BOOTSTRAP_SERVER="host:9092";
    private static String TOPIC_NAME="";
    private static String GROUP_ID="";

    public static void main(String[] args) throws Exception{
        StreamExecutionEnvironment env=StreamExecutionEnvironment.getExecutionEnvironment();
        Properties sourceKafkaProperties = new Properties();
        sourceKafkaProperties.setProperty("bootstrap.servers",BOOTSTRAP_SERVER);
        sourceKafkaProperties.setProperty("group.id",GROUP_ID);


        //compress data
        sourceKafkaProperties.put("compression.type", "gzip");
        String jaasTemplate = "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"username\" password=\"password\";";
        sourceKafkaProperties.put("security.protocol", "SASL_PLAINTEXT");
        sourceKafkaProperties.put("sasl.mechanism", "PLAIN");
        sourceKafkaProperties.put("sasl.jaas.config", jaasTemplate);


        FlinkKafkaConsumer010<String> consumer010 = new FlinkKafkaConsumer010(TOPIC_NAME,new SimpleStringSchema(),sourceKafkaProperties);


        DataStream<String> dataStream=env
                .addSource(consumer010)
                .flatMap(new KafkaDateJsonFilter());


        dataStream.print();
        env.execute("flink-job start");
    }
}
