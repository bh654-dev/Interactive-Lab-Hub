import argparse
import json
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--log", default="bottle_night_log.jsonl")
args = parser.parse_args()

with open(args.log) as f:
    entries = [json.loads(line) for line in f if line.strip()]

readings = [e for e in entries if "reading" in e]
if not readings:
    print("No confirmed bottle readings were recorded.")
    raise SystemExit

print("Desk Watch — detection log")
for e in readings:
    print(e["t"], e["reading"])

if len(readings) == 1:
    facts = (
        "Only one confirmed state was recorded. "
        "No further confirmed state changes were logged. "
        "This does not prove that the bottle never moved."
    )
else:
    facts = (
        f"{len(readings) - 1} confirmed detection-state changes were logged. "
        "These are changes in detection, not proof of physical movement."
    )

prompt = f"""Write a short morning report about a bottle on a desk.
Use only these recorded observations:
{json.dumps(readings)}

Facts: {facts}
Each state required three consecutive matching samples.
Timestamps mark confirmation, not the exact time of movement.
A missing detection may be caused by poor lighting or obstruction.
Do not claim anyone took, used, or returned the bottle.
Do not invent an unusual event.
Write at most three plain English sentences."""

print("\nGenerating morning report...", flush=True)
r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:0.6b",
        "prompt": prompt,
        "think": False,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 220},
    },
    timeout=600,
)
r.raise_for_status()
print("\n" + r.json()["response"])
