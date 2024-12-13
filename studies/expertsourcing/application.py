from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd
import os
import datetime
from flask_sqlalchemy import SQLAlchemy
from itertools import permutations
basedir = os.path.abspath(os.path.dirname(__file__))


application = Flask(__name__)


# set up sqlite database
application.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'accountability.sqlite')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SECRET_KEY'] = ''
application.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(application)


df = pd.read_csv("data/accountability_questions.csv")
df = df.sample(frac=1).reset_index(drop=True)
instance_list = list(range(1000))  # df.id.tolist()  # 1000 instances
instances_per_worker = 10
num_workers = 300
annos_per_instance = 3
worker_instance_1phase_dict = {}

# shuffle the instances, then assign to workers.
# num_instances should be a multiple of instances_per_worker
for i in range(annos_per_instance):  # shuffle and assign for 3 times
    random.seed(i)
    random.shuffle(instance_list)
    chunks = [instance_list[i:(i+instances_per_worker)]
              for i in range(0, len(instance_list), instances_per_worker)]
    for j, c in enumerate(chunks):
        worker_instance_1phase_dict[i *
                                    len(instance_list)/instances_per_worker+j] = c
worker_instance_3phase_dict = {}
for i in range(0, 300):
    id1 = i
    id2 = (i-i//100*100+1) % 100+i//100*100
    id3 = (i-i//100*100+2) % 100+i//100*100
    instance_list_per_worker = worker_instance_1phase_dict[id1] + \
        worker_instance_1phase_dict[id2]+worker_instance_1phase_dict[id3]
    if len(set(instance_list_per_worker)) != 30:
        print('duplicate worker instance queue', i)
    worker_instance_3phase_dict[i] = instance_list_per_worker
# check if the assignment is correct, phase 1-3
for phase in [1,2,3]:
    check_dict = {i:0 for i in range(1000)}
    for w, l in worker_instance_3phase_dict.items():
        for i in l[(phase-1)*10:phase*10]:
            check_dict[i] += 1
    for k in check_dict:
        if check_dict[k] != 3:
            print('!=3 annotation instance id:', k, check_dict[k])

# Get all permutations of [1, 2, 3]
treatment_order_list = list(permutations([1, 2, 3]))   
 # assign phase order to workers
worker_treatment_order_dict = {}
for i in range(0, 300):
    worker_treatment_order_dict[i] = list(treatment_order_list)[i % 6]

# print out the worker instance queue and phase order
for i in range(0, 10):
    print(worker_instance_3phase_dict[i], worker_treatment_order_dict[i])

def choices2options(input_string):
    result_list = input_string.split(') ')

    current_index = result_list[0]
    final_result = []
    for i in range(1, len(result_list)):
        items = result_list[i].split(" ")
        if i != len(result_list)-1:
            tmp_index = items[-1:][0]
            items = items[:len(items)-1]
        current_item = "{}) {}".format(current_index, " ".join(items))
        final_result.append(current_item)
        if i != len(result_list)-1:
            current_index =  tmp_index

    return final_result


class WorkerData(db.Model):
    # __tablename__ = 'workers'
    worker_id = db.Column(db.String(64), primary_key=True)
    hit_id = db.Column(db.String(64), nullable=False)
    assignment_id = db.Column(db.String(50), nullable=False)
    worker_queue_id = db.Column(db.Integer, nullable=False)  # from 0 to 299, determines the instance list and phase order, 
    finished = db.Column(db.Boolean, default=False)
    pass_attention_check = db.Column(db.Boolean, default=True)
    bonus = db.Column(db.Integer, default=None)
    enter_time = db.Column(db.DateTime, default=datetime.datetime.now())
    exit_time = db.Column(db.DateTime, default=None)

    def __repr__(self):
        return '<Worker %r>' % self.worker_id

    def __init__(self, worker_id, hit_id, assignment_id):
        self.worker_id = worker_id
        self.hit_id = hit_id
        self.assignment_id = assignment_id
        # assign a random instance list to the worker
        assigned_worker_queue_ids = WorkerData.query.filter_by(
            pass_attention_check=True).with_entities(WorkerData.worker_queue_id).all()
        # Extract the assigned_worker_queue_id values from the result
        assigned_worker_queue_ids = [
            id for (id,) in assigned_worker_queue_ids]
        print('assigned_worker_queue_ids: ', assigned_worker_queue_ids)
        self.worker_queue_id = random.choice(
            list(set(worker_instance_3phase_dict.keys()) - set(assigned_worker_queue_ids)))


class PreSurveyData(db.Model):
    worker_id = db.Column(db.String(64), primary_key=True)
    age = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(64), nullable=False)
    education = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Worker %r>' % self.worker_id

    def __init__(self, worker_id, age, gender, education):
        self.worker_id = worker_id
        self.age = age
        self.gender = gender
        self.education = education


class InstructionData(db.Model):
    worker_id = db.Column(db.String(64), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Worker %r>' % self.worker_id

    def __init__(self, worker_id):
        self.worker_id = worker_id


class PhaseInstructionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(64), unique=False)
    phase_id = db.Column(db.Integer, unique=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Worker %r>' % self.worker_id

    def __init__(self, worker_id, phase_id):
        self.worker_id = worker_id
        self.phase_id = phase_id


class TaskData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(64), unique=False)
    task_id = db.Column(db.Integer, unique=False)
    phase_id = db.Column(db.Integer, unique=False)
    q1_a = db.Column(db.String(64), unique=False)
    q0_a = db.Column(db.String(64), unique=False)
    q2_a = db.Column(db.String(64), unique=False, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Worker %r, Task %r>' % self.worker_id, self.task_id

    def __init__(self, worker_id, task_id, phase_id, q1_a, q0_a, q2_a):
        self.worker_id = worker_id
        self.task_id = task_id
        self.phase_id = phase_id
        self.q1_a = q1_a
        self.q0_a = q0_a
        self.q2_a = q2_a


class TaskAttentionCheckData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(64), unique=False)
    task_id = db.Column(db.Integer, unique=False)
    phase_id = db.Column(db.Integer, unique=False)
    q1_a = db.Column(db.String(64), unique=False)
    q0_a = db.Column(db.String(64), unique=False)
    q2_a = db.Column(db.String(64), unique=False, nullable=True)
    pass_attention_check = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Worker %r, Task %r>' % self.worker_id, self.task_id

    def __init__(self, worker_id, task_id, phase_id, q1_a, q0_a, q2_a, pass_attention_check):
        self.worker_id = worker_id
        self.task_id = task_id
        self.phase_id = phase_id
        self.q1_a = q1_a
        self.q0_a = q0_a
        self.q2_a = q2_a
        self.pass_attention_check = pass_attention_check


class PostSurveyData(db.Model):
    worker_id = db.Column(db.String(64), primary_key=True)
    q1_a = db.Column(db.PickleType, unique=False)
    q2_a = db.Column(db.PickleType, unique=False)
    q3_a = db.Column(db.PickleType, unique=False)
    q4_a = db.Column(db.PickleType, unique=False)
    pass_attention_check = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Worker %r>' % self.worker_id

    def __init__(self, worker_id, q1_a, q2_a, q3_a, q4_a, pass_attention_check):
        self.worker_id = worker_id
        self.q1_a = q1_a
        self.q2_a = q2_a
        self.q3_a = q3_a
        self.q4_a = q4_a
        self.pass_attention_check = pass_attention_check


@application.route('/test', methods=['GET', 'POST'])
def test_page():
    if request.method == 'POST':
        print(request.form.get('returnvalue'))
    return render_template("drag-example.html")


@application.route('/', methods=['GET', 'POST'])
def index():

    if request.method == "POST":
        worker_id = request.args.get('workerId')
        hit_id = request.args.get('hitId')
        assignment_id = request.args.get('assignmentId')
        print('worker_id, hit_id, assignment_id: ',
              worker_id, hit_id, assignment_id)

        if worker_id and hit_id and assignment_id:
            existing_worker = WorkerData.query.filter_by(
                worker_id=worker_id).first()
            if existing_worker:
                print('existing worker:', existing_worker.worker_id, existing_worker.hit_id, existing_worker.assignment_id, 
                      existing_worker.worker_queue_id, existing_worker.finished, existing_worker.pass_attention_check, existing_worker.bonus)
                return render_template("index.html", entered=True)
            else:
                new_worker = WorkerData(
                    worker_id=worker_id, hit_id=hit_id, assignment_id=assignment_id)
                print('new worker:', new_worker.worker_id, new_worker.hit_id, new_worker.assignment_id, 
                      new_worker.worker_queue_id, new_worker.finished, new_worker.pass_attention_check, new_worker.bonus)
                db.session.add(new_worker)
                db.session.commit()
                return redirect(url_for('instruction_page', workerId=worker_id))
        else:
            return 'Invalid request. Please add ?workerId=[workerId]&hitId=[hitId]&assignmentId=[assignmentId] to the URL.'
    return render_template("index.html", entered=False, new_tab=True) # open in new tab if true


@application.route('/presurvey', methods=['GET', 'POST'])
def presurvey_page():
    if request.method == "POST":
        worker_id = request.args.get('workerId')
        gender = request.form.get('gender')
        age = request.form.get('age')
        education = request.form.get('education')
        timestamp = datetime.datetime.now()
        print('worker_id, gender, age, education, time: ',
              worker_id, gender, age, education, timestamp)
        data = PreSurveyData(worker_id=worker_id, age=age,
                             gender=gender, education=education)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('instruction_page', workerId=worker_id))
    worker_id = request.args.get('workerId')
    return render_template("presurvey.html", worker_id=worker_id)


