import csv
from datetime import datetime
from helpers import constants as ct
from helpers import  utils as ut
import time


def get_data_unsorted(FILE_PATH, options = 'timestamp'):
    data_list = []
    with open(FILE_PATH, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if options != 'timestamp':
                date_time = int((row['submission_time']))
                row['submission_time'] = ut.get_formatted_time(date_time)
            data_list.append(row)
    return data_list


def get_data_for_id(FILE_PATH, id, options):
    data_list = get_data_unsorted(FILE_PATH)
    index = 0
    for element in data_list:
        if id == element['id']:
            result_list = data_list[index][options]
        else:
            index += 1
    return result_list


# to do
def post_question(question_list):
    question_data = []
    questions_data_list = get_data_unsorted(ct.FILE_QUESTIONS)
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
    if question_list[2] != '':
        question_data.append(question_list[2])
    with open(ct.FILE_QUESTIONS, 'a', newline = '') as csv_file:
        fieldnames = ct.QUESTION_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        data_dict = dict(zip(ct.QUESTION_HEADER, question_data))
        writer.writerow(data_dict)
    return question_data[0]


def get_answers(question_id):
    answers_list = get_data_unsorted(ct.FILE_ANSWERS, 'formatted_date')
    result_list = []
    for element in answers_list:
        if question_id == 'ALL':
            print('getting all')
            result_dict = {}
            result_dict['id'] = element['id']
            result_dict['submission_time'] = element['submission_time']
            result_dict['vote_number'] = element['vote_number']
            result_dict['question_id'] = element['question_id']
            result_dict['message'] = element['message']
            result_dict['image'] = element['image']
            result_list.append(result_dict)
        elif question_id == element['question_id']:
                print('getting for question id ', question_id)
                result_dict = {}
                result_dict['id'] = element['id']
                result_dict['message'] = element['message']
                result_dict['vote_number'] = element['vote_number']
                result_dict['image'] = element['image']
                result_list.append(result_dict)
    return result_list


def post_answer(question_id, answer):
    print('posting answer')
    answer_data = []
    all_answers_list = get_data_unsorted(ct.FILE_ANSWERS)
    data_list = get_answers(question_id)
    max_id = 0
    for element in all_answers_list:
        if int(element['id']) > max_id:
            max_id = int(element['id'])
    print('max id is ', max_id)
    answer_data.append(max_id + 1)
    answer_data.append(round(time.time()))
    answer_data.append(0)
    answer_data.append(question_id)
    answer_data.append(answer[0])
    if answer[1] != '':
        answer_data.append(answer[1])
    with open(ct.FILE_ANSWERS, 'a', newline='') as csv_file:
        fieldnames = ct.ANSWER_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        data_dict = dict(zip(ct.ANSWER_HEADER, answer_data))
        writer.writerow(data_dict)
    return answer_data[0]


def sort_questions(order_by, order_direction):
    current_questions_list = get_data_unsorted(ct.FILE_QUESTIONS)
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

# to do
# def delete_from_database() for questions or answers


# to do
def edit_question(question_id, question_data):
    result_list = []
    final_list = [ct.QUESTION_HEADER]
    questions_list = []
    with open(ct.FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    for dictionary in questions_list:
        if dictionary['id'] == question_id:
            dictionary['submission_time'] = round(time.time())
            dictionary['title'] = question_data[0]
            dictionary['message'] = question_data[1]
        result_list.append(dictionary)
    for element in result_list:
        final_list.append(list(element.values()))
    print('final list is ', final_list)
    with open(ct.FILE_QUESTIONS, 'w', newline='') as csv_file:
        fieldnames = ct.QUESTION_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(ct.QUESTION_HEADER, data))
            writer.writerow(data_dict)


# to do
def delete_answer(question_id = None, answer_id = None):
    result_list = []
    final_list = [ct.ANSWER_HEADER]
    answers_list = get_data_unsorted(ct.FILE_ANSWERS)
    if answer_id is None:
        for dictionary in answers_list:
            if dictionary['question_id'] != question_id:
                result_list.append(dictionary)
        write_data(ct.FILE_ANSWERS, ct.ANSWER_HEADER, result_list, final_list)
    else:
        for dictionary in answers_list:
            if dictionary['id'] == answer_id:
                question_id = dictionary['question_id']
            else:
                result_list.append(dictionary)
        write_data(ct.FILE_ANSWERS, ct.ANSWER_HEADER, result_list, final_list)
        return question_id


def delete_question(question_id):
    result_list = []
    final_list = [ct.QUESTION_HEADER]
    questions_list = get_data_unsorted(ct.FILE_QUESTIONS)
    for element in questions_list:
        if element['id'] != question_id:
            result_list.append(element)
    write_data(ct.FILE_QUESTIONS, ct.QUESTION_HEADER, result_list, final_list)


def write_data(FILE_PATH, HEADER, result_list, final_list):
    for element in result_list:
        final_list.append(list(element.values()))
    with open(FILE_PATH, 'w', newline='') as csv_file:
        fieldnames = HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(HEADER, data))
            writer.writerow(data_dict)


def count_vote(FILE_PATH, HEADER, element_id, vote_type):
    result_list = []
    final_list = [HEADER]
    data_list = []
    with open(FILE_PATH, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data_list.append(row)
    for dictionary in data_list:
        if dictionary['id'] == element_id:
            if vote_type == 'up':
                dictionary['vote_number'] = int(dictionary['vote_number']) + 1
            else:
                dictionary['vote_number'] = int(dictionary['vote_number']) - 1
        result_list.append(dictionary)
    write_data(FILE_PATH, HEADER, result_list, final_list)


def get_question_id_with_answer_id(answer_id):
    questions_list = []
    with open(ct.FILE_ANSWERS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    for dictionary in questions_list:
        if dictionary['id'] == answer_id:
            return dictionary['question_id']


def increment_view_number(question_id):
    result_list = []
    final_list = [ct.QUESTION_HEADER]
    questions_list = []
    with open(ct.FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    for dictionary in questions_list:
        if dictionary['id'] == question_id:
            dictionary['view_number'] = int(dictionary['view_number']) + 1
        result_list.append(dictionary)
    for element in result_list:
        final_list.append(list(element.values()))
    with open(ct.FILE_QUESTIONS, 'w', newline='') as csv_file:
        fieldnames = ct.QUESTION_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(ct.QUESTION_HEADER, data))
            writer.writerow(data_dict)

