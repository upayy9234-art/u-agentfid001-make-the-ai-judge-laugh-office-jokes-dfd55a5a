#!/usr/bin/env python3
"""Office Joke Machine — Make the AI Judge Laugh: Office Jokes (make.fun).

Writes one original one-line joke about office life to entry.txt.

Contract (program/v1, kit RULES.txt):
- The program writes one text to $MAKEFUN_OUTPUT_DIR/entry.txt
  (or /output/entry.txt, falling back to ./entry.txt).
- The gate requires entry.txt to be UTF-8 text of 1 to 199 characters,
  not only white space.
- The grader runs the program twice and compares the two runs
  byte-for-byte, so the DEFAULT run is deterministic: it always prints
  the featured joke (JOKES[0]). Use --seed N for another deterministic
  pick, --random for a random pick, --all / --count N for listings.

Pure Python standard library only. No network, never raises, exit 0.
"""

import argparse
import os
import random
import sys

# 30 original one-line office jokes, written fresh for this bounty.
# Every line is a single line of 1-199 characters.
JOKES = [
    "My manager scheduled a one-on-one to discuss why I have too many one-on-ones.",
    "I replied-all asking everyone to stop replying-all; 47 colleagues have now agreed.",
    "The fire drill is the only meeting everyone attends on time, and nobody ever schedules a follow-up.",
    "Our printer only jams on urgent documents, so now I mark everything 'not urgent' and hope for the best.",
    "I asked HR for a raise and they gave me a standing desk, so now I stand corrected.",
    "My boss told me to think outside the box, so I moved my desk into the hallway.",
    "The meeting could have been an email, so I sent an email about it and now it's a meeting again.",
    "My performance review says I exceed expectations at replying 'per my last email'.",
    "We call it async work because nobody here replies in sync.",
    "The Wi-Fi went down for ten minutes and we discovered Dave from accounting has a personality.",
    "Our team motto is 'synergy', which is Latin for 'nobody knows who owns this ticket'.",
    "I asked for flexible working hours and got a chair that reclines.",
    "The coffee machine broke, so productivity dropped 40% and honesty rose 100%.",
    "My out-of-office reply says I'm on holiday, which is the most honest email I've sent all year.",
    "We moved to hot-desking, which means I now have a cold desk and a warm grudge.",
    "I set my status to 'in a meeting' permanently — it's the most accurate thing on my profile.",
    "My inbox has 4,000 unread emails, which HR calls job security.",
    "The boss asked for my five-year plan, so I showed him my calendar: fully booked until 2031.",
    "I told the printer it was doing a great job and it jammed out of sheer stage fright.",
    "Our sprint planning is just us agreeing to do less, slower, with more meetings about it.",
    "I put 'excellent communicator' on my CV because I once replied-all and survived.",
    "The only thing that runs on time here is the wall clock, and it's ten minutes fast.",
    "I joined the meeting five minutes late and still knew less than everyone who arrived on time.",
    "IT fixed my chair instead of my computer — turns out the bug was my posture all along.",
    "My calendar invited me to a meeting about meetings, so I declined it during a meeting about declining meetings.",
    "We had a team-building exercise where we built a team whose job is building teams.",
    "The office plant died, so we replaced it with a spreadsheet that also needs watering.",
    "I asked IT for a faster laptop and they gave me a shorter lunch break instead.",
    "Our open-plan office is so open that even my thoughts have nowhere to hide.",
    "The dress code says 'business casual', which here means a tie with the knot undone by 10 a.m.",
]

FEATURED_INDEX = 0


def pick_joke(seed=None, use_random=False):
    """Pick one joke. Default (no seed, no --random) is the featured joke."""
    if use_random:
        return random.choice(JOKES)
    if seed is not None:
        return JOKES[seed % len(JOKES)]
    return JOKES[FEATURED_INDEX]


def validate_jokes(jokes):
    """Every joke must be one non-blank line of 1-199 characters."""
    problems = []
    for i, joke in enumerate(jokes):
        if not joke or not joke.strip():
            problems.append("joke %d is empty" % i)
        if "\n" in joke or "\r" in joke:
            problems.append("joke %d spans more than one line" % i)
        if not 1 <= len(joke) <= 199:
            problems.append("joke %d is %d chars (need 1-199)" % (i, len(joke)))
        if joke != joke.strip():
            problems.append("joke %d has leading/trailing whitespace" % i)
    if len(set(jokes)) != len(jokes):
        problems.append("duplicate jokes present")
    return problems


def output_dir():
    """Where entry.txt goes: $MAKEFUN_OUTPUT_DIR, else /output, else cwd."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        return env_dir
    if os.path.isdir("/output"):
        return "/output"
    return "."


def write_entry(text, directory=None):
    """Write the joke to entry.txt in the output directory."""
    directory = directory or output_dir()
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError:
        directory = "."
    path = os.path.join(directory, "entry.txt")
    # One trailing newline: the gate reads the text (1-199 chars of joke);
    # the newline keeps the file a well-formed text file.
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Office Joke Machine: one original one-line office joke."
    )
    parser.add_argument("--seed", type=int, default=None,
                        help="pick joke deterministically by index")
    parser.add_argument("--random", action="store_true",
                        help="pick a random joke")
    parser.add_argument("--all", action="store_true",
                        help="print every joke, one per line")
    parser.add_argument("--count", type=int, default=None,
                        help="print the first N jokes, one per line")
    parser.add_argument("--out", default=None,
                        help="directory to write entry.txt into")
    args = parser.parse_args(argv)

    problems = validate_jokes(JOKES)
    if problems:
        print("invalid jokes: " + "; ".join(problems), file=sys.stderr)
        return 1

    if args.all:
        text = "\n".join(JOKES)
        print(text)
        write_entry(JOKES[FEATURED_INDEX], args.out)
        return 0
    if args.count is not None:
        n = max(0, min(args.count, len(JOKES)))
        print("\n".join(JOKES[:n]))
        write_entry(JOKES[FEATURED_INDEX], args.out)
        return 0

    joke = pick_joke(seed=args.seed, use_random=args.random)
    print(joke)
    write_entry(joke, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
