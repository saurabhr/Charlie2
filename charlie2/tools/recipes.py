"""Miscellaneous convenience functions go in here.

"""
import argparse


def str2bool(v):
    """Nice function to convert cmd-line args to bool."""
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        """Handy converter from dict to class with attributes."""
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def charlie1_trials():
    """Details of the trials from charlie v1 trail-making test.

    """
    blocks = ([0] * 8) + ([1] * 25) + ([2] * 8) + ([3] * 25) + ([4] * 8) + ([5] * 25)
    block_types = (
            (["practice"] * 8)
            + (["test"] * 25)
            + (["practice"] * 8)
            + (["test"] * 25)
            + (["practice"] * 8)
            + (["test"] * 25)
    )
    trials = (list(range(8)) + list(range(25))) * 3
    blaze_positions = [
        (-238, -111),
        (387, 60),
        (347, -269),
        (135, -157),
        (34, -360),
        (-227, 17),
        (130, 122),
        (400, 320),
        (-264, -59),
        (257, 205),
        (-156, 238),
        (90, -144),
        (370, -146),
        (205, -348),
        (-209, -253),
        (-358, -211),
        (-43, -37),
        (122, -264),
        (-176, -359),
        (-139, -185),
        (170, 12),
        (400, 0),
        (396, 88),
        (347, 316),
        (-5, 172),
        (138, -67),
        (-11, -165),
        (211, -216),
        (400, -300),
        (250, -46),
        (-200, 101),
        (237, 103),
        (35, 329),
        (-285, -22),
        (-44, 131),
        (-291, 138),
        (26, -219),
        (261, 41),
        (-324, -200),
        (258, -342),
        (191, 353),
        (344, 272),
        (-58, 254),
        (-353, -329),
        (243, -172),
        (150, -400),
        (300, -309),
        (380, -18),
        (-387, -47),
        (-186, -385),
        (-189, -153),
        (361, 125),
        (-311, 104),
        (-231, 247),
        (-71, -192),
        (92, -310),
        (298, -88),
        (-77, 36),
        (98, 73),
        (244, 187),
        (33, 169),
        (146, 341),
        (-136, 336),
        (-147, 201),
        (-294, -102),
        (-33, -313),
        (337, 13),
        (-345, -3),
        (396, 280),
        (-365, 118),
        (86, -231),
        (-306, -275),
        (366, -125),
        (-165, -131),
        (-316, -140),
        (-385, 6),
        (-387, -346),
        (296, -328),
        (303, -57),
        (308, 252),
        (361, 23),
        (127, 30),
        (-266, -64),
        (-166, -64),
        (193, -217),
        (-88, 123),
        (178, 213),
        (353, -240),
        (-27, -399),
        (-65, -228),
        (-248, 58),
        (-33, 270),
        (-371, 180),
        (-205, -274),
        (60, -276),
        (-132, 28),
        (76, 101),
        (91, 346),
        (-126, 345),
    ]
    glyphs = (
            list(range(1, 9))
            + list(range(1, 26))
            + list("abcdefgh")
            + list("abcdefghijklmnopqrstuvwxy")
            + list("1a2b3c4d")
            + [
                1,
                "a",
                2,
                "b",
                3,
                "c",
                4,
                "d",
                5,
                "e",
                6,
                "f",
                7,
                "g",
                8,
                "h",
                9,
                "i",
                10,
                "j",
                11,
                "k",
                12,
                "l",
                "13",
            ]
    )
    glyphs = [str(g) for g in glyphs]
    details = list(zip(blocks, block_types, trials, blaze_positions, glyphs))
    names = ["block", "block_type", "trial", "blaze_position", "glyph"]
    control = [dict(zip(names, d)) for d in details]
    return control


def charlie2_trials():
    """Details of the trials from charlie v2 trail-making test (shorter).

    """
    blocks = ([0] * 5) + ([1] * 20) + ([2] * 5) + ([3] * 20) + ([4] * 5) + ([5] * 20)
    block_types = (
            (["practice"] * 5)
            + (["test"] * 20)
            + (["practice"] * 5)
            + (["test"] * 20)
            + (["practice"] * 5)
            + (["test"] * 20)
    )
    trials = (list(range(5)) + list(range(20))) * 3
    blaze_positions = [
        (-183, -85),
        (298, 276),
        (267, -207),
        (104, -121),
        (26, -267),
        (-203, -45),
        (198, 158),
        (-120, 183),
        (69, -111),
        (285, -112),
        (158, -268),
        (-161, -195),
        (-275, -162),
        (-33, -28),
        (94, -203),
        (-135, -276),
        (-107, -142),
        (131, 9),
        (308, 0),
        (305, 68),
        (267, 243),
        (-4, 132),
        (106, -52),
        (-8, -127),
        (162, -166),
        (-219, -17),
        (-34, 101),
        (-224, 106),
        (20, -168),
        (201, 32),
        (265, 209),
        (-45, 195),
        (-272, -253),
        (187, -132),
        (115, -308),
        (231, -238),
        (292, -14),
        (-298, -36),
        (-143, -296),
        (-145, -118),
        (278, 96),
        (-239, 80),
        (-178, 190),
        (-55, -148),
        (71, -238),
        (229, -68),
        (-59, 28),
        (75, 56),
        (188, 144),
        (25, 130),
        (259, 10),
        (-265, -2),
        (305, 215),
        (-281, 91),
        (66, -178),
        (-243, -108),
        (-296, 5),
        (-298, -266),
        (228, -252),
        (233, -44),
        (237, 194),
        (278, 18),
        (98, 23),
        (-205, -49),
        (-128, -49),
        (148, -167),
        (-68, 95),
        (137, 164),
        (272, -185),
        (-21, -307),
        (-50, -175),
        (-191, 45),
        (-25, 208),
        (-285, 138),
        (-158, -211),
    ]
    glyphs = (
            list(range(1, 6))
            + list(range(1, 21))
            + list("abcde")
            + list("abcdefghijklmnopqrst")
            + list("1a2b3")
            + [
                1,
                "a",
                2,
                "b",
                3,
                "c",
                4,
                "d",
                5,
                "e",
                6,
                "f",
                7,
                "g",
                8,
                "h",
                9,
                "i",
                10,
                "j",
            ]
    )
    glyphs = [str(g) for g in glyphs]
    details = list(zip(blocks, block_types, trials, blaze_positions, glyphs))
    names = ["block_number", "block_type", "trial_number", "blaze_position", "glyph"]
    control = [dict(zip(names, d)) for d in details]
    return control


