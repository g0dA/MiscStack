package com.ang.sec;

public class cveInfo {
    private Integer level;
    private String referer;

    public cveInfo(String ref,Integer lev){

        this.referer=ref;
        this.level=lev;
    }

    public Integer getLevel() {
        return level;
    }

    public String getReferer() {
        return referer;
    }
}


