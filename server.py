import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from helpers import constants as ct
from helpers import utils
import data_handler
import cryptography as cy


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = ct.UPLOAD_FOLDER
app.config["MAX_CONTENT_PATH"] = ct.MAX_PHOTO_SIZE
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def route_home():
    questions_data = data_handler.get_data_sorted()
    if "username" in session:
        username = session["username"]
        user_id = data_handler.get_user_column(username, "id")[0]["id"]
        return render_template('home.html', questions_data=questions_data, username=username, user_id=user_id)
    return render_template('home.html', questions_data=questions_data, username=None)


@app.route('/search')
def search():
    questions_data = []
    answers_data = []

    input_text = request.args.get('q')
    question_id_list, answer_id_list = data_handler.search_database(input_text)

    for question_id in question_id_list:
        questions_data.append(data_handler.get_all_data_for_id(ct.TABLE_QUESTION, question_id)[0])
    for answer_id in answer_id_list:
        answers_data.append(data_handler.get_all_data_for_id(ct.TABLE_ANSWER, answer_id)[0])

    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
    else:
        username = None
        user_id = None
    return render_template('search.html', questions_data=questions_data, answers_data=answers_data, username=username, user_id=user_id)


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
    print("sesssion", session)
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
    else:
        username = None
        user_id = None
    return render_template("list.html", questions=questions, username=username, user_id=user_id)


@app.route("/question/<question_id>")
def route_question(question_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
    else:
        username = None
        user_id = None
    data_handler.increment_view_number(question_id)

    question_message_content = data_handler.get_data_for_id(
        ct.TABLE_QUESTION, question_id, "message"
    ).split(";")
    question_data = data_handler.get_all_data_for_id(ct.TABLE_QUESTION, question_id)[0]
    question_message_content = question_data["message"].split(";")
    question_image_path = data_handler.get_data_for_id(
        ct.TABLE_QUESTION, question_id, "image"
    )
    answers_data = data_handler.get_answers(question_id)
    question_comments_data = data_handler.get_comments_with_id(question_id, "question")
    all_comments_data = data_handler.get_all_comments()
    tag_data = []
    tag_ids_list = data_handler.get_all_data_for_id(ct.TABLE_QUESTION_TAG, question_id, "question_id")

    if tag_ids_list:
        for element in tag_ids_list:
            data = {}
            data.update({"tag_id": element["tag_id"]})
            data.update({"tag_name": data_handler.get_data_for_id(ct.TABLE_TAG, element["tag_id"], "name")})
            tag_data.append(data)
    print("comm data", all_comments_data[2]["user_id"])
    accepted_answer_id = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, "accepted_answer_id", el_id="id")
    return render_template(
        "question.html",
        question_id=question_id,
        question_data=question_data,
        question_message_content=question_message_content,
        answers_data=answers_data,
        question_image_path=question_image_path,
        comments_data=question_comments_data,
        all_comments_data=all_comments_data,
        question_tags_list=tag_data,
        username=username,
        user_id=user_id,
        accepted_answer_id=accepted_answer_id
    )


