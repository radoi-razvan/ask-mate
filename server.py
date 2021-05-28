import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from helpers import constants as ct
from helpers import utils
import data_handler


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = ct.UPLOAD_FOLDER
app.config["MAX_CONTENT_PATH"] = ct.MAX_PHOTO_SIZE


@app.route("/")
def route_home():
    questions_data = data_handler.get_data_sorted()
    return render_template('home.html', questions_data=questions_data)


@app.route('/search')
def search():
    questions_data = []
    answers_data = []

    input_text = request.args.get('q')
    question_id_list, answer_id_list = data_handler.search_database(input_text)

    for question_id in question_id_list:
        questions_data.append(data_handler.get_all_data_for_id(ct.TABLE_QUESTION, question_id))
    for answer_id in answer_id_list:
        answers_data.append(data_handler.get_all_data_for_id(ct.TABLE_ANSWER, answer_id))

    return render_template('search.html', questions_data=questions_data, answers_data=answers_data)


@app.route("/list")
def route_list():
    if "order_by" and "order_direction" in request.args:
        if (
            "title"
            or "submission_time"
            or "message"
            or "view_number"
            or "vote_number" in request.args
        ):
            order_by, order_direction = (
                request.args["order_by"],
                request.args["order_direction"],
            )
            questions = data_handler.sort_questions(order_by, order_direction)
        else:
            questions = data_handler.get_data_unsorted(ct.TABLE_QUESTION)
    else:
        questions = data_handler.get_data_unsorted(ct.TABLE_QUESTION)
    print('sum thing ', questions[0]['title'])
    return render_template("list.html", questions=questions)


@app.route("/question/<question_id>")
def route_question(question_id):

    data_handler.increment_view_number(question_id)

    question_message_content = data_handler.get_data_for_id(
        ct.TABLE_QUESTION, question_id, "message"
    ).split(";")
    question_title = data_handler.get_data_for_id(
        ct.TABLE_QUESTION, question_id, "title"
    )
    question_image_path = data_handler.get_data_for_id(
        ct.TABLE_QUESTION, question_id, "image"
    )
    answers_data = data_handler.get_answers(question_id)
    question_comments_data = data_handler.get_comments_with_id(question_id, "question")
    all_comments_data = data_handler.get_all_comments()

    tag_id = data_handler.get_data_for_id(
        ct.TABLE_QUESTION_TAG, question_id, "tag_id", "question_id"
    )

    if tag_id:
        tag_name = data_handler.get_data_for_id(ct.TABLE_TAG, tag_id, "name")
    else:
        tag_name = None
    print('tag_id', tag_id)
    if not tag_id:
        tag_id = None
    return render_template(
        "question.html",
        question_id=question_id,
        question_data=question_message_content,
        title=question_title,
        answers_data=answers_data,
        question_image_path=question_image_path,
        comments_data=question_comments_data,
        all_comments_data=all_comments_data,
        question_tag=tag_name,
        tag_id=tag_id
    )


@app.route("/add-question", methods=["GET", "POST"])
def add_new_question():
    question_list = []
    if request.method == "POST":
        form_dict = request.form
        for value in form_dict.values():
            question_list.append(value)
        file = request.files["file"]
        if str(file) != "<FileStorage: '' ('application/octet-stream')>" and utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            file.save(file_path)
            question_list.append(file_path)
        else:
            question_list.append("")
        question_id = data_handler.post_question(question_list)
        return redirect(url_for("route_question", question_id=question_id))
    return render_template("add_question.html")


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def add_new_answer(question_id):
    answer_list = []
    if request.method == "POST":
        form_dict = request.form
        for value in form_dict.values():
            answer_list.append(value)
        file = request.files["file"]
        if str(
            file
        ) != "<FileStorage: '' ('application/octet-stream')>" and utils.allowed_file(
            file.filename
        ):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename).replace(
                "\\", "/"
            )
            file.save(file_path)
            answer_list.append(file_path)
        else:
            answer_list.append("")
        data_handler.post_answer(question_id, answer_list)
        return redirect(url_for("route_question", question_id=question_id))
    return render_template("post_answer.html", question_id=question_id)


