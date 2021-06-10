import csv
from datetime import datetime
from helpers import constants as ct
from helpers import utils as ut
import time

from typing import List, Dict
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import database_common


@database_common.connection_handler
def get_data_unsorted(cursor, table, order_by="submission_time", sort_option="DESC"):
    query = f"""
        SELECT *
        FROM {table}
        ORDER BY {order_by}
        {sort_option}
            """
    cursor.execute(query)
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_data_sorted(cursor):
    query = sql.SQL(
        """
        SELECT *
        FROM {table_name}
        ORDER BY {submission_time_col}
        DESC
        LIMIT 5
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        submission_time_col=sql.Identifier("submission_time"),
    )
    cursor.execute(query)
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_all_data_for_id(cursor, table, element_id, el_id="id"):
    result_list = []
    query = sql.SQL(
        """
        SELECT *
        FROM {table_name}
        WHERE {id_col} = %(el_id)s
            """
    ).format(
        table_name=sql.Identifier(table),
        id_col=sql.Identifier(el_id)
    )
    cursor.execute(query, {"el_id": element_id})
    result_list = cursor.fetchall()
    return result_list


@database_common.connection_handler
def get_data_for_id(cursor, table, element_id, options, el_id="id"):
    result_list = []
    query = sql.SQL(
        """
        SELECT {options_col}
        FROM {table_name}
        WHERE {id_col} = %s
            """
    ).format(
        table_name=sql.Identifier(table),
        id_col=sql.Identifier(el_id),
        options_col=sql.Identifier(options),
    )
    cursor.execute(query, (element_id,))
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        result_list = dictionary[options]
    return result_list


@database_common.connection_handler
def post_question(cursor, question_list, user_id):
    if question_list[2] == "":
        question_list[2] = None
    post_time = ut.get_formatted_time(round(time.time()))
    query = sql.SQL(
        """
        INSERT INTO {table_name} ({submission_time_col},{view_number_col},
        {vote_number_col},{title_col},{message_col},{image_col}, {user_id_col})
        VALUES(%(s_m)s, %(vote_n)s, %(view_n)s, %(t)s, %(m)s, %(i)s, %(u_i)s)
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        submission_time_col=sql.Identifier("submission_time"),
        vote_number_col=sql.Identifier("vote_number"),
        view_number_col=sql.Identifier("view_number"),
        title_col=sql.Identifier("title"),
        message_col=sql.Identifier("message"),
        image_col=sql.Identifier("image"),
        user_id_col=sql.Identifier("user_id"),
    )
    cursor.execute(
        query,
        {
            "s_m": post_time,
            "vote_n": 0,
            "view_n": 0,
            "t": question_list[0],
            "m": question_list[1],
            "i": question_list[2],
            "u_i": question_list[3]
        },
    )

    count_user_xp(user_id, "count_of_asked_questions", reputation=1)

    query = sql.SQL(
        """
            SELECT MAX({id_col})
            FROM {table_name}
                """
    ).format(table_name=sql.Identifier(ct.TABLE_QUESTION), id_col=sql.Identifier("id"))
    cursor.execute(query)
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        result_list = dictionary["max"]
    return result_list


def get_answers(question_id):
    answers_list = get_data_unsorted(ct.TABLE_ANSWER)
    result_list = []
    for element in answers_list:
        if question_id == "ALL":
            result_dict = {"id": element["id"], "submission_time": element["submission_time"],
                           "vote_number": element["vote_number"], "question_id": element["question_id"],
                           "message": element["message"], "image": element["image"], "user_id": element["user_id"]}
            result_list.append(result_dict)
        elif int(question_id) == element["question_id"]:
            result_dict = {"id": element["id"], "message": element["message"], "vote_number": element["vote_number"],
                           "image": element["image"], "user_id": element["user_id"]}
            result_list.append(result_dict)
    return result_list


