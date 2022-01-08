package com.ang.sec;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.util.Collector;


public class KafkaDateJsonFilter implements FlatMapFunction<String, String> {


    private String jsonFilter(JSONObject data) throws Exception {
        String cmdline = data.getJSONObject("columns").getString("cmdline");
        if (cmdline == null) {
            cmdline = "null";
        }

        return cmdline;
    }

    @Override
    public void flatMap(String value, Collector<String> out) throws Exception {
        JSONObject data = JSON.parseObject(value);
        CheckRules checkRules=new CheckRules();
        if (data != null) {
            String cmdline=jsonFilter(data);
            if(checkRules.checkRule(cmdline)) {

                out.collect(cmdline);
            }
        }

    }


}