@application.route('/instruction', methods=['GET', 'POST'])
def instruction_page():
    if request.method == "POST":
        worker_id = request.args.get('workerId')
        q1_a = request.form.get('q1')
        q2_a = request.form.get('q2')
        q3_a = request.form.get('q3')
        timestamp = datetime.datetime.now()
        print('worker_id, q1_a, q2_a, q3_a, time: ',
              worker_id, q1_a, q2_a, q3_a, timestamp)
        data = InstructionData(worker_id=worker_id)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('task_page', id=1, workerId=worker_id))
    worker_id = request.args.get('workerId')
    return render_template("instruction.html", worker_id=worker_id)


@application.route('/phase_instruction/<phase_id>', methods=['GET', 'POST'])
def phase_instruction_page(phase_id):
    if request.method == "POST":
        worker_id = request.args.get('workerId')
        timestamp = datetime.datetime.now()
        print('worker_id, time: ', worker_id, timestamp)
        data = PhaseInstructionData(worker_id=worker_id, phase_id=phase_id)
        db.session.add(data)
        db.session.commit()
        if int(phase_id) == 1:
            return redirect(url_for('task_page', id=1, workerId=worker_id))
        elif int(phase_id) == 2:
            return redirect(url_for('task_page', id=11, workerId=worker_id))
        elif int(phase_id) == 3:
            return redirect(url_for('task_page', id=21, workerId=worker_id))
    worker_id = request.args.get('workerId')
    worker = WorkerData.query.filter_by(worker_id=worker_id).first()
    treatment_id = 3 #worker_treatment_order_dict[worker.worker_queue_id][int(phase_id)-1]
    return render_template('phase_instruction.html', phase_id=int(phase_id), worker_id=worker_id, treatment_id=treatment_id)


