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
        parent.icon = qt.QIcon(os.path.dirname(os.path.realpath(__file__)) + '/NeedleDeviationPredictor GUI/icon.png')
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
        inputBox.setTitle('Input:')
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
        image = qt.QPixmap(self.dir + "/NeedleDeviationPredictor GUI/output1.png")
        self.label1 = qt.QLabel("")

        # Scaling and sizing
        self.label1.setScaledContents(True)
        self.label1.setMargin(0)
        self.label1.setPixmap(image)
        qSize = qt.QSizePolicy()
        self.label1.setSizePolicy(qSize)
        self.outputBox.addRow(self.label1)

        # Vertical spacer
        self.layout.addStretch(1)

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
            "The needle has a %.2f %% chance of %s the target, %.2f %% chance \nof deflecting %s, and %.2f %% chance of"
            " deflecting to the %s." % (self.below5Accuracy, self.hitMiss, self.inRightAccuracy, self.rightLeft,
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
        image = qt.QPixmap(self.dir + ("/NeedleDeviationPredictor GUI/%s%s.png" % (str(self.quarter), str(self.hitMiss
                                                                                                            ))))
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

        # Logistic regression model used to classify whether the targeting error was above or below 5 mm
        self.below5 = 1 / (1 + exp(0.0007 * self.bevelAngleval - 0.1495 * self.entryErrRval - 0.119 * self.entryErrAval
                           + 0.0179 * self.entryErrSval - 0.0001 * self.curveRadiusval + 0.0221 *
                           self.insertionLengthval - 0.0385 * self.len1val - 0.0013 * self.len2val - 0.0001 *
                           self.len3val - 0.0068 * self.len4val - 0.0084 * self.len5val - 0.8513))

        if self.below5 > 0.5:
            self.hitMiss = "hitting"
            # Probability of targeting error less than 5 mm
            self.below5Accuracy = 100 * self.below5
        else:
            self.hitMiss = "missing"
            # Probability of targeting error greater than 5 mm
            self.below5Accuracy = 100 - 100 * self.below5

        # Logistic regression model used to classify whether the needle deviated to the right or to the left of the
        # target
        self.inRight = 1 / (1 + exp(-0.0037 * self.bevelAngleval - 0.8917 * self.entryErrRval - 0.2234 *
                            self.entryErrAval - 0.0303 * self.entryErrSval + 0.0002 * self.curveRadiusval + 0.0095 *
                            self.insertionLengthval - 0.068))
        print self.inRight
        if self.inRight > 0.5:
            self.rightLeft = "right"
            # Probability of needle deviation to the right
            self.inRightAccuracy = 100 * self.inRight
        else:
            self.rightLeft = "left"
            # Probability of needle deviation to the left
            self.inRightAccuracy = 100 - 100 * self.inRight

        # Logistic regression model used to classify whether the needle deviated to the top or to the bottom of the
        # target
        self.inTopPlus2 = 1 / (1 + exp(0.0013 * self.bevelAngleval - 0.0996 * self.entryErrRval - 0.7932 *
                               self.entryErrAval + 0.0384 * self.entryErrSval - 0.0002 * self.curveRadiusval + 0.0279 *
                               self.insertionLengthval - 3.0831))
        print self.inTopPlus2
        if self.inTopPlus2 > 0.5:
            self.topBottom = "top"
            # Probability of needle deviation to the top
            self.inTopAccuracy = 100 * self.inTopPlus2
        else:
            self.topBottom = "bottom"
            # Probability of needle deviation to the bottom
            self.inTopAccuracy = 100 - 100 * self.inTopPlus2

        # Update output text and visual
        self.display_output()
