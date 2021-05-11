import csv
from datetime import datetime
import time

FILE_QUESTIONS = 'sample_data/question.csv'
FILE_ANSWERS = 'sample_data/answer.csv'
DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title' , 'message', 'image']


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



def get_question_answers(question_id):
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for line in reader:
            if line['id'] == question_id:
                answers_list = line['message'].split(';')
    return answers_list


def write_user_question(question):
    question_data = []
    questions_data_list = get_all_data_from_question() 
    max = 0
    for element in question_data_list:
        if int(element['id']) > max:
            max = int(element['id'])
    question_data.append(max + 1)
    question_data.append(round(time.time() * 1000)
    print(question_data)
    question_data.append(0)
    question_data.append(0)
    question_data.append(question)
    with open(FILE_QUESTIONS, 'a', newline = '') as csv_file:
        fieldnames = DATA_HEADER
        writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
        data_dict = dict(zip(DATA_HEADER, question_data))
        writer.writerow(data_dict)

