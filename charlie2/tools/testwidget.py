from logging import getLogger
from .data import TestData
from .paths import get_vis_stim_paths, get_aud_stim_paths, get_instructions
from .procedure import SimpleProcedure
from PyQt5.QtCore import QTime, Qt, QTimer, QEventLoop, QPoint
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton


logger = getLogger(__name__)


class BaseTestWidget(QWidget):
    def __init__(self, parent=None):
        """Base class for test widgets.

        This is not called directly, but contains methods which are inherited by all
        tests which between them do much of the heavy lifting regarding running tests,
        storing data, and so on.

        """
        super(BaseTestWidget, self).__init__(parent)
        logger.info("test widget created")

        self.vis_stim_paths = get_vis_stim_paths(self.parent().args.test_name)
        self.aud_stim_paths = get_aud_stim_paths(self.parent().args.test_name)
        self.instructions_font = QFont("Helvetica", 24)
        self._trial_on = False
        self._mouse_on = True
        self.test_time = QTime()
        self.block_time = QTime()
        self.trial_time = QTime()
        self.args = self.parent().args
        self.block_silent = False
        self.skip_countdown = False
        self.test_max_time = None
        self.block_max_time = None
        self.trial_max_time = None
        self.data = TestData(**vars(self.args))
        self.zones = []
        self.instructions = get_instructions(self.args.test_name, self.args.language)

        self.setFocusPolicy(Qt.StrongFocus)

    def begin(self):
        """Start the test. This is called automatically by the parent widget. Don't call
        it manually!

        """
        self._step()

    @property
    def trial_on(self):
        return self._trial_on

    @trial_on.setter
    def trial_on(self, value):
        assert isinstance(value, bool), "trial_on must be a bool"
        if value is False:
            self._stop_trial_timeout()
        elif self.trial_max_time:
            self._start_trial_timeout()
        self._trial_on = value

    @property
    def mouse_on(self):
        return self._mouse_on

    @mouse_on.setter
    def mouse_on(self, value):
        assert isinstance(value, bool), "mouse_on must be a bool"
        if value is False:
            self.setCursor(Qt.BlankCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        self._mouse_on = value

    def get_procedure(self):
        """Override this method."""
        logger.info("using a simple procedure (default)")
        remaining_trials = self.make_trials()
        return SimpleProcedure(remaining_trials)

    def make_trials(self):
        """Override this method."""
        raise AssertionError("make_trials must be overridden")

    def block(self):
        """Override this method."""
        raise AssertionError("block must be overridden")

    def trial(self):
        """Override this method."""
        raise AssertionError("trial must be overridden")

    def summarise(self):
        """Override this method."""
        raise AssertionError("summarise must be overridden")

    def mousePressEvent_(self, event):
        """Override this method."""
        pass

    def keyReleaseEvent_(self, event):
        """Override this method."""
        pass

    def stopping_rule(self):
        """Override this method."""
        return False

    def begin(self):
        """Start the test.

        This is called automatically. Don't call it manually!

        """
        self._step()

    def sleep(self, t):
        """Sleep for `t` s.

        Use instead of `time.sleep()` or any other method of sleeping because (a) Qt
        handles it properly and (b) it prevents a `closeEvent` from quitting the test
        during this time.

        Args:
            t (float): Time to sleep in seconds.

        """
        logger.info("sleeping for %i s" % t)
        self.parent().ignore_close_event = True
        loop = QEventLoop()
        QTimer.singleShot(t * 1000, loop.quit)
        loop.exec_()
        self.parent().ignore_close_event = False

    def display_instructions(self, message):
        """Display instructions.

        This method will first hide any visible widgets (e.g., images from the last
        trial). Typically `message` is an item from the list `self.instructions`.

        Args:
            message (str): Message to display.

        Returns:
            label (QLabel): Object containing the message.

        """
        logger.info('displaying the following message:')
        logger.info("\n   ", message, "\n")
        self.clear_screen()
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(self._instructions_font)
        label.resize(self.size())
        label.show()
        return label

    def display_instructions_with_continue_button(self, message):
        """Display instructions with a continue button.

        This is the same as `self.display_instructions` except that a continue button is
        additionally displayed. Continue buttons prevent the test from moving forward
        until pressed. Generally this is used at the beginning of blocks of trials.

        Args:
            message (str): Message to display.

        Returns:
            label (QLabel): Object containing the message.
            button (QPushButton): Button.

        """
        label = self.display_instructions(message)
        button = self._display_continue_button()
        logger.info("now waiting for continue button to be pressed")
        return label, button

    def load_image(self, s):
        """Return an image.

        It is possibly important for correct alignment to explicitly set the size of the
        label after setting its pixmap since it does not inherit this attribute even
        though the entire pixmap may br visible.

        Args:
            s (str): Path to the .png image file.

        Returns:
            label (QLabel): Label containing the image as a pixmap.

        """
        label = QLabel(self)
        pixmap = QPixmap(self._vis_stim_paths[s])
        label.setPixmap(pixmap)
        label.resize(pixmap.size())
        label.hide()
        return label

    def move_widget(self, widget, pos):
        """Move `widget` to new coordinates.

        Coords are relative to the centre of the window where (1, 1) would be the upper
        right.

        Args:
            widget (QWidget): Any widget.
            pos (:obj:`tuple` of :obj:`int`): New position.

        Returns:
            g (QRect): Updated geometry of the wdiget.

        """
        x = self.frameGeometry().center().x() + pos[0]
        y = self.frameGeometry().center().y() - pos[1]
        point = QPoint(x, y)
        g = widget.frameGeometry()
        g.moveCenter(point)
        widget.move(g.topLeft())
        return g

    def display_image(self, s, pos=None):
        """Show an image on the screen.

        Args:
            s (:obj:`str` or :obj:`QLabel`): Path to image or an image itself.
            pos (:obj:`tuple` of :obj:`int`, optional): Coords of image.

        Returns:
            label (QLabel): Label containing the image as a pixmap.

        """
        if isinstance(s, str):
            label = self.load_image(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)
        label.show()
        return label

    def load_text(self, s):
        """Return a QLabel containing text.

        Args:
            s (str): Text.

        Returns:
            label (QLabel): Label containing the text.

        """
        label = QLabel(s, self)
        label.setFont(self._instructions_font)
        label.setAlignment(Qt.AlignCenter)
        label.resize(label.sizeHint())
        label.hide()
        return label

    def display_text(self, s, pos=None):
        """Same as `load_text` but also display it.

        Args:
            s (:obj:`str` or :obj:`QLabel`): Text or label containing text.
            pos (:obj:`tuple` of :obj:`int`, optional): Coords.

        Returns:
            label (QLabel): Label containing the text.

        """
        if isinstance(s, str):
            label = self.load_text(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)
        label.show()
        return label

    def load_keyboard_arrow_keys(self, instructions, y=-225):
        """Load keyboard arrow keys.

        Args:
            instructions (list): Labels to display under the keys. Must be of length 2
                (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
                Items can be :obj:`str` or `None`. If `None`, no text is displayed.
            y (:obj:`int`, optional): Vertical position of key centres.

        Returns:
            w (:obj:`list` of :obj:`QLabel`): The created labels.

        """
        w = []
        lx = -75
        rx = 75
        if len(instructions) == 3:
            lx = -225
            rx = 225
        l = self.load_image("l.png")
        self.move_widget(l, (lx, y))
        l.hide()
        w.append(l)
        r = self.load_image("r.png")
        self.move_widget(r, (rx, y))
        r.hide()
        w.append(r)
        xs = [lx, rx]
        if len(instructions) == 3:
            d = self.load_image("d.png")
            self.move_widget(d, (0, y))
            d.hide()
            w.append(d)
            xs = [lx, 0, rx]
        for x, instr in zip(xs, instructions):
            if instr is not None:
                a = self.load_text(instr)
                self.move_widget(a, (x, y - 75))
                a.hide()
                w.append(a)
        return w

    def display_keyboard_arrow_keys(self, instructions, y=-225):
        """Same as `load_keyboard_arrow_keys` except also show them.

        Args:
            instructions (list): Labels to display under the keys. Must be of length 2
                (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
                Items can be :obj:`str` or `None`. If `None`, no text is displayed.
            y (:obj:`int`, optional): Vertical position of key centres.

        Returns:
            w (:obj:`list` of :obj:`QLabel`): The created labels.

        """
        print(instructions)
        widgets = self.load_keyboard_arrow_keys(instructions, y)
        [w.show() for w in widgets]
        return widgets

    def make_zones(self, rects, reset=True):
        """Update `self.zones`.

        `self.zones` contains areas of the window (`QRect` objects) that can be pressed.

        Args:
            rects (:obj:`list` of :obj:`QRect`): List of `QRects`.
            reset (:obj:`bool`, optional): Remove previous items.

        """

        if reset:
            self.zones = []
        for rect in rects:
            self.zones.append(rect)

    def clear_screen(self, delete=False):
        """Hide widgets.

        Hides and optionally deletes all children of this widget.

        Args:
            delete (:obj:`bool`, optional): Delete the widgets as well.

        """
        # for widgets  organized in a layout
        if self.layout() is not None:
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    if delete:
                        widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        # for widgets not organized
        for widget in self.children():
            if hasattr(widget, 'hide'):
                widget.hide()
            if delete:
                widget.deleteLater()

    def basic_summary(self, trials=None, adjust_time_taken=False):
        """Returns an basic set of summary statistics.

        Args:
            trials (:obj:`list` of :obj:`Trial`, optional): List of trials to analyse.
                By default this is `self.completed_trials`, but doesn't have to be, for
                example if condition-specific summaries are required.
            adjust_time_taken (:obj:`bool`, optional): Apply adjustment to time_taken.

        Returns:
            dic (dict): dictionary of results.

        """
        if self.proc.all_skipped: return {'completed': False}

        # get all completed trials
        if trials is None:
            trials = self.proc.completed_trials

        skipped = [t for t in trials if t.skipped]
        any_skipped = len(skipped) > 0

        if all('block_type' in trial for trial in trials):
            trials = [t for t in trials if t.block_type != "practice"]

        # count responses and skips
        not_skipped = [t for t in trials if not t.skipped]
        dic = {
            'completed': True,
            'responses': len(not_skipped),
            'any_skipped': any_skipped,
        }

        # this is the easiest case
        if not any_skipped and not self.data.test_resumed:
            dic['time_taken'] = trials[-1].time_elapsed

        # more complicated
        elif not any_skipped and self.data.test_resumed:
            idx = [trials.index(t) - 1 for t in trials if 'resumed_from_here' in t]
            res = sum([trials[i].time_elapsed for i in idx])
            dic['time_taken'] = trials[-1].time_elapsed + res

        # not meaningful
        elif any_skipped and not adjust_time_taken:
            pass

        # adjustment
        elif any_skipped and adjust_time_taken:
            meanrt = sum(t.rt for t in not_skipped) / len(not_skipped)
            dic['time_taken'] = int(self.block_max_time * 1000 + meanrt * len(skipped))

        else:
            raise AssertionError('should not be possible!')

        # accuracy
        if 'correct' in trials[0]:
            dic['correct'] = len([t for t in not_skipped if t.correct])
            dic['accuracy'] = dic['correct'] / dic['responses']

        return dic

    def display_trial_continue_button(self):
        """Display a continue button

        The button is connected to `self._next_trial` instead of `self._trial`. This
        modification causes the button to **end** the current trial and move onto the
        next one.

        """
        button = self._display_continue_button()
        button.clicked.disconnect()
        button.clicked.connect(self._next_trial)

    def next_trial(self):
        """Manually move on to next trial.

        """
        self._next_trial()

    def _next_trial(self):
        """Move from one trial to the next, checking whether to skip the remainder of
        the block via `self.stopping_rule`."""
        if self.save_after_each_trial:
            self.data.save()
        if self.stopping_rule():
            logger.info('stopping rule failed')
            self.proc.skip_block()
        else:
            logger.info('stopping rule passed')
        self._step()

    def _display_continue_button(self):
        """Display a continue button."""
        logger.info('displaying the continue button')
        self.block_silent = False  # TODO: Do I need this?
        button = QPushButton(self.instructions[1], self)
        button.resize(button.sizeHint())
        button.clicked.connect(self._trial)
        x = (self.frameGeometry().width() - button.width()) // 2
        y = self.frameGeometry().height() - (button.height() + 20)
        button.move(x, y)
        button.show()
        return button

    def _display_countdown(self, t=5, s=1):
        """Display the countdown timer."""
        logger.info("displaying the countdown timer")
        for i in range(t):
            self.display_instructions(self.instructions[0] % (t - i))
            self.sleep(s)
    
    def _step(self):
        """Step forward in the test. This could mean displaying instructions at the
        start of a block, starting the next trial, or continuing to the next test.

        """
        logger.info("stepping forward in test")

        if self.data.test_resumed is False and self.data.test_completed is False:
            logger.info("this is the very first trial, so creating a new procedure")
            self.proc = self.get_procedure()

        try:
            next(self.proc)

            if self.proc.current_trial.first_trial_in_block:
                logger.info("this is the first trial in a new block")
                self._block()

            else:
                logger.info("this is a regular trial")
                self._trial()

        except StopIteration:

            logger.info("this test is over, moving on to next test")
            self.safe_close()

    def safe_close(self):
        """Safely clean up and save the data at the end of the test."""
        logger.info("called safe_close()")
        logger.info('data look like this:')
        logger.info('   ', self.data.safe_vars)
        self._stop_block_timeout()
        self._stop_trial_timeout()
        if not self.proc.test_completed:
            logger.info("aborting")
            self.proc.abort()
        else:
            summary = self.summarise()
            summary['resumed'] = self.data.test_resumed
            logger.info('summary looks like this:')
            logger.info('   ', summary)
            self.data.summary.update(summary)
        self.data.save()
        self.parent().switch_central_widget()

    def _block(self):
        """Runs at the start of a new block of trials. Typically this is used to give
        the proband a break or display new instructions."""
        self.trial_on = False
        self._stop_block_timeout()
        self._block_time.restart()

        if self.block_silent:
            logger.info('this is a silent block')
            self.skip_countdown = True
            logger.info('running _trial()')
            self._trial()

        else:
            self.mouse_on = True
            logger.info('this is a not a silent block')
            logger.info('running user-defined block()')
            self.block()

    def _trial(self):
        """Runs at the start of a new trial. Displays the countdown if first in a new
        block, checks if very last trial, flags the fact that a trial is in progress,
        updates the results list."""
        self._stop_trial_timeout()
        self._trial_time.restart()

        logger.info('now starting the actual trial')
        logger.info('current trial looks like this:')
        logger.info("   ", self.proc.current_trial)
        logger.info('currently the wdiget has the layout', self.layout())

        ftib = self.proc.current_trial.first_trial_in_block
        if ftib and not self.skip_countdown:
            logger.info('countdown requested')
            self._display_countdown()

        if ftib:
            if self.block_max_time:
                self._start_block_timeout()

        self.repaint()
        self.trial_on = True
        self.trial()

    def _start_block_timeout(self):
        """Initialise a timer which automatically ends the block after time elapses."""
        btt = self._block_timeout_timer
        try:
            btt.timeout.disconnect()
            logger.info("disconnecting block timeout timer")
        except TypeError:
            logger.info("block timeout timer wasn't connected to anything")
            pass
        btt.timeout.connect(self._end_block_early)
        logger.info("connected block timeout timer")
        btt.start(self.block_max_time * 1000)
        logger.info("block timeout timer started")

    def _start_trial_timeout(self):
        """Initialise a timer which automatically ends the block after time elapses."""
        ttt = self._trial_timeout_timer
        try:
            ttt.timeout.disconnect()
        except TypeError:
            pass
        ttt.timeout.connect(self._end_trial_early)
        ttt.start(self.trial_max_time * 1000)
        logger.info("trial timeout timer started")

    def _stop_block_timeout(self):
        """Stop the block timeout timer."""
        btt = self._block_timeout_timer
        if btt.isActive():
            logger.info('stopping the block timeout timer')
            btt.stop()
        else:
            logger.info("requested to stop the block timeout timer, but wasn't not on")

    def _stop_trial_timeout(self):
        """Stop the trial timeout timer."""
        ttt = self._trial_timeout_timer
        if ttt.isActive():
            logger.info('stopping the trial timeout timer')
            ttt.stop()
        else:
            logger.info("requested to stop the trial timeout timer, but wasn't not on")

    def _end_block_early(self):
        """End the block early."""
        logger.info('block timed out')
        self.proc.skip_block()
        logger.info('skipping block in procedure')
        self._next_trial()

    def _end_trial_early(self):
        """End the trial early."""
        logger.info('trial timed out')
        self.proc.skip_current_trial()
        logger.info('skipping trial in procedure')
        self._next_trial()

    def mousePressEvent(self, event):
        """Overridden from `QtWidget`."""
        dpct = self.proc.current_trial
        if dpct and self.trial_on:
            self.mousePressEvent_(event)
            if dpct:
                dpct.rt = self._trial_time.elapsed()
                dpct.time_elapsed = self._block_time.elapsed()
                if dpct.completed:
                    self._next_trial()

    def keyReleaseEvent(self, event):
        """Overridden from `QtWidget`."""
        dpct = self.proc.current_trial
        if dpct and self.trial_on:
            self.keyReleaseEvent_(event)
            if dpct:
                dpct.rt = self._trial_time.elapsed()
                dpct.time_elapsed = self._block_time.elapsed()
                if dpct.completed:
                    self._next_trial()
