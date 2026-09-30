#!/usr/bin/env python3
"""Build an IELTS-style listening tape: narrator framing + prep silence + dialogue.

Usage from a per-exercise script:
    from build_tape import build
    build(out="L1-meadow.mp3", intro="You will hear ...", q_range="one to nine",
          part="one", turns=[(voice, wpm, text, gap_after), ...],
          prep_seconds=30, check_seconds=30)
"""
import os, shutil, subprocess

NARRATOR = "Ava (Premium)"          # deliberately a different accent from the speakers
NARRATOR_WPM = 138                  # slightly slower than dialogue: it carries instructions


def _say(voice, wpm, text, stem):
    subprocess.run(["say", "-v", voice, "-r", str(wpm), "-o", f"{stem}.aiff", text], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{stem}.aiff",
                    "-ar", "24000", "-ac", "1", f"{stem}.wav"], check=True)
    return f"{stem}.wav"


def _silence(seconds, stem):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi",
                    "-i", "anullsrc=r=24000:cl=mono", "-t", str(seconds), f"{stem}.wav"], check=True)
    return f"{stem}.wav"


def build(out, intro, q_range, part, turns, prep_seconds=30, check_seconds=30, workdir="_tape"):
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir)
    seq, n = [], 0

    def add(path):
        seq.append(path)

    def narrate(text):
        nonlocal n
        add(_say(NARRATOR, NARRATOR_WPM, text, f"{workdir}/{n:03d}_nar")); n += 1

    def pause(sec):
        nonlocal n
        add(_silence(sec, f"{workdir}/{n:03d}_sil")); n += 1

    narrate(f"Part {part}. {intro} First, you have some time to look at questions {q_range}.")
    pause(prep_seconds)
    narrate(f"Now listen carefully and answer questions {q_range}.")
    pause(1.2)

    for voice, wpm, text, gap in turns:
        nonlocal_stem = f"{workdir}/{n:03d}_t"
        add(_say(voice, wpm, text, nonlocal_stem)); n += 1
        pause(gap)

    pause(1.0)
    narrate(f"That is the end of part {part}. You now have half a minute to check your answers.")
    pause(check_seconds)

    listing = f"{workdir}/list.txt"
    with open(listing, "w") as fh:
        for p in seq:
            fh.write(f"file '{os.path.basename(p)}'\n")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", listing, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-codec:a", "libmp3lame", "-b:a", "96k", out], check=True)
    shutil.rmtree(workdir, ignore_errors=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", out], capture_output=True, text=True).stdout.strip()
    print(f"{out}: {float(dur)/60:.1f} min ({float(dur):.0f}s)")
