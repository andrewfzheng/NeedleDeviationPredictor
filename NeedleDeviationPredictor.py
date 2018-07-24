from __main__ import vtk, qt, ctk, slicer
from math import exp
import os


class NeedleDeviationPredictor:
    def __init__(self, parent):
        parent.title = "Needle Deviation Predictor"
        parent.categories = ["Utilities"]
        parent.contributors = ["Andrew Zheng"]
        parent.helpText = """
        """
        parent.acknowledgementText = """
        Pedro Moreira, PhD, Nobuhiko Hata, PhD
        """        
        parent.icon = qt.QIcon(os.path.dirname(os.path.realpath(__file__)) + '/Needle Deviation Predictor GUI/icon.png')
        self.parent = parent


class NeedleDeviationPredictorWidget:
    def __init__(self, parent=None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
            self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):
        self.dir = os.path.dirname(os.path.realpath(__file__))

        #
        # Setup
        #
        setupWindow = ctk.ctkCollapsibleButton()
        setupWindow.text = 'Setup'
        self.layout.addWidget(setupWindow)
        self.setupLayout = qt.QFormLayout(setupWindow)

        # Input box
        inputBox = ctk.ctkCollapsibleGroupBox()
        inputBox.setTitle('Input')
        self.setupLayout.addRow(inputBox)
        self.inputBox = qt.QFormLayout(inputBox)

        # Bevel angle
        self.bevelAngle = qt.QLineEdit()
        self.bevelAngle.setPlaceholderText("Enter angle (deg)")
        self.inputBox.addRow("Bevel Angle:", self.bevelAngle)

        # R-Axis Entry Error
        self.entryErrR = qt.QLineEdit()
        self.entryErrR.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("R-Axis Entry Error:", self.entryErrR)

        # A-Axis Entry Error
        self.entryErrA = qt.QLineEdit()
        self.entryErrA.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("A-Axis Entry Error:", self.entryErrA)

        # S-Axis Entry Error
        self.entryErrS = qt.QLineEdit()
        self.entryErrS.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("S-Axis Entry Error:", self.entryErrS)

        # Curve Radius
        self.curveRadius = qt.QLineEdit()
        self.curveRadius.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("Curve Radius:", self.curveRadius)

        # Insertion Length
        self.insertionLength = qt.QLineEdit()
        self.insertionLength.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("Insertion Length:", self.insertionLength)

        # Needle length in prostate
        self.len1 = qt.QLineEdit()
        self.len1.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("Needle length in prostate:", self.len1)

        # Needle Length in pelvic diaphragm
        self.len2 = qt.QLineEdit()
        self.len2.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("Needle length in pelvic diaphragm:", self.len2)

        # Needle length in bulbospongiosus
        self.len3 = qt.QLineEdit()
        self.len3.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("Needle length in bulbospongiousus:", self.len3)

        # Needle length in ischiocavernosus
        self.len4 = qt.QLineEdit()
        self.len4.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("Needle length in ischiocavernosus:", self.len4)

        # Needle length in unsegmented tissue
        self.len5 = qt.QLineEdit()
        self.len5.setPlaceholderText("Enter length (mm)")
        self.inputBox.addRow("Needle length in unsegmented tissue:", self.len5)

        # Calculate Error
        self.calculateError = qt.QPushButton("Calculate Error")
        self.calculateError.clicked.connect(self.run_regressions)
        self.setupLayout.addWidget(self.calculateError)

        # Disable calculation until data is entered
        self.calculateError.setEnabled(0)
        self.calculateError.setText('Enter all data first!')

        #
        # Output
        #
        outputWindow = ctk.ctkCollapsibleButton()
        outputWindow.text = 'Output'
        self.layout.addWidget(outputWindow)
        self.outputLayout = qt.QFormLayout(outputWindow)

        # Output box
        outputBoxCollapsible = ctk.ctkCollapsibleGroupBox()
        outputBoxCollapsible.setTitle('Results')
        self.outputLayout.addRow(outputBoxCollapsible)
        self.outputBox = qt.QFormLayout(outputBoxCollapsible)

        # Initial output text
        self.outputLabel = qt.QLabel("")
        self.outputBox.addRow(self.outputLabel)
        self.outputLabel.setText("The needle has a 0.00% chance of hitting the target, 0.00% chance \nof deflecting "
                                 "right, and 0.00% chance of deflecting to the top.")
        # Initial visual output
        image = qt.QPixmap(self.dir + "/Needle Deviation Predictor GUI/output1.png")
        self.label1 = qt.QLabel("")

        # Scaling and sizing
        self.label1.setScaledContents(True)
        self.label1.setMargin(0)
        self.label1.setPixmap(image)
        qSize = qt.QSizePolicy()
        self.label1.setSizePolicy(qSize)
        self.outputBox.addRow(self.label1)

        # Check all entered values are floats
        values = [self.bevelAngle, self.entryErrR, self.entryErrA, self.entryErrS, self.curveRadius,
                  self.insertionLength, self.len1, self.len2, self.len3, self.len4, self.len5]
        for value in values:
            value.textChanged.connect(self.check_inputs)

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def check_inputs(self):

        # Count number of entered values that are floats
        counter = 0
        values = [self.bevelAngle, self.entryErrR, self.entryErrA, self.entryErrS, self.curveRadius,
                  self.insertionLength, self.len1, self.len2, self.len3, self.len4, self.len5]
        for value in values:
            if self.is_float(value.text):
                counter += 1
            else:
                counter -= 1

        # Total number of values
        if counter == 11:
            self.calculateError.setEnabled(1)
            self.calculateError.setText('Calculate Error:')
        else:
            self.calculateError.setEnabled(0)
            self.calculateError.setText('Enter all data first!')

    def display_output(self):

        # Update output text
        self.outputLabel.setText(
            "The needle has a %.2f %% chance of %s the target, %.2f %% chance of \ndeflecting %s, and %.2f %% chance \n"
            "of deflecting to the %s." % (self.below5Accuracy, self.hitMiss, self.inRightAccuracy, self.rightLeft,
                                          self.inTopAccuracy, self.topBottom))

        # Get predicted quadrant that needle will deviate towards
        if self.rightLeft == "right" and self.topBottom == "top":
            self.quarter = "Q1"
        elif self.rightLeft == "right" and self.topBottom == "bottom":
            self.quarter = "Q2"
        elif self.rightLeft == "left" and self.topBottom == "bottom":
            self.quarter = "Q3"
        else:
            self.quarter = "Q4"

        # Update output visual
        image = qt.QPixmap(self.dir + ("/Needle Deviation Predictor GUI/%s%s.png" % (str(self.quarter), str(self.hitMiss)))
                           )
        self.label1.setPixmap(image)

        # Set size policy for updated output
        qSize = qt.QSizePolicy()
        qSize.setHorizontalPolicy(qt.QSizePolicy.Ignored)
        qSize.setVerticalPolicy(qt.QSizePolicy.Preferred)

    def run_regressions(self):
        
        # Convert user input to float
        self.bevelAngleval = float(self.bevelAngle.text)
        self.entryErrRval = float(self.entryErrR.text)
        self.entryErrAval = float(self.entryErrA.text)
        self.entryErrSval = float(self.entryErrS.text)
        self.curveRadiusval = float(self.curveRadius.text)
        self.insertionLengthval = float(self.insertionLength.text)
        self.len1val = float(self.len1.text)
        self.len2val = float(self.len2.text)
        self.len3val = float(self.len3.text)
        self.len4val = float(self.len4.text)
        self.len5val = float(self.len5.text)

        # Average percentage of instances classified correctly over 10 logistic regressions using data from 175
        # insertions, 2/3 as training and 1/3 as testing data split randomly for each test.
        self.below5Accuracy = 63.87

        # Logistic regression model used to classify whether the insertion error was above or below 5 mm.
        self.below5 = 1 / (1 + exp(0.0004 * self.bevelAngleval - 0.1537 * self.entryErrRval - 0.1052 * self.entryErrAval
                           + 0.0239 * self.entryErrSval + 0.00003 * self.curveRadiusval + 0.0232 *
                           self.insertionLengthval - 0.0306 * self.len1val - 0.0001 * self.len2val - 0.0133 *
                           self.len3val - 0.0072 * self.len4val - 0.0053 * self.len5val - 1.4805))
        print self.below5
        if self.below5 > 0.5:
            self.hitMiss = "hitting"
        else:
            self.hitMiss = "missing"

        # Average percentage of instances classified correctly over 10 logistic regressions using data from 175
        # insertions, 2/3 as training and 1/3 as testing data split randomly for each test.
        self.inRightAccuracy = 77.29

        # Logistic regresion model used to classify whether the needle deviated to the right or to the left of the
        # target.
        self.inRight = 1 / (1 + exp(-0.0037 * self.bevelAngleval - 0.8917 * self.entryErrRval - 0.2234 *
                            self.entryErrAval - 0.0303 * self.entryErrSval + 0.0002 * self.curveRadiusval + 0.0095 *
                            self.insertionLengthval - 0.068))
        print self.inRight
        if self.inRight > 0.5:
            self.rightLeft = "right"
        else:
            self.rightLeft = "left"

        # Average percentage of instances classified correctly over 10 logistic regressions using data from 175
        # insertions, 2/3 as training and 1/3 as testing data split randomly for each test.
        self.inTopAccuracy = 74.92

        # Logistic regression model used to classify whether the needle deviated to the top or to the bottom of the
        # target.
        self.inTopPlus2 = 1 / (1 + exp(0.0013 * self.bevelAngleval - 0.0996 * self.entryErrRval - 0.7932 *
                               self.entryErrAval + 0.0384 * self.entryErrSval - 0.0002 * self.curveRadiusval + 0.0279 *
                               self.insertionLengthval - 3.0831))
        print self.inTopPlus2
        if self.inTopPlus2 > 0.5:
            self.topBottom = "top"
        else:
            self.topBottom = "bottom"

        # Update output text and visual
        self.display_output()
