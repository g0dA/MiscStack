package com.ang.sec;

import java.util.regex.Pattern;

public class VersionCompare {
    /*
    * rpmversion < rule <0
    * rpmversion = rule 0
    * rpmversion > rule >0
    * */
    public int versionCompare(String ver1,String ver2){
        if(ver1 == null && ver2 == null){
            throw new RuntimeException("版本号不能都为空");
        }

        if(ver1 == null){
            return -1;
        }

        if(ver2 == null){
            return 1;
        }

        if(ver1.equals(ver2)) {
            return 0;
        }

        String [] version1 = ver1.split("\\.");
        String [] version2 = ver2.split("\\.");


        String defValue = "0000000000000000";
        String format = "%" + defValue.length() + "s";
        StringBuilder ver1Builder = new StringBuilder(version1.length * 10);
        StringBuilder ver2Builder = new StringBuilder(version2.length * 10);

        if(version1.length > version2.length) {
            for (int i=0; i<version1.length ;i++ ) {
                ver1Builder.append(String.format(format, version1[i]).replace(' ', '0'));
                ver2Builder.append(version2.length > i? String.format(format, version2[i]).replace(' ', '0') : defValue);
            }

        } else if(version1.length < version2.length){
            for (int i=0; i<version2.length ;i++ ) {
                ver2Builder.append(String.format(format, version2[i]).replace(' ', '0'));
                ver1Builder.append(version1.length > i? String.format(format, version1[i]).replace(' ', '0') : defValue);
            }

        } else {
            for (int i=0; i<version2.length ;i++ ) {
                ver1Builder.append(String.format(format, version1[i]).replace(' ', '0'));
                ver2Builder.append(String.format(format, version2[i]).replace(' ', '0'));
            }
        }

        return ver1Builder.toString().compareTo(ver2Builder.toString());
}
}