@database_common.connection_handler
def post_answer(cursor, question_id, answer, user_id):
    if answer[1] == "":
        answer[1] = None
    post_time = ut.get_formatted_time(round(time.time()))
    query = sql.SQL(
        """
        INSERT INTO {table_name} ({submission_time_col},{vote_number_col},
        {question_id_col},{message_col},{image_col},{user_id_col})
        VALUES(%(s_m)s, %(vote_n)s, %(q_i)s, %(m)s, %(i)s, %(u_id)s)
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        submission_time_col=sql.Identifier("submission_time"),
        vote_number_col=sql.Identifier("vote_number"),
        view_number_col=sql.Identifier("view_number"),
        question_id_col=sql.Identifier("question_id"),
        message_col=sql.Identifier("message"),
        image_col=sql.Identifier("image"),
        user_id_col=sql.Identifier("user_id"),
    )
    cursor.execute(
        query,
        {
            "s_m": post_time,
            "vote_n": 0,
            "q_i": question_id,
            "m": answer[0],
            "i": answer[1],
            "u_id": answer[2]
        },
    )

    count_user_xp(user_id, "count_of_answers", reputation=1)

    query = sql.SQL(
        """
            SELECT MAX({id_col})
            FROM {table_name}
                """
    ).format(table_name=sql.Identifier(ct.TABLE_ANSWER), id_col=sql.Identifier("id"))
    cursor.execute(query)
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        result_list = dictionary["max"]
    return result_list


@database_common.connection_handler
def edit_answer(cursor, answer_id, content):
    print('content is ', content)
    query = sql.SQL(
        """
        UPDATE {table_name} 
        SET {message_col} = %(message)s
        WHERE {id_col} = %(id)s
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        id_col=sql.Identifier("id"),
        message_col=sql.Identifier("message"),
    )
    cursor.execute(query, {"id": answer_id, "message": content})


def sort_questions(order_by, order_direction):
    current_questions_list = get_data_unsorted(ct.TABLE_QUESTION)
    if order_direction == "desc":
        direction = True
    elif order_direction == "asc":
        direction = False
    if order_by == "view_number" or order_by == "vote_number":
        sorted_questions_list = sorted(
            current_questions_list,
            key=lambda current_dict: int(current_dict[order_by]),
            reverse=direction,
        )
    else:
        sorted_questions_list = sorted(
            current_questions_list,
            key=lambda current_dict: current_dict[order_by],
            reverse=direction,
        )
    return sorted_questions_list


@database_common.connection_handler
def edit_question(cursor, question_id, question_data):
    query = sql.SQL(
        """
        UPDATE {table_name} 
        SET {title_col} = %(t)s,{message_col} = %(m)s
        WHERE {id_col} = %(i)s
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        id_col=sql.Identifier("id"),
        title_col=sql.Identifier("title"),
        message_col=sql.Identifier("message"),
    )
    cursor.execute(
        query, {"t": question_data[0], "m": question_data[1], "i": question_id}
    )


@database_common.connection_handler
def delete_answer(cursor, answer_id, user_id):
    question_id = get_question_id_with_answer_id(answer_id)
    query = sql.SQL(
        """
        DELETE FROM {table_name}
        WHERE {id_col} = %s
            """
    ).format(table_name=sql.Identifier(ct.TABLE_ANSWER), id_col=sql.Identifier("id"))
    delete_comment(ct.TABLE_COMMENT, answer_id, options="answer_id", user_id=user_id)
    cursor.execute(query, (answer_id,))
    count_user_xp(user_id, "count_of_answers", reputation=-1)
    return question_id


@database_common.connection_handler
def delete_question(cursor, question_id, user_id):
    print("id is ", question_id)
    query_questions = sql.SQL(
        """
        DELETE FROM {table_name}
        WHERE {id_col} = %s
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        id_col=sql.Identifier("id"))

    query_select_answers = sql.SQL(
        """
        SELECT id
        FROM answer 
        WHERE question_id=%s
        """
    )
    cursor.execute(query_select_answers, (question_id,))
    answer_ids = cursor.fetchall()

    for el in answer_ids:
        delete_comment(ct.TABLE_COMMENT, el["id"], options="answer_id", user_id=user_id)
        delete_answer(el["id"], user_id)
    delete_comment(ct.TABLE_COMMENT, question_id, options="question_id", user_id=user_id)
    delete_question_tag(ct.TABLE_QUESTION_TAG, question_id)
    cursor.execute(query_questions, (question_id,))

    count_user_xp(user_id, "count_of_asked_questions", reputation=-1)


