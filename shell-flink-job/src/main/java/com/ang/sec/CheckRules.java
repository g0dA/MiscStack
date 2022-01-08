package com.ang.sec;

import java.util.List;
import java.util.regex.Pattern;

public class CheckRules {
    //分为正则和关键字两种，正则比关键字靠谱点，所以先正则
    //反弹shell返回True
    public Boolean checkRule(String cmdline){
        //初始化规则列表
        RulesList rulesList=new RulesList();

        List<String> reglist = rulesList.getRegList();
        List<List> blacklist = rulesList.getBlackList();

        for(String singleRule:reglist){
            if(regRuleCheck(cmdline,singleRule))
                return Boolean.TRUE;
        }

        for(List singleBlack:blacklist){
            if(blacklistCheck(cmdline,singleBlack))
                return Boolean.TRUE;
        }


        return Boolean.FALSE;
    }

    //正则校验
    public Boolean regRuleCheck(String cmdline,String rule){
        //Linux严格大小写
        boolean isMatch = Pattern.matches(rule,cmdline);
        if(isMatch)
            return Boolean.TRUE;
        return Boolean.FALSE;
    }

    //黑名单校验
    public Boolean blacklistCheck(String cmdline, List<String> blacklist){
        //list中的每一个都出现则认为反弹
        int count=0;
        for(String single:blacklist){
            if(cmdline.contains(single))
                count++;
        }
        if(count==blacklist.size())
            return Boolean.TRUE;

        return Boolean.FALSE;
    }
}
