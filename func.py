from fpdf import FPDF
import csv,os,re
import pandas as pd

def generate_header_layout(pdf,*stud_info):
    pdf.set_font("Times",'B',size=10)
    pdf.image('./static/photos/Picture.png' ,15,11,30,25)
    pdf.image('./static/photos/Picture3.png',50,11,300,25)
    pdf.image('./static/photos/Picture.png' ,365,11,30,25)

    pdf.rect(10,10,390,277)
    pdf.rect(10,40,390,0)
    pdf.rect(50,11,0,29)
    pdf.rect(360,11,0,29)
    pdf.rect(95,43,240,13)
    
    lst,x,y= ["INTERIM TRANSCRIPT","TRANSCRIPT","INTERIM TRANSCRIPT"],10,36
    for item in lst:
        pdf.set_xy(x,36)
        pdf.cell(25,5,item)
        x+=175
    x=0
    for index,item in enumerate(["Roll No:","Name:","Year of Admission:","Programme:","Course:"]):
        x+=95
        k=((index)//3) * 6
        pdf.set_xy(x,43+k)
        pdf.set_font("Times",'B',size=10)
        pdf.cell(10,7,item)
        pdf.set_x(x+2*len(item))
        pdf.set_font("Times",'',size=10)
        pdf.cell(10,7,str(stud_info[index]))
        x%=285
    
    return 


def generate_cpi_credits(x,y,w,pdf,spi,cpi,total_credits):
    pdf.set_font("Times",'B',size=8)
    summ_list = [f"Credits taken: {total_credits}",f"Credits cleared: {total_credits}",f"SPI: {round(spi,2)}",f" CPI:{round(cpi,2)}"]
    for item in summ_list:
        pdf.set_xy(x,y)
        pdf.cell(10,7,item) 
        x+=(w/4)
    return


def generate_footer_layout(mth,pdf):
    pdf.rect(10,mth,390,277)
    pdf.set_xy(19.8,mth+(287-mth)/2)
    pdf.cell(15,7,"Date of Issue")
    pdf.rect(pdf.get_x()+5,pdf.get_y()+5,30,0)
    pdf.rect(350,pdf.get_y(),30,0)
    pdf.set_xy(350,pdf.get_y())
    pdf.cell(15,7,"Assistant Registrar(Academic)")
    return

def generate_data(nr,sm,names_list):   
    nr_dict = {}
    for i in range(len(nr)): nr_dict[nr.at[i,"Roll"]] = nr.at[i,"Name"]
    sm_dict = {}
    for i in range(len(sm)): 
        sm_dict[sm.at[i,"subno"]] = [sm.at[i,"subno"],sm.at[i,"subname"],sm.at[i,"ltp"],sm.at[i,"crd"]]   
    table_dict = {}
    for row in names_list:
        rollno,semno,subcode,credit,grade,Sub_Type = row
        st_list = sm_dict[f"{subcode}"].copy()
        grade = str(grade)
        st_list.append(grade)
        if (rollno,semno) not in table_dict:
            table_dict[rollno,semno] = [["Sub Code","Subject Name","L-T-P","CRD","GRD"]]
        table_dict[rollno,semno].append(st_list)
    return table_dict

def generate_rollno_list(nr,start_roll,end_roll):
    nr_dict,missing_nums,existing_nums={},[],[]
    for i in range(len(nr)): nr_dict[nr.at[i,"Roll"]] = nr.at[i,"Name"]
    start_roll_no,end_roll_no = int(start_roll[6:]),int(end_roll[6:])
    st = start_roll[:6]
    for i in range(start_roll_no,end_roll_no+1):
        if len(str(i))==1: num = "0"+str(i)
        else: num = str(i)
        rollno = st+num
        if rollno not in nr_dict:
            missing_nums.append(rollno)
        else :
            existing_nums.append([rollno,nr_dict[rollno]]) 
    return pd.DataFrame(existing_nums,columns = ["Roll","Name"]),missing_nums

def generate_transcripts(nr,sm,names_list,start_roll='',end_roll=''):
    credit_map = {'AA':10,'AB':9,'BB':8,'BC':7,'CC':6,'CD':5,'DD':4,'F':0,'I':0,
                'AA*':10,'AB*':9,'BB*':8,'BC*':7,'CC*':6,'CD*':5,'DD*':4,'F*':0,'I*':0}
    courses = {"CS":"Computer Science and Technology","EE":"Electrical Engineering","ME":"Mechanical Engineering","CE":"Civil and Environmental Engineering","CB":"Chemical Engineering","MM":"Metallurgical and Materials Engineering"}
    table_dict= generate_data(nr,sm,names_list)
    missing_nums = []
    if start_roll:
        nr,missing_nums= generate_rollno_list(nr,start_roll,end_roll)
    for index,row in nr.iterrows():
        pdf = FPDF("L" , "mm" ,"A3")
        pdf.add_page()
        roll,name,cpi= row["Roll"],row["Name"],0
        generate_header_layout(pdf,roll,name,2000+int(roll[0:2]),'Btech',courses[roll[4:6]])
        pdf.set_font("Times", size=8)
        col_width_list = [15,70,13,10,10]
        coll_width = sum(col_width_list)
        stx,sty,mth,count,line_height= 19.8,60,0,1,4
        while count<=8:
            if (roll,str(count)) not in table_dict:
                break
            data = table_dict[roll,str(count)]
            credits = sum([item[3]*credit_map[item[4].strip()] for item in data[1:]])
            total_credits = sum([item[3] for item in data[1:]])
            spi = credits/total_credits
            cpi+=spi
            prestx = stx
            pdf.set_xy(stx,sty)
            pdf.set_font("Times",'B',size=8)
            pdf.cell(10,7,f"Semester {count}")
            pdf.set_xy(stx,sty+7)
            sum1 = sty+7
            for row in data:   
                for ind,datum in enumerate(row):
                    pdf.multi_cell(col_width_list[ind], line_height, str(datum), border=1,align="C", ln=3, max_line_height=pdf.font_size)
                pdf.set_font("Times",'',size=8)
                sum1+=line_height
                pdf.set_xy(stx,sum1)
            stx+=coll_width+10
            pdf.rect(prestx,sum1+2,100,7)
            generate_cpi_credits(prestx,sum1+2,100,pdf,spi,cpi/count,total_credits)
            mth = max(mth,sum1+10)
            if count%3==0:
                stx=19.8
                pdf.rect(10,mth,390,0)
                sty=mth+2
            count+=1

        generate_footer_layout(mth,pdf)
        pdf.output('./transcriptsIITP/{}.pdf'.format(roll))
    return missing_nums

# generate_transcripts(nr,sm,names_list,start_roll='0601CS01',end_roll='0601CS28')

