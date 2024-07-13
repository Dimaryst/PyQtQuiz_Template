import sqlite3
# Функция для чтения изображения и преобразования его в бинарный формат
def read_image(path):
    with open(path, 'rb') as file:
        return file.read()
conn = sqlite3.connect('questions.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    answer1 TEXT,
    answer2 TEXT,
    answer3 TEXT,
    answer4 TEXT,
    right_answer INTEGER NOT NULL,
    picture BLOB,
    points INTEGER NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS quiz_settings (
    pass_percent INTEGER NOT NULL,
    random_questions BOOL
)
''')

# Вставка данных
cursor.execute('INSERT INTO quiz_settings (pass_percent, random_questions) VALUES (?, ?)', (80, True))

questions = [
    ("Столица Франции", "Париж", "Москва", "Киев", "Вашингтон", 1, read_image("paris.jpeg"), 10),
    ("What is 2 + 2?", "3", "4", "Я не понимаю по-английски", None, 2, None, 5),
    ("Факториал 8?", "40320", "8!", "Восемь", "Что такое факториал?", 1, None, 5),
    ("Красная планета это где?", "Земля", "Марс", "Юпитер", "Солнце", 2, None, 10),
    ("What is the boiling point of water?", "90°C", "100°C", "80°C", None, 2, None, 5),
    ("Что изображено на картинке?", "Кот", "Собака", "Олег", "Где я?", 4, read_image("dog.jpeg"), 5),
    ("Где истина?", "Помогите", "Меня", "Заставялют", "Писать говнокод", 1, read_image("pizded.jpeg"), 5)
]

cursor.executemany('INSERT INTO quiz_questions (question, answer1, answer2, answer3, answer4, right_answer, picture, points) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', questions)

conn.commit()
conn.close()