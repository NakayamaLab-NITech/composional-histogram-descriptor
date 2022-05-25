#! /usr/bin/env python

import re
import os
import numpy as np
import argparse
import math
import tqdm
import subprocess as sp
from subprocess import check_output
import pandas as pd
import shutil

path=os.getcwd()
defvasp ="DefVASP"  
defelem="DefElem"
histdef='histdef.dat'

def argument():

    for i in tqdm.tqdm(range(int(1e7))):
        np.pi*np.pi

    parser = argparse.ArgumentParser(
    usage='python make_hist.py structure -his= -sigma= -kh= -pos=\n\nstructure         : enter a composition name (e.g. LiCoO2) or POSCAR.names formatted file (if -pos=T)\n-his=histdef.dat  : histdef.dat formatted strucure file (def. histdef.dat)\n-sigma=T          : sigma value for Gaussian broadning\n-kh=T             : output histgram descriptors considering two elements (Def. F)\n-pos=T            : use POSCAR.names file instead of direct input.(Def. F)\nHistogram format  : 1:Prop (eg. AN, EN)  2: 3  3: prop_min  4: prop_max  5: bin_num  6: gaussian_sigma\n')

    parser.add_argument('-his',type=str, default=histdef,help='histdef.dat formatted structure file (def. histdef.dat)')
    parser.add_argument('structure',type=str, help='enter a compositon name')
    parser.add_argument('-sigma',help=" -sigma=T\: sigma value for Gaussian broadning\n")
    parser.add_argument('-kh',help=" -kh=T\: output histgram descriptors considering two elements (Def. F)\n")
    parser.add_argument('-pos',default='F',help=" -pos=T use POSCAR.names file instead of direct input.\n")

    args = parser.parse_args(args=['-his=histdef.dat',structure,'-kh=T'])
    reference = args.structure
    histdef = args.his
    aparam2=args.sigma
    aparam3=args.kh
    sparam=args.pos
    reference = reference.split()

    if aparam2 is None:
        aparam2 = ''

    if aparam3 is None:
        aparam3 = ''
    return 

def defvasptable(): #-----------------------------------------------------------------------       
                                                            
#-- ionic energy -------------------------------------------                                                                                          
#    type = use, WEL, CRC                                                                        
#   "use" and "WEL" give former in the unit "kJ/mol"  "CRC" gives latter in the unit "eV"        
#----------------------------------------------------------------------------------------- \      
#    print "reading defvasp\n"                                                           
     
    INvasp= open(defvasp,'r')     
    vaspdef = INvasp.readlines()   
    for in_vaspdef in vaspdef:     
        in_vaspdef.rstrip('\n')
    INvasp.close()
    atom2Z={}
    Z2atom=[]
    vaspdef.pop(0)
    for i in vaspdef:     
        field=i.split()
        if field[0] != "ZZZ":     
            atom2Z[field[0]]=field[7]
            while len(Z2atom) -1 < int(field[7]):
                Z2atom.append('')    
            Z2atom[int(field[7])]=field[0]     
            
    return atom2Z,Z2atom

