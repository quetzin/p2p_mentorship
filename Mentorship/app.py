from flask import Flask, render_template, request, redirect, session, url_for, send_file
import urllib.parse
import json
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

SUBMISSIONS_FILE = "submissions.json"
EXCEL_FILE = "submissions.xlsx"

def load_submissions():
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "r") as f:
            return json.load(f)
    return []

def save_all_submissions(data):
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_submission(data):
    all_data = load_submissions()
    all_data.append(data)
    save_all_submissions(all_data)

def generate_excel():
    data = load_submissions()
    if not data:
        return None
    df = pd.DataFrame(data)
    df.to_excel(EXCEL_FILE, index=False)
    return EXCEL_FILE

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    session['login_initial'] = request.form['login']
    return redirect('/mentee_count')

@app.route('/mentee_count')
def mentee_count():
    return render_template('mentee_count.html')

@app.route('/mentee_count', methods=['POST'])
def handle_mentee_count():
    count = int(request.form['count'])
    session['mentee_count'] = count
    return redirect('/mentee_names')

@app.route('/mentee_names')
def mentee_names():
    count = session.get('mentee_count', 0)
    return render_template('mentee_names.html', count=count)

@app.route('/mentee_names', methods=['POST'])
def handle_mentee_names():
    mentees = [request.form.get(f'mentee_{i}') for i in range(session['mentee_count'])]
    session['mentees'] = mentees
    return redirect('/focus_areas')

@app.route('/focus_areas')
def focus_areas():
    areas = [
        "Proper use of Personal Protective Equipment (PPE)",
        "Safe lifting techniques and ergonomics",
        "Hazard identification and reporting",
        "Emergency response procedures",
        "Equipment operation safety"
    ]
    return render_template('focus_areas.html', areas=areas)

@app.route('/focus_areas', methods=['POST'])
def handle_focus_areas():
    selected = request.form.getlist('areas')
    other_text = request.form.get('other_text')

    if 'Other' in selected and other_text:
        selected.remove('Other')
        selected.append(other_text)

    session['focus_areas'] = selected
    return redirect('/final_questions')

@app.route('/final_questions')
def final_questions():
    return render_template('final_questions.html')

@app.route('/final_questions', methods=['POST'])
def handle_final_submission():
    data = {
        "timestamp": datetime.now().isoformat(),
        "login_initial": session.get('login_initial'),
        "mentee_count": session.get('mentee_count'),
        "mentees": session.get('mentees'),
        "focus_areas": session.get('focus_areas'),
        "specific_focus": request.form['specific_focus'],
        "concerns": request.form['concerns'],
        "follow_up": request.form.get('follow_up', '')
    }
    save_submission(data)
    session['specific_focus'] = data['specific_focus']
    session['concerns'] = data['concerns']
    session['follow_up'] = data['follow_up']
    return redirect('/send_email')

@app.route('/send_email')
def send_email():
    to = "detacins@amazon.com; qpimente@amazon.com"
    subject = "New Mentoring Session Submission"

    body = f"""A new mentoring session has been submitted:

Initial Login: {session.get('login_initial')}
Mentee Count: {session.get('mentee_count')}
Mentees: {', '.join(session.get('mentees', []))}
Focus Areas: {', '.join(session.get('focus_areas', []))}
Specific Focus: {session.get('specific_focus')}
Concerns: {session.get('concerns')}
Follow Up: {session.get('follow_up')}
"""

    mailto_link = f"mailto:{urllib.parse.quote(to)}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    return render_template('send_email.html', mailto_link=mailto_link)

@app.route('/download_excel')
def download_excel():
    filepath = generate_excel()
    if filepath:
        return send_file(filepath, as_attachment=True)
    return "No data available to export."

@app.route('/submissions')
def view_submissions():
    submissions = load_submissions()
    return render_template('submissions.html', submissions=submissions)

@app.route('/add_submission', methods=['POST'])
def add_submission():
    data = {
        "timestamp": datetime.now().isoformat(),
        "login_initial": request.form['login_initial'],
        "mentee_count": int(request.form['mentee_count']),
        "mentees": request.form['mentees'].split(','),
        "focus_areas": request.form['focus_areas'].split(','),
        "specific_focus": request.form['specific_focus'],
        "concerns": request.form['concerns'],
        "follow_up": request.form.get('follow_up', '')
    }
    save_submission(data)
    return redirect('/submissions')

@app.route('/delete_submission/<int:index>', methods=['POST'])
def delete_submission(index):
    data = load_submissions()
    if 0 <= index < len(data):
        data.pop(index)
        save_all_submissions(data)
    return redirect('/submissions')

@app.route('/edit_submission/<int:index>', methods=['POST'])
def edit_submission(index):
    data = load_submissions()
    if 0 <= index < len(data):
        data[index] = {
            "timestamp": datetime.now().isoformat(),
            "login_initial": request.form['login_initial'],
            "mentee_count": int(request.form['mentee_count']),
            "mentees": request.form['mentees'].split(','),
            "focus_areas": request.form['focus_areas'].split(','),
            "specific_focus": request.form['specific_focus'],
            "concerns": request.form['concerns'],
            "follow_up": request.form.get('follow_up', '')
        }
        save_all_submissions(data)
    return redirect('/submissions')

if __name__ == '__main__':
    app.run(debug=True)
