'''
Checkers
'''
import sys
from enum import Enum
from functools import partial

from PySide2.QtCore import Qt, QRect
from PySide2.QtGui import QPainter, QColor, QFont, QPaintEvent, QRegion
from PySide2.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QGridLayout,
    QWidget,
    QListWidget,
    QHBoxLayout,
    QVBoxLayout,
    QAbstractItemView,
    QAbstractButton,
    QGraphicsLineItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsGridLayout,
    QGraphicsItem,
    QGraphicsView,
    QMessageBox
)

class CheckerType(Enum):
    BLACK = 1
    RED = 2
    EMPTYWHITE = 3
    EMPTYGRAY = 4

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.buttons = [[], [], [], [], [], [], [], []]
        self.turn = 0
        self.blackWins = 0
        self.redCheckers = 0
        self.redWins = 0
        self.blackCheckers = 0
        self.selected = None
        self.secondTurnBool = False
        
        self.setWindowTitle("Checkers")
        
        self.checkers = QGridLayout()
        taskbar = QHBoxLayout()
        layout = QVBoxLayout()
        
        for row in range(8):
            for col in range(8):
                if ( col % 2 == 1 and ( row == 0 or row == 2 ) ) or ( col % 2 == 0 and row == 1 ):
                    self.buttons[row].append(CheckerSpace(CheckerType.RED, row, col))
                    self.buttons[row][col].clicked.connect(partial(self.buttonClicked, self.buttons[row][col]))
                elif ( col % 2 == 0 and ( row == 5 or row == 7 ) ) or ( col % 2 == 1 and row == 6 ):
                    self.buttons[row].append(CheckerSpace(CheckerType.BLACK, row, col))
                    self.buttons[row][col].clicked.connect(partial(self.buttonClicked, self.buttons[row][col]))
                elif ( col % 2 == 0 and row == 3 ) or ( col % 2 == 1 and row == 4 ):
                    self.buttons[row].append(CheckerSpace(CheckerType.EMPTYWHITE, row, col))
                    self.buttons[row][col].clicked.connect(partial(self.buttonClicked, self.buttons[row][col]))
                else:
                    self.buttons[row].append(CheckerSpace(CheckerType.EMPTYGRAY, row, col))
                    self.buttons[row][col].clicked.connect(partial(self.buttonClicked, self.buttons[row][col]))
        
        self.checkers.setVerticalSpacing(6)
        self.checkers.setHorizontalSpacing(6)
        
        for row in range(8):
            for col in range(8):
                self.checkers.addWidget(self.buttons[row][col], row, col)
        
        
        
        self.blackWinsLabel = QLabel(f"Black Wins: {self.blackWins}")
        self.redCheckersLabel = QLabel(f"Stolen Red Checkers: {self.redCheckers}")
        self.textInfo = QLabel("Black's Turn")
        restart = QPushButton("Restart")
        restart.clicked.connect(self.restartButton)
        self.redWinsLabel = QLabel(f"Red Wins: {self.redWins}")
        self.blackCheckersLabel = QLabel(f"Stolen Black Checkers: {self.blackCheckers}")
        
        taskbar.addWidget(self.blackWinsLabel)
        taskbar.addWidget(self.redCheckersLabel)
        taskbar.addWidget(self.textInfo)
        taskbar.addWidget(restart)
        taskbar.addWidget(self.redWinsLabel)
        taskbar.addWidget(self.blackCheckersLabel)
        layout.addLayout(self.checkers)
        layout.addLayout(taskbar)
        
        widget = QWidget()
        widget.setLayout(layout)
        widget.setStyleSheet("QLabel"
                             "{"
                             "border: 1px solid black; color: red;"
                             "}"
                             "cellRect"
                             "{"
                             "border: 1px solid black; background-color: red;"
                             "}")
        
        self.setCentralWidget(widget)
        
    def buttonClicked(self, checkerSpace):
        self.checkerType = checkerSpace.getType()
        if self.selected == None:
            if self.checkerType == CheckerType.EMPTYGRAY or self.checkerType == CheckerType.EMPTYWHITE:
                self.textInfo.setText("Pick a checker piece.")
            elif self.turn % 2 == 0 and self.checkerType == CheckerType.RED:
                self.textInfo.setText("You can't move the red pieces!")
            elif self.turn % 2 == 1 and self.checkerType == CheckerType.BLACK:
                self.textInfo.setText("You can't move the black pieces!")
            else:
                checkerSpace.addStyle("border : 3px solid blue; ")
                self.selected = checkerSpace
        else:
            if self.checkerType == CheckerType.EMPTYWHITE:
                if self.CheckMove(self.selected, checkerSpace, self.secondTurnBool):
                    self.MakeMove(self.selected, checkerSpace)
                    if self.turn % 2 == 1:
                        self.textInfo.setText("Red's Turn")
                    else:
                        self.textInfo.setText("Black's Turn")
                    self.selected = None
                    
                else:
                    self.textInfo.setText("You can't make that move!")
            elif self.selected == checkerSpace:
                checkerSpace.addStyle("border : 1px solid rgba(0, 0, 0, 150); ")
                self.selected = None
            else:
                self.textInfo.setText("Please pick a empty white space.")
        
    def CheckMove(self, checker, space, secondTurn=False):
        self.opposite = CheckerType.RED if self.turn % 2 == 0 else CheckerType.BLACK
        if ( ( checker.row + 1 == space.row and ( checker.getQueen() or checker.getType() == CheckerType.RED ) ) \
        or ( checker.row - 1 == space.row and ( checker.getQueen() or checker.getType() == CheckerType.BLACK ) ) ) \
        and ( ( checker.col + 1 == space.col ) or ( checker.col - 1 == space.col ) ) and not secondTurn:
            return True 
        elif ( ( checker.row + 2 == space.row ) or ( checker.row - 2 == space.row ) ) and ( ( checker.col + 2 == space.col ) or ( checker.col - 2 == space.col ) ):
            if checker.getQueen() or checker.getType() == CheckerType.RED:
                if checker.row + 2 == space.row and checker.col + 2 == space.col:
                    if self.buttons[checker.row + 1][checker.col + 1].getType() == self.opposite:
                        self.StealChecker(self.buttons[checker.row + 1][checker.col + 1])
                        self.secondTurn(space)
                        return True
                elif checker.row + 2 == space.row and checker.col - 2 == space.col:
                    if self.buttons[checker.row + 1][checker.col - 1].getType() == self.opposite:
                        self.StealChecker(self.buttons[checker.row + 1][checker.col - 1])
                        self.secondTurn(space)
                        return True
            if checker.getQueen() or checker.getType() == CheckerType.BLACK:
                if checker.row - 2 == space.row and checker.col + 2 == space.col:
                    if self.buttons[checker.row - 1][checker.col + 1].getType() == self.opposite:
                        self.StealChecker(self.buttons[checker.row - 1][checker.col + 1])
                        self.secondTurn(space)
                        return True
                elif checker.row - 2 == space.row and checker.col - 2 == space.col:
                    if self.buttons[checker.row - 1][checker.col - 1].getType() == self.opposite:
                        self.StealChecker(self.buttons[checker.row - 1][checker.col - 1])
                        self.secondTurn(space)
                        return True
                else:
                    return False
        else:
            return False
        
    def secondTurn(self, space):
        self.secondTurnBool = False
        return False
        self.opposite = CheckerType.RED if self.turn % 2 == 0 else CheckerType.BLACK
        if space.row + 2 < 8 and space.col + 2 < 8:
            if self.buttons[space.row + 2][space.col + 2].getType() == CheckerType.EMPTYWHITE:
                if self.buttons[space.row + 1][space.col + 1].getType() == self.opposite:
                    self.turn -= 1
                    self.secondTurnBool = True
                    return True
        if space.row + 2 < 8 and space.col - 2 >= 0:
            if self.buttons[space.row + 2][space.col - 2].getType() == CheckerType.EMPTYWHITE:
                if self.buttons[space.row + 1][space.col - 1].getType() == self.opposite:
                    self.turn -= 1
                    self.secondTurnBool = True
                    return True
        if space.row - 2 >= 0 and space.col + 2 < 8:
            if self.buttons[space.row - 2][space.col + 2].getType() == CheckerType.EMPTYWHITE:
                if self.buttons[space.row - 1][space.col + 1].getType() == self.opposite:
                    self.turn -= 1
                    self.secondTurnBool = True
                    return True
        if space.row - 2 < 8 and space.col - 2 < 8:
            if self.buttons[space.row - 2][space.col - 2].getType() == CheckerType.EMPTYWHITE:
                if self.buttons[space.row - 1][space.col - 1].getType() == self.opposite:
                    self.turn -= 1
                    self.secondTurnBool = True
                    return True
        
            
    def MakeMove(self, checker, space):
        space.changeCheckerType(checker.getType())
        checker.changeCheckerType(CheckerType.EMPTYWHITE)
        self.turn += 1
        if checker.getQueen():
            checker.delQueen()
            space.setQueen()
        if space.row == 7 and space.getType() == CheckerType.RED:
            space.setQueen()
        if space.row == 0 and space.getType() == CheckerType.BLACK:
            space.setQueen()
        if self.redCheckers == 12 or self.blackCheckers == 12:
            self.winGame()
    
    def StealChecker(self, checker):
        print(checker.getType())
        if checker.getType() == CheckerType.RED:
            self.redCheckers += 1
            self.redCheckersLabel.setText(f"Stolen Red Checkers: {self.redCheckers}")
        elif checker.getType() == CheckerType.BLACK:
            self.blackCheckers += 1
            self.blackCheckersLabel.setText(f"Stolen Black Checkers: {self.blackCheckers}")
        tempRow = checker.row
        tempCol = checker.col
        checker.changeCheckerType(CheckerType.EMPTYWHITE)
    
    def winGame(self):
        msg = QMessageBox()
        msg.setWindowTitle("GAME OVER")
        if self.redCheckers == 12:
            self.blackWins += 1
            self.blackWinsLabel.setText(f"Black Wins: {self.blackWins}")
            self.textInfo.setText("Black WON!")
            msg.setText("Black WON!")
            msg = msg.exec_()
        if self.blackCheckers == 12:
            self.redWins += 1
            self.redWinsLabel.setText(f"Red Wins: {self.redWins}")
            self.textInfo.setText("Red WON!")
            msg.setText("Red WON!")
            msg = msg.exec_()
        for row in range(8):
            for col in range(8):
                self.buttons[row][col].setDisabled(True)
        
        
    def restartButton(self):
        msg = QMessageBox()
        msg.setText("Are you sure?")
        msg.setWindowTitle("Restart")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgAnswer = msg.exec_()
        if msgAnswer == 16384:
            for row in range(8):
                for col in range(8):
                    self.buttons[row][col].setDisabled(False)
                    if ( col % 2 == 1 and ( row == 0 or row == 2 ) ) or ( col % 2 == 0 and row == 1 ):
                        self.buttons[row][col].changeCheckerType(CheckerType.RED)
                    elif ( col % 2 == 0 and ( row == 5 or row == 7 ) ) or ( col % 2 == 1 and row == 6 ):
                        self.buttons[row][col].changeCheckerType(CheckerType.BLACK)
                    elif ( col % 2 == 0 and row == 3 ) or ( col % 2 == 1 and row == 4 ):
                        self.buttons[row][col].changeCheckerType(CheckerType.EMPTYWHITE)
            self.textInfo.text() == "Black's Turn"
            self.blackCheckers = 0
            self.blackCheckersLabel.setText(f"Stolen Black Checkers: {self.blackCheckers}")
            self.redCheckers = 0
            self.redCheckersLabel.setText(f"Stolen Red Checkers: {self.redCheckers}")

