package com.ang.sec;

public class test {
    public static void main(String[] args) throws Exception{
        RpmGet rpmGet=new RpmGet();

        String name = "dnsmasq";
        String version="2.66";
        String arch="x86_64";

        System.out.print(rpmGet.getCveDetail(name,version,arch));

    }
}
