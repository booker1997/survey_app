from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
import random
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = 'IDEATION2024'

# Set up Firebase Realtime Database
firebase_cred = {
  "type": "service_account",
  "project_id": "needs-proj",
  "private_key_id": "ac20b236f5e294f18bf15fb1c6df3a95e7bf2a06",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDAcpx9rw2revaw\n3KtpAvK1jtYnA6zxO/BVqZbSlTll8SjHcH0CrKhAqCXlGA1kaLPDhldPQs8vOSWc\nCe9Yi1JMgRJsNSp1O8weUpmS8bGS1lLMiEZhtdQ8I9QdDWNDY3+UTtLARTpN25kR\nxWY4HQy5mGkEarijaC0gcsmHAu5vZoEs/H+6qUstceqdyUmAHhfUScet+CtHD8C/\njPu0hwlMF58n+uZ7DzhsS7bG7bl8tEB5gG5FBq7+H1BGT+nmFg04dR//RS2gz8gk\nWElIwnyu39p2BFoyD4YfzYxul70nXpyXuMpcVpb8r/NlxJQYscytRCDPJE05g1/H\nV6hnBQ3FAgMBAAECggEABp7KuF4hw8DmpJ3qvaGO1OUVg+ER/Xh445GCcTsV7uZV\nZ0r82e8zmInQR+nEaCxb5sGD1mOveenm28/RroOYcK5OAm/vxnmoo3Bm/RGYcLsz\nvPqBJVJaezkmTluMCyDsnh76DAg1ocEIqn5Wbl69ddMC5daABIsMZl3cher5Zdab\nEaQqpkXN4hoVlpvTZXxgXSo5dmqnsEiYC/1GDLQCsYelBg8vqtlQ/QopsqY4qqCV\nXudpZefS5TH1FGq9OOiUaq3FvhAArOaXbJafxI2WnzQ/TszMYlnJcviZQV9HGiyk\n/WtobdYTmqnOQ0bv4TRWkN/sjf2e5R0+W1nAa/LjMQKBgQDvKjJLh3uIsfLOy1cm\nw403/5Hv1MKIN000102LBWAeloHXz1fdisT31O+4s9yGVd6KGOvMgDtRAnEI5/35\ngE494f6Ijc5lk1Rq3xixRIO+oca8NL83SV6rvNX9EuhOO4pJ5dcM/7wuTY0ee5zB\nI3LtAkO3/U4++J5ou0jvPYyxyQKBgQDN/o/OS4pmO69KEnD/5d4MkLD1eBw/FlBV\nc0EVDSpHP5/SZO7q9Q+fMf+JBmpbplLm+ndqQ2DSim5DAtGcaPt+zQuiwp/5LJ8K\nBHZXcWI1BOFrk926QUw2j3k1ivmyxe6l65O/YL9DTHiDml0Pv5FzfJ4Gm6cPBYxm\nFsaWcxKaHQKBgQC7P+9W4UFgGeq/68ZVTD/RuyAYhRy1p46kM3m7wb6q1C3euLDT\nfKWQYEA7/V5IMwzkVHSxjShj2aSEU5audL1NiBZP9a7GKl6qufdMOxdm9qRxkF6x\nu5kKnvNvjBEjx0wTZYdE3ykHm6JEXoWxVb7SP7ajZAiSFvd3ikKlRSxVuQKBgQCx\n9D/3T3r4Zoc/zj6gUsxIvpag+GoudfBgYXjP3tevRV+kOl3LzHj6Zg8DKO+ozT7B\nG48d1adHOx+V9FFwdaEOIcTzjn70m3+o/8HcOK9Gbjju3oal6NMWL0ve3Xho4GUS\nITk6EzInyWAzEJ9kg3H7+qPpwX3IlFp9tx9HyZFAYQKBgES+Uyo0AqFmrIaDnZ+z\nQ+begxuFyneKr0rqTgssTb/ckwaD6JfrtR5Un7+k6fGMnFpo9/mAcQILGWyom3K/\ntd6hRhaWWXs3A7ZNw2HAshWOIrWuAKWSIaGaiyeEGjeEw3uGDrxtzmcIUjmeu3rr\nWYbAwvRFUJqmyWCAl1uc/ZHc\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-inqqa@needs-proj.iam.gserviceaccount.com",
  "client_id": "101100983857220373179",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-inqqa%40needs-proj.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
cred = credentials.Certificate(firebase_cred)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://needs-proj-default-rtdb.firebaseio.com/'
})

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

@app.route('/')
def index():
    return redirect(url_for('instructions'))

@app.route('/<video>/<group>/instructions', methods=['GET', 'POST'])
def instructions(video, group):
    session['name'] = request.form.get('name')
    session['email'] = request.form.get('email')
    groups = ['Group 1a', 'Group 1b', 'Group 2a', 'Group 2b', 'Group 3a', 'Group 3b']
    print(video)
    if video == 'desk':
        needs_dict = pd.read_csv('data/need_groups_desk.csv')
        phrases = [[need for need in list(needs_dict[GROUP]) if type(need) == str] for GROUP in groups]
        
        # File path for the CSV file
        session['CSV_FILE'] = 'data/responses_desk.csv'
        session['instructions_file'] = 'instructions_desk.html'
    else:
        needs_dict = pd.read_csv('data/need_groups_vacuum.csv')
        phrases = [[need for need in list(needs_dict[GROUP]) if type(need) == str] for GROUP in groups]
        
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
    groups = ['Group 1a', 'Group 1b', 'Group 2a', 'Group 2b', 'Group 3a', 'Group 3b']

    if video == 'desk':
        needs_dict = pd.read_csv('data/need_groups_desk.csv')
        phrases = [[need for need in list(needs_dict[GROUP]) if type(need) == str] for GROUP in groups]
    else:
        needs_dict = pd.read_csv('data/need_groups_vacuum.csv')
        phrases = [[need for need in list(needs_dict[GROUP]) if type(need) == str] for GROUP in groups]
    
    phrase = phrases[group][index]
    person_group_text = groups[group]
    
    if request.method == 'POST':
        responses = {
            "impactful": request.form.get('impactful'),
            "implicit": request.form.get('implicit'),
            "obvious": request.form.get('obvious'),
            "inefficient": request.form.get('inefficient')
        }
        save_response(session['name'], session['email'], phrase, responses, video, person_group_text)

        if index + 1 < len(phrases[group]):
            return redirect(url_for('survey', phrase=phrase, video=video, group=group, name=name, email=email, index=index+1))
        else:
            return redirect(url_for('thank_you'))

    name = session.get('name', '')
    email = session.get('email', '')
    total_phrases = len(phrases[group])
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
    # df = pd.read_csv(session['CSV_FILE'])
    new_entry = {
        'name': name,
        'email': email,
        'video': video,
        'group': person_group_text,
        'phrase': phrase,
        'impactful': responses["impactful"],
        'implicit': responses["implicit"],
        'obvious': responses["obvious"],
        'inefficient': responses["inefficient"]
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

if __name__ == "__main__":
    print('URL for desk group 1a: http://127.0.0.1:5000/desk/0/instructions')
    print('URL for vacuum group 1b: http://127.0.0.1:5000/vacuum/1/instructions')

    app.run(debug=True)