class CheckerSpace(QPushButton):
    def __init__(self, checkerType, row, col, init=True, queen=False):
        if init:
            super().__init__()
        self.checkerType = checkerType
        self.row = row
        self.col = col
        self.queen = queen
        self.styles = " height: 100px; width: 100px; font-size: 60px; color: blue; "
        if self.queen:
            self.setText("Q")
        else:
            self.setText("")
        if self.checkerType == CheckerType.BLACK:
            self.styles += "background-color : rgba(0, 0, 0, 250); border :3px solid rgba(0, 0, 0, 150); border-radius: 50px; "
        elif self.checkerType == CheckerType.RED:
            self.styles += "background-color : red; border :3px solid rgba(0, 0, 0, 150); border-radius: 50px; "
        elif self.checkerType == CheckerType.EMPTYGRAY:
            self.styles += "background-color : gray; border : 0px ; "
        elif self.checkerType == CheckerType.EMPTYWHITE:
            self.styles += "background-color : rgba(240,240,240,255); border : 0px; "
        self.setStyleSheet(self.styles)
        
    def getType(self):
        return self.checkerType
    
    def addStyle(self, style):
        self.styles += style
        self.setStyleSheet(self.styles)
        return self
    def changeCheckerType(self, checkerType):
        self.__init__(checkerType, self.row, self.col, False, self.queen)
        return self
    def getQueen(self):
        return self.queen
    def setQueen(self):
        self.__init__(self.checkerType, self.row, self.col, False, True)
        return self
    def delQueen(self):
        self.__init__(self.checkerType, self.row, self.col, False, False)
        return self
        
app = QApplication()
window = MainWindow()
window.show()
app.exec_()




