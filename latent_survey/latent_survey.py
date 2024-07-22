from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
import random
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = 'IDEATION2024'

# Set up Firebase Realtime Database

cred = credentials.Certificate('firebase_secret.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://needs-proj-default-rtdb.firebaseio.com/'
})

# Global variable to store phrases
actual_phrases = []
groups = []
# Reference to the Realtime Database
database_ref = db.reference('responses')

# List of questions
questions = [
    "Is the need impactful?: The need has the potential to create a real difference. This will delight the user.",
    "Is it an implicit need?: This is not a common requirement. Not a general requirement given to the designers.",
    "Is it obvious?: In all circumstances, the majority of the users will express this need. If 20 users were interviewed, the majority will share this need.",
    "Is it inefficient?: This will not have a positive effect on the user experience. Not going to improve the experience with the product, service or system."
]

# Initialize the CSV file
def init_csv(CSV_FILE):
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['name','email','video','group', 'phrase', 'impactful', 'implicit', 'obvious', 'inefficient'])
        df.to_csv(CSV_FILE, index=False)

# @app.route('/')
# def index():
#     print('HERE',url_for('instructions'))
#     return redirect(url_for('instructions'))

@app.route('/<video>/<int:group>/instructions', methods=['GET', 'POST'])
def instructions(video, group):
    global actual_phrases
    global groups
    session['name'] = request.form.get('name')
    session['email'] = request.form.get('email')
    groups = ['Group 1a', 'Group 1b', 'Group 2a', 'Group 2b', 'Group 3a', 'Group 3b']
    if video == 'desk':
        needs_dict = pd.read_csv('data/need_groups_desk.csv')
        groups = needs_dict.columns.tolist()
        groups.pop(0)
        phrases = [[need for need in list(needs_dict[GROUP]) if len(need)>1] for GROUP in groups]
        actual_phrases = phrases[group] 
        random.shuffle(actual_phrases)
        # File path for the CSV file
        session['CSV_FILE'] = 'data/responses_desk.csv'
        session['instructions_file'] = 'instructions_desk.html'
    else:
        needs_dict = pd.read_csv('data/need_groups_vacuum.csv')
        groups = needs_dict.columns.tolist()
        groups.pop(0)
        phrases = [[need for need in list(needs_dict[GROUP]) if len(need)>1] for GROUP in groups]
        actual_phrases = phrases[group] 
        random.shuffle(actual_phrases)
        # File path for the CSV file
        session['CSV_FILE'] = 'data/responses_vacuum.csv'
        session['instructions_file'] = 'instructions_vacuum.html'
    
    init_csv(session['CSV_FILE']) 

    if request.method == 'POST':
        session['name'] = request.form.get('name')
        session['email'] = request.form.get('email')
        session['video'] = video
        session['group'] = group
        return redirect(url_for('survey', video=video, group=group, name=session['name'], email=session['email'], index=0))  
    
    return render_template(session['instructions_file'], name=session['name'], email=session['email'])

@app.route('/<video>/<int:group>/survey/<name>/<email>/<int:index>', methods=['GET', 'POST'])
def survey(video, group, name, email, index):
    global actual_phrases
    global groups
    
    print(groups,'GROUPS')
    phrase = actual_phrases[index]
    person_group_text = groups[group]
    
    if request.method == 'POST':
        responses = {
            "impactful": request.form.get('impactful'),
            "implicit": request.form.get('implicit'),
            "obvious": request.form.get('obvious'),
            "inefficient": request.form.get('inefficient')
        }
        save_response(session['name'], session['email'], phrase, responses, video, person_group_text)

        if index + 1 < len(actual_phrases):
            return redirect(url_for('survey', phrase=phrase, video=video, group=group, name=name, email=email, index=index+1))
        else:
            return redirect(url_for('thank_you'))

    name = session.get('name', '')
    email = session.get('email', '')
    total_phrases = len(actual_phrases)
    remaining_phrases = total_phrases - index - 1
    
    return render_template('survey.html', phrase=phrase, index=index, total_phrases=total_phrases, remaining_phrases=remaining_phrases, questions=questions, video=video, group=group, name=name, email=email)

@app.route('/thank_you')
def thank_you():
    return "Thank you for completing the survey!"

@app.route('/responses')
def view_responses():
    df = pd.read_csv(session['CSV_FILE'])
    return render_template('responses.html', rows=df.to_dict(orient='records'))

def save_response(name, email, phrase, responses, video, person_group_text):
    if responses["impactful"] == 'Strongly agree' or responses["impactful"] == 'Agree':
        if responses["implicit"] == 'Strongly agree' or responses["implicit"] == 'Agree':
            if responses["obvious"] == 'Strongly disagree' or responses["obvious"] == 'Disagree':
                if responses["inefficient"] == 'Strongly disagree' or responses["inefficient"] == 'Disagree':
                    latent = 1
                else:
                    latent = 0
            else:
                latent = 0
        else:
            latent = 0
    else:
        latent = 0
    new_entry = {
        'name': name,
        'email': email,
        'video': video,
        'group': person_group_text,
        'phrase': phrase,
        'impactful': responses["impactful"],
        'implicit': responses["implicit"],
        'obvious': responses["obvious"],
        'inefficient': responses["inefficient"],
        'latent': latent
    }
    # df = df.append(new_entry, ignore_index=True)
    # df.to_csv(session['CSV_FILE'], index=False)
    
    # Save to Realtime Database
    try:
        current_data = database_ref.get() or {}
        
        for key, value in new_entry.items():
            if key in current_data:
                current_data[key].append(value)
            else:
                current_data[key] = [value]
        
        database_ref.set(current_data)
    except Exception as e:
        print(f"Error saving to Realtime Database: {e}")

if __name__ == "__main__": #comment or delete this if running on real website
    print('URL for desk group 1a: http://127.0.0.1:5000/desk/0/instructions')
    print('URL for vacuum group 1b: http://127.0.0.1:5000/vacuum/1/instructions')

    app.run(debug=True)
