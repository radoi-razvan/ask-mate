from flask import Flask, render_template, request, redirect, url_for

import data_handler

app = Flask(__name__)

@app.route("/")
def route_home():
    return render_template('home.html')


@app.route('/add-question', methods=['GET', 'POST'])
def add_new_question():
    question = ''
    if request.method == 'POST':
        form_dict = request.form
        for value in form_dict.values():
            question = value
        data_handler.write_user_story(question)
        return redirect(url_for('route_list'))


@app.route("/list")
def route_list():
    questions = data_handler.get_all_data_from_questions()
    return render_template('list.html', questions=questions)


@app.route("/question/<question_id>")
def route_question(question_id):
    question_data = data_handler.get_question_answers(question_id)
    title = data_handler.get_question_data(question_id, 'title')
    return render_template('question.html', question=question_id, question_data=question_data, title=title)


if __name__ == "__main__":
    app.run(
        port=5000,
        debug=True
    )
