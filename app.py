import sys
import sqlite3
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QCheckBox, QPushButton, QProgressBar
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

# Класс для основного окна приложения
class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design.ui', self)  # Загрузка дизайна
        self.conn = sqlite3.connect('questions.db')
        self.cursor = self.conn.cursor()
        
        self.questions = self.load_questions()
        self.total_questions = len(self.questions)
        self.current_question_index = 0
        self.answers = [None] * self.total_questions
        
        self.initUI()
        self.show_popup()
        
    def initUI(self):
        self.serviceLabel.setVisible(False)
        self.NextQuestionButton.clicked.connect(self.next_question)
        self.PrevQuestionButton.clicked.connect(self.prev_question)
        self.pushButtonFinish.clicked.connect(self.finish_quiz)
        self.actionExit.triggered.connect(self.close)
        self.actionRestart_Test.triggered.connect(self.restart_quiz)

        self.check_boxes = [
            self.checkBox_answer_1,
            self.checkBox_answer_2,
            self.checkBox_answer_3,
            self.checkBox_answer_4
        ]

        for check_box in self.check_boxes:
            check_box.stateChanged.connect(self.on_checkbox_state_changed)

        self.update_ui()
    
    def load_questions(self):
        self.cursor.execute('SELECT pass_percent, random_questions FROM quiz_settings')
        settings = self.cursor.fetchone()
        self.pass_percent = settings[0]
        random_questions = settings[1]

        self.cursor.execute('''
            SELECT id, question, answer1, answer2, answer3, answer4, right_answer, picture, points 
            FROM quiz_questions
            WHERE (answer1 IS NOT NULL OR answer2 IS NOT NULL OR answer3 IS NOT NULL OR answer4 IS NOT NULL)
            AND (answer1 IS NOT NULL AND answer2 IS NOT NULL)
        ''')
        questions = self.cursor.fetchall()

        if random_questions:
            random.shuffle(questions)
        
        return questions
    
    def show_popup(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Для прохождения теста необходимо набрать {self.pass_percent} процентов правильных ответов")
        msg.setWindowTitle("Информация")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.start_test)
        msg.exec_()
        
    def start_test(self, i):
        pass  # Ничего не делаем, просто закрываем поп-ап

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

    def update_ui(self):
        question = self.questions[self.current_question_index]
        self.labelQuestionText.setText(question[1])
        
        # Обновляем виджет изображения
        if question[7]:
            pixmap = QPixmap()
            pixmap.loadFromData(question[7])
            self.labelImage.setPixmap(pixmap)
        else:
            self.labelImage.clear()
        
        # Обновляем варианты ответов
        answers = [question[2], question[3], question[4], question[5]]
        for i, check_box in enumerate(self.check_boxes):
            if answers[i]:
                check_box.setText(answers[i])
                check_box.setEnabled(True)
                check_box.setChecked(False)
            else:
                check_box.setText("")
                check_box.setEnabled(False)
        
        self.CounterQuestionsLabel.setText(f"Вопросов: {self.current_question_index + 1}/{self.total_questions}")
        self.CurrentQuestionLabel.setText(f"Текущий вопрос: {self.current_question_index + 1}")
        self.update_progress()
        self.update_navigation_buttons()
    
    def update_progress(self):
        progress = (self.current_question_index + 1) / self.total_questions * 100
        self.progressBar.setValue(int(progress))

    def update_navigation_buttons(self):
        if self.current_question_index == 0:
            self.PrevQuestionButton.setEnabled(False)
        else:
            self.PrevQuestionButton.setEnabled(True)

        if self.current_question_index == self.total_questions - 1:
            self.NextQuestionButton.setEnabled(False)
        else:
            self.NextQuestionButton.setEnabled(True)
    
    def next_question(self):
        self.save_current_answer()
        if self.current_question_index < self.total_questions - 1:
            self.current_question_index += 1
            self.update_ui()
    
    def prev_question(self):
        self.save_current_answer()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.update_ui()
    
    def save_current_answer(self):
        for i, check_box in enumerate(self.check_boxes):
            if check_box.isChecked():
                self.answers[self.current_question_index] = i + 1
                break
        else:
            self.answers[self.current_question_index] = None
    
    def restart_quiz(self):
        self.answers = [None] * self.total_questions
        self.current_question_index = 0
        self.update_ui()
    
    def finish_quiz(self):
        self.save_current_answer()
        correct_answers = sum(1 for i, ans in enumerate(self.answers) if ans == self.questions[i][6])
        total_points = sum(self.questions[i][8] for i, ans in enumerate(self.answers) if ans == self.questions[i][6])
        max_points = sum(q[8] for q in self.questions)
        passed = (correct_answers / self.total_questions) * 100 >= self.pass_percent

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Количество правильных ответов: {correct_answers}\n"
                    f"Количество очков: {total_points}\n"
                    f"Максимально возможный бал: {max_points}\n"
                    f"{'Пройден' if passed else 'Не пройден'}")
        msg.setWindowTitle("Результаты")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.restart_quiz)
        msg.exec_()

    def on_checkbox_state_changed(self, state):
        sender = self.sender()
        if state == 2:  # Если чекбокс включен
            for check_box in self.check_boxes:
                if check_box != sender:
                    check_box.setChecked(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    quiz_app = QuizApp()
    quiz_app.show()
    sys.exit(app.exec_())