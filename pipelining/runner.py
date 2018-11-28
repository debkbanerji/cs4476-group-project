import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from pipelining.utils import ImageWidget
from scipy import misc
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox, QErrorMessage
from cornerDetection.cornerDetector import getShirtCorners
sys.path.append('../')
global currentImageName


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

        # self.referenceImageList = [("./images/referenceLeftSleeve.png", "leftSleeve", 4),
                                    # ("./images/referenceRightSleeve.png", "rightSleeve", 5),
                                    # ("./images/referenceTorso.png", "torso", 8)]
        self.referenceImage = "./images/referenceShirt.png"
        self.numPoints = 10
        self.referenceImageWidget = ImageWidget(self.referenceImage)
        self.collectingTShirtPts = False

        # self.referenceWidgetList = [ImageWidget(s[0]) for s in self.referenceImageList]

        # self.leftSleeve = ImageWidget(str())
        # self.rightSleeve = ImageWidget(str())
        # self.torso = ImageWidget(str())
        self.currentImageName = None
        self.currentImageWidget = None
        # self.currentRefImage = 0

        self.countShirts = 0
        self.tShirtButton = QPushButton('Add A T-Shirt')
        self.tShirtButton.clicked.connect(self.addShirt)

        self.submitButton = QPushButton('Submit')
        self.submitButton.clicked.connect(self.submitPoints)

        self.setLayout(QVBoxLayout())

        # self.layout = QHBoxLayout()
        self.initUI()

    def submitPoints(self):
        if self.currentImageWidget is not None:
            try:
                self.currentImageWidget.savePoints()
                np.save("userImage.npy", misc.imread(self.currentImageName))
                self.addShirt()
            except Exception as err:
                messageBox = QErrorMessage()
                messageBox.showMessage(err.args[0])
                messageBox.exec()

            # for i in reversed(range(self.layout().count())):
            #     item = self.layout().itemAt(i).widget()
            #     if item:
            #         item.setParent(None)
            # self.layout = QHBoxLayout()
            # self.layout.addWidget(self.submitButton)
            # self.currentRefImage += 1
            # self.currentRefImage %= len(self.referenceImageList)
            # print(self.referenceImageList[self.currentRefImage][1])

            # save the points for the user's image
            # now ask for t-shirt image uploads

    def saveShirtCorners(self, shirtCorners, saveName):
        global currentImageName
        # leftNeckCorner, leftShoulderCorner, leftSleeveTopCorner, leftSleeveBottomCorner, bottomLeftCorner
        # saved as y,x, need to change to x,y
        # print(shirtCorners['leftNeckCorner'].shape)
        y, x = shirtCorners['leftNeckCorner']
        savedCorners = np.array([x, y])
        y, x = shirtCorners['leftShoulderCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['leftSleeveTopCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['leftSleeveBottomCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['bottomLeftCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['bottomRightCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['rightSleeveBottomCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['rightSleeveTopCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['rightShoulderCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))
        y, x = shirtCorners['rightNeckCorner']
        savedCorners = np.vstack((savedCorners, [x, y]))

        np.save(saveName + "Points.npy", savedCorners)

        currentImageName = self.currentImageName

    def addAnotherShirt(self):
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
            shirtSaveName = "t_shirt" + str(self.countShirts)
            shirtImg = misc.imread(self.currentImageName)
            shirtCorners, maskWithoutCollar = getShirtCorners(shirtImg)

            np.save(shirtSaveName + "Img.npy", shirtImg)
            np.save(shirtSaveName + "Mask.npy", maskWithoutCollar)
            self.saveShirtCorners(shirtCorners, shirtSaveName)
            self.addAnotherShirt()
        # foregroundMask(misc.imread(self.currentImageName, mode='RGBA'), "t_shirt" + str(self.countShirts))
        # # self.collectCorrespondences(self.currentImageName, self.referenceWidgetList[self.currentRefImage], # "t_shirt" + str(self.countShirts) + self.referenceImageList[self.currentRefImage][1])

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # loop = QEventLoop()
        # QTimer.singleShot(1000, loop.quit)
        # loop.exec_()

        # user loads in image of self just once and selects correspondences
        self.currentImageName = self.openImageFileDialog("Select image of yourself")
        self.collectCorrespondences(self.currentImageName, self.referenceImageWidget, "user")
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
        return fileName  # let it return None

    # https://www.programcreek.com/python/example/82618/PyQt5.QtWidgets.QLabel
    def collectCorrespondences(self, uploadedImage, referenceImageWidget, savePointsName):
        print('collecting')

        self.currentImageWidget = ImageWidget(str(uploadedImage), savePointsName, numPoints=self.numPoints)

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

        # self.deleteItems(self.layout())

        self.layout().addLayout(vbox)
        self.show()

    # def getPixel(self, event):
    #     x = event.pos().x()
    #     y = event.pos().y()
    #     print(x, y)
        # return (x,y)
    # def deleteItems(self, layout):
    #     if layout is not None:
    #         while layout.count():
    #             item = layout.takeAt(0)
    #             widget = item.widget()
    #             if widget is not None:
    #                 if widget not in self.referenceWidgetList:
    #                     widget.deleteLater()
    #                 else:
    #                     widget.hide()
    #             else:
    #                 self.deleteItems(item.layout())


def pipeline():
    app = QApplication(sys.argv)
    ex = SeamApp()
    try:
        sys.exit(app.exec_())
    finally:
        return currentImageName


def computeH(t1, t2):
    pre_matrix = []
    for i in range(len(t1[0])):
        x1 = t1[0][i]
        x2 = t1[1][i]

        x1_prime = t2[0][i]
        x2_prime = t2[1][i]

        transposed1 = [x1, x2, 1, 0, 0, 0, -x1_prime * x1, -x1_prime * x2, -x1_prime]
        transposed2 = [0, 0, 0, x1, x2, 1, -x2_prime * x1, -x2_prime * x2, -x2_prime]
        pre_matrix.append(transposed1)
        pre_matrix.append(transposed2)

    matrix = np.matrix(pre_matrix)

    u, s, v = np.linalg.svd(matrix)
    homography = np.reshape(v[-1], (3, 3))
    return homography


def warpImage(inputIm, image, refIm, H):
    homography = H
    inverted_H = np.linalg.inv(homography)

    input_maxRow = inputIm.shape[0]
    input_maxCol = inputIm.shape[1]

    BACKGROUND_PIXEL = inputIm[0][0]
    print('background_pixel = ', BACKGROUND_PIXEL)

    ## WARP ##
    input_TOP_L = np.asarray(homography.dot(np.asarray([0, 0, 1])))
    input_TOP_L_actual = input_TOP_L[0][0] / input_TOP_L[0][2], input_TOP_L[0][1] / input_TOP_L[0][2]
    input_TOP_R = np.asarray(homography.dot(np.asarray([input_maxCol, 0, 1])))
    input_TOP_R_actual = input_TOP_R[0][0] / input_TOP_R[0][2], input_TOP_R[0][1] / input_TOP_R[0][2]
    input_BOT_L = np.asarray(homography.dot(np.asarray([0, input_maxRow, 1])))
    input_BOT_L_actual = input_BOT_L[0][0] / input_BOT_L[0][2], input_BOT_L[0][1] / input_BOT_L[0][2]
    input_BOT_R = np.asarray(homography.dot(np.asarray([input_maxCol, input_maxRow, 1])))
    input_BOT_R_actual = input_BOT_R[0][0] / input_BOT_R[0][2], input_BOT_R[0][1] / input_BOT_R[0][2]

    input_coords = []
    input_coords.append(input_TOP_L_actual)
    input_coords.append(input_TOP_R_actual)
    input_coords.append(input_BOT_L_actual)
    input_coords.append(input_BOT_R_actual)

    input_smallest_x = min([x[0] for x in input_coords])
    input_greatest_x = max([x[0] for x in input_coords])
    input_smallest_y = min([x[1] for x in input_coords])
    input_greatest_y = max([x[1] for x in input_coords])

    # find 4 corners in new image
    x_shape = int(input_greatest_x - input_smallest_x)
    y_shape = int(input_greatest_y - input_smallest_y)

    newImg = np.zeros((y_shape, x_shape, 3), dtype=np.uint8)
    for rows in range(newImg.shape[0]):
        for cols in range(newImg.shape[1]):
            homogenous_coords = np.asarray([cols + input_smallest_x, rows + input_smallest_y, 1])
            input_coords = np.asarray(inverted_H.dot(homogenous_coords))

            # Convert out of homogenous
            input_coords_normed = (input_coords[0][0] / input_coords[0][2], input_coords[0][1] / input_coords[0][2])
            input_coords_actual = (int(input_coords_normed[0]),
                                   int(input_coords_normed[1]))

            if input_coords_actual[0] >= 0 and input_coords_actual[0] < inputIm.shape[1]:
                if input_coords_actual[1] >= 0 and input_coords_actual[1] < inputIm.shape[0]:
                    if not np.array_equal(BACKGROUND_PIXEL, inputIm[input_coords_actual[1]][input_coords_actual[0]]):
                        newImg[rows][cols] = inputIm[input_coords_actual[1]][input_coords_actual[0]]

    ## MERGE ##
    # find 4 corners in new image
    x_min = min(input_smallest_x, 0)
    x_max = max(input_greatest_x, refIm.shape[1])
    y_min = min(input_smallest_y, 0)
    y_max = max(input_greatest_y, refIm.shape[0])

    x_shape = int(x_max - x_min)
    y_shape = int(y_max - y_min)

    stitchedImg = np.zeros((y_shape, x_shape, 3), dtype=np.uint8)

    for rows in range(stitchedImg.shape[0]):
        for cols in range(stitchedImg.shape[1]):
            homogenous_coords = np.asarray([int(cols + x_min), int(rows + y_min), 1])
            input_coords = np.asarray(inverted_H.dot(homogenous_coords))

            # Convert out of homogenous
            input_coords_normed = (input_coords[0][0] / input_coords[0][2], input_coords[0][1] / input_coords[0][2])
            input_coords_actual = (int(input_coords_normed[0]),
                                   int(input_coords_normed[1]))

            if rows + (y_min) >= 0 and rows + y_min < refIm.shape[0] and cols + x_min < refIm.shape[1] and (
                    cols + (x_min)) >= 0:
                stitchedImg[rows][cols] = refIm[int(rows + y_min)][int(cols + x_min)]
            if input_coords_actual[0] >= 0 and input_coords_actual[0] < inputIm.shape[1]:
                if input_coords_actual[1] >= 0 and input_coords_actual[1] < inputIm.shape[0]:
                    if not np.array_equal(BACKGROUND_PIXEL, inputIm[input_coords_actual[1]][input_coords_actual[0]]):
                        stitchedImg[rows][cols] = image[input_coords_actual[1]][input_coords_actual[0]]

    fig, ax = plt.subplots(1, 2)
    img_vec2 = stitchedImg
    ax[0].imshow(img_vec2)
    blurred = cv2.medianBlur(stitchedImg, 15)
    sharpened = misc.imfilter(blurred, 'sharpen')
    ax[1].imshow(sharpened)
    plt.title('Merged Shirt with blurring')
    plt.show()


def mapShirt(shirt):
    human = 'kirtan_img.jpg'
    image_path = 'images/'

    shirt_img = plt.imread(shirt)
    shirt_foreground_img = np.asarray(np.load('t_shirt1Mask.npy'))
    human_img = plt.imread(image_path + human)

    pts_human = np.asarray(np.load('userPoints.npy'))
    userpoints = [pts_human[:, 0], pts_human[:, 1]]

    pts_shirt = np.asarray(np.load('t_shirt1Points.npy'))
    shirtpoints = [pts_shirt[:, 0], pts_shirt[:, 1]]

    homography = computeH(shirtpoints, userpoints)
    warpImage(shirt_foreground_img, shirt_img, human_img, homography)


if __name__ == "__main__":
    shirt = pipeline()
    mapShirt(shirt)
