#!/usr/bin/env python3
"""Build the L3-L5 tapes from their transcripts (the transcript is the single source of truth).

Each non-empty paragraph is "SPEAKER: text"; SPEAKER maps to a macOS voice below.
Usage: python3 build_L3_L5.py [L3 L4 L5]
"""
import os, sys
from build_tape import build

HERE = os.path.dirname(os.path.abspath(__file__))

TAPES = {
    "L3": dict(
        out="L3-kestrel-point.mp3", part="two", q_range="one to thirteen",
        intro="You will hear a warden at a nature reserve talking to a group of new volunteers.",
        voices={"WARDEN": ("Lee (Premium)", 165)}, gap=0.7,
    ),
    "L4": dict(
        out="L4-study-hub.mp3", part="three", q_range="one to twelve",
        intro="You will hear two students, Oscar and Nadia, discussing their proposal "
              "for redesigning a study space.",
        voices={"OSCAR": ("Jamie (Premium)", 172), "NADIA": ("Karen (Premium)", 172)}, gap=0.45,
    ),
    "L5": dict(
        out="L5-qanat.mp3", part="four", q_range="one to twelve",
        intro="You will hear part of a lecture about an ancient method of supplying water.",
        voices={"LECTURER": ("Serena (Premium)", 160)}, gap=0.8,
    ),
}


def turns_from(transcript, voices, gap):
    turns = []
    for para in open(transcript, encoding="utf-8").read().split("\n\n"):
        para = para.strip()
        if not para:
            continue
        speaker, text = para.split(":", 1)
        voice, wpm = voices[speaker.strip()]
        turns.append((voice, wpm, text.strip(), gap))
    return turns


if __name__ == "__main__":
    os.chdir(HERE)
    for key in sys.argv[1:] or TAPES:
        cfg = TAPES[key]
        build(out=cfg["out"], intro=cfg["intro"], q_range=cfg["q_range"], part=cfg["part"],
              turns=turns_from(f"{key}-transcript.txt", cfg["voices"], cfg["gap"]))