@app.route("/add-question", methods=["GET", "POST"])
def add_new_question():
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        question_list = []
        if request.method == "POST":
            form_dict = request.form
            for value in form_dict.values():
                question_list.append(value)
            file = request.files["file"]
            if utils.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
                print(file_path)

                file.save(file_path)
                question_list.append(file_path)
            else:
                question_list.append("")
            question_list.append(user_id)
            question_id = data_handler.post_question(question_list, user_id)
            print("ok")
            return redirect(url_for("route_question", question_id=question_id))
        return render_template("add_question.html", username=username, user_id=user_id)
    return redirect(url_for("route_home"))


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def add_new_answer(question_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
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
            answer_list.append(user_id)
            data_handler.post_answer(question_id, answer_list, user_id)
            return redirect(url_for("route_question", question_id=question_id))
        return render_template("post_answer.html", question_id=question_id, username=username, user_id=user_id)
    return redirect(url_for("route_home"))


@app.route("/question/<question_id>/delete")
def delete_question_route(question_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        data_handler.delete_question(question_id, user_id)
        return redirect(url_for("route_list"))
    return redirect(url_for("route_home"))


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question_route(question_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
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
            "edit_question.html", question_id=question_id, title=title, message=message, username=username, user_id=user_id)
    return redirect(url_for("route_home"))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer_route(answer_id):
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    if request.method == 'POST':
        answer_message = request.form['message']
        data_handler.edit_answer(answer_id, answer_message)
        return redirect(url_for('route_question', question_id=question_id))
    message = data_handler.get_data_for_id(ct.TABLE_ANSWER, answer_id, 'message')
    return render_template('edit_answer.html', answer_id=answer_id, message=message)


@app.route("/answer/<answer_id>/delete")
def delete_answer_route(answer_id):
    if "username" in session:
        username = session["username"]
        user_id = data_handler.get_user_column(username, "id")[0]["id"]
        question_id = data_handler.delete_answer(answer_id, user_id)
        return redirect(url_for("route_question", question_id=question_id))
    return redirect(url_for("route_home"))


@app.route("/question/<question_id>/vote_up")
def vote_up_question_route(question_id):
    if "username" in session:
        username = session["username"]
        vote_type = 1
        user_id = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, "user_id", el_id="id")
        data_handler.count_vote(ct.TABLE_QUESTION, question_id, vote_type, user_id)
        return redirect(url_for("route_list"))
    return redirect(url_for("route_home"))


@app.route("/question/<question_id>/vote_down")
def vote_down_question_route(question_id):
    if "username" in session:
        username = session["username"]
        user_id = data_handler.get_user_column(username, "id")[0]["id"]
        vote_type = -1
        data_handler.count_vote(ct.TABLE_QUESTION, question_id, vote_type, user_id)
        return redirect(url_for("route_list"))
    return redirect(url_for("route_home"))


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer_route(answer_id):
    if "username" in session:
        username = session["username"]
        vote_type = 1
        question_id = data_handler.get_question_id_with_answer_id(answer_id)
        user_id = data_handler.get_data_for_id(ct.TABLE_QUESTION, question_id, "user_id", el_id="id")
        data_handler.count_vote(ct.TABLE_ANSWER, answer_id, vote_type, user_id)
        return redirect(url_for("route_question", question_id=question_id))
    return redirect(url_for("route_home"))


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer_route(answer_id):
    if "username" in session:
        username = session["username"]
        user_id = data_handler.get_user_column(username, "id")[0]["id"]
        vote_type = -1
        data_handler.count_vote(ct.TABLE_ANSWER, answer_id, vote_type, user_id)
        question_id = data_handler.get_question_id_with_answer_id(answer_id)
        return redirect(url_for("route_question", question_id=question_id))
    return redirect(url_for("route_home"))


@app.route("/question/<question_id>/new-comment", methods=["GET", "POST"])
def add_question_comment(question_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        if request.method == "POST":
            comment_message = request.form["message"]
            data_handler.post_comment(question_id, None, comment_message, user_id)
            return redirect(url_for("route_question", question_id=question_id))
        return render_template("question_comment.html", question_id=question_id)
    return redirect(url_for("route_home"))


@app.route("/answer/<answer_id>/new-comment", methods=["GET", "POST"])
def add_answer_comment(answer_id):
    question_id = data_handler.get_question_id_with_answer_id(answer_id)
    if request.method == "POST":
        username = session["username"]
        user_id = data_handler.get_user_column(username, "id")[0]["id"]
        comment_message = request.form['message']
        data_handler.post_comment(None, answer_id, comment_message, user_id)
        return redirect(url_for("route_question", question_id=question_id))
    return render_template("answer_comment.html", answer_id=answer_id)


@app.route("/comment/<comment_id>/edit", methods=['GET', 'POST'])
def edit_comment_route(comment_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        requested_id = 'question_id'
        question_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
        if question_id is None:
            requested_id = 'answer_id'
            answer_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
            # find question id with answer id
            question_id = data_handler.get_question_id_with_answer_id(answer_id)
        if request.method == 'POST':
            comment_message = request.form['message']
            data_handler.increment_edited_count(comment_id)
            data_handler.edit_comment(comment_id, comment_message)
            return redirect(url_for('route_question', question_id=question_id))
        message = data_handler.get_data_for_id(ct.TABLE_COMMENT, comment_id, 'message')
        return render_template('edit_comment.html', comment_id=comment_id, message=message, username=username, user_id=user_id)
    return redirect(url_for("route_home"))


@app.route('/comments/<comment_id>/delete')
def delete_comment_route(comment_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        requested_id = 'question_id'
        question_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
        if question_id is None:
            requested_id = 'answer_id'
            answer_id = data_handler.get_option_id_with_comment_id(comment_id, requested_id)
            # find question id with answer id
            question_id = data_handler.get_question_id_with_answer_id(answer_id)
        data_handler.delete_comment(ct.TABLE_COMMENT, comment_id, "id", user_id)
        return redirect(url_for('route_question', question_id=question_id))
    return redirect(url_for("route_home"))


@app.route("/tags")
def route_tags():
    tags_data = data_handler.get_counted_tags()
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        return render_template("tags_page.html", tags_data=tags_data, username=username, user_id=user_id)
    return render_template("tags_page.html", tags_data=tags_data)


@app.route("/question/<question_id>/new-tag", methods=["GET", "POST"])
def add_question_tag(question_id):
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        tags_list = data_handler.get_tags()
        if request.method == "POST":
            try:
                tag_name = request.form["tag"]
            except:
                tag_name = request.form["tag_name"]
                data_handler.create_tag(tag_name)

            tag_id = data_handler.get_tag_id(tag_name)
            data_handler.add_tag_to_question(question_id, tag_id[0]['id'])
            return redirect(url_for("route_question", question_id=question_id))
        return render_template("tag_question.html", tags=tags_list, question_id=question_id, username=username, user_id=user_id)
    return redirect(url_for("route_home"))


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_tag_route(question_id, tag_id):
    data_handler.delete_tag(ct.TABLE_QUESTION_TAG, question_id, tag_id)
    return redirect(url_for('route_question', question_id=question_id))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            if username == data_handler.get_user_column(username, "name")[0]["name"] and cy.verify_password(password, data_handler.get_user_column(username, "password")[0]["password"]):
                session.update({"username": username})
                session.update({"user_id": data_handler.get_user_column(session["username"], "id")[0]["id"]})
                return redirect(url_for("route_home"))
            else:
                return render_template("login.html", message="Invalid login")
        except:
            return render_template("login.html", message="Invalid login")
    return render_template("login.html", message=None)


@app.route('/registration', methods=["GET", "POST"])
def registration_route():
    if request.method == "POST":
        user_name = request.form["username"]
        password = request.form["password"]
        if not data_handler.get_user_column(user_name, "name") and len(user_name) > 5 and len(password) > 5:
            password = cy.hash_password(password)
            if data_handler.add_user(user_name, password) == "ok":
                session.update({ "username": user_name })
                session.update({"user_id": data_handler.get_user_column(session["username"], "id")[0]["id"]})
        return redirect(url_for("route_home"))
    return render_template("registration.html")


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('route_home'))


@app.route('/users')
def users():
    if "username" in session:
        username = session["username"]
        user_id = session["user_id"]
        users_data = data_handler.get_data_unsorted(ct.TABLE_USERS, "registration_date")
        return render_template("users.html", users_data=users_data, username=username, user_id=user_id)
    return redirect(url_for("route_home"))


@app.route('/user/<user_id>')
def user_profile(user_id):
    if "username" in session:
        username = session["username"]
        user_data = data_handler.get_all_data_for_id(ct.TABLE_USERS, user_id, el_id="id")[0]
        question_data = data_handler.get_all_data_for_id(ct.TABLE_QUESTION, user_id, el_id="user_id")
        answer_data = data_handler.get_all_data_for_id(ct.TABLE_ANSWER, user_id, el_id="user_id")
        comment_data = data_handler.get_all_data_for_id(ct.TABLE_COMMENT, user_id, el_id="user_id")
        comments = []
        for comment in comment_data:
            if comment["question_id"] is None:
                question_id = data_handler.get_question_id_with_answer_id(comment["answer_id"])
                comment["question_id"] = question_id
            comments.append(comment)
        return render_template("user_profile.html", user_data=user_data, question_data=question_data, answer_data=answer_data, comment_data=comments)
    return redirect(url_for("route_home"))


@app.route('/<question_id>/<answer_id>/accepted' , methods=["GET", "POST"])
def accepted(question_id, answer_id):
    if "username" in session:
        username = session["username"]
        try:
            form_value = request.form["accepted"]
        except:
            form_value = None
        user_id = data_handler.get_data_for_id(ct.TABLE_ANSWER, answer_id, "user_id", el_id="id")
        data_handler.add_accepted_answer(question_id, form_value, user_id)
        return redirect(url_for("route_question", question_id=question_id))
    return redirect(url_for("route_home"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)