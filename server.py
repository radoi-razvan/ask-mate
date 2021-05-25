import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from helpers import constants as ct
from helpers import utils
import data_handler


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = ct.UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = ct.MAX_PHOTO_SIZE


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
            # questions = data_handler.get_data_unsorted(ct.FILE_QUESTIONS)
            questions = data_handler.get_data_unsorted(ct.TABLE_QUESTION)
    else:
        # questions = data_handler.get_data_unsorted(ct.FILE_QUESTIONS, 'formatted-time')
        questions = data_handler.get_data_unsorted(ct.TABLE_QUESTION)
    return render_template('list.html', questions=questions)


@app.route("/question/<question_id>")
def route_question(question_id):
    data_handler.increment_view_number(question_id)
    # question_message_content = data_handler.get_data_for_id(ct.FILE_QUESTIONS, question_id, 'message').split(';')
    # question_title = data_handler.get_data_for_id(ct.FILE_QUESTIONS, question_id, 'title')
    # question_image_path = data_handler.get_data_for_id(ct.FILE_QUESTIONS, question_id, 'image')
    question_message_content = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, 'message').split(';')
    question_title = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, 'title')
    question_image_path = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, 'image')
    answers_data = data_handler.get_answers(question_id)
    return render_template('question.html', question_id=question_id, question_data=question_message_content, title=question_title, answers_data=answers_data, question_image_path=question_image_path)


@app.route('/add-question', methods=['GET', 'POST'])
def add_new_question():
    question_list = []
    if request.method == 'POST':
        form_dict = request.form
        for value in form_dict.values():
            question_list.append(value)
        file = request.files['file']
        if str(file) != "<FileStorage: '' ('application/octet-stream')>" and utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            file.save(file_path)
            question_list.append(file_path)
        else:
            question_list.append('')
        question_id = data_handler.post_question(question_list)
        return redirect(url_for('route_question', question_id=question_id))
    return render_template('add_question.html')


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_new_answer(question_id):
    answer_list = []
    if request.method == 'POST':
        form_dict = request.form
        for value in form_dict.values():
            answer_list.append(value)
        file = request.files['file']
        if str(file) != "<FileStorage: '' ('application/octet-stream')>" and utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            file.save(file_path)
            answer_list.append(file_path)
        else:
            answer_list.append('')
        data_handler.post_answer(question_id, answer_list)
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
    title = data_handler.get_data_for_id(ct.FILE_QUESTIONS, question_id, 'title')
    message = data_handler.get_data_for_id(ct.FILE_QUESTIONS, question_id, 'message')
    return render_template('edit_question.html', question_id=question_id, title=title, message=message)


@app.route('/answer/<answer_id>/delete')
def delete_answer_route(answer_id):
    question_id = data_handler.delete_answer(None, answer_id)
    return redirect(url_for('route_question', question_id=question_id))


@app.route('/question/<question_id>/vote_up')
def vote_up_question_route(question_id):
    vote_type = 'up'
    data_handler.count_vote(ct.FILE_QUESTIONS, ct.QUESTION_HEADER, question_id, vote_type)
    return redirect(url_for('route_list'))


@app.route('/question/<question_id>/vote_down')
def vote_down_question_route(question_id):
    vote_type = 'down'
    data_handler.count_vote(ct.FILE_QUESTIONS, ct.QUESTION_HEADER, question_id, vote_type)
    return redirect(url_for('route_list'))


@app.route('/answer/<answer_id>/vote_up')
def vote_up_answer_route(answer_id):
    vote_type = 'up'
    data_handler.count_vote(ct.FILE_ANSWERS, ct.ANSWER_HEADER, answer_id, vote_type)
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    print('question_id is ', question_id)
    return redirect(url_for('route_question', question_id=question_id))


@app.route('/answer/<answer_id>/vote_down')
def vote_down_answer_route(answer_id):
    vote_type = 'down'
    data_handler.count_vote(ct.FILE_ANSWERS, ct.ANSWER_HEADER, answer_id, vote_type)
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    return redirect(url_for('route_question', question_id=question_id))



if __name__ == "__main__":
    app.run(
        port=5000,
        debug=True
    )
