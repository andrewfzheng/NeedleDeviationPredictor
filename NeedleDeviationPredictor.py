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
        Pedro Moreira, PhD, Junichi Tokuda, PhD, Nobuhiko Hata, PhD
        """        
        parent.icon = qt.QIcon(os.path.dirname(os.path.realpath(__file__)) + '/NeedleDeviationPredictor GUI/icon.png')
        self.parent = parent


class NeedleDeviationPredictorWidget:
    def __init__(self, parent=None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
        else:
            self.parent = parent
            self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()
        self.inputsFilled = False

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
        self.inputBoxLayout = qt.QFormLayout(inputBox)

        # Bevel angle slider
        self.bevelAngleSlider = ctk.ctkSliderWidget()
        self.bevelAngleSlider.connect('valueChanged(double)', self.bevel_angle_changed)
        self.bevelAngleSlider.decimals = 0
        self.bevelAngleSlider.minimum = 0
        self.bevelAngleSlider.maximum = 360
        self.inputBoxLayout.addRow("Bevel Angle:", self.bevelAngleSlider)

        # R-Axis Entry Error
        self.entryErrR = qt.QLineEdit()
        self.entryErrR.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("R-Axis Entry Error:", self.entryErrR)

        # A-Axis Entry Error
        self.entryErrA = qt.QLineEdit()
        self.entryErrA.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("A-Axis Entry Error:", self.entryErrA)

        # S-Axis Entry Error
        self.entryErrS = qt.QLineEdit()
        self.entryErrS.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("S-Axis Entry Error:", self.entryErrS)

        # Curve Radius
        self.curveRadius = qt.QLineEdit()
        self.curveRadius.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("Curve Radius:", self.curveRadius)

        # Insertion Length
        self.insertionLength = qt.QLineEdit()
        self.insertionLength.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("Insertion Length:", self.insertionLength)

        # Needle length in prostate
        self.len1 = qt.QLineEdit()
        self.len1.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("Needle length in prostate:", self.len1)

        # Needle Length in pelvic diaphragm
        self.len2 = qt.QLineEdit()
        self.len2.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("Needle length in pelvic diaphragm:", self.len2)

        # Needle length in bulbospongiosus
        self.len3 = qt.QLineEdit()
        self.len3.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("Needle length in bulbospongiousus:", self.len3)

        # Needle length in ischiocavernosus
        self.len4 = qt.QLineEdit()
        self.len4.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("Needle length in ischiocavernosus:", self.len4)

        # Needle length in unsegmented tissue
        self.len5 = qt.QLineEdit()
        self.len5.setPlaceholderText("Enter length (mm)")
        self.inputBoxLayout.addRow("Needle length in unsegmented tissue:", self.len5)

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
        outputBoxCollapsible.setTitle('Output')
        self.outputLayout.addRow(outputBoxCollapsible)
        self.outputBox = qt.QFormLayout(outputBoxCollapsible)

        # Initial output text
        self.outputLabel = qt.QLabel("")
        self.outputBox.addRow(self.outputLabel)
        self.outputLabel.setText("The needle has a rating of 0.0/10.0 for hitting the \ntarget, a rating of 0.0/10.0 "
                                 "for deflecting to the right,\nand a rating of 0.0/10.0 for deflecting to the top.")
        # Initial visual output
        image = qt.QPixmap(self.dir + "/NeedleDeviationPredictor GUI/empty.png")
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
        values = [self.entryErrR, self.entryErrA, self.entryErrS, self.curveRadius,
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
        counter = 0

        # Count number of entered values that are floats except bevel angle
        values = [self.entryErrR, self.entryErrA, self.entryErrS, self.curveRadius,
                  self.insertionLength, self.len1, self.len2, self.len3, self.len4, self.len5]
        for value in values:
            if self.is_float(value.text):
                counter += 1
            else:
                counter -= 1

        # Total number of values except bevel angle
        if counter == 10:
            self.calculateError.setEnabled(1)
            self.calculateError.setText('Calculate Error:')
            self.inputsFilled = True
        else:
            self.calculateError.setEnabled(0)
            self.calculateError.setText('Enter all data first!')

    def bevel_angle_changed(self, newValue):
        self.bevelAngleval = newValue

        # Actively calculate output as bevel angle is changed if all other inputs are given
        if self.inputsFilled:
            self.run_regressions()

    def display_output(self):

        # Update output text
        self.outputLabel.setText(
            "The needle has a rating of %0.2f/10.0 for %s \nthe target, a rating of %0.2f/10.0 for deflecting %s,\nand "
            "a rating of %0.2f/10.0 for deflecting to the %s." % (self.below5dot76Accuracy, self.hitMiss,
                                                                  self.inRightAccuracy, self.rightLeft,
                                                                  self.inTopAccuracy, self.topBottom))

        # Get predicted quadrant that needle will deviate towards unless insertion error <5mm
        if self.below5dot76 > 0.5:
            quarter = ""
        elif self.rightLeft == "right" and self.topBottom == "top":
            quarter = "Q1"
        elif self.rightLeft == "right" and self.topBottom == "bottom":
            quarter = "Q2"
        elif self.rightLeft == "left" and self.topBottom == "bottom":
            quarter = "Q3"
        else:
            quarter = "Q4"

        # Update output visual
        image = qt.QPixmap(self.dir + ("/NeedleDeviationPredictor GUI/%s%s.png" % (str(quarter), str(self.hitMiss))))
        self.label1.setPixmap(image)

    def run_regressions(self):

        # Convert user input to float
        entryErrRval = float(self.entryErrR.text)
        entryErrAval = float(self.entryErrA.text)
        entryErrSval = float(self.entryErrS.text)
        curveRadiusval = float(self.curveRadius.text)
        insertionLengthval = float(self.insertionLength.text)
        self.len1val = float(self.len1.text)
        self.len2val = float(self.len2.text)
        self.len3val = float(self.len3.text)
        self.len4val = float(self.len4.text)
        self.len5val = float(self.len5.text)

        # Logistic regression model used to classify whether the targeting error was above or below 5.76 mm
        self.below5dot76 = 1 / (1 + exp(-0.0003 * self.bevelAngleval - 0.1615 * entryErrRval - 0.1894 * entryErrAval
                           + 0.0379 * entryErrSval - 0.0001 * curveRadiusval + 0.0177 *
                           insertionLengthval - 0.0076 * self.len1val - 0.0017 * self.len2val - - 0.0228 *
                           self.len3val - 0.0112 * self.len4val - 0.0304 * self.len5val - 1.9245))

        if self.below5dot76 > 0.5:
            self.hitMiss = "hitting"
            # Probability of targeting error less than 5.76 mm
            self.below5dot76Accuracy = 10 * self.below5dot76
        else:
            self.hitMiss = "missing"
            # Probability of targeting error greater than 5.76 mm
            self.below5dot76Accuracy = 10 - 10 * self.below5dot76

        # Logistic regression model used to classify whether the needle deviated to the right or to the left of the
        # target
        self.inRight = 1 / (1 + exp(-0.0037 * self.bevelAngleval - 0.8917 * entryErrRval - 0.2234 *
                            entryErrAval - 0.0303 * entryErrSval + 0.0002 * curveRadiusval + 0.0095 *
                            insertionLengthval - 0.068))
        if self.inRight > 0.5:
            self.rightLeft = "right"
            # Probability of needle deviation to the right
            self.inRightAccuracy = 10 * self.inRight
        else:
            self.rightLeft = "left"
            # Probability of needle deviation to the left
            self.inRightAccuracy = 10 - 10 * self.inRight

        # Logistic regression model used to classify whether the needle deviated to the top or to the bottom of the
        # target
        self.inTopPlus2 = 1 / (1 + exp(0.0013 * self.bevelAngleval - 0.0996 * entryErrRval - 0.7932 *
                               entryErrAval + 0.0384 * entryErrSval - 0.0002 * curveRadiusval + 0.0279 *
                               insertionLengthval - 3.0831))
        if self.inTopPlus2 > 0.5:
            self.topBottom = "top"
            # Probability of needle deviation to the top
            self.inTopAccuracy = 10 * self.inTopPlus2
        else:
            self.topBottom = "bottom"
            # Probability of needle deviation to the bottom
            self.inTopAccuracy = 10 - 10 * self.inTopPlus2

        # Update output text and visual
        self.display_output()
