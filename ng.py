# SWAMI KARUPPASWAMI THUNNAI

import sys
from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget, QPlainTextEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QThread
from sklearn.externals import joblib
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from nltk.tokenize import TweetTokenizer
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import numpy as np


def preprocesst(tweet_text):
    """
    Will preprocess the tweets like remove the usernames, hashtags, urls and
    will preprocess the content suitable for NLP.
    :return: preprocessed tweet
    """
    # convert the tweet to the lower case
    tweet_text = tweet_text.lower()
    tokenizer = TweetTokenizer()
    words = tokenizer.tokenize(tweet_text)
    preprocessed_words = []
    for word in words:
        if word.startswith("@") or word.startswith("#") or word.startswith("https://") or word.startswith("http://"):
            pass
        else:
            preprocessed_words.append(word)
    # remove the stop words
    stopwords_removed = [word for word in preprocessed_words if not word in stopwords.words("english")]
    # make sure they are words
    punc_remover = lambda word: re.sub("[^A-Za-z]", " ", word)
    # get the pure words without punctuation
    pure_words = list(map(punc_remover, stopwords_removed))
    # Stem the words
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in pure_words]
    # strip the words
    stripper = lambda word: word.strip()
    stemmed_words = list(map(stripper, stemmed_words))
    stemmed_words = filter(None, stemmed_words)
    # Get our processed tweet
    processed_tweet = " ".join(stemmed_words)
    return processed_tweet

class BadCommentThread(QThread):

    def __init__(self, comment, signal):
        QThread.__init__(self)
        self.comment = comment
        print(self.comment)
        self.signal = signal

    def run(self):
        table = {
            1: "General message",
            2: "Offensive message",
            0: "Hate message"
        }
        cv = joblib.load("hate_cv.pkl")
        classifier = joblib.load("hate.pkl")
        self.comment = preprocesst(self.comment)
        array = cv.transform([self.comment,]).toarray()
        result = classifier.predict(array)
        self.signal.emit([self.comment, table[result[0]]])



class BadComment(QWidget):

    signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.thread = None
        self.signal.connect(self.add)
        main_layout = QVBoxLayout()
        heading = QLabel("<h1>Kick out the bad guys from your forum at ease!</h>")
        heading.setPixmap(QPixmap("one.png"))
        main_layout.addWidget(heading)
        main_layout.addWidget(QLabel("<h3>Enter your text: </h3>"))
        self.text = QPlainTextEdit()
        main_layout.addWidget(self.text)
        check = QPushButton("Check this comment")
        check.clicked.connect(self.check)
        main_layout.addWidget(check)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(("COMMENT", "TYPE"))
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)


    def check(self):
        print(self.text.toPlainText())
        self.thread = BadCommentThread(self.text.toPlainText(), self.signal)
        self.thread.start()

    @pyqtSlot(list)
    def add(self, value):
        row_count = self.table.rowCount()
        self.table.setRowCount(row_count+1)
        self.table.setItem(row_count, 0, QTableWidgetItem(value[0]))
        self.table.setItem(row_count, 1, QTableWidgetItem(value[1]))

class NightGhost(QTabWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("The NightGhost Company")
        self.setGeometry(300,300,800,600)
        self.addTab(BadComment(), "Kick Out the bad guys")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ng = NightGhost()
    ng.show()
    sys.exit(app.exec())
