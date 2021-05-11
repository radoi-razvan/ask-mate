import csv
from datetime import datetime
import time

FILE_QUESTIONS = 'sample_data/question.csv'
FILE_ANSWERS = 'sample_data/answer.csv'
DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title' , 'message', 'image']
DATA_HEADER_ANSWERS = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_all_data_from_questions():
    questions_list = []
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = int(row['submission_time'])
            date_time = datetime.fromtimestamp(timestamp)
            row['submission_time'] = date_time
            questions_list.append(row)
    return questions_list


def get_question_data(question_id, options):
    questions_data_list = get_all_data_from_questions()
    index = 0
    for element in questions_data_list:
        if question_id in element.values():
            result_list = questions_data_list[index][options]
        else:
            index += 1
    return result_list


def get_question_content(question_id):
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for line in reader:
            if line['id'] == question_id:
                answers_list = line['message'].split(';')
    return answers_list


def write_user_question(question_list):
    question_data = []
    questions_data_list = get_all_data_from_questions()
    max = 0
    for element in questions_data_list:
        if int(element['id']) > max:
            max = int(element['id'])
    question_data.append(max + 1)
    question_data.append(round(time.time()))
    question_data.append(0)
    question_data.append(0)
    question_data.append(question_list[0])
    question_data.append(question_list[1])
    with open(FILE_QUESTIONS, 'a', newline = '') as csv_file:
        fieldnames = DATA_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        data_dict = dict(zip(DATA_HEADER, question_data))
        writer.writerow(data_dict)
    return question_data[0]


def get_answers(question_id):
    answers_list = get_all_data_from_answers()
    result_list = []
    for element in answers_list:
        if question_id == element['question_id']:
            result_list.append(element['message'])
    return result_list


def get_all_data_from_answers():
    answers_list = []
    with open(FILE_ANSWERS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = int(row['submission_time'])
            date_time = datetime.fromtimestamp(timestamp)
            row['submission_time'] = date_time
            answers_list.append(row)
    return answers_list


def write_answer(question_id, answer):
    answer_data = []
    questions_data_list = get_all_data_from_answers()
    max = 0
    for element in questions_data_list:
        if int(element['id']) > max:
            max = int(element['id'])
    answer_data.append(max + 1)
    answer_data.append(round(time.time()))
    answer_data.append(0)
    answer_data.append(0)
    answer_data.append(question_id)
    answer_data.append(answer)
    with open(FILE_ANSWERS, 'a', newline = '') as csv_file:
        fieldnames = DATA_HEADER_ANSWERS
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        data_dict = dict(zip(DATA_HEADER_ANSWERS, answer_data))
        writer.writerow(data_dict)
    return answer_data[0]


