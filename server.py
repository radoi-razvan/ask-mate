from flask import Flask, render_template, request, redirect, url_for

import data_handler

app = Flask(__name__)

@app.route("/")
def route_home():
    return render_template('home.html')


@app.route("/list")
def route_list():
    questions = data_handler.get_all_data_from_questions()
    return render_template('list.html', questions=questions)


@app.route("/question/<question_id>")
def route_question(question_id):
    question_data = data_handler.get_question_content(question_id)
    title = data_handler.get_question_data(question_id, 'title')
    answers_data = data_handler.get_answers(question_id)
    return render_template('question.html', question=question_id, question_data=question_data, title=title, answers_data=answers_data )


@app.route('/add-question', methods=['GET', 'POST'])
def add_new_question():
    question_list = []
    if request.method == 'POST':
        form_dict = request.form
        for value in form_dict.values():
            question_list.append(value)
        question_id = data_handler.write_user_question(question_list)
        return redirect(url_for('route_question', question_id=question_id))
    return render_template('add_question.html')


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_new_answer(question_id):
    answer_list = []
    if request.method == 'POST':
        form_dict = request.form
        for value in form_dict.values():
            answer_list.append(value)
        new_answer_id = data_handler.write_answer(question_id, answer_list)
        # post answer form html
        return redirect(url_for('route_question', question_id=question_id))
    
    return render_template('route_question')





if __name__ == "__main__":
    app.run(
        port=5000,
        debug=True
    )