@database_common.connection_handler
def count_vote(cursor, table, element_id, vote, user_id):
    reputation = 0
    if vote == 1:
        if table == ct.TABLE_QUESTION:
            reputation = 5
        if table == ct.TABLE_ANSWER:
            reputation = 10
    if vote == -1:
        reputation = -2
    query = sql.SQL(
        """
        UPDATE {table_name}
        SET {vote_number_col} = {vote_number_col} + %s
        WHERE {id_col} = %s
            """
    ).format(
        table_name=sql.Identifier(table),
        vote_number_col=sql.Identifier("vote_number"),
        id_col=sql.Identifier("id")
    )
    cursor.execute(
        query,
        (
            vote,
            element_id,
        ),
    )
    print("reputation = ", reputation)
    count_user_xp(user_id, "reputation", reputation)


@database_common.connection_handler
def get_question_id_with_answer_id(cursor, answer_id):
    print(answer_id)
    query = sql.SQL(
        """
                SELECT {question_id_col}
                FROM {table_name}
                WHERE {id_col} = %s
                    """
    ).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        id_col=sql.Identifier("id"),
        question_id_col=sql.Identifier("question_id"),
    )
    cursor.execute(query, (answer_id,))
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        question_id = dictionary["question_id"]
    print(data_dict)
    return question_id


@database_common.connection_handler
def increment_view_number(cursor, question_id):
    query = sql.SQL(
        """
        UPDATE {table_name}
        SET {view_number_col} = {view_number_col} + 1
        WHERE {id_col} = %s
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        view_number_col=sql.Identifier("view_number"),
        id_col=sql.Identifier("id"),
    )
    cursor.execute(query, (question_id,))


@database_common.connection_handler
def get_comments_with_id(cursor, corespondent_id, options):
    question_id = None
    answer_id = None
    if options == "question":
        question_id = corespondent_id
    elif options == "answer":
        answer_id = corespondent_id
    print("question id = ", question_id)
    print("answer id = ", answer_id)
    query = sql.SQL(
        """
        SELECT * 
        FROM {table_name} 
        WHERE {question_id_col} = %(q_id)s AND {answer_id_col} IS NULL OR {question_id_col} IS NULL AND {answer_id_col} = %(a_id)s
        """
    ).format(
        table_name=sql.Identifier(ct.TABLE_COMMENT),
        question_id_col=sql.Identifier("question_id"),
        answer_id_col=sql.Identifier("answer_id"),
    )
    cursor.execute(query, {"q_id": question_id, "a_id": answer_id})
    results = []
    ex = cursor.fetchall()
    for dictionary in ex:
        results.append(dictionary)
    return results


@database_common.connection_handler
def get_option_id_with_comment_id(cursor, comment_id, options):
    query = sql.SQL("""
        SELECT {question_id_col} FROM {table_name}
        WHERE ({id_col} = %(id)s)
        """).format(
        table_name=sql.Identifier(ct.TABLE_COMMENT),
        question_id_col=sql.Identifier(options),
        id_col=sql.Identifier('id'))
    cursor.execute(query, {'id': comment_id})
    data = cursor.fetchall()
    print(data)
    return data[0][options]


@database_common.connection_handler
def get_all_comments(cursor):
    query = sql.SQL(
        """
    SELECT * FROM {table_name}
        """
    ).format(table_name=sql.Identifier(ct.TABLE_COMMENT))
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def post_comment(cursor, question_id, answer_id, content, user_id):
    print('content is ', content)
    post_time = ut.get_formatted_time(round(time.time()))
    query = """
        INSERT INTO comment (question_id,answer_id,message,submission_time,edited_count,user_id)
        VALUES (%(q_id)s, %(a_id)s, %(message)s, %(submission_time)s, %(edited_count)s, %(u_id)s)
            """
    cursor.execute(
        query,
        {
            "q_id": question_id,
            "a_id": answer_id,
            "message": content,
            "submission_time": post_time,
            "edited_count": None,
            "u_id": user_id
        },
    )
    count_user_xp(user_id, "count_of_comments", reputation=1)


@database_common.connection_handler
def delete_comment(cursor, table_name, element_id, options, user_id):
    query = sql.SQL(
        """
        DELETE FROM {table_name}
        WHERE {id_col} = %s
            """
    ).format(
        table_name=sql.Identifier(table_name),
        id_col=sql.Identifier(options))
    cursor.execute(query, (element_id,))
    count_user_xp(user_id, "count_of_comments", reputation=-1)


@database_common.connection_handler
def edit_comment(cursor, comment_id, content):
    query = sql.SQL(
        """
        UPDATE {table_name} 
        SET {chosen_col} = %(content)s
        WHERE {id_col} = %(id)s
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_COMMENT),
        id_col=sql.Identifier("id"),
        chosen_col=sql.Identifier("message"),
    )
    cursor.execute(query, {"content": content, "id": comment_id})


