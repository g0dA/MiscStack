# -*- coding: utf-8 -*-

"""
Module implementing des.
"""
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from Ui_des import Ui_descbc


class des(QDialog, Ui_descbc):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(des, self).__init__(parent)
        self.setupUi(self)
        

    @pyqtSlot()
    def on_sure_clicked(self):

        data0 = self.mingwen.text()
        key0 = self.key.text()
        IV = self.VI.text()
        IV_decode = IV
        key_decode = key0
        e_data0 = ''
        data_cbc = ''
        data0_decode = ''
        
        #自定义十六进制转ascii
        def hextranslate(s):
                res = ""
                for i in range(len(s)/2):
                        realIdx = i*2
                        res = res + chr(int(s[realIdx:realIdx+2],16))
                return res

        if8 = int(len(data0))%8
        if len(data0) >= 8 & len(key0)==8 & len(IV)==8:
            if if8 != 0:
                data1 = data0+(7-if8)*'0'+str(8-if8)
                data0 = data1
            data = data0
            #整个字符串转二进制
            for i in data0:
                e_data = bin(ord(i))[2:]
                #补全单个字符为8bit
                if 8-len(e_data) !=0:
                    e_data = (8-len(e_data))*'0'+e_data
                e_data0 =e_data0+str(e_data)
                 
            #print '初始明文:'+data0
            #print '填充明文:'+data1
            #print 'bit明文:'+e_data0
            
            #分组
            group = len(e_data0)/64
            
            #设定key
            key_test = key0
            key0_test = ''
            for key in key_test:
                key =bin(ord(key))[2:]
                if 8-len(key) !=0:
                    key = (8-len(key))*'0'+key
                key0_test +=str(key)
            #print key0_test
            
            #设定IV
            IV0 = IV
            IV = ''
            for iv in IV0:
                iv =bin(ord(iv))[2:]
                if 8-len(iv) !=0:
                    iv = (8-len(iv))*'0'+iv
                IV +=str(iv)
            #输出分组后的数据
                IV_decode = IV
            for j in range(group):
                e_data = e_data0[64*j:64*(j+1)]
                #每一组的输入明文
                #print e_data
            
                #试验用初始值
                #print hex(int(key0_test,2))
                IV = IV
                
                data_test = e_data
                self.decoding.append('第'+str(j+1)+'组数据:\n分组明文与十六进制：'+hextranslate(hex(int(data_test,2))[2:])+' ==> '+hex(int(data_test,2))+'\n')
                data_test = str(bin(int(e_data,2)^int(IV,2))[2:])
                self.decoding.append('加密异或IV：'+str(hex(int(IV,2))).replace('L','')+'\n')
                #print data_test
                if len(data_test)<64:
                    data_test = (64-len(data_test))*'0'+str(data_test)
                self.decoding.append('待加密值：'+str(hex(int(data_test,2))).replace('L','')+'\n')
                #64bit情况下des算
                #DES初始置换IP
                #初始IP置换表
                __ip = [ 
                58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,
                62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,
                 57,49,41,33,25,17, 9,1,59,51,43,35,27,19,11,3, 
                61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7,
                ]
                
                #逆初始IP置换表
                __ip1 = [ 
                40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,
                38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
                36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,
                 34,2,42,10,50,18,58,26,33,1,41, 9,49,17,57,25, 
                ]
                
                
                data0_test = ''
                #做IP置换
                for ip in __ip:
                    data0_test += data_test[ip-1]
                #print 'IP置换后数据:'+data0_test
                

                
                    
                
                #初始置换选择PC-1
                __PC1 = [ 
                57,49,41,33,25,17, 9, 
                1 ,58,50,42,34,26,18, 
                10, 2,59,51,43,35,27, 
                19,11, 3,60,52,44,36, 
                63,55,47,39,31,23,15,
                7 ,62,54,46,38,30,22, 
                14, 6,61,53,45,37,29, 
                21,13, 5,28,20,12, 4, 
                ]
                #置换选择PC-2
                __PC2 = [ 
                14,17,11,24,1,5,3,28, 
                15,6,21,10,23,19,12,4, 
                26,8,16, 7,27,20,13,2, 
                41,52,31,37,47,55,30,40,
                51,45,33,48,44,49,39,56,
                34,53,46,42,50,36,29,32,
                ]
                key_test_PC = ''
                for PC1 in __PC1:
                     key_test_PC += key0_test[PC1-1]
                
                #循环左移
                ld = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
                key_test_left = key_test_PC[:28]
                key_test_right = key_test_PC[28:]
                key_test_chi = ['','','','','','','','','','','','','','','','']
                for k in range(16):
                    key_test_left = key_test_left[int(ld[k]):]+key_test_left[0:int(ld[k])]
                    key_test_right = key_test_right[int(ld[k]):]+key_test_right[0:int(ld[k])]
                    key_test = key_test_left+key_test_right        
                    for PC2 in __PC2:
                        key_test_chi[k] += key_test[PC2-1]
                    #print '第'+str(k)+'轮子密钥:'+key_test_chi[k]
                
                #自定义F函数
                def F(dataR,key):
                    dataR = str(dataR)
                    key = str(key)
                    #print len(key)
                    #E盒扩展
                    __e = [ 
                    32,1,2,3,4,5, 
                    4,5,6,7,8,9, 
                    8,9,10,11,12,13, 
                    12,13,14,15,16,17,
                    16,17,18,19,20,21,
                    20,21,22,23,24,25,
                    24,25,26,27,28,29,
                    28,29,30,31,32,1, 
                    ]
                    dataR0=''
                    for e in __e:
                        dataR0 += dataR[e-1]
                    
                    #测试E盒扩展(没问题)
                    #print len(dataR0)
                    #E盒扩展后与key异或
                    dataR0 = str(bin(int(dataR0,2)^int(key,2))[2:])
                    #测试异或(没问题)(二次问题：自动约0)
                    #print dataR0
                    if len(dataR0)<48:
                        dataR0 = (48-len(dataR0))*'0'+str(dataR0)
                    
                    #8个S盒
                    __s1 = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
                            0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
                            4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
                            15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
                    __s2 = [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
                            3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
                            0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
                            13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
                    __s3 = [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
                            13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
                            13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
                            1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
                    __s4 = [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
                            13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
                            10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
                            3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
                    __s5 = [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
                            14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
                            4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
                            11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
                    __s6 = [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
                            10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
                            9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
                            4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
                    __s7 = [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
                            13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
                            1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
                            6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
                    __s8 = [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
                            1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
                            7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
                            2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
                    #S盒输出
                    def S(data,s):
                        data = str(data)
                        #print data
                        hang = int(str(data[0])+str(data[5]),2)
                        lie = int(str(data[1:5]),2)
                        data = int(hang)*16+int(lie)
                        data = int(s[data])
                        data = bin(data)[2:]
                        if len(str(data)) <4:
                            data = (4-len(str(data)))*'0'+str(data)
                        return data
                    #测试第一个S盒输入
                    #print dataR0[:6]
                    #测试单个S盒结果
                    #print S(dataR0[:6],__s1)
                    dataR0 = str(S(dataR0[:6],__s1))+str(S(dataR0[6:12],__s2))+str(S(dataR0[12:18],__s3))+str(S(dataR0[18:24],__s4))+str(S(dataR0[24:30],__s5))+str(S(dataR0[30:36],__s6))+str(S(dataR0[36:42],__s7))+str(S(dataR0[42:],__s8))
                    
            
                    #测试S盒结果
                    #print dataR0
                    __p = [ 
                    16, 7,20,21,29,12,28,17, 
                    1 ,15,23,26, 5,18,31,10, 
                    2 ,8 ,24,14,32,27, 3, 9, 
                    19,13,30, 6,22,11, 4,25, 
                    ]
                    
                    dataR = ''
                    for p in __p:
                        dataR += dataR0[p-1]
                    #测试P盒置换结果
                    #print dataR
                    return dataR
                
                dataL = data0_test[:32]
                dataR = data0_test[32:]
                #print '初始左值:'+str(dataL)
                #print '初始右值:'+str(dataR)
                for b in range(16):
                    dataL0 = dataR
                    dataR = F(dataR,key_test_chi[b])
                    dataR = str(bin(int(dataR,2)^int(dataL,2))[2:])
                    dataL = dataL0
                    if len(dataR)<32:
                        dataR = (32-len(dataR))*'0'+str(dataR)
                    if len(dataL)<32:
                        dataL = (32-len(dataL))*'0'+str(dataL)
                    #print '第'+str(b+1)+'次轮结构的左值:'+ str(dataL)
                    #print '第'+str(b+1)+'次轮结构的右值:'+ str(dataR)
                    
                data0 = dataR+dataL
                #data0 ='1111111110111000011101100101011100000000111111110000011010000011'
                data = ''
                for ip1 in __ip1:
                    data += data0[ip1-1]
                #print '二进制形式:'+data
                #print data
                    
               
                long = hex(int(data,2))
                if len(long) !=18:
                    long = long[:18]
                self.decoding.append('分组加密密文:'+long+'\n')
                data_cbc +=data
                
                
                IV = data


                
                #解密流程
                #data_decode是二进制数
                IV_decode = IV_decode
                data_decode = data
                IV_decode_ne = data_decode
                data_decode_ip = ''
                for ip in __ip:
                    data_decode_ip+=data_decode[ip-1]
                data_decode = data_decode_ip
                key_decode = key_decode
                data_decode_L = str(data_decode[:32])
                data_decode_R = str(data_decode[32:])
                #print data_decode_L
                delist = [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
                for de in delist:
                    data_decode_Ls = data_decode_R
                    data_decode_R = str(F(data_decode_R,key_test_chi[de]))
                    #print data_decode_L
                    data_decode_R = str(bin(int(data_decode_R,2)^int(data_decode_L,2))[2:])
                    #print data_decode_R
                    data_decode_L = data_decode_Ls
                    if len(data_decode_R)<32:
                        data_decode_R = (32-len(data_decode_R))*'0'+str(data_decode_R)
                    if len(data_decode_L)<32:
                        data_decode_L = (32-len(data_decode_L))*'0'+str(data_decode_L)
                
                data_decode0 = data_decode_R+data_decode_L
                data_decode = ''
                for ip1 in __ip1:
                    data_decode += data_decode0[ip1-1]
                data_decode = str(bin(int(data_decode,2)^int(IV_decode,2))[2:])
                self.decoding.append('解密异或IV：'+str(hex(int(IV_decode,2))).replace('L','')+'\n')
                if len(data_decode)<64:
                    data_decode = (64-len(data_decode))*'0'+str(data_decode)

                data0_decode += data_decode
                self.decoding.append('分组解密数据与十六进制：'+hextranslate(str(hex(int(data_decode,2))).replace('L','')[2:])+' ==> '+str(hex(int(data_decode,2))).replace('L','')+'\n')
                IV_decode = IV_decode_ne
                self.decoding.append( '******************************'+'\n')
            data = hex(int(data_cbc,2))
            data_decode = hex(int(data0_decode,2))
            #print data
            self.decoding.append( '******************************'+'\n')
            self.decoding.append('最终加密结果: '+data.replace('L','')+'\n')
            self.decoding.append('最终解密结果：'+ hextranslate(data_decode.replace('L','')[2:])+'\n')

            
        else:
            self.decoding.append( '明文长度不能小于8,秘钥必须要8位,初始向量必须要8位'+'\n')
        
        
        
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = des()
    dlg.show()
    sys.exit(app.exec_())
    

