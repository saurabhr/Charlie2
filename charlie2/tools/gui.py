from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QCheckBox,
)
from .paths import (
    logo_path,
    get_instructions,
    tests_list,
    get_tests_from_batch,
    batches_list,
)


class GUIWidget(QWidget):
    def __init__(self, parent=None):
        """Widget for the front end graphical user interface (GUI). Allows the
        experimenter to choose the proband ID, which tests to run, etc.

        """
        super(GUIWidget, self).__init__(parent=parent)
        self.args = self.parent().args
        self.vprint = print if self.args.verbose else lambda *a, **k: None
        self.vprint("GUI intialised")
        self.instructions = get_instructions("gui", self.args.language)
        self.vbox = QVBoxLayout()
        self.img = QLabel(self)
        self.img.setPixmap(QPixmap(logo_path))
        self.img.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.img)
        self.txt = QLabel(self.instructions[4])
        self.txt.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.txt)

        self.proband_groupbox = QGroupBox(self.instructions[5])
        self.proband_grid = QGridLayout()
        self.proband_grid.addWidget(QLabel(self.instructions[6]), 0, 0)
        self.proband_id_box = QLineEdit(self.args.proband_id, self)
        self.proband_id_box.textEdited.connect(self._set_proband_id)
        self.proband_grid.addWidget(self.proband_id_box, 0, 1)
        self.proband_grid.addWidget(QLabel(self.instructions[7]), 2, 0, 1, 0)
        self.proband_groupbox.setLayout(self.proband_grid)
        self.vbox.addWidget(self.proband_groupbox)

        self.options_groupbox = QGroupBox(self.instructions[8])
        self.options_grid = QGridLayout()
        self.fullscreen_checkbox = QCheckBox(self.instructions[9], self)
        self.fullscreen_checkbox.setChecked(self.args.fullscreen)
        self.fullscreen_checkbox.stateChanged.connect(self._toggle_fullscreen)
        self.options_grid.addWidget(self.fullscreen_checkbox)
        self.resume_checkbox = QCheckBox(self.instructions[10], self)
        self.resume_checkbox.setChecked(self.args.resume)
        self.resume_checkbox.stateChanged.connect(self._toggle_resume)
        self.options_grid.addWidget(self.resume_checkbox)
        self.backup_checkbox = QCheckBox(self.instructions[11], self)
        font = self.backup_checkbox.font()
        font.setStrikeOut(True)
        self.backup_checkbox.setFont(font)
        self.backup_checkbox.setCheckable(False)
        self.options_grid.addWidget(self.backup_checkbox)
        self.options_groupbox.setLayout(self.options_grid)
        self.vbox.addWidget(self.options_groupbox)

        self.test_groupbox = QGroupBox(self.instructions[12])
        self.test_grid = QGridLayout()
        self.test_grid.addWidget(QLabel(self.instructions[13]), 0, 0)
        self.test_name_box = QComboBox(self)
        self.test_name_box.addItems([""] + tests_list)
        self.test_name_box.activated.connect(self._set_test_names_single)
        self.test_grid.addWidget(self.test_name_box, 0, 1)
        self.test_button = QPushButton(self.instructions[14], self)
        self.test_button.clicked.connect(self.parent().switch_central_widget)
        self.test_grid.addWidget(self.test_button, 1, 0, 1, 0)
        self.test_groupbox.setLayout(self.test_grid)
        self.vbox.addWidget(self.test_groupbox)

        self.batch_groupbox = QGroupBox(self.instructions[15])
        self.batch_grid = QGridLayout()
        self.batch_grid.addWidget(QLabel(self.instructions[16]), 0, 0)
        self.batch_name_box = QComboBox(self)
        self.batch_name_box.addItems([""] + batches_list)
        self.batch_name_box.activated.connect(self._set_test_names_batch)
        self.batch_grid.addWidget(self.batch_name_box, 0, 1)
        self.batch_button = QPushButton(self.instructions[17], self)
        self.batch_button.clicked.connect(self.parent().switch_central_widget)
        self.batch_grid.addWidget(self.batch_button, 3, 0, 1, 0)
        self.batch_groupbox.setLayout(self.batch_grid)
        self.vbox.addWidget(self.batch_groupbox)
        self.setLayout(self.vbox)

    def _set_proband_id(self):
        """Change the proband ID."""
        self.args.proband_id = self.sender().text()

    def _set_test_names_single(self):
        """Set the next test to be the selected one."""
        self.args.test_names = [self.sender().currentText()]

    def _set_test_names_batch(self):
        """Load the test names from the selected batch file."""
        batch_file = self.sender().currentText()
        if batch_file:
            self.args.test_names = get_tests_from_batch(batch_file)
        else:
            self.args.test_names = []

    def _toggle_fullscreen(self, state):
        """Toggle fullscreen mode."""
        if state == Qt.Checked:
            self.args.fullscreen = True
        else:
            self.args.fullscreen = False

    def _toggle_resume(self, state):
        """Toggle resume mode."""
        if state == Qt.Checked:
            self.args.resume = True
        else:
            self.args.resume = False