def compconv(reference): #-------------------------------------------------------------------------------                                                                         
#input incomp or reference[0]  eg Li0.1CoO2                                                                                                                          
#output  indexions[i] -> element                                                                                                                                     
#        ions[i]      -> number of ions                                                                                                                              
#        totalion      -> summation of ions                                                                                             
#---------------------------------------------------------------------------------------------                                                                         
    incomp=reference[0]
    
    ions=[]
    totalion=0
    indexions=[]
    factor=[]
    composition=[]
    elemcomp=[]
    nfactor=[]
    nions={}

    if incomp != "":
        compositionprim = incomp
        printoff="T"
    else:
        compositionprim = reference[0]
    
    #z = readdefelem
    re.sub(r'\[','\(',compositionprim)
    re.sub(r'\]','\)',compositionprim)
    if printoff != "T":
        print ("{} input: {}\n".format(composition,compositionprim))
    i=0
    if not  bool(re.search(r'\(/',compositionprim)):
        composition.append(compositionprim)
        factor.append(1)                                                                                                                                                    
    else:
        if not compositionprim == "":
            if bool(re.search(r'^([A-Z].*?)(\(.*)',compositionprim)):
                search = re.search(r'^([A-Z].*?)(\(.*)',compositionprim)
                ate1 = search.group(1)
                ate2 =search.group(2)
                composition.append(ate1)
                factor.append(1)
                compositionprim = ate2
            elif bool(re.search(r'^\(([A-Z].*?)\)([0-9\.]*)([A-Z].*)',compositionprim)):
                search = re.search(r'^\(([A-Z].*?)\)([0-9\.]*)([A-Z].*)',compositionprim)
                ate1 = search.group(1)
                ate2 = search.group(2)
                ate3 = search.group(3)
                composition.append(ate1)
                factor.append(ate2)
                compositionprim=ate3
            elif bool(re.search(r'^\(([A-Z].*?)\)([0-9\.]*)(\(.*)',compositionprim)):
                search = re.search(r'^\(([A-Z].*?)\)([0-9\.]*)(\(.*)',compositionprim)
                ate1 = search.group(1)
                ate2 =search.group(2)
                ate3  = search.group(3)
                composition.append(ate1)
                if ate2 == "":
                    factor.append(1)
                else:
                    factor.append(ate2)
                compositionprim=ate3
            elif bool(re.search(r'^\(([A-Z].*)\)([0-9\.]*)',compositionprim)):
                search = re.search(r'^\(([A-Z].*)\)([0-9\.]*)',compositionprim)
                ate1 = search.group(1)                
                ate2 = search.group(2)
                composition.append(ate1)
                if ate2 == "":
                    factor[i]=1
                else:
                    factor[i]=ate2
                compositionprim=""
            elif bool(re.search(r'^\(([A-Z].*)\)',compositionprim)):
                search = re.search(r'^\(([A-Z].*)\)',compositionprim)
                ate1 = search.group(1)
                composition.append(ate1)
                factor.append(1)
                compositionprim=""
            else:
                composition.append(compositionprim)
                factor.append(1)
                compositionprim=""                                                                                                       
            i = i+1
    i=0
    j=0
    
    for compositionflag in composition:                                        
        while compositionflag != "":
            if bool(re.search(r'^([A-Z].*?)([A-Z].*)',compositionflag)):
                search = re.search(r'^([A-Z].*?)([A-Z].*)',compositionflag)
                ate1 = search.group(1)
                ate2 = search.group(2)
                elemcomp.append(ate1)
                nfactor.append(factor[j])
                compositionflag=ate2
            elif bool(re.search(r'^([A-Z].*[0-9\.]*)',compositionflag)):
                search = re.search(r'^([A-Z].*[0-9\.]*)',compositionflag)
                ate1 = search.group(1)
                elemcomp.append(ate1)
                compositionflag=""
                nfactor.append(factor[j])                                                                                                        
            i = i + 1
            if i>9999 :
                break
        j =j +1
    i=0
    
    for j in  elemcomp:                                                                                                                                         
        if  bool(re.search(r'^([A-Za-z]*)([0-9\.].*)',str(j))):
            search = re.search(r'^([A-Za-z]*)([0-9\.].*)',str(j))
            ate1 = search.group(1)
            ate2 = search.group(2)
            nions[ate1]=0
            nions[ate1]=float(ate2)*nfactor[i]+nions[ate1]                                                                                                                      
        elif bool(re.search('^([A-Za-z]*)',str(j))):
            search = re.search('^([A-Za-z]*)',str(j))
            ate1 = search.group(1)
            nions[ate1]=0
            nions[ate1]=1*nfactor[i]+nions[ate1]
        i = i + 1
    totalion=0
    i=0
    
    for l in  sorted(nions.keys()):
        indexions.append(l)
        ions.append(nions[l])
        #if printoff != "T":

            #print("{} ".format(l))
            #print("{} ".format(nions[l]))

        totalion=totalion+nions[l]
        i = i + 1

    if printoff != "T":
        print ("\n")
        print ("total ions   {}\n".format(totalion))

    return ions,compositionprim,indexions,totalion

def readdefelem(atom,defelem): #------------------------------------------------------------------------------
    
    IN =open(defelem,'r')
    defelem=IN.readlines()
    for line in defelem:
        line=line.rstrip('\n')
    IN.close()

    el_dic = {'AN':'AN','EN':'EN','MP':'MP','PN':'PN','PG':'PG','MN':'MN','AW':'AW','AR':'AR','IR':'IR','CoR':'CoR','CrR':'CrR','spdf':'spdf'}
    for e in defelem:
        field=e.split()
        defatom=field[1]
        element = '0'
        def_atom = {defatom : element}
        el_dic['AN'] = dict(def_atom)
        el_dic['EN'] = dict(def_atom)
        el_dic['MP'] = dict(def_atom)
        el_dic['PN'] = dict(def_atom)
        el_dic['PG'] = dict(def_atom)
        el_dic['MN'] = dict(def_atom)
        el_dic['AW'] = dict(def_atom)
        el_dic['AR'] = dict(def_atom)
        el_dic['IR'] = dict(def_atom)
        el_dic['CoR'] = dict(def_atom)
        el_dic['CrR'] = dict(def_atom)
        el_dic['spdf'] = dict(def_atom)

        if atom == defatom:
            el_dic['AN'][atom]=field[0]       
            el_dic['EN'][atom]=field[2]
            el_dic['MP'][atom]=field[4]
            el_dic['PN'][atom]=field[5]       
            el_dic['PG'][atom]=field[6]
            el_dic['MN'][atom]=field[7]
            el_dic['AW'][atom]=field[8]
            el_dic['AR'][atom]=field[9]
            el_dic['IR'][atom]=field[10]
            el_dic['CoR'][atom]=field[11]
            el_dic['CrR'][atom]=field[12]
            el_dic['spdf'][atom]=field[13]
        if atom == defatom:
            return el_dic

