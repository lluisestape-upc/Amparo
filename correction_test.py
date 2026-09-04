"""Verify the fix: a person correcting an earlier answer must overwrite it."""
from dotenv import load_dotenv
load_dotenv()
import brain

answers = {}


def turn(text, label):
    r = brain.step(answers, text)
    answers.update(r["answers"])
    print(f"\n--- {label} ---")
    print("reply :", r["reply"][:150])
    print("state :", answers)
    return r


turn("", "greeting")
turn("My name is Fatima Nour and there are four of us at home, two are kids", "first answer")
turn("Sorry, I made a mistake. There are three of us, not four.", "CORRECTION 4 -> 3")

hh = answers.get("household_size", "")
print("\nRESULT:", "PASS — correction applied" if str(hh) == "3" else f"FAIL — household_size is {hh!r}")
