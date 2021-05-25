UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg'}
MAX_PHOTO_SIZE = 10**6

# FILE_QUESTIONS = 'sample_data/question.csv'
# FILE_ANSWERS = 'sample_data/answer.csv'
FILE_QUESTIONS = "D:\\Codecool\\Module_Web\\ask-mate-2-python-radoi-razvan\\sample_data\\question.csv"
FILE_ANSWERS = "D:\\Codecool\\Module_Web\\ask-mate-2-python-radoi-razvan\\sample_data\\answer.csv"
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title' , 'message', 'image']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']

TABLE_QUESTION = 'question'
TABLE_ANSWER = 'answer'
TABLE_QUESTION_TAG = 'question_tag'
TABLE_TAG = 'tag'
TABLE_COMMENT = 'comment'