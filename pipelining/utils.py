# helper function to collect all the image correspondences
# import matplotlib
# matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap

# https://stackoverflow.com/questions/12459811/how-to-embed-matplotlib-in-pyqt-for-dummies


class ImageWidget(QWidget):
    def __init__(self, imageName, saveName=None, numPoints=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.imageName = imageName
        self.saveName = saveName
        self.numPoints = numPoints
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.canvas, self)

        # self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # self.qimg = QImage(str(self.imageName))
        # self.pixmap = QPixmap(QPixmap.fromImage(self.qimg))
        # self.imageLabel = QLabel()
        # self.imageLabel.setPixmap(self.pixmap)
        # self.imageLabel.mousePressEvent = self.getPixel
        # self.layout.addWidget(self.imageLabel)
        # self.setLayout(self.layout)

        self.correspondenceList = []
        print("Created Widget for ", imageName)
        self.displayImage()
        #self.show()

    # def getPixel(self, event):
    #     x = event.pos().x()
    #     y = event.pos().y()
    #     print(x, y)
    #     self.correspondenceList.append((x, y))




    # a figure instance to plot on


        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__


        # this is the Navigation widget
        # it takes the Canvas widget and a parent


        # Just some button connected to `plot` method


        # set the layout
    def savePoints(self):
        print(np.array(self.correspondenceList))
        if len(self.correspondenceList) < self.numPoints:
            self.correspondenceList = [] # reset points
            self.displayImage()
            raise Exception('Not enough points selected. Please select ' + str(self.numPoints) +  ' points.')
            # if buttonReply == QMessageBox.Yes:
            #     print('Yes clicked.')
            #     self.addShirt()
            # else:
            #     print('User is done adding shirts.')
            #     return
        else:
            np.save(str(self.saveName + 'Points.npy'), np.array(self.correspondenceList))
        # self.close()


    def displayImage(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        image_array = plt.imread(self.imageName)
        ax.imshow(image_array)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        def onclick(event):
            if event.inaxes is ax:
                if self.numPoints is not None and len(self.correspondenceList) < self.numPoints:
                    self.correspondenceList.append(np.array((event.xdata, event.ydata)))
                    ax.plot(event.xdata, event.ydata, 'rx')
                    ax.annotate(len(self.correspondenceList), (event.xdata, event.ydata))
                    ax.margins(0)
                    print(event.xdata, event.ydata)
                    self.canvas.draw()

        if self.saveName is not None: # if clicking a reference image, nothing will happen
            cid = self.canvas.mpl_connect('button_press_event', onclick)
        self.canvas.draw()
        # plt.tight_layout() # does not work with plotting markers
        # self.show()



# def collectCorrespondences(image1, image2):
#
#     qimg1 = QImage(str(image1))
#     pixmap1 = QPixmap(QPixmap.fromImage(qimg1))
#     img_label1 = QLabel()
#     img_label1.setPixmap(pixmap1)
#     img_label1.mousePressEvent = getPixel
#     img_label1.show()
    # qimg2 = QImage(str(image2))
    # pixmap2 = QPixmap(QPixmap.fromImage(qimg2))
    # img_label2 = QLabel()
    # img_label2.setPixmap(pixmap2)
    # img_label2.mousePressEvent = getPixel




    # plt.close()

    # if len(points1) < 4 or len(points2) < 4:
    #     print("ERROR: Please select at least 4 corresponding coordinates.")
    # elif len(points1) != len(points2):
    #     print("ERROR: Please select the same number of coordinates on each image.")

    # return [np.matrix.transpose(np.array(points1)),
    #         np.matrix.transpose(np.array(points2))]
