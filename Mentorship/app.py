from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  

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
    areas = ["Proper use of Personal Protective Equipment (PPE)", 
             "Safe lifting techniques and ergonomics", 
             "Hazard identification and reporting", "Emergency response procedures", 
             "Emergency response procedures", "Equipment operation safety"]
    return render_template('focus_areas.html', areas=areas)

@app.route('/focus_areas', methods=['POST'])
def handle_focus_areas():
    selected = request.form.getlist('areas')
    session['focus_areas'] = selected
    return redirect('/final_questions')

@app.route('/final_questions')
def final_questions():
    return render_template('final_questions.html')

@app.route('/final_questions', methods=['POST'])
def handle_final_submission():
    session['login_final'] = request.form['login']
    session['specific_focus'] = request.form['specific_focus']

    # Print collected data to console (can be replaced with DB insert)
    print("Submission received:")
    print(session)

    return "Thank you! Submission complete."

if __name__ == '__main__':
    app.run(debug=True)
