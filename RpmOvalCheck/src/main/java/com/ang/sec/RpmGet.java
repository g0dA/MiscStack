package com.ang.sec;

import org.dom4j.DocumentException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;


public class RpmGet {
    //获取到rpm<name,version,arch>
    OVALDb OVALDB;
    public RpmGet() throws Exception{
        OVALDB = new OVALDb();

    }

    public Map<Integer,Map<String,cveInfo >> getCveDetail(String rpmName,String rpmVersion,String rpmArch) throws DocumentException {
        Map<Integer,Map<String,cveInfo >> resultReturn = new HashMap<>();
        try{
            String name = rpmName;
            String version = rpmVersion;
            String arch = rpmArch;

            String objectid = OVALDB.getObjectId(name);
            Integer rpmlevel=0;
            Map<String,cveInfo> AllCveList = new HashMap<String,cveInfo>();
            //返回值
            List<List> testsIdandstateId=OVALDB.getTestsIdAndStateRef(objectid);
            //一个rpm有多个tests
            //此处改为多线程提速
            for(List single:testsIdandstateId){
                //获取单个的testsid对应的所有的CVE。
                List singlerule = OVALDB.getRules(single.get(1).toString());
                VersionParse versionParse =new VersionParse();
                VersionCompare versionCompare=new VersionCompare();
                String archRule =null;
                String verRule =null;
                String singletestID=null;
                if(singlerule.size()==2){
                    archRule = singlerule.get(1).toString();
                    verRule = singlerule.get(0).toString();
                }else if(singlerule.size()==1){

                    verRule = singlerule.get(0).toString();
                }else {
                    continue;
                }

                if(verRule==null)
                    continue;
                if(archRule!=null && archRule.indexOf(arch)!=-1){

                    verRule = versionParse.versionparse(verRule);

                    if(versionCompare.versionCompare(version,verRule)<0){
                        singletestID = single.get(0).toString();
                    }

                }else if(archRule==null){
                    verRule = versionParse.versionparse(verRule);
                    if(versionCompare.versionCompare(version,verRule)<0){
                        singletestID = single.get(0).toString();
                    }

                }

                if(singletestID==null)
                    continue;

                //get a 有效的testsid
                //0:20170606-57.gitc990aae.el7_4
                Map<Integer,Map<String,cveInfo>> single_cvelist = OVALDB.getCvelist(singletestID);
                int current_level = (Integer) single_cvelist.keySet().toArray()[0];
                //没有CVE就直接不返回
                if(current_level == 0)
                    continue;

                if(current_level==3&&rpmlevel<3)
                    rpmlevel =3;
                if(current_level==2&&rpmlevel<2)
                    rpmlevel = 2;
                if(current_level==1&&rpmlevel<1)
                    rpmlevel=1;

                AllCveList.putAll(single_cvelist.get(current_level));



            }
        resultReturn.put(rpmlevel,AllCveList);
        return resultReturn;

    }catch (Exception e){
        return resultReturn;
    }
    }
}
