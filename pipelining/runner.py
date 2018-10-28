from utils import ImageWidget
import matplotlib.pyplot as plt
from scipy import misc
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
#https://stackoverflow.com/questions/35992088/why-mousemoveevent-does-nothing-in-pyqt5
class SeamApp(QWidget):
    # source: https://pythonspot.com/pyqt5-image/
    def __init__(self):
        super().__init__()
        self.title = 'Does it Fit'
        self.left = 0
        self.top = 0
        self.width = 640
        self.height = 480
        self.tShirtName = ""
        self.userImageName = ""

        self.referenceImageList = [("./images/referenceLeftSleeve.png", "leftSleeve"),
                                    ("./images/referenceRightSleeve.png", "rightSleeve"),
                                    ("./images/referenceTorso.png", "torso")]
        self.collectingTShirtPts = False

        self.referenceWidgetList = [ImageWidget(s[0]) for s in self.referenceImageList]

        # self.leftSleeve = ImageWidget(str())
        # self.rightSleeve = ImageWidget(str())
        # self.torso = ImageWidget(str())
        self.currentImageName = None
        self.currentImageWidget = None
        self.currentRefImage = 0

        self.countShirts = 0
        self.tShirtButton = QPushButton('Add A T-Shirt')
        self.tShirtButton.clicked.connect(self.addShirt)

        self.submitButton = QPushButton('Submit')
        self.submitButton.clicked.connect(self.submitPoints)

        self.setLayout(QVBoxLayout())

        #self.layout = QHBoxLayout()
        self.initUI()

    def submitPoints(self):
        if self.currentImageWidget is not None:
            self.currentImageWidget.savePoints()
            # for i in reversed(range(self.layout().count())):
            #     item = self.layout().itemAt(i).widget()
            #     if item:
            #         item.setParent(None)
            #self.layout = QHBoxLayout()
            # self.layout.addWidget(self.submitButton)
            self.currentRefImage += 1
            self.currentRefImage %= len(self.referenceImageList)
            print(self.referenceImageList[self.currentRefImage][1])
            if self.currentRefImage != 0: # wrap around to the beginning again
                if self.collectingTShirtPts:
                    file_name = "t_shirt" + str(self.countShirts) + self.referenceImageList[self.currentRefImage][1]
                    self.collectCorrespondences(self.currentImageName, self.referenceWidgetList[self.currentRefImage],
                                            file_name)
                else:
                    self.collectCorrespondences(self.currentImageName,
                    self.referenceWidgetList[self.currentRefImage],
                    self.referenceImageList[self.currentRefImage][1])
            else:
                if self.countShirts == 0:
                    self.addShirt()
                else:
                    buttonReply = QMessageBox.question(self, 'Add a Shirt', "Would you like to add another shirt?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if buttonReply == QMessageBox.Yes:
                        print('Yes clicked.')
                        self.addShirt()
                    else:
                        print('User is done adding shirts.')
                        return


    def addShirt(self):
        self.currentImageName = self.openImageFileDialog("Select image of your T-Shirt")
        self.collectingTShirtPts = True
        if self.currentImageName is not None:
            self.countShirts += 1
        self.collectCorrespondences(self.currentImageName, self.referenceWidgetList[self.currentRefImage],
        "t_shirt" + str(self.countShirts) + self.referenceImageList[self.currentRefImage][1])


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # loop = QEventLoop()
        # QTimer.singleShot(1000, loop.quit)
        # loop.exec_()

        # user loads in image of self just once and selects correspondences
        self.currentImageName = self.openImageFileDialog("Select image of yourself")
        self.collectCorrespondences(self.currentImageName, self.referenceWidgetList[self.currentRefImage],
                                    self.referenceImageList[self.currentRefImage][1])
        # self.collectCorrespondences(self.userImageName, self.leftSleeve, "userImageLeftSleeve")
        # self.collectCorrespondences(self.userImageName, self.rightSleeve, "userImageRightSleeve")
        # self.collectCorrespondences(self.userImageName, self.torso, "userImageTorso")

        # userImage = plt.imread(self.userImageName)

        # countShirts = 1


            # tShirtImage = plt.imread(self.tShirtName)
            # collectCorrespondences(self.tShirtName, self.userImageName)
            # countShirts += 1
            # downsize image to match user dimensions
            # correspondences
            # save image and correspondences
            # ask about another picture



        #self.openFileNamesDialog()
        #self.saveFileDialog()

        self.show()

    def openImageFileDialog(self, message):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,str(message), "","Images (*.png *.jpeg *.jpg)", options=options)
        return fileName # let it return None


    # https://www.programcreek.com/python/example/82618/PyQt5.QtWidgets.QLabel
    def collectCorrespondences(self, uploadedImage, referenceImageWidget, savePointsName):
        print('collecting')

        self.currentImageWidget = ImageWidget(str(uploadedImage), savePointsName)

        hbox = QHBoxLayout()
        hbox.addWidget(self.currentImageWidget)
        hbox.addWidget(referenceImageWidget)
        referenceImageWidget.show()
        self.currentImageWidget.show()

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.submitButton)


        # self.layout.addLayout(hbox)
        # self.layout.addWidget(self.submitButton)
        # self.layout.setContentMargins(0, 0, 0, 0)

        self.deleteItems(self.layout())

        self.layout().addLayout(vbox)
        self.show()

    # def getPixel(self, event):
    #     x = event.pos().x()
    #     y = event.pos().y()
    #     print(x, y)
        # return (x,y)
    def deleteItems(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    if widget not in self.referenceWidgetList:
                        widget.deleteLater()
                    else:
                        widget.hide()
                else:
                    self.deleteItems(item.layout())

def pipeline():
    app = QApplication(sys.argv)
    ex = SeamApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    pipeline()
