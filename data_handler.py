import csv
from datetime import datetime

FILE_QUESTIONS = 'sample_data/question.csv'
FILE_ANSWERS = 'sample_data/answer.csv'


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
    question_id = int(question_id) - 1
    questions_data_list = get_all_data_from_questions()
    result_list = questions_data_list[question_id][options]
    return result_list


def get_question_answers(question_id):
    with open(FILE_QUESTIONS, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for line in reader:
            if line['id'] == question_id:
                answers_list = line['message'].split(';')
    return answers_list