@application.route('/task/<id>', methods=['GET', 'POST'])
def task_page(id):
    if request.method == "POST":
        worker_id = request.args.get('workerId')
        q1_a = request.form.get('q1')
        q0_a = request.form.get('q0')
        q2_a = request.form.get('q2')
        timestamp = datetime.datetime.now()
        print('worker_id, q1_a, q0_a, q2_a, time: ',
              worker_id, q1_a, q0_a, q2_a, timestamp)
        id = int(id)
        # check human label correctness
        worker = WorkerData.query.filter_by(worker_id=worker_id).first()
        # task4worker = worker_instance_3phase_dict[worker.worker_queue_id]
        # task4worker = df.loc[df['id'].isin(list(task4worker))]
        # gold_label = task4worker.iloc[int(id)-1]['answer']
        data = TaskData(worker_id=worker_id, task_id=id, phase_id=1, 
                        q1_a=q1_a, q0_a=q0_a,
                        q2_a=q2_a)
        db.session.add(data)
        db.session.commit()

        attn1 = random.randint(2, 9)
        attn2 = random.randint(11, 19)
        if id == 20:
            return redirect(url_for('postsurvey_page', workerId=worker_id))
        elif id == 6:
            return redirect(url_for('attention_check_page', id=id, workerId=worker_id))
        elif id == 13:
            return redirect(url_for('attention_check_page', id=id, workerId=worker_id))
        else:
            return redirect(url_for('task_page', id=id+1, workerId=worker_id))
    worker_id = request.args.get('workerId')
    print('worker_id: ', worker_id)
    worker = WorkerData.query.filter_by(worker_id=worker_id).first()
    print('worker_id, worker_worker_queue_id: ',
          worker_id, worker.worker_queue_id)
    #task4worker = worker_instance_3phase_dict[worker.worker_queue_id]
    #task4worker = df.loc[df['id'].isin(list(task4worker))]
    treatment_id = 3 #worker_treatment_order_dict[worker.worker_queue_id][(int(id)-1)//10]
    question = df.iloc[int(id)-1]['question']
    choices = df.iloc[int(id)-1]['choices']
    answer = df.iloc[int(id)-1]['answer']
    rationale = df.iloc[int(id)-1]['our_rationale']
    input = "Question: {}[mcq]Choices: {}".format(question, choices)
    options = choices2options(choices)
    print(options)
    return render_template('task.html', worker_id=worker_id, id=int(id), treatment_id=treatment_id, input=input, gpt_label=answer, gpt_explanation=rationale, options=options)