def broad(df,arg1,arg2,arg3,histdef,j_list_nise,FN): #--------------------------------------------------------------- Broad                                                                                                        

    tlimit=0.000001
    inpf=df

    if arg1 == "":
        rowx=1
    else:
        rowx=arg1

    if arg2 == "":
        rowy=2
    else:
        rowy=arg2

    if arg3 == "":
        sigma=1
    else:
        sigma=arg3

    if not histdef == "":
        tlimit=histdef                                                                                                                                                              
    #f =open(inpf,'r')
    #lines=f.readlines()
    #print(df)
    col_list2=df.columns.tolist()
    data_list2=[]
    for df_col2 in col_list2: 
        #print(df[df_col2])
        df_data2 = df[df_col2]
        #print(df_data2)
        data_list2.append(df_data2)

    n=0
    sumy1=0
    xval=[]
    yval=[]
    for i in data_list2:
        field=i.str.split()
        #xval.append(field[0][rowx-1])
        yval.append(field[0][rowx-1])
        sumy1=sumy1+float(yval[n])
        n = n+1
    
    for nise in j_list_nise:
        xval.append(nise)

    g_list_index=[]
    g_list_columns=[]
    x=0
    #print(data_list2)
    try :
        sumy2
    except:
        sumy2=0
    while x<=len(data_list2)-1:
        sumy=0
        i=1
        while i<=len(data_list2)-1:
            sumy=sumy+(float(yval[i])/(math.sqrt(2*math.pi*sigma**2)))*math.exp(-((float(xval[i])-float(xval[x]))**2)/(2*sigma**2))*(float(xval[i])-float(xval[i-1]))
            i = i + 1
        sumy2=sumy2+sumy
        ssi=""
        ssi=abs(sumy)
        if ssi < tlimit:
            sumy=0
        
        g_list_index.append("{}".format(sumy))
        #g_list_index.append("{}".format(sumy))
        g_list_columns.append('out_{}'.format(x))
        x = x +1
    g_dict=dict(zip(g_list_columns,g_list_index))
    g_df=pd.DataFrame(g_dict,index=['test'])
    
    return g_df


def dfmake(arg0,arg1,arg2,arg3,arg4,arg5,arg6,histdef,aparam2,aparam3,df,FN): #----------------------------------------------------------------------------------                                                                        

    """
    try:
        ofile
    except:
        ofile = ''

    if ofile == "":
        ofile="out.distfunc"
    """
    
    col_list=df.columns.tolist()
    data_list=[]
    for df_col in col_list:
        #print(df[df_col])
        df_data=df[df_col]
        data_list.append(df_data)
    #print(data_list)

    """
    IN= open(arg0)
    datalines=IN.readlines()
    for i in datalines:
        i=i.rstrip('\n')
    """

    histdef=1

    clmx=arg1 
    clmy=arg2
    minx=arg3 
    maxx=arg4
    binnum=arg5
    sigma=arg6
    
    if histdef == "":
        norm=1
    else:
        norm=histdef
    histdef = ""

    n=0
    field=[]
    orgx=[]
    orgy=[]
    
    for j in data_list:
        field =j.str.split()
        orgx.append(field[0][int(clmx)-1])                                                                                                          
        if not clmy == 0:
            orgy.append(field[0][int(clmy)-1])
        else:
            orgy.append(1)
        if bool(re.search(r'[T]',aparam3,re.I)):
            orgy[n]=abs(float(orgy[n]))
        n = n+1
    

    totaldata=n-1

    int_=[]
    i=0
    bin0=[]
    bin1=[]
    while i<= int(binnum)-1:
        bin0.append((float(maxx)-float(minx))/float(binnum)*i+float(minx))
        bin1.append((float(maxx)-float(minx))/float(binnum)*(i+1)+float(minx))
        j=0
        while j<=totaldata:
            if float(orgx[j]) >= float(bin0[i]) and float(orgx[j]) < float(bin1[i]):
                while len(int_)-1 < i:
                    int_.append('')
                if int_[i] == '':
                    int_[i]=0
                int_[i]=(float(int_[i])+float(orgy[j]))
            j = j+1
        i = i +1
    
    j_list_index=[]
    j_list_columns=[]
    j_list_nise=[]
    if bool(re.search(r'[T]',str(aparam2),re.I)):
        norm=totaldata+1

    elif aparam2 != '':
        if aparam2 > 0:
            sumint=0
            i=0
            while i<=binnum-1:
                sumint=sumint+int_[i]
                i = i + 1
            norm=sumint/aparam2
                                                                                                                               
    i=0
    while i<= int(binnum)-1:
        while len(int_)-1 < i:
            int_.append('')
        if int_[i] == "":
            int_[i]=0
        int_[i]=int_[i]/norm                                                                                                                     
        j_list_index.append("{}".format(int_[i]))
        j_list_nise.append('{}'.format(bin0[i]))
        #j_list_index.append("{}".format(int_[i]))
        j_list_columns.append('out_{}'.format(i))
        i = i +1
    j_dict=dict(zip(j_list_columns,j_list_index))
    j_df=pd.DataFrame(j_dict,index=['test'])
    if sigma !='T':
        if float(sigma) > 0:
            df = j_df
            arg1 = 1
            arg2 = 2
            arg3 = sigma
            histdef = ""
            X =broad(df,arg1,arg2,arg3,histdef,j_list_nise,FN)
            j_df = X
    
    return arg1,arg2,arg3,arg4,arg5,arg6,j_df


