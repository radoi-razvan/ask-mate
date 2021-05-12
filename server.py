from flask import Flask, render_template, request, redirect, url_for

import data_handler

app = Flask(__name__)

@app.route("/")
def route_home():
    return render_template('home.html')

@app.route("/list")
def route_list():
    if 'order_by' and 'order_direction' in request.args:
        if 'title' or 'submission_time' or 'message' or 'view_number' or 'vote_number' in request.args:
            order_by, order_direction = request.args["order_by"], request.args["order_direction"]
            questions = data_handler.sort_questions(order_by, order_direction)
        else:
            questions = data_handler.get_all_data_from_questions()
    else:
        questions = data_handler.get_all_data_from_questions()
    return render_template('list.html', questions=questions)


@app.route("/question/<question_id>")
def route_question(question_id):
    question_data = data_handler.get_question_content(question_id)
    title = data_handler.get_question_data(question_id, 'title')
    answers_data = data_handler.get_answers(question_id)
    return render_template('question.html', question_id=question_id, question_data=question_data, title=title, answers_data=answers_data)


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
        data_handler.write_answer(question_id, answer_list)
        return redirect(url_for('route_question', question_id=question_id))
    return render_template('post_answer.html', question_id=question_id)


@app.route('/question/<question_id>/delete')
def delete_question_route(question_id):
    data_handler.delete_question(question_id)
    return redirect(url_for('route_list'))


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question_route(question_id):
    question_data = []
    if request.method == 'POST':
        form_dict = request.form
        for value in form_dict.values():
            question_data.append(value)
        data_handler.edit_question(question_id, question_data)
        return redirect(url_for('route_question', question_id=question_id))
    title = data_handler.get_question_data(question_id, 'title')
    message = data_handler.get_question_data(question_id, 'message')
    return render_template('edit_question.html', question_id=question_id, title=title, message=message)


if __name__ == "__main__":
    app.run(
        port=5000,
        debug=True
    )
