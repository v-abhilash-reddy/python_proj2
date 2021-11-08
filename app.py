from flask import Flask,render_template,redirect,url_for,request
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

bool_dict = {}
sample_input_path = "./sample_input"
sample_output_path = "./transciptsIITP"
def handle_file_save(FileObject,req_resp_name):
    if not FileObject.filename:
        bool_dict[f"{req_resp_name}"] = "Didn't upload any file.Its ok its optional"
        return   
    file_name = FileObject.filename
    sample_input= os.path.join(os.getcwd(),"sample_input")
    os.makedirs(sample_input,exist_ok = True)
    if os.path.exists(f"./sample_input/{file_name}"):
        os.remove(f"./sample_input/{file_name}")
    filename = secure_filename(file_name)
    FileObject.save(os.path.join(sample_input_path,filename))
    bool_dict[f"{req_resp_name}"] = "Uploaded Successfully"
    return 
@app.route('/',methods=['GET','POST'])
def index(): 
    return render_template('index.html',data = bool_dict)

@app.route('/create_range',methods=['GET','POST'])
def create_range():
    os.makedirs(sample_output_path,exist_ok = True)
    range_str = request.form['range']
    try :
        start_roll,end_roll = range_str.split('-')
        #check whether they are numbers
    except:
        bool_dict['create_range'] = 'Invalid Input'
        return redirect(url_for('index'))
    #Python code to create pdfs 
    bool_dict['create_range'] = 'Created Successfully'
    # send list of not rollnumbers present in the given range
    return redirect(url_for('index'))

@app.route('/create_all',methods=['GET','POST'])
def create_all():
    os.makedirs(sample_output_path,exist_ok = True)
    return redirect(url_for('index'))
@app.route('/seal',methods=['GET','POST'])
def seal():
    FileObject = request.files.get("seal")
    handle_file_save(FileObject,"seal")
    return redirect(url_for('index'))


@app.route('/signature',methods=['GET','POST'])
def signature():
    FileObject = request.files.get("signature")
    handle_file_save(FileObject,"signature")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)