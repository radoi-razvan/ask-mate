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
def get_data_unsorted(cursor, table):
    query = sql.SQL("""
        SELECT *
        FROM {table_name}
        ORDER BY {submission_time_col}
        DESC
            """).format(
            table_name=sql.Identifier(table),
            submission_time_col=sql.Identifier('submission_time'))
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_data_for_id(cursor, table, question_id, options):
    result_list = []
    query = sql.SQL("""
        SELECT {options_col}
        FROM {table_name}
        WHERE {id_col} = %s
            """).format(
        table_name=sql.Identifier(table),
        id_col=sql.Identifier('id'),
        options_col=sql.Identifier(options))
    cursor.execute(query, (question_id,))
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        result_list = dictionary[options]
    return result_list


@database_common.connection_handler
def post_question(cursor, question_list):
    if question_list[2] == '':
        question_list[2] = None
    post_time = ut.get_formatted_time(round(time.time()))
    query = sql.SQL("""
        INSERT INTO {table_name} ({submission_time_col},{view_number_col},
        {vote_number_col},{title_col},{message_col},{image_col})
        VALUES(%(s_m)s, %(vote_n)s, %(view_n)s, %(t)s, %(m)s, %(i)s)
            """).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        submission_time_col=sql.Identifier('submission_time'),
        vote_number_col=sql.Identifier('vote_number'),
        view_number_col=sql.Identifier('view_number'),
        title_col=sql.Identifier('title'),
        message_col=sql.Identifier('message'),
        image_col=sql.Identifier('image'))
    cursor.execute(query, {'s_m': post_time,
                           'vote_n': 0,
                           'view_n': 0,
                           't': question_list[0],
                           'm': question_list[1],
                           'i': question_list[2]
                           })
    query = sql.SQL("""
            SELECT MAX({id_col})
            FROM {table_name}
                """).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        id_col=sql.Identifier('id'))
    cursor.execute(query)
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        result_list = dictionary['max']
    return result_list


def get_answers(question_id):
    answers_list = get_data_unsorted(ct.TABLE_ANSWER)
    result_list = []
    for element in answers_list:
        if question_id == 'ALL':
            result_dict = {}
            result_dict['id'] = element['id']
            result_dict['submission_time'] = element['submission_time']
            result_dict['vote_number'] = element['vote_number']
            result_dict['question_id'] = element['question_id']
            result_dict['message'] = element['message']
            result_dict['image'] = element['image']
            result_list.append(result_dict)
        elif int(question_id) == element['question_id']:
                result_dict = {}
                result_dict['id'] = element['id']
                result_dict['message'] = element['message']
                result_dict['vote_number'] = element['vote_number']
                result_dict['image'] = element['image']
                result_list.append(result_dict)
    return result_list


@database_common.connection_handler
def post_answer(cursor, question_id, answer):
    if answer[1] == '':
        answer[1] = None
    post_time = ut.get_formatted_time(round(time.time()))
    query = sql.SQL("""
        INSERT INTO {table_name} ({submission_time_col},{vote_number_col},
        {question_id_col},{message_col},{image_col})
        VALUES(%(s_m)s, %(vote_n)s, %(q_i)s, %(m)s, %(i)s)
            """).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        submission_time_col=sql.Identifier('submission_time'),
        vote_number_col=sql.Identifier('vote_number'),
        view_number_col=sql.Identifier('view_number'),
        question_id_col=sql.Identifier('question_id'),
        message_col=sql.Identifier('message'),
        image_col=sql.Identifier('image'))
    cursor.execute(query, {'s_m': post_time,
                           'vote_n': 0,
                           'q_i': question_id,
                           'm': answer[0],
                           'i': answer[1]
                           })
    query = sql.SQL("""
            SELECT MAX({id_col})
            FROM {table_name}
                """).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        id_col=sql.Identifier('id'))
    cursor.execute(query)
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        result_list = dictionary['max']
    return result_list


def sort_questions(order_by, order_direction):
    current_questions_list = get_data_unsorted(ct.TABLE_QUESTION)
    if order_direction == 'desc':
        direction = True
    elif order_direction == 'asc':
        direction = False
    if order_by == 'view_number' or order_by == 'vote_number':
        sorted_questions_list = sorted(current_questions_list, key=lambda current_dict: int(current_dict[order_by]),
                                           reverse=direction)
    else:
        sorted_questions_list = sorted(current_questions_list, key=lambda current_dict: current_dict[order_by],
                                       reverse=direction)
    return sorted_questions_list


@database_common.connection_handler
def edit_question(cursor, question_id, question_data):
    query = sql.SQL("""
        UPDATE {table_name} 
        SET {title_col} = %(t)s,{message_col} = %(m)s
        WHERE {id_col} = %(i)s
            """).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        id_col=sql.Identifier('id'),
        title_col=sql.Identifier('title'),
        message_col=sql.Identifier('message'))
    cursor.execute(query, {'t': question_data[0],
                           'm': question_data[1],
                           'i': question_id
                           })


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    question_id = get_question_id_with_answer_id(answer_id)
    query = sql.SQL("""
        DELETE FROM {table_name}
        WHERE {id_col} = %s
            """).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        id_col=sql.Identifier('id'))
    cursor.execute(query, (answer_id,))
    return question_id


@database_common.connection_handler
def delete_question(cursor, question_id):
    query = sql.SQL("""
        DELETE FROM {table_name}
        WHERE {id_col} = %s
            """).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        id_col=sql.Identifier('id'))
    cursor.execute(query, (question_id,))
    query = sql.SQL("""
        DELETE FROM {table_name}
        WHERE {question_id_col} = %s
            """).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        question_id_col=sql.Identifier('question_id'))
    cursor.execute(query, (question_id,))


@database_common.connection_handler
def count_vote(cursor, table, element_id, vote):
    query = sql.SQL("""
        UPDATE {table_name}
        SET {vote_number_col} = {vote_number_col} + %s
        WHERE {id_col} = %s
            """).format(
        table_name=sql.Identifier(table),
        vote_number_col=sql.Identifier('vote_number'),
        id_col=sql.Identifier('id'))
    cursor.execute(query, (vote,element_id,))


@database_common.connection_handler
def get_question_id_with_answer_id(cursor, answer_id):
    query = sql.SQL("""
                SELECT {question_id_col}
                FROM {table_name}
                WHERE {id_col} = %s
                    """).format(
        table_name=sql.Identifier(ct.TABLE_ANSWER),
        id_col=sql.Identifier('id'),
        question_id_col=sql.Identifier('question_id'))
    cursor.execute(query, (answer_id,))
    data_dict = cursor.fetchall()
    for dictionary in data_dict:
        question_id = dictionary['question_id']
    return question_id


@database_common.connection_handler
def increment_view_number(cursor, question_id):
    query = sql.SQL("""
        UPDATE {table_name}
        SET {view_number_col} = {view_number_col} + 1
        WHERE {id_col} = %s
            """).format(
        table_name=sql.Identifier(ct.TABLE_QUESTION),
        view_number_col=sql.Identifier('view_number'),
        id_col=sql.Identifier('id'))
    cursor.execute(query, (question_id,))