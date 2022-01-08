package com.ang.sec;

public class VersionParse {

    public String versionparse(String evr){
        String version=evr;
        if(evr.indexOf(":")!=-1 && evr.indexOf("-")!=-1){

             version = version.split(":")[1];
             version = version.split("-")[0];
        }else if(evr.indexOf(":")!=-1 && evr.indexOf("-")==-1){

            version = version.split(":")[1];
        }else if(evr.indexOf(":")==-1 && evr.indexOf("-")!=-1){
            version = version.split("-")[0];
        }else {
            version=version;
        }
        return version;
    }
}