@app.route("/question/<question_id>/delete")
def delete_question_route(question_id):
    data_handler.delete_question(question_id)
    return redirect(url_for("route_list"))


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question_route(question_id):
    question_data = []
    if request.method == "POST":
        form_dict = request.form
        for value in form_dict.values():
            question_data.append(value)
        data_handler.edit_question(question_id, question_data)
        return redirect(url_for("route_question", question_id=question_id))
    title = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, "title")
    message = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, "message")
    return render_template(
        "edit_question.html", question_id=question_id, title=title, message=message)


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer_route(answer_id):
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    print('first q_id ', question_id)
    if request.method == 'POST':
        print('okkk')
        answer_message = request.form['message']
        data_handler.edit_answer(answer_id, answer_message)
        print('question id is ', question_id)
        return redirect(url_for('route_question', question_id=question_id))
    message = data_handler.get_data_for_id(ct.TABLE_ANSWER, answer_id, 'message')
    return render_template('edit_answer.html', answer_id=answer_id, message=message)


@app.route("/answer/<answer_id>/delete")
def delete_answer_route(answer_id):
    question_id = data_handler.delete_answer(answer_id)
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/question/<question_id>/vote_up")
def vote_up_question_route(question_id):
    vote_type = 1
    data_handler.count_vote(ct.TABLE_QUESTION, question_id, vote_type)
    return redirect(url_for("route_list"))


@app.route("/question/<question_id>/vote_down")
def vote_down_question_route(question_id):
    vote_type = -1
    data_handler.count_vote(ct.TABLE_QUESTION, question_id, vote_type)
    return redirect(url_for("route_list"))


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer_route(answer_id):
    vote_type = 1
    data_handler.count_vote(ct.TABLE_ANSWER, answer_id, vote_type)
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer_route(answer_id):
    vote_type = -1
    data_handler.count_vote(ct.TABLE_ANSWER, answer_id, vote_type)
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/question/<question_id>/new-comment", methods=["GET", "POST"])
def add_question_comment(question_id):
    print("question id is ", question_id)
    if request.method == "POST":
        print("ok123")
        comment_message = request.form["message"]
        print("comment mess is ", comment_message)
        data_handler.post_comment(question_id, None, comment_message)
        return redirect(url_for("route_question", question_id=question_id))
    return render_template("question_comment.html", question_id=question_id)


@app.route("/answer/<answer_id>/new-comment", methods=["GET", "POST"])
def add_answer_comment(answer_id):
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    if request.method == "POST":
        comment_message = request.form['message']
        data_handler.post_comment(None, answer_id, comment_message)
        return redirect(url_for("route_question", question_id=question_id))
    return render_template("answer_comment.html", answer_id=answer_id)


@app.route("/comment/<comment_id>/edit", methods=['GET', 'POST'])
def edit_comment_route(comment_id):
    requested_id = 'question_id'
    question_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
    if question_id is None:
        requested_id = 'answer_id'
        answer_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
        # find question id with answer id
        question_id = data_handler.get_question_id_with_answer_id(answer_id)
    print('question_id ', question_id)
    if request.method == 'POST':
        comment_message = request.form['message']
        data_handler.increment_edited_count(comment_id)
        data_handler.edit_comment(comment_id, comment_message)
        return redirect(url_for('route_question', question_id=question_id))
    message = data_handler.get_data_for_id(ct.TABLE_COMMENT, comment_id, 'message')
    return render_template('edit_comment.html', comment_id=comment_id, message=message)


@app.route("/question/<question_id>/new-tag", methods=["GET", "POST"])
def add_question_tag(question_id):
    tags_list = data_handler.get_tags()
    if request.method == "POST":
        try:
            tag_name = request.form["tag"]
            print('tagssss ', tag_name)
        except:
            tag_name = request.form["tag_name"]
            data_handler.create_tag(tag_name)

        tag_id = data_handler.get_tag_id(tag_name)
        print('tag name is ', tag_name)
        data_handler.add_tag_to_question(question_id, tag_id[0]['id'])
        return redirect(url_for("route_question", question_id=question_id))
    return render_template("tag_question.html", tags=tags_list, question_id=question_id)


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_tag_route(question_id, tag_id):
    data_handler.delete_element(ct.TABLE_QUESTION_TAG, question_id, "question_id")
    return redirect(url_for('route_question', question_id=question_id))


@app.route('/comments/<comment_id>/delete')
def delete_comment_route(comment_id):
    requested_id = 'question_id'
    question_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
    if question_id is None:
        requested_id = 'answer_id'
        answer_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
        # find question id with answer id
        question_id = data_handler.get_question_id_with_answer_id(answer_id)
    data_handler.delete_element(ct.TABLE_COMMENT, comment_id, "id")
    return redirect(url_for('route_question', question_id=question_id))


# @app.route("/search?q=<search_phrase>")
# def search_data_route(search_phrase):
#     print('k')
#     return redirect(url_for("route_list"))




if __name__ == "__main__":
    app.run(port=5000, debug=True)