def readposcar(inputf):     #------------------------------------------------------ read poscar (VASP)                                                                                              
    n=0 
    POSCAR=[] 
    ions=[] 
    totalion=0 
    
    dir_list =os.listdir(os.getcwd())
    for ii in dir_list:
        if ii == inputf:
            with open(inputf,'r')as IN:     
                POSCAR = IN.readlines()     
    k=0        
    for l in POSCAR:
        l = re.sub('\s^', '', l)
        POSCAR[k]=l      
        k = k+1      

    while len(POSCAR) -1 < 5:
        POSCAR.append('')   
    _=POSCAR[5] 
    fieldline5=_.split()
    if not fieldline5:
        chr5=''
    else:
        chr5 = fieldline5[0][:2]

    if bool(re.search('[A-Za-z]',chr5)):
        ver5name=fieldline5     
        ver5add=1 
        DorC=1     
    else:     
        ver5add=0 
        DorC=0     
        ver5name=[]     
        
    i=5+ver5add     
    ions = POSCAR[i].split()     
     
    _=POSCAR[6+ver5add] 
    fieldline6=_.split()

    if not fieldline6:
        chr6=''
    else:
        chr6=fieldline6[0][:2]     
     
    if bool(re.search('d',chr6, re.I)) or bool(re.search('c',chr6,re.I)):     
        selectiveadd=0     
        DorCchr=chr6     
    elif re.search('s',chr6,re.I):     
        selectiveadd=1     
        _=POSCAR[6+ver5add+selectiveadd]     
        fielddorc=_.split()     
        DorCchr=fielddorc[0][:2]     
         
    try:
        DorCchr
    except:
        DorCchr=''
        selectiveadd=0
    if DorCchr == "d":     
        DorCchr ="D"     
    if DorCchr == "c":     
        DorCchr ="C"     

    i = 0
    indexions=[]
    indexionsend=[]
    try:
        totalion
    except:
        totalion=0
    while i <= len(ions)-1 :     
        indexions.append(totalion+1)
        totalion=totalion+int(ions[i])     
        indexionsend.append(totalion)     
        i = i + 1
                                                                       
    i=0 
    ii=0
    coodAtom=[]
    coodocp=[]
    Idx1=[]
    Idx2=[]
    ionslabel=[]
    i = 7+ver5add+selectiveadd
    while i<=totalion+6+ver5add+selectiveadd:      
        ii = ii + 1
        _=POSCAR[i]     
        splitline=_.split()
        if DorCchr == "D":
            k = 0
            while k<=2:     
                if splitline[k] >= 1.0:
                    splitline[k]=splitline[k]-1      
                if splitline[k] <  0.0:
                    splitline[k]=splitline[k]+1      
                k = k +1    
             
        while len(coodAtom)-1 < ii:
            coodAtom.append('')

        coodAtom[ii]=splitline[3+selectiveadd*3]

        if coodAtom[ii] == "\!":
            coodAtom[ii]=splitline[4]

        while len(splitline)-1 < 4+selectiveadd*3 :
            splitline.append('')

        while len(splitline)-1 < 5+selectiveadd:
            splitline.append('')
        
        sln = 4

        for line_pos in splitline:   
            if bool(re.search(r'OC_([0-9\.]*)',line_pos)):
                search=re.search(r'OC_([0-9\.]*)',line_pos)
                ate1 = search.group(1)
                coodocp.append(ate1) 
            if bool(re.search(r'Idx1_(.*)',line_pos)):
                search=re.search(r'Idx1_(.*)',line_pos)
                ate1 = search.group(1)
                Idx1[ii]=ate1
            if bool(re.search(r'Idx2_(.*)',line_pos)):
                search=re.search(r'Idx2_(.*)',line_pos)
                ate1 = search.group(1)
                while len(Idx2)-1 < ii:
                    Idx2.append('')
                Idx2[ii]=ate1
        i = i + 1
        sln = sln + 1
        
    
    loci = 1
    while loci <= totalion:
        while len(coodocp)-1 < loci:
            coodocp.append('')
        if coodocp[loci] == "":
            coodocp[loci] =1
        loci = loci + 1    
     
    jelem=0
    outcomp=[]
    for labelelem  in ionslabel:     
        outcomp.append("{}".format(outcomp)+"{}".format(labelelem)+"{}".format(ions[jelem]))      
        jelem = jelem + 1      
                                                                                      
    POSCAR1=[]
    if DorC == 1:     
        for POS_i in POSCAR:     
            if not n == 5:     
                POSCAR1.append(POS_i)     
            n = n + 1      
        POSCAR=POSCAR1  
        POSCAR1=[]      
     
    ii=0 
    iii=-1      
    for numa in ions:     
        iii = iii + 1
        i = 1
        while i<= int(numa):     
            ii = ii + 1      
            if not bool(re.search(r'^[A-Z]',coodAtom[ii])):     
                coodAtom[ii] = ver5name[iii]      
            i = i + 1         
                 
    if ver5add == 1:
        ionslabel=ver5name      
    
    return ions,coodAtom,totalion,coodocp
     
