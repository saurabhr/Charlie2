"""
=====================
Verbal working memory
=====================

:Version: 2.0
:Source: http://github.com/sammosummo/Charlie2/tests/recipes.py
:Author: Sam Mathias

Description
===========

This test is a combination of the digit span forward, digit span backward, and letter-
number sequencing tests from the WAIS-III and WMC-III [1]_. This test requires the
proband to relinquish control to the experimenter. There are four blocks in the test.
In the first block, the experimenter reads aloud sequences of letters and digits to the
proband. The proband then repeats the sequence back to the experimenter, in the same
order. The first sequence is two digits in length; sequence length increases by one
digit every two sequences. If the proband responds incorrectly to both sequences of the
same length, the block is terminated. The second block is the same as the first except
that probands repeat the sequences in reverse order. In the third phase, the sequences
contain both digits and letters, and probands repeat the letters in numerical order,
followed by the letters in alphabetical order. The third block serves as a practice for
the fourth block. In the fourth block there are three sequences of the same length; if
probands get all three wrong, the block is terminated.

Reference
=========

.. [1] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual. San
  Antonio, TX: The Psychological Corporation.

"""
from logging import getLogger

from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QSound

from charlie2.tools.stats import basic_summary

from ..tools.basetestwidget import BaseTestWidget
from ..tools.recipes import get_vwm_stimuli

__version__ = 2.0
__author__ = "Sam Mathias"


logger = getLogger(__name__)


class TestWidget(BaseTestWidget):
    def make_trials(self):

        sequences = get_vwm_stimuli(self.kwds["language"])
        trial_types = ["forward", "backward", "lns_prac", "lns"]
        practices = {
            "forward": False,
            "backward": False,
            "lns_prac": True,
            "lns": False,
        }
        details = []
        for block, sequences_ in enumerate(sequences):
            for trial, sequence in enumerate(sequences_):
                details.append(
                    {
                        "block_number": block,
                        "trial_number": trial,
                        "block_type": trial_types[block],
                        "practice": practices[trial_types[block]],
                        "sequence": str(sequence),
                        "length": len(str(sequence)),
                    }
                )
        return details

    def block(self):

        self.first_digit_horrible_lag = True
        self.skip_countdown = True
        t = self.current_trial
        s = self.instructions[5 + t.block_number]
        label, btn = self.display_instructions_with_continue_button(
            s, QFont("Helvetica", 18), False
        )

        # if very first trial, show message to proband
        if t.first_trial_in_test:
            label.hide()
            btn.hide()
            s = self.instructions[4]
            a, b = self.display_instructions_with_continue_button(s)
            b.clicked.disconnect()
            b.clicked.connect(lambda: [a.hide(), b.hide(), btn.show(), label.show()])

    def trial(self):

        t = self.current_trial

        # calculate the correct answer
        if t.block_type == "forward":
            answer = t.sequence
        elif t.block_type == "backward":
            answer = t.sequence[::-1]
        else:
            digits = []
            letters = []
            for a in t.sequence:
                if a.isdigit():
                    digits.append(a)
                elif a.isalpha():
                    letters.append(a)
            answer = sorted(digits) + sorted(letters)

        # instructions and buttons
        self.display_instructions(self.instructions[9] % "-".join(t.sequence))
        corr_button = self._display_continue_button()
        corr_button.setText(self.instructions[10] % "-".join(answer))
        corr_button.setFont(QFont("Helvetica", 18))
        corr_button.resize(corr_button.sizeHint())
        corr_button.setMinimumHeight(120)
        corr_button.setMinimumWidth(320)

        x = (self.frameGeometry().width() - corr_button.width()) // 2 - 250
        y = self.frameGeometry().height() - (corr_button.height() + 20)
        corr_button.move(x, y)
        corr_button.clicked.disconnect()
        corr_button.clicked.connect(self._correct)
        incorr_button = self._display_continue_button()
        incorr_button.setText(self.instructions[11])
        incorr_button.setFont(QFont("Helvetica", 18))
        incorr_button.resize(incorr_button.sizeHint())
        incorr_button.setMinimumHeight(120)
        incorr_button.setMinimumWidth(320)
        x = (self.frameGeometry().width() - incorr_button.width()) // 2 + 250
        y = self.frameGeometry().height() - (incorr_button.height() + 20)
        incorr_button.move(x, y)
        incorr_button.clicked.disconnect()
        incorr_button.clicked.connect(self._incorrect)

        sound = QSound(self.aud_stim_paths[f"{str(t.sequence)}.wav"])
        corr_button.setEnabled(False)
        incorr_button.setEnabled(False)
        sound.play()
        while not sound.isFinished():
            self.sleep(100)
        corr_button.setEnabled(True)
        incorr_button.setEnabled(True)

    def _correct(self):

        t = self.current_trial
        if t:
            t.correct = True
            t.status = "completed"
            self._add_timing_details()
            logger.debug("current_trial was completed successfully")
            logger.debug("(final version) of current_trial looks like %s" % str(t))
            self.next_trial()

    def _incorrect(self):

        t = self.current_trial
        if t:
            t.correct = False
            t.status = "completed"
            self._add_timing_details()
            logger.debug("current_trial was completed successfully")
            logger.debug("(final version) of current_trial looks like %s" % str(t))
            self.next_trial()

    def mousePressEvent(self, event):

        pass

    def summarise(self):
        trials = self.procedure.completed_trials
        dic = {"total_time_taken": basic_summary(trials)["total_time_taken"]}
        for b in ("forward", "backward", "lns"):
            trials_ = [t for t in trials if t["block_type"] == b]
            dic.update(basic_summary(trials_, prefix=b))
        return dic

    def block_stopping_rule(self):

        last_trial = self.procedure.completed_trials[-1]
        logger.debug("applying stopping rule to this trial: %s" % str(last_trial))
        if last_trial["practice"]:
            logger.debug("practice trial, so don't apply stopping rule")
            return False
        if "lns" in last_trial["block_type"]:
            logger.debug("lns trial, 3 trials per length")
            n = 3
        else:
            logger.debug("fwd or bwd trial, 2 trials per length")
            n = 2
        ct = self.procedure.completed_trials
        trials = [t for t in ct if t["block_number"] == last_trial["block_number"]]
        trials = [t for t in trials if t["length"] == last_trial["length"]]
        logger.debug("%s trials to evaluate: %s" % (len(trials), trials))
        if len(trials) < n:
            logger.debug("too few trials")
            return False
        errs = [t for t in trials if t["correct"] is False]
        logger.debug(logger.debug("%s error trials: %s" % (len(errs), errs)))
        logger.debug("number of errors: %s" % len(errs))
        return True if len(errs) == n else False