@application.route('/attention_check/<id>', methods=['GET', 'POST'])
def attention_check_page(id):
    if request.method == "POST":
        worker_id = request.args.get('workerId')
        worker = WorkerData.query.filter_by(worker_id=worker_id).first()
        treatment_id = worker_treatment_order_dict[worker.worker_queue_id][(int(id)-1)//10]
        q1_a = request.form.get('q1')
        q0_a = request.form.get('q0')
        q2_a = request.form.get('q2')
        timestamp = datetime.datetime.now()
        id = int(id)
        pass_attention_check = ("c)" in q1_a and q0_a == "Undecided" and q2_a == "7")
        data = TaskAttentionCheckData(worker_id=worker_id, task_id=id, 
                                      phase_id=1, 
                                      q1_a=q1_a, q0_a=q0_a, q2_a=q2_a, pass_attention_check=pass_attention_check)
        db.session.add(data)
        db.session.commit()
        print('worker_id, q1_a, q2_a, pass_attention_check, time: ',
              worker_id, q1_a, q2_a, pass_attention_check, timestamp)
        return redirect(url_for('task_page', id=id+1, workerId=worker_id))
    worker_id = request.args.get('workerId')
    worker = WorkerData.query.filter_by(worker_id=worker_id).first()
    treatment_id = 3#worker_treatment_order_dict[worker.worker_queue_id][(int(id)-1)//10]
    question = df.iloc[int(id)-1]['question']
    choices = df.iloc[int(id)-1]['choices']
    answer = df.iloc[int(id)-1]['answer']
    rationale = df.iloc[int(id)-1]['our_rationale']
    input = "Question: {}[mcq]Choices: {}".format(question, choices)
    options = choices2options(choices)
    return render_template('attention_check.html', worker_id=worker_id, id=int(id), treatment_id=treatment_id, input=input, gpt_label=answer, gpt_explanation=rationale, options=options)


@application.route('/postsurvey', methods=['GET', 'POST'])
def postsurvey_page():
    if request.method == "POST":
        worker_id = request.args.get('workerId')
        q1_a = [request.form.get('q1_phase1'), request.form.get('q1_phase2'), request.form.get('q1_phase3')]
        q2_a = [request.form.get('q2_phase1'), request.form.get('q2_phase2'), request.form.get('q2_phase3')]
        q3_a = [request.form.get('q3_phase1'), request.form.get('q3_phase2'), request.form.get('q3_phase3')]
        q4_a = [request.form.get('q4_phase1'), request.form.get('q4_phase2'), request.form.get('q4_phase3')]
        timestamp = datetime.datetime.now()
        print('q1_a, q2_a, q3_a, q4_a, time: ',
              q1_a, q2_a, q3_a, q4_a, timestamp)
        data = PostSurveyData(worker_id=worker_id, q1_a=q1_a, q2_a=q2_a, q3_a=q3_a, q4_a=q4_a, 
                              pass_attention_check=(q3_a == ['6', '2', '5']))
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('end_page', workerId=worker_id))
    worker_id = request.args.get('workerId')
    worker = WorkerData.query.filter_by(worker_id=worker_id).first()
    treatment_order = worker_treatment_order_dict[worker.worker_queue_id]
    # treatment_order = [3,1,2]
    questions = [
        {"id":"q1", "text":"I am confident in the AI-generated rationales. I feel that it works well."},
        {"id":"q2", "text":"The outputs of the AI rationalizer are very predictable."},
        {"id":"q3", "text":"The AI rationalizer is very reliable. I can count on it to be correct all the time."},
        {"id":"q4", "text":"I feel safe that when I rely on the AI rationalizer I will get the right rationales."},
        {"id":"q5", "text":"This is an attention check. Please select 5 as your response. The AI rationalizer is efficient in that it works very quickly."},
        {"id":"q6", "text":"The AI rationalizer can perform the task better than a novice human user."},
        {"id":"q7", "text":"I like using the AI rationalizer for understanding decision making process of a AI model."},
        {"id":"q8", "text":"Overall the AI rationalizer generates highly acceptable rationales of AI predictions."}
    ]
    random.shuffle(questions)
    return render_template("postsurvey.html", worker_id=worker_id, questions=questions)