def compdescript(defelem,aparam2,sparam,aparam3,reference):
     
    filename=["AN","EN","MP","PN","PG","MN","AW","AR","IR","CoR","CrR","spdf"]     
    ini_r=[["AN","EN","MP","PN","PG","MN","AW","AR","IR","CoR","CrR","spdf"]]     

    ans_df_dict={}
    ans_df_hiki_dict={}
    ans_df_kake_dict={}
    df_dict={}
    df_kake_dict={}
    df_hiki_dict={}

    ini_r = {"AN":"AN","EN":"EN","MP":"MP","PN":"PN","PG":"PG","MN":"MN","AW":"AW","AR":"AR","IR":"IR","CoR":"CoR","CrR":"CrR","spdf":"spdf"}
    ini_r["AN"] = {k:k for k in range(7)}
    ini_r["EN"] = {k:k for k in range(7)}
    ini_r["MP"] = {k:k for k in range(7)}
    ini_r["PN"] = {k:k for k in range(7)}
    ini_r["PG"] = {k:k for k in range(7)}
    ini_r["MN"] = {k:k for k in range(7)}
    ini_r["AW"] = {k:k for k in range(7)}
    ini_r["AR"] = {k:k for k in range(7)}
    ini_r["IR"] = {k:k for k in range(7)}
    ini_r["CoR"] = {k:k for k in range(7)}
    ini_r["CrR"] = {k:k for k in range(7)}
    ini_r["spdf"] = {k:k for k in range(7)}
  
    for i in filename:
        ini_r[i][1]=2

    for k in filename:
        ini_r[k][2]=3

    ini_r['AN'][4]=120
    ini_r['AN'][3]=-0.2*ini_r['AN'][4]
    ini_r['AN'][5]=102
    ini_r['AN'][6]=0

    ini_r["EN"][4]=5.0
    ini_r["EN"][3]=-0.2*ini_r["EN"][4]
    ini_r["EN"][5]=50
    ini_r["EN"][6]=0.2
            
    ini_r["MP"][4]=5000
    ini_r["MP"][3]=-0.2*ini_r["MP"][4]
    ini_r["MP"][5]=50
    ini_r["MP"][6]=ini_r["MP"][4]/25
     
    ini_r["PN"][4]=10
    ini_r["PN"][3]=-0.2*ini_r["PN"][4]
    ini_r["PN"][5]=20
    ini_r["PN"][6]=ini_r["PN"][4]/25
    
    ini_r["PG"][4]=20
    ini_r["PG"][3]=-0.2*ini_r["PG"][4]
    ini_r["PG"][5]=20
    ini_r["PG"][6]=ini_r["PG"][4]/25
                            
    ini_r["MN"][4]=120
    ini_r["MN"][3]=-0.2*ini_r["MN"][4]
    ini_r["MN"][5]=102
    ini_r["MN"][6]=ini_r["MN"][4]/25
                        
    ini_r["AW"][4]=400
    ini_r["AW"][3]=-0.2*ini_r["AW"][4]
    ini_r["AW"][5]=50
    ini_r["AW"][6]=ini_r["AW"][4]/25
                                       
    ini_r["AR"][4]=3.2
    ini_r["AR"][3]=-0.2
    ini_r["AR"][5]=50
    ini_r["AR"][6]=ini_r["AR"][4]/25

    ini_r["IR"][4]=3.2
    ini_r["IR"][3]=-0.2
    ini_r["IR"][5]=50
    ini_r["IR"][6]=ini_r["IR"][4]/25

    ini_r["CoR"][4]=3.2
    ini_r["CoR"][3]=-0.2
    ini_r["CoR"][5]=50
    ini_r["CoR"][6]=ini_r["CoR"][4]/25
    
    ini_r["CrR"][4]=3.2
    ini_r["CrR"][3]=-0.2
    ini_r["CrR"][5]=50
    ini_r["CrR"][6]=ini_r["CrR"][4]/25
                
    ini_r["spdf"][4]=5
    ini_r["spdf"][3]=1
    ini_r["spdf"][5]=4
    ini_r["spdf"][6]=0
    
    if aparam2 != "":     
        for ff in filename:     
            ini_r[ff][6]=aparam2
     
     
    if histdef != "":     
        f= open(histdef)
        linesem = f.readlines()
        for line in linesem:
            line.rstrip('\n')
        
        for k in linesem:   
            field=k.split()  
            if bool(re.search('^\#', field[0])):
                continue     
            label = field[0]
            ie =1
            while ie<=6 :
                ini_r[label][ie]=field[ie]
                ie = ie+1

    #aparam=[]
    #aparam3=1
    numatom={}
    if sparam != '':
        if bool(re.search(r'T', sparam, re.I)):     
            YY=defvasptable()     
            inputf=reference[0]     
            XX =readposcar(inputf)     
            i=1     
            atom=[]
            while len(XX[1]) -1 < 1:
                XX[1].append('')
            if XX[1][1] == "":    
                print("POTCAR is read......\n")
                vrh = str(check_output('grep VRH POTCAR',shell=True))#.split('\n'))
                vrh = vrh.split('\\n')
                for k in vrh:
                    if bool(re.search('(VRHFIN =)(.+)(\:)', k)):
                        search =re.search('(VRHFIN =)(.+)(\:)', k)
                        ate2 = search.group(2)
                        while len(atom) -1 < i:
                            atom.append('')
                        atom[i] = ate2
                        while len(XX[0]) -1 < i-1:
                            XX[0].append('')
                        numatom[int(YY[0][atom[i]])]=XX[0][i-1]     
                    i = i + 1
                    #print(numatom)     
            else:    
                ia=1
                while ia<=XX[2]:
                    try:
                        numatom[int(YY[0][XX[1][ia]])]
                    except:
                        numatom[int(YY[0][XX[1][ia]])]=0
                    numatom[int(YY[0][XX[1][ia]])]=float(numatom[int(YY[0][XX[1][ia]])])+1*float(XX[3][ia]) 
                    ia = ia + 1

            f =open("out.composition_label",'w')
            i =1
            while i<=103 :
                try:
                    numatom[i]
                except:
                    numatom[i]=''
                
                if numatom[i] != '':
                    if int(numatom[i]) >0:
                        while len(YY[1])-1 < i:
                            YY[1].append('')
                        try:
                            compname
                        except:
                            compname=''
                        f.write("{}{}".format(YY[1][i],numatom[i]))
                        compname="{}{}{}".format(compname,YY[1][i],numatom[i])      
                    f.write("\n")
                i = i + 1
            f.close()      
            try:
                compname
            except:
                compname=''

            #print("composition: {}\n".format(compname))      
            reference[0]=compname      
     
    #incomp=reference[0]     
    x =compconv(reference) 
    y =readdefelem
    reference.append('')
    #if reference[1] == "":
    #    sigma=0.0 
    #else:
    #    sigma=reference[1] 

    PGBox={k: k for k in range(19)}
    def_PGBox={l: l for l in range(19)}
    for ii in range(19):
        PGBox[ii]=dict(def_PGBox)
    
    for FN in filename:     
        if FN == "PG":
            i=0
            while  i<=len(x[0]) - 1:
                ENatom1=x[2][i]      
                inty1=x[0][i]/x[3]
                j = i + 1
                while  j<=len(x[0]) - 1:    
                    if i >= j:
                       continue
                    ENatom2=x[2][j]      
                    inty2=x[0][j]/x[3]
                    if int(y(ENatom1,defelem)[FN][ENatom1]) > int(y(ENatom2,defelem)[FN][ENatom2]):     
                        kk1=y(ENatom2,defelem)[FN][ENatom2]  
                        kk2=y(ENatom1,defelem)[FN][ENatom1]
                    else:     
                        kk2=y(ENatom2,defelem)[FN][ENatom2]  
                        kk1=y(ENatom1,defelem)[FN][ENatom1]
                    
                    PGBox[int(kk1)][int(kk2)]=inty1+inty2+PGBox[int(kk1)][int(kk2)]
                    j = j + 1
                i= i + 1
                          
            #g=open("out.PGmatrix",'w')
            k_list_columns=[]
            k_list_index=[]       
            PGmtrx={}
            k=-1
            i=1
            while i<=18:
                j=i
                while j<=18:     
                    k = k + 1      
                    PGmtrx[int(k)]=PGBox[int(i)][int(j)]  
                    k_list_index.append("{:.6f}".format(PGmtrx[k]))
                    k_list_columns.append('PNmatrix_{}'.format(k))
                    j = j + 1
                i = i + 1
            k_dict=dict(zip(k_list_columns,k_list_index))
            k_df=pd.DataFrame(k_dict,index=['test'])    
       
        PGBox={k: k for k in range(19)}
        def_PGBox={l: 0 for l in range(19)}
        for ii in range(19):
            PGBox[ii]=dict(def_PGBox)
        if FN == "PN":
            i = 0
            while i<=len(x[0]) -1:     
                ENatom1=x[2][i]      
                inty1=x[0][i]/x[3]
                j=i+1
                while  j<=len(x[0])-1:      
                    if i >= j:
                        continue     
                    ENatom2=x[2][j]      
                    inty2=x[0][j]/x[3]      
     
                    if y(ENatom1,defelem)[FN][ENatom1] > y(ENatom2,defelem)[FN][ENatom2]:     
                        kk1=y(ENatom2,defelem)[FN][ENatom2]  
                        kk2=y(ENatom1,defelem)[FN][ENatom1]      
                    else:     
                        kk2=y(ENatom2,defelem)[FN][ENatom2]  
                        kk1=y(ENatom1,defelem)[FN][ENatom1]      
                    j = j + 1
                    PGBox[int(kk1)][int(kk2)]=inty1+inty2+PGBox[int(kk1)][int(kk2)]      
                i = i + 1
            h_list_index=[]
            h_list_columns=[]     
            k=-1
            i=1
            PGmtrx={m:0 for m in range(8)}
            while i<=7 :
                j=i
                while j<=7:      
                    k = k + 1      
                    PGmtrx[k]=PGBox[i][j]      
                    h_list_index.append("{:1.6f}".format(PGmtrx[k]))
                    h_list_columns.append("PGmatrix_{}".format(k))
                    j = j + 1
                i = i + 1     
            h_dict=dict(zip(h_list_columns,h_list_index))
            h_df=pd.DataFrame(h_dict,index=['test'])    
                     
     
        #PGBox=[]  
        #PGmtrx=[]      
        if FN == "spdf":     
            i=0
            while i<=len(x[0])-1:      
                ENatom1=x[2][i]      
                inty1=x[0][i]/x[3]
                j=i+1
                while j<=len(x[0])-1:     
                    if i >= j:
                        continue   
                    ENatom2=x[2][j]      
                    inty2=x[0][j]/x[3]      
     
                    if y(ENatom1,defelem)[FN][ENatom1] > y(ENatom2,defelem)[FN][ENatom2]:     
                        kk1=y(ENatom2,defelem)[FN][ENatom2]
                        kk2=y(ENatom1,defelem)[FN][ENatom1]      
                    else:     
                        kk2=y(ENatom2,defelem)[FN][ENatom2]  
                        kk1=y(ENatom1,defelem)[FN][ENatom1]
                        
                    if  kk1 == 'nodata' or kk2 == 'nodata':
                        PGBox[11][11]=inty1+inty2+PGBox[11][11]
                    else:
                        PGBox[int(kk1)][int(kk2)]=inty1+inty2+PGBox[int(kk1)][int(kk2)]
                    j = j+1
                i = i + 1
                 
            #l = open("out.SPDFmatrix",'w')      
     
            k=-1
            i=1
            l_list_index=[]
            l_list_columns=[]
            while i<=4:
                j=i
                while j<=4:     
                    k = k + 1      
                    PGmtrx[k]=PGBox[i][j]      
                    l_list_index.append("{:1.6f}".format(PGmtrx[k]))
                    l_list_columns.append('SPDFmatrix_{}'.format(k))      
                    j = j + 1
                i = i + 1
            l_dict=dict(zip(l_list_columns,l_list_index))
            l_df=pd.DataFrame(l_dict,index=['test']) 
             
        #'list.{}-distfunc'.format(FN), )
        #f_list.write("# Atom-Atom characteristics Concentration\n")      
        i=0
        f_list_index=[]
        f_list_columns=[]
        while  i <= len(x[0])-1:
            ENatom=x[2][i]
            inty=x[0][i]/x[3]
            if y(ENatom,defelem)[FN][ENatom] != 'nodata':      
                f_list_index.append("{} {:1.6f} {:1.6f}".format(ENatom,float(y(ENatom,defelem)[FN][ENatom]),inty))
                f_list_columns.append('out.{}_{}'.format(FN,i))
            else:
                f_list_index.append("{} {} {:1.6f}".format(ENatom,y(ENatom,defelem)[FN][ENatom],inty))
                f_list_columns.append('out.{}_{}'.format(FN,i))
            i = i + 1
        f_dict=dict(zip(f_list_columns,f_list_index))
        f_df = pd.DataFrame(f_dict,index=['test'])
        ans_df_dict[FN]=f_df
        if aparam3 == 'T':
            #m=open("list.{}{}-distfunc".format(FN,FN),'w')      
            #m.write("# Atom*Atom characteristics^2 Concentration^2\n")
            m_list_index=[]
            m_list_columns=[]      
            i=0
            while i<=len(x[0])-1:     
                ENatom1=x[2][i]       
                inty1=x[0][i]/x[3]
                j=i+1
                while j <= len(x[0]) - 1 :     
                    if i >= j:
                        continue     
                    ENatom2=x[2][j]      
                    inty2=x[0][j]/x[3]    
                    m_list_index.append("{}-{} {:1.6f} {:1.6f}".format(ENatom1,ENatom2,math.log(float(y(ENatom1,defelem)[FN][ENatom1]))+math.log(float(y(ENatom2,defelem)[FN][ENatom2])),inty1+inty2))
                    m_list_columns.append('out.{}{}_{}'.format(FN,FN,i))
                    j = j + 1
                i = i + 1
            #m.close()
            m_dict=dict(zip(m_list_columns,m_list_index))
            m_df=pd.DataFrame(m_dict,index=['test']) 
            ans_df_kake_dict[FN]=m_df   
            
            #o = open("list.{}-{}-distfunc".format(FN,FN),'w')      
            #o.write("# ABS(Atom-Atom) characteristics Concentration\n")      
            i=0
            o_list_index=[]
            o_list_columns=[]
            while i<=len(x[0])-1:      
                ENatom1=x[2][i]      
                inty1=x[0][i]/x[3]
                j=i+1
                while j <= len(x[0])-1:     
                    if i >= j:
                        continue     
                    ENatom2=x[2][j]      
                    inty2=x[0][j]/x[3]    
                    o_list_index.append("{}-{} {:1.6f} {:1.6f}".format(ENatom1,ENatom2,abs(float(y(ENatom1,defelem)[FN][ENatom1])-float(y(ENatom2,defelem)[FN][ENatom2])),inty1+inty2))      
                    o_list_columns.append('out.{}-{}_{}'.format(FN,FN,i))
                    j = j + 1
                i= i + 1
            o_dict=dict(zip(o_list_columns,o_list_index))
            o_df=pd.DataFrame(o_dict,index=['test'])
            ans_df_hiki_dict[FN]=o_df
            #o.close()   

        list_reference = reference[0].split()
        #list_reference[0]="list.{}-distfunc".format(FN)     
        list_reference.append(float(ini_r[FN][1]))      
        list_reference.append(float(ini_r[FN][2]))      
        list_reference.append(float(ini_r[FN][3]))      
        list_reference.append(float(ini_r[FN][4]))      
        list_reference.append(float(ini_r[FN][5]))
        #print(list_reference)
        if ini_r[FN][6] =='T':
            list_reference.append(ini_r[FN][6])
        else:
            list_reference.append(float(ini_r[FN][6]))    
        #       if ($aparam[3] == 0){$reference[6]=0 } 
        #if aparam3 == 0:
        #    list_reference[6]=0
        
        z = dfmake(*list_reference,histdef,aparam2,aparam3,ans_df_dict[FN],FN)
        old_col=list(z[6].columns)
        new_col=[]
        for col in range(len(old_col)):
            new_col.append('{}_{}'.format(FN,col))
        z[6].set_axis(new_col, axis='columns',inplace=True)
        df_dict[FN]=z[6]
        #os.system('mv {} out.{}'.format(z[7],FN))     
        #outcompfile.append("out.{}".format(FN))
        #outcompfile.append(z[7])

        if aparam3 == 'T':        
            #list_reference[0]="list.{}{}-distfunc".format(FN,FN)     
            list_reference[1]=float(ini_r[FN][1])     
            list_reference[2]=float(ini_r[FN][2])     
            list_reference[3]=-0.2*math.log(float(ini_r[FN][4]))     
            list_reference[4]=2*math.log(float(ini_r[FN][4]))     
            list_reference[5]=float(ini_r[FN][5])
            list_reference[6]=2*math.log(float(ini_r[FN][4]))/float(ini_r[FN][5])      
            #if aparam3 == 0:        
            #    list_reference[6]=0
            z = dfmake(*list_reference,histdef,aparam2,aparam3,ans_df_kake_dict[FN],FN)
            old_col=list(z[6].columns)
            new_col=[]
            for col in range(len(old_col)):
                new_col.append('{}{}_{}'.format(FN,FN,col))
            z[6].set_axis(new_col, axis='columns',inplace=True)
            df_kake_dict[FN] =z[6]


            #os.system('mv {} out.{}{}'.format(z[7],FN,FN))      
            #outcompfile.append("out.{}{}".format(FN,FN))   
            #outcompfile.append(z[7]) 

            #list_reference[0]="list.{}-{}-distfunc".format(FN,FN)      
            list_reference[1]=float(ini_r[FN][1])       
            list_reference[2]=float(ini_r[FN][2])      
            list_reference[3]=float(ini_r[FN][3])      
            list_reference[4]=float(ini_r[FN][4])      
            list_reference[5]=float(ini_r[FN][5])
            if ini_r[FN][6] =='T':
                list_reference[6]=ini_r[FN][6]
            else:    
                list_reference[6]=float(ini_r[FN][6]) 

            #if aparam3 == 0:
            #list_reference[6]=0
            z = dfmake(*list_reference,histdef,aparam2,aparam3,ans_df_hiki_dict[FN],FN)
            old_col=list(z[6].columns)
            new_col=[]
            for col in range(len(old_col)):
                new_col.append('{}-{}_{}'.format(FN,FN,col))
            z[6].set_axis(new_col, axis='columns',inplace=True)     
            df_hiki_dict[FN]=z[6] 
            #os.system('mv {} out.{}-{}'.format(z[7],FN,FN))      
            #outcompfile.append("out.{}-{}".format(FN,FN)) 
            #outcompfile.append(z[7]) 

    return k_df,h_df,l_df,df_dict,df_kake_dict,df_hiki_dict


     
#compdescript(defelem)

"""  
lsafter=str(sp.check_output("ls -alh --full-time",shell=True))
ls_list =lsafter.split('\\n')
ls_list.pop(0)

for aft in ls_list:
    ruleout=0
    for bfr in ls_bflist:
        if aft == bfr:
            ruleout =ruleout+1
    aft=aft.split()
    if aft[-1] == '.'or aft[-1]=='..' or aft[-1]=="'":
        ruleout=ruleout+1
    if ruleout==0:
        print('Output file: {}'.format(aft[-1]))
"""     
