import csv
from datetime import datetime
import time

FILE_QUESTIONS = 'sample_data/question.csv'
FILE_ANSWERS = 'sample_data/answer.csv'
DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title' , 'message', 'image']
DATA_HEADER_ANSWERS = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_data_questions_unsorted():
    questions_list = []
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = int(row['submission_time'])
            date_time = datetime.fromtimestamp(timestamp)
            row['submission_time'] = date_time
            questions_list.append(row)
    return questions_list


def get_all_data_from_questions():
    questions_list = get_data_questions_unsorted()
    questions_list = sorted(questions_list, key=lambda current_dict: current_dict['submission_time'], reverse=True)
    return questions_list


def get_question_data(question_id, options):
    questions_data_list = get_all_data_from_questions()
    index = 0
    for element in questions_data_list:
        if question_id == element['id']:
            result_list = questions_data_list[index][options]
        else:
            index += 1
    return result_list


def get_question_content(question_id):
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for line in reader:
            if int(line['id']) == int(question_id):
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
            result_dict = {}
            result_dict['id'] = element['id']
            result_dict['message'] = element['message']
            result_dict['vote_number'] = element['vote_number']
            result_list.append(result_dict)
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
    answer_data.append(question_id)
    answer_data.append(answer[0])
    with open(FILE_ANSWERS, 'a', newline='') as csv_file:
        fieldnames = DATA_HEADER_ANSWERS
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        data_dict = dict(zip(DATA_HEADER_ANSWERS, answer_data))
        writer.writerow(data_dict)
    return answer_data[0]


def sort_questions(order_by, order_direction):
    current_questions_list = get_all_data_from_questions()
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


def delete_question(question_id):
    result_list = []
    final_list = [DATA_HEADER]
    questions_list = []
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    for dictionary in questions_list:
        if dictionary['id'] != question_id:
            result_list.append(dictionary)
    for element in result_list:
        final_list.append(list(element.values()))
    with open(FILE_QUESTIONS, 'w', newline='') as csv_file:
        fieldnames = DATA_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(DATA_HEADER, data))
            writer.writerow(data_dict)
    delete_answer(question_id)


def edit_question(question_id, question_data):
    result_list = []
    final_list = [DATA_HEADER]
    questions_list = []
    with open(FILE_QUESTIONS, 'r') as csv_file:
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
    with open(FILE_QUESTIONS, 'w', newline='') as csv_file:
        fieldnames = DATA_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(DATA_HEADER, data))
            writer.writerow(data_dict)


def delete_answer(question_id=None, answer_id=None):
    result_list = []
    final_list = [DATA_HEADER_ANSWERS]
    questions_list = []
    with open(FILE_ANSWERS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    if answer_id == None:
        for dictionary in questions_list:
            if dictionary['question_id'] != question_id:
                result_list.append(dictionary)
        write_data(result_list, final_list)
    else:
        for dictionary in questions_list:
            if dictionary['id'] == answer_id:
                question_id = dictionary['question_id']
            else:
                result_list.append(dictionary)
        write_data(result_list, final_list)
        return question_id


def write_data(result_list, final_list):
    for element in result_list:
        final_list.append(list(element.values()))
    with open(FILE_ANSWERS, 'w', newline='') as csv_file:
        fieldnames = DATA_HEADER_ANSWERS
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(DATA_HEADER_ANSWERS, data))
            writer.writerow(data_dict)


def vote_up_question(question_id, vote_type):
    result_list = []
    final_list = [DATA_HEADER]
    questions_list = []
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    for dictionary in questions_list:
        if dictionary['id'] == question_id:
            if vote_type == 'up':
                dictionary['vote_number'] = int(dictionary['vote_number']) + 1
            else:
                dictionary['vote_number'] = int(dictionary['vote_number']) - 1
        result_list.append(dictionary)
    for element in result_list:
        final_list.append(list(element.values()))
    with open(FILE_QUESTIONS, 'w', newline='') as csv_file:
        fieldnames = DATA_HEADER
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(DATA_HEADER, data))
            writer.writerow(data_dict)


def vote_up_answer(question_id, vote_type):
    result_list = []
    final_list = [DATA_HEADER_ANSWERS]
    questions_list = []
    with open(FILE_ANSWERS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    for dictionary in questions_list:
        if dictionary['id'] == question_id:
            if vote_type == 'up':
                dictionary['vote_number'] = int(dictionary['vote_number']) + 1
            else:
                dictionary['vote_number'] = int(dictionary['vote_number']) - 1
        result_list.append(dictionary)
    for element in result_list:
        final_list.append(list(element.values()))
    with open(FILE_ANSWERS, 'w', newline='') as csv_file:
        fieldnames = DATA_HEADER_ANSWERS
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for data in final_list:
            data_dict = dict(zip(DATA_HEADER_ANSWERS, data))
            writer.writerow(data_dict)


def get_question_by_answer_id(answer_id):
    questions_list = []
    with open(FILE_ANSWERS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            questions_list.append(row)
    for dictionary in questions_list:
        if dictionary['id'] == answer_id:
            return dictionary['question_id']