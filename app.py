from flask import Flask,render_template,redirect,url_for,request
import os,csv
import re
import pandas as pd
from werkzeug.utils import secure_filename
import func
app = Flask(__name__)

bool_dict = {}
sample_input_path = "./sample_input"
sample_output_path = "./transcriptsIITP"

def handle_file_save(FileObject,req_resp_name):
    sample_input= os.path.join(os.getcwd(),"sample_input")
    os.makedirs(sample_input,exist_ok = True)
    if FileObject.filename :
        file_name = FileObject.filename
        filename = secure_filename(file_name)
        FileObject.save(os.path.join(sample_input_path,filename))
        return True
    elif os.path.exists(f"./sample_input/{req_resp_name}"): return True
    else : return False 
     

def check_roll(rollno):
    pattern = re.compile(r'\d\d\d\d\w\w\d\d') 
    check = re.search(pattern,rollno)
    if check == None:
        return True
    return False

def check_files():
    c1 = os.path.exists('./sample_input/grades.csv')
    c2 = os.path.exists('./sample_input/names-roll.csv')
    c3 = os.path.exists('./sample_input/subjects_master.csv')
    return c1 and c2 and c3
@app.route('/',methods=['GET','POST'])
def index(): 
    return render_template('index.html',data = bool_dict)

@app.route('/upload_files',methods=['GET','POST'])
def upload_files(): 
    bool_dict['upload_files'] = ''
    c1 = handle_file_save(request.files.get("grades"),"grades.csv")
    c2 = handle_file_save(request.files.get("names-roll"),"names-roll.csv")
    c3 =handle_file_save(request.files.get("subjects_master"),"subjects_master.csv")
    if c1 and c2 and c3:
        bool_dict['upload_files'] = "Uploaded Successfully"
    else:
        string = "didn't upload" + " grades.csv" if not c1 else ""+" names-roll.csv" if not c2 else ""+" subjects_master.csv" if not c3 else ""+"files"
        bool_dict['upload_files'] = string
    return redirect(url_for('index'))

@app.route('/create_range',methods=['GET','POST'])
def create_range():
    bool_dict['create_range'],bool_dict['missing_nums'] = '',[]
    os.makedirs(sample_output_path,exist_ok = True)
    range_str = request.form['range']
    try:
        start_roll,end_roll = range_str.split('-')
    except:
        bool_dict['create_range'] = 'Invalid Input'
        return redirect(url_for('index'))

    if check_roll(start_roll) or check_roll(end_roll):
        bool_dict['create_range'] = 'Invalid Input'
        return redirect(url_for('index'))
    elif not check_files():
        bool_dict['create_range'] = "plz upload the files some files are missing"
        return redirect(url_for('index'))      
    nr = pd.read_csv('./sample_input/names-roll.csv')
    sm = pd.read_csv('./sample_input/subjects_master.csv')
    names_data = open("./sample_input/grades.csv","r")
    names_csv = csv.reader(names_data)
    names_list = [list(record) for record in names_csv][1:]

    missing_nums = func.generate_transcripts(nr,sm,names_list,start_roll,end_roll)
    bool_dict['create_range'] = 'Created Successfully'
    bool_dict['missing_nums'] = missing_nums.copy()
    return redirect(url_for('index'))

@app.route('/create_all',methods=['GET','POST'])
def create_all():
    bool_dict['create_all']= ''
    bool_dict['create_range'],bool_dict['missing_nums'] = '',[]
    os.makedirs(sample_output_path,exist_ok = True)
    if not check_files():
        bool_dict['create_range'] = "plz upload the files some files are missing"
        return redirect(url_for('index')) 
    nr = pd.read_csv('./sample_input/names-roll.csv')
    sm = pd.read_csv('./sample_input/subjects_master.csv')
    names_data = open("./sample_input/grades.csv","r")
    names_csv = csv.reader(names_data)
    names_list = [list(record) for record in names_csv][1:]
    func.generate_transcripts(nr,sm,names_list)
    bool_dict['create_all'] = 'Created Successfully'
    return redirect(url_for('index'))

@app.route('/seal',methods=['GET','POST'])
def seal():
    bool_dict['seal'] = ''
    handle_file_save(request.files.get("seal"),"seal.csv")
    return redirect(url_for('index'))


@app.route('/signature',methods=['GET','POST'])
def signature():
    bool_dict['signature']= ''
    handle_file_save(request.files.get("signature"),"signature.csv")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)