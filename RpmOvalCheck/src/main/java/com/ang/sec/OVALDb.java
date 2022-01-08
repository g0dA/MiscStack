package com.ang.sec;

import com.alibaba.fastjson.JSON;
import org.dom4j.Document;
import org.dom4j.DocumentException;
import org.dom4j.Element;
import org.dom4j.Node;
import org.dom4j.io.SAXReader;

import java.io.File;
import java.util.*;

public class OVALDb {
    //加载centos7需要的oval文档
    Element ovalDefinitions;
    Element ovalObjects;
    Element ovalStates;
    Element ovalTests;

    public OVALDb() throws DocumentException {
        String ovalPath = "src/main/resources/Red_Hat_Enterprise_Linux_7.xml";

        //流方式读取
        SAXReader reader = new SAXReader();
        File file = new File(ovalPath);
        Document ovalXml = reader.read(file);

        Element root = ovalXml.getRootElement();

        //生成四个节点的List
        ovalDefinitions = root.element("definitions");
        ovalTests = root.element("tests");
        ovalObjects = root.element("objects");
        ovalStates = root.element("states");
    }



    //根据packageName提取id，一对一
    public String getObjectId(String rpmName){
        String objectid;
        String value;
        List<Element> rpminfo_objects = ovalObjects.elements("rpminfo_object");
        try{
        for(Element rpminfo_object:rpminfo_objects){
            value = rpminfo_object.element("name").getText();
            objectid = rpminfo_object.attributeValue("id");
            if(value.equals(rpmName)){

                return objectid;
            }
        }
        }
        catch (Exception e){
            return "";
        }
        return "";
    }

    //根据objectid提取testid和stateid，一对多对多
    public List<List> getTestsIdAndStateRef(String objectid) {

        List<List> All = new LinkedList<List>();

        String testid;
        String stateref;
        String object_ref;

        List<Element> rpminfo_tests = ovalTests.elements("rpminfo_test");
        for (Element rpminf_test : rpminfo_tests) {
            object_ref = rpminf_test.element("object").attributeValue("object_ref");

            if (object_ref.equals(objectid)) {
                List<String> Single = new LinkedList<String>();
                testid = rpminf_test.attributeValue("id");
                stateref = rpminf_test.element("state").attributeValue("state_ref");
                Single.add(testid);
                Single.add(stateref);
                All.add(Single);
            }
        }
        return All;
    }

    //根据stateid提取检测逻辑,一对一
    public List getRules(String stateid){
        List<String> SingleRule = new LinkedList<String>();
        //架构界定
        String arch=null;
        //版本界定
        String evr=null;

        List<Element> rpminfo_states = ovalStates.elements("rpminfo_state");
        for(Element rpminfo_state:rpminfo_states){
            if(rpminfo_state.attributeValue("id").equals(stateid)){
                if(rpminfo_state.elements("signature_keyid").size()==1)
                    continue;
                if(rpminfo_state.elements("version").size()==1)
                    continue;

                evr = rpminfo_state.element("evr").getText();
                SingleRule.add(evr);
                try {
                    arch = rpminfo_state.element("arch").getText();
                }catch (Exception e){
                    arch=null;
                }

                if(arch!=null)
                    SingleRule.add(arch);




                return SingleRule;
            }

        }
        return SingleRule;
    }

    //根据testsid提取到CVE，一对多-多
    public Map<Integer,Map<String,cveInfo>> getCvelist(String testsid){
        List<Element> definitions = ovalDefinitions.elements("definition");
        Map<String,cveInfo > cveDetail = new HashMap<>();
        Map<Integer,Map<String,cveInfo >> cveResult = new HashMap<>();
        //要返回的东西

        /*
        * 高危：3
        * 中危：2
        * 低危：1
        * 无:0
        * */
        int level=0;
        //提取到单个的definition
        for(Element definition:definitions){
            Element criteria = definition.element("criteria");
            /*
            如果testsid出现在criteria的大字符串中，则可以理解为是一个检查项目，
            无论其余条件，则一律认为符合该检查项目的rpm包存在此问题，则输出当前
            definition所有的cve与对应的referer;
            */

            //判断是否存在criteria
            List<Element> child_criteria = new LinkedList<Element>();
            List<Element> criterion=new LinkedList<Element>();
            child_criteria = criteria.elements("criteria");
            //搜集最上层所有的criterion
            criterion.addAll(criteria.elements("criterion"));


            //只解了3层
            if(child_criteria.size()>0){
                for(Element child_single_criteria:child_criteria){
                    criterion.addAll(child_single_criteria.elements("criterion"));
                    List<Element> child_child_criteria = child_single_criteria.elements("criteria");
                    if(child_child_criteria.size()>0){
                        for(Element child_child_single_criteria:child_child_criteria){

                            criterion.addAll(child_child_single_criteria.elements("criterion"));
                        }

                    }
                }
            }


            for(Element single:criterion){
                if(single.attributeValue("test_ref").equals(testsid)){
                    //可能没有CVE，加个判断
                    List<Element> current_cvelist = definition.element("metadata").element("advisory").elements("cve");
                    if(current_cvelist.size()==0)
                        continue;
                    for(Element single_cve:current_cvelist){
                        double single_cve_score=0;
                        if(single_cve.attributeValue("cvss3")!=null){
                            single_cve_score = Double.valueOf(single_cve.attributeValue("cvss3").split("/")[0]);
                        }else if(single_cve.attributeValue("cvss2")!=null){
                            single_cve_score = Double.valueOf(single_cve.attributeValue("cvss2").split("/")[0]);
                        }
                        Integer cve_level=0;
                        if(single_cve_score>7)
                            cve_level=3;
                        else if(single_cve_score>4)
                            cve_level=2;
                        else if(single_cve_score>0)
                            cve_level=1;



                        if(single_cve_score>7 && level<3)
                            level=3;
                        else if(single_cve_score>4 && level<2)
                            level=2;
                        else if(level==1||level==0)
                            level=1;
                        cveInfo cveInfo = new cveInfo(single_cve.attributeValue("href"),cve_level);
                        cveDetail.put(single_cve.getText(),cveInfo);
                        //System.out.print(cveInfo.getReferer());
                    }
                    break;

                }
            }
            //System.out.print(level);



        }
        cveResult.put(level,cveDetail);
        return cveResult;
    }

}