@database_common.connection_handler
def increment_edited_count(cursor, comment_id):
    data = get_data_for_id(ct.TABLE_COMMENT, comment_id, "edited_count")
    print('data is ', data)
    if data is None:
        edited_count = 1
    else:
        edited_count = data + 1
    query = sql.SQL(
        """
        UPDATE {table_name}
        SET {chosen_col} = %(edited_count)s
        WHERE {id_col} = %(id)s
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_COMMENT),
        id_col=sql.Identifier("id"),
        chosen_col=sql.Identifier("edited_count"),
    )
    cursor.execute(query, {"edited_count": edited_count, "id": comment_id})


@database_common.connection_handler
def get_tags(cursor):
    query = sql.SQL(
        """
    SELECT {tag_name} FROM {table_name}
        """
    ).format(table_name=sql.Identifier(ct.TABLE_TAG), tag_name=sql.Identifier("name"))
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tag_id(cursor, tag_name):
    query = sql.SQL(
        """
    SELECT {id_col} FROM {table_name}
    WHERE {name_col} = %(name)s
    LIMIT 1
        """
    ).format(
        table_name=sql.Identifier(ct.TABLE_TAG),
        id_col=sql.Identifier("id"),
        name_col=sql.Identifier("name"),
    )
    cursor.execute(query, {"name": tag_name})
    return cursor.fetchall()


@database_common.connection_handler
def create_tag(cursor, tag_name):
    query = sql.SQL(
        """
        INSERT INTO {table_name} ({name_col})
        VALUES (%(name)s)
            """
    ).format(table_name=sql.Identifier(ct.TABLE_TAG), name_col=sql.Identifier("name"))
    cursor.execute(query, {"name": tag_name})


@database_common.connection_handler
def add_tag_to_question(cursor, question_id, tag_id):
    query = sql.SQL(
        """
        INSERT INTO {table_name} ({id_col}, {tag_col})
        VALUES (%(id_q)s, %(id_tag)s)
        """
    ).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION_TAG),
        id_col=sql.Identifier("question_id"),
        tag_col=sql.Identifier("tag_id"),
    )
    cursor.execute(query, {"id_q": question_id, "id_tag": tag_id})


@database_common.connection_handler
def delete_question_tag(cursor, table_name, question_id):
    query = sql.SQL(
        """
        DELETE FROM {table_name}
        WHERE {id_col} = %s 
        """
    ).format(
        table_name=sql.Identifier(table_name),
        id_col=sql.Identifier("question_id"))
    cursor.execute(query, (question_id,))



@database_common.connection_handler
def delete_tag(cursor, table_name, question_id, tag_id):
    query = sql.SQL(
        """
        DELETE FROM {table_name}
        WHERE {id_col} = %s 
        AND {tag_col} = %s
        """
    ).format(
        table_name=sql.Identifier(table_name),
        tag_col=sql.Identifier("tag_id"),
        id_col=sql.Identifier("question_id"))
    cursor.execute(query, (question_id, tag_id))


@database_common.connection_handler
def get_counted_tags(cursor):
    query = f"""
            SELECT t.name, count(t.id)
            FROM tag t
            INNER JOIN question_tag qt on t.id = qt.tag_id
            GROUP BY t.name
            ORDER BY count(t.id) DESC
                """
    cursor.execute(query)
    data = cursor.fetchall()
    return data


# should return the id's of the questions where the string 'content' is found
@database_common.connection_handler
def search_database(cursor, content):
    question_id_list = []
    answer_id_list = []

    query = sql.SQL(
        """
        SELECT {id_col} FROM {table_name}
        WHERE {title_col} LIKE '%%'|| %(some_text)s ||'%%' 
        OR {message_col} LIKE '%%'|| %(some_text)s ||'%%' 
        """).format(
            table_name=sql.Identifier(ct.TABLE_QUESTION),
            id_col=sql.Identifier("id"),
            title_col=sql.Identifier("title"),
            message_col=sql.Identifier("message")
        )
    cursor.execute(query, {"some_text": content})

    for el in cursor.fetchall():
        question_id_list.append(el["id"])

    # now search in answers

    query = sql.SQL(
        """
        SELECT {q_id_col}, {a_id_col} FROM {table_name}
        WHERE {message_col} LIKE '%%'|| %(some_text)s ||'%%' 
        """).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        q_id_col=sql.Identifier("question_id"),
        a_id_col=sql.Identifier("id"),
        message_col=sql.Identifier("message")
    )
    cursor.execute(query, {"some_text": content})
    for el in cursor.fetchall():
        if el['question_id'] not in question_id_list:
            question_id_list.append(el['question_id'])
        answer_id_list.append(el['id'])
    return question_id_list, answer_id_list


@database_common.connection_handler
def get_user_column(cursor, value, options):
    query = sql.SQL(
        """
        SELECT {field_col}
        FROM {table_name}
        WHERE {username_col} = %(u_f)s
        """
    ).format(
        table_name=sql.Identifier(ct.TABLE_USERS),
        field_col=sql.Identifier(options),
        username_col=sql.Identifier("name")
    )
    cursor.execute(query, {"u_f": value})
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def add_user(cursor, user_name, password):
    registration_date = ut.get_formatted_time(round(time.time()))
    query = sql.SQL (
        """
        INSERT INTO {table_name} ({name_col},{password_col},
        {registration_date_col},{count_of_asked_questions_col},
        {count_of_answers_col},{count_of_comments_col},{reputation_col})
        VALUES(%(u_n)s, %(p)s, %(r_d)s, 0, 0, 0, 0)
        """
    ).format(
        table_name=sql.Identifier(ct.TABLE_USERS),
        name_col=sql.Identifier("name"),
        password_col=sql.Identifier("password"),
        registration_date_col=sql.Identifier("registration_date"),
        count_of_asked_questions_col=sql.Identifier("count_of_asked_questions"),
        count_of_answers_col=sql.Identifier("count_of_answers"),
        count_of_comments_col=sql.Identifier("count_of_comments"),
        reputation_col=sql.Identifier("reputation"),
    )
    cursor.execute(query, {"u_n": user_name, "p": password, "r_d": registration_date})
    return "ok"


@database_common.connection_handler
def add_accepted_answer(cursor, question_id, answer_id, user_id):
    reputation = 15
    if answer_id == "None" or answer_id is None:
        answer_id = None
        reputation = -15
    query = sql.SQL(
        """
        UPDATE {table_name} 
        SET {accepted_answer_id_col} = %(a_i)s
        WHERE {question_id_col} = %(q_i)s
        """
    ).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        accepted_answer_id_col=sql.Identifier("accepted_answer_id"),
        question_id_col=sql.Identifier("id")
    )
    cursor.execute(query, {"q_i": question_id, "a_i": answer_id})
    count_user_xp(user_id, "reputation", reputation)


@database_common.connection_handler
def count_user_xp(cursor, user_id, column, reputation):
    print("rep is ", reputation)
    query = sql.SQL(
        """
        UPDATE {table_name}
        SET {selected_col} = {selected_col} + %s
        WHERE {id_col} = %s
            """
    ).format(
        table_name=sql.Identifier(ct.TABLE_USERS),
        selected_col=sql.Identifier(column),
        id_col=sql.Identifier("id")
    )
    cursor.execute(query, (reputation, user_id,), )
    print("ok")