@application.route('/end', methods=['GET', 'POST'])
def end_page():
    if request.method == "POST":
        worker_id = request.args.get('workerId')
        worker = WorkerData.query.filter_by(worker_id=worker_id).first()
        submit_url = f'https://www.mturk.com/mturk/externalSubmit?workerId={worker.worker_id}&assignmentId={worker.assignment_id}&hitId={worker.hit_id}'
        return redirect(submit_url)

    worker_id = request.args.get('workerId')
    worker_task_attention_check = TaskAttentionCheckData.query.filter_by(
        worker_id=worker_id).all()
    worker_survey_attention_check = PostSurveyData.query.filter_by(
        worker_id=worker_id).first().pass_attention_check
    pass_attention_check = all(
        [t.pass_attention_check for t in worker_task_attention_check]) and worker_survey_attention_check
    # for each treatment
    
    bonus = 0 if pass_attention_check == False else 0.07*30
    # update workerdata
    worker = WorkerData.query.get(worker_id)  # Retrieve the row to be updated
    worker.finished = True
    worker.pass_attention_check = pass_attention_check
    worker.bonus = bonus
    worker.exit_time = datetime.datetime.now()
    db.session.commit()
    return render_template("end.html", worker_id=worker_id, bonus=bonus, pass_attention_check=pass_attention_check)


# run the application.
if __name__ == "__main__":
    with application.app_context():
        db.drop_all()
        db.create_all()

    application.run(port=2020, host="0.0.0.0", debug=True)
