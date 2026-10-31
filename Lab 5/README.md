<img width="960" height="1280" alt="3591793459625_ pic" src="https://github.com/user-attachments/assets/1e5ac47c-3123-4f58-ad8f-bc0e44a9ca0d" />
# Observant Systems: Overnight Sensation

**Team:** Individual

**Members:** Bowei Huang (bh654)

**Project name:** Night Desk Watch

<details>
	<summary><strong>Instructions for Students (Click to Expand)</strong></summary>
  
	**Submission Cleanup Reminder:**
	- This README.md contains extra instructional text for guidance.
	- Before submitting, remove all instructional text and example prompts from this file.
	- You may delete these sections or use the toggle/hide feature in VS Code to collapse them for a cleaner look.
	- Your final submission should be neat, focused on your own work, and easy to read for grading.
  
	This helps ensure your README.md is clear, professional, and uniquely yours!
</details>


For lab this week, we focus on creating interactive systems that can detect and respond to events or stimuli in the environment of the Pi, like the Boat Detector we mentioned in lecture. 
Your **observant device** could, for example, count items, find objects, recognize an event or continuously monitor a room.

This lab will help you think through the design of observant systems, particularly corner cases that the algorithms need to be aware of.

**New this year: the AI runs on the Pi.** Your Pi 5 can run an object detector ([YOLO](https://docs.ultralytics.com/)) and a small language model ([Qwen](https://ollama.com/library/qwen3.5) through [Ollama](https://ollama.com)) completely offline. In Part 1 you get both running and connect them: YOLO *sees*, Qwen *reasons* about what was seen. These models are slow, but they have all night. In Part 2 you use them to design a **night-time interaction**: what you tell the device before bed, what it does while you sleep, and what it shows you when you wake up.

**Please indicate anyone that helped with this Lab here.**
Be generous in acknowledging their contributions! And also recognizing any other influences (e.g. from YouTube, Github, Twitter) that informed your design. 

## Overview

**Part 1: the tools**

A) [Set up your Pi for on-device AI](#part-a)

B) [See: recognize people in real time with YOLO](#part-b)

C) [See more: hands and pose with MediaPipe](#part-c)

D) [Reason: run Qwen on the Pi with Ollama](#part-d)

E) [Connect: from YOLO readings to Qwen reasoning](#part-e)

**Part 2: Overnight Sensation**

F) [Read Part 2 and storyboard your night-time interaction](#part-f)

G) [Design the interaction before bed](#part-g)

H) [Incorporate the observant system during sleep](#part-h)

I) [Design the interaction when awake](#part-i)

The tools from earlier versions of this lab (MobileNet, Teachable Machine, Moondream, audio analysis, classic OpenCV) live in the [legacy folder](legacy/README.md). They are optional, but any of them can be the sensor in your Part 2 system.


## Prep for Part 1

Please check the instructions in [prep.md](prep.md) and complete them before lab. The installs in Part A take a while, so prep.md also tells you how to get a head start.

## The Report

This readme.md page in your own repository should be edited to include the work you have done. You can delete everything but the headers and the sections between the \*\*\***stars**\*\*\*. Write the answers to the questions under the starred sentences. Include any material that explains what you did in this lab hub folder, and link it in the readme.

---

# Part 1

## Part A. 
### Set up your Pi for on-device AI

Create a virtual environment and install the requirements. They include `ultralytics` (YOLO), which pulls in torch, so this takes a while:

```
pi@raspberrypi:~$ cd Interactive-Lab-Hub/Lab\ 5
pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python3 -m venv .venv
pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ source .venv/bin/activate
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ pip install -r requirements.txt
```

As in Lab 3, [`uv`](https://docs.astral.sh/uv/) is a much faster drop-in for `pip`: `pip install uv && uv pip install -r requirements.txt`.

### YOLO: download the nano model and export it for the Pi

We use the nano model of [YOLO26](https://docs.ultralytics.com/models/yolo26/), exported once to NCNN, the format that runs fastest on the Pi. This downloads the weights:

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python -c "from ultralytics import YOLO; YOLO('yolo26n.pt').export(format='ncnn')"
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ yolo export model=yolo26n.pt format=ncnn
```
If every ultralytics message is followed by a `--- Logging error ---` traceback ending in `UnicodeEncodeError: 'latin-1' codec can't encode character`, fix your shell's locale once::

```
echo 'export LANG=C.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=C.UTF-8' >> ~/.bashrc
echo 'export PYTHONIOENCODING=utf-8' >> ~/.bashrc
source ~/.bashrc
```

The second command converts the .pt model to a .ncnn model.

Test it on an image from the internet. `project="$PWD"` keeps the output in `predict` in the current lab folder; without it, ultralytics writes to a `runs/` folder at the top of your git repo, where you will not think to look.

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ yolo predict model=yolo26n_ncnn_model source=https://ultralytics.com/images/bus.jpg project="$PWD"
```

The result is in `predict/bus.jpg`: boxes around the people and the bus.

Now a photo of your own. Plug in the webcam and take one with `snap.py` (`--delay 3` gives you three seconds to get into the frame), or choose any picture you downloaded from the internet and put under this folder. Put your selected picture after the `source=` Then run the same command on it:

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python snap.py --delay 3
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ yolo predict model=yolo26n_ncnn_model source=snap.jpg project=runs
```

Every run gets its own numbered folder, so this one is in `runs/predict2/snap.jpg`; the command prints where it saved. Keep `snap.jpg`, you will show it to Qwen in Part D.

### Ollama: install it and pull Qwen

[Ollama](https://ollama.com) runs language models locally. Nothing leaves the Pi: no API key, no internet after the download.

```
pi@raspberrypi:~ $ curl -fsSL https://ollama.com/install.sh | sh
pi@raspberrypi:~ $ ollama pull qwen3.5:0.8b
pi@raspberrypi:~ $ ollama pull qwen3:0.6b
pi@raspberrypi:~ $ ollama list
```

| model | download | what it does |
|---|---|---|
| `qwen3.5:0.8b` | ~1.3 GB | text **and images**; the one we use in this lab |
| `qwen3:0.6b` | ~0.5 GB | text only, smaller and faster (~16 tokens/s on a Pi 5) |

\*\*\***Include a screenshot of `ollama list` showing your models.**\*\*\*

<img width="550" height="300" alt="3481792937031_ pic" src="https://github.com/user-attachments/assets/5fab4314-0100-4be3-ae6c-182fa1fdcecb" />


## Part B. 
### See: recognize people in real time with YOLO

YOLO is an *object detector*: it finds every person, cup, cat and so on (the 80 [COCO](https://cocodataset.org/) classes), draws a box around each, and gives a confidence. For an observant system that is exactly what you want: *how many*, *where*, *how sure*.

Connect your webcam, connect to your Pi through **VNC** (the script opens a window), and run the person detector. Read `yolo_person.py` first; the loop at the bottom is the whole idea.

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python yolo_person.py
```

While it runs, walk in and out of the frame, sit down, turn your back, hold up a photo of a person on your phone. Watch the confidence number on the box change with each.

Then press q to quit and run it again with a flag. Each one changes a single thing:

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python yolo_person.py --conf 0.2     # lower the bar: see what the model is unsure about
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python yolo_person.py --conf 0.7     # raise the bar: see what you lose
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python yolo_person.py --all          # all 80 classes, not only people: what else is on your desk, and what does it get wrong?
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python yolo_person.py --headless     # no window, only the printed readings: how it runs over ssh, and at night
```

\*\*\***Include a short video or screenshots of your experiments with the person detection. Write down three situations where it did not see you, or saw a person who was not there, and what you think the cause was.**\*\*\*

### Person detection experiments

I ran `yolo_person.py` and tested different positions, partial occlusion, and a photo displayed on my phone. When I was sitting sideways with my upper body visible, YOLO detected me with a confidence of 0.91.

#### 1. A photo caused an extra person detection

When I held a portrait photo on my phone in front of the camera, two overlapping person boxes appeared, with confidence scores of 0.53 and 0.58, although I was the only person physically present. The boxes were also poorly aligned. The portrait likely provided enough human features to trigger an additional detection. This shows a limitation of using person detection to count people in a room.

<img width="500" height="300" alt="截屏2026-10-25 上午10 44 17" src="https://github.com/user-attachments/assets/95a7eb1f-b72c-4002-af74-70f4dc76be62" />


#### 2. Heavy occlusion caused a missed detection

When I hid my head and most of my body behind a cushion, YOLO did not detect me, even though part of my sleeve and arm remained visible. The cushion covered most of the features the model could use to recognize a person. With less coverage in an earlier test, it still detected me at 0.65 confidence.

<img width="500" height="300" alt="截屏2026-10-25 上午10 58 13" src="https://github.com/user-attachments/assets/817b17c4-6fbc-45c8-a47a-6e73183646f1" />


#### 3. Being mostly outside the frame caused a missed detection

When I moved almost completely out of the camera view, a small part of my back was still visible at the left edge, but no person box appeared. The visible area was probably too small and lacked a recognizable body shape. This could make the system miss someone entering or leaving at the edge of the camera view.

<img width="500" height="300" alt="截屏2026-10-25 上午11 01 53" src="https://github.com/user-attachments/assets/40c84124-8055-48a7-9b06-fadd98237620" />


### Comparing confidence thresholds

I tested `--conf 0.7` and `--conf 0.2` while keeping part of my body near the edge of the frame. At 0.7, no person box appeared. At 0.2, a similar position produced a detection with a confidence of 0.37. Lowering the threshold allowed a less certain detection to appear, while the higher threshold filtered it out. The positions were similar, but not exactly identical.

<img width="500" height="300" alt="截屏2026-10-25 上午11 04 57" src="https://github.com/user-attachments/assets/4ebbc137-64e0-4b22-a6e2-df4143aba490" />
<img width="500" height="300" alt="截屏2026-10-25 上午11 20 30" src="https://github.com/user-attachments/assets/1ad85e42-7a33-4e09-9a18-048cbbefea32" />



### Other modes

With `--all`, the model detected me as a person at 0.81 confidence and labeled the handheld device as a remote at 0.72 confidence.

<img width="500" height="300" alt="截屏2026-10-25 上午11 09 38" src="https://github.com/user-attachments/assets/66e47e15-5313-4fac-9dc8-176f143b2bd6" />


I also tested `--headless`. It ran without a camera window and printed the person's horizontal position, bounding-box height, confidence, and object count in the terminal. This would be useful when running the system over SSH or leaving it running overnight.

<img width="500" height="300" alt="截屏2026-10-25 上午11 13 07" src="https://github.com/user-attachments/assets/dab1cefa-1b1a-4fa6-a1c1-3f33acd04008" />





## Part C. 
### See more: hands and pose with MediaPipe

YOLO tells you that a person is there. Google's [MediaPipe](https://mediapipe.dev/) tells you what their hands and body are doing: face, hand and body pose detection, fast on the Pi.

![Media pipe](Readme_files/mp.gif)

The demo plays a looping audio file, so make the helper script executable first:

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ chmod +x loop_audio.sh
```

Connect your webcam, connect to your Pi through **VNC**, and run the hand pose script:
(***it will not work if you use ssh from your laptop***)

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python hand_pose.py
```

Try the two main features of this script: 1) pinching for percentage control (the thumb-to-index distance sets the volume), and 2) "[Quiet Coyote](https://www.youtube.com/watch?v=qsKlNVpY7zg)" for instant percentage setting (the gesture mutes it). Notice how this example uses hardcoded positions and relates those positions with a desired set of events, in `hand_pose.py`: a hand is 21 landmark coordinates, and an *event* is a rule you write over them. That is the same job as `interpret()` in Part E.

Consider how you might use this position based approach to create an interaction, and write how you might use it on either face, hand or body pose tracking.

\*\*\***Include a screenshot or short video of the hand pose demo, and write how you might use face, hand or body pose tracking in your observant system.**\*\*\*



https://github.com/user-attachments/assets/92b422d0-9d7a-4eda-83db-bb3ec5048300



### Hand pose experiment

I ran `hand_pose.py` through VNC and tested both gestures. Moving my thumb and index finger closer together lowered the displayed volume percentage, while moving them apart raised it. When I made the Quiet Coyote gesture, the screen showed “Quiet coyote!” and the percentage dropped to 0%.

### Using hand tracking in my observant system

I could use the Quiet Coyote gesture to start the night-time monitoring before bed. The device would play a short tone and display “Monitoring started” to confirm that it received the command. I would require the gesture to be held for two seconds to reduce accidental activation.

## Part D. 
### Reason: run Qwen on the Pi with Ollama

Talk to the model in the terminal first. Qwen3 models "think" before they answer, which is slow on a Pi, so turn it off. Then ask about something you can check:

```
pi@raspberrypi:~ $ ollama run qwen3.5:0.8b
>>> /set nothink
>>> Tell me a bit about the history of Roosevelt Island. Three sentences.
>>> /bye
```

Roosevelt Island is a good first question because you know the ground truth: it was Blackwell's Island, then Welfare Island, got its current name in 1973, and Cornell Tech opened on it in 2017. Count how many of the model's facts are true.

From Python, qwen requests can be triggered by the `ask_qwen.py` script. It turns thinking off, tells the model to answer in at most three sentences, and cuts it off after 120 tokens (`--max-tokens` changes that), because a small model left alone writes an essay. Read the script, then run:

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python ask_qwen.py "Tell me a bit about the history of Roosevelt Island."
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python ask_qwen.py --model qwen3:0.6b "Tell me a bit about the history of Roosevelt Island."
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python ask_qwen.py --image snap.jpg "What is in this photo?"
```

Things in the [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) worth knowing:

* `think: false` skips the reasoning trace. Always, on a Pi. `ask_qwen.py` sends it on every request; `--think` turns the trace back on for one question, so you can see what you are skipping and how long it takes.
* `format` makes the model answer as JSON with the fields you name (`--json`). Handy when a display or a servo has to read the answer.
* `images` sends a photo along with the prompt (`--image snap.jpg`, the photo from Part A). `qwen3.5:0.8b` can look at pictures.

A 0.8B model is slow and sometimes wrong. It will invent events that are not in the data and agree with a wrong premise. Give it the data, keep its job narrow, and decide what the device does when the model is unsure.

\*\*\***Ask Qwen three questions to answer. Paste the questions, the answers and how long each took. Try one of them with `qwen3:0.6b` and compare.**\*\*\*

### Question 1: Roosevelt Island history

Prompt: “Tell me a bit about the history of Roosevelt Island.”

Model: qwen3.5:0.8b  
Time: 36.6 seconds

Answer:
“Roosevelt Island was originally built as a military fortification during World War II, later repurposed for housing and education. It is now a historic district featuring over 100 buildings that have been restored to reflect their original architectural styles. Today, it serves as a vital educational center for the Greater New York area and a popular destination for visitors interested in history and architecture.”

The answer sounded confident, but its claim about the island's origin did not match the history provided in the lab.

#### Comparison with qwen3:0.6b

Time: 16.9 seconds

Answer:
“Roosevelt Island, a small island in the Pacific Ocean, has a rich and mysterious history. It was originally a remote and uninhabited island, but it became a significant location for the United States during the early 20th century. The island was chosen by the U.S. government as a base for the Pacific Fleet, which was stationed there during World War II. It became a symbol of the U.S. in the Pacific, and its history is closely tied to the broader story of the United States in the Pacific.”

The smaller model was faster in this test, but described a different location instead of the New York island intended by the lab. Neither answer was reliable for this question. These were single runs, so the times also include differences in model loading and response length.

### Question 2: Describing a photo

Prompt: “What is in this photo?”  
Image: snap.jpg  
Model: qwen3.5:0.8b  
Time: 52.3 seconds

Answer:
“This photo shows a close-up of a young person's face, focusing on their nose and mouth. They have dark hair and appear to be looking slightly off-camera.”

The image request took the longest of my tests. 

### Question 3: Summarizing a supplied log

Prompt: “A camera log says: 22:00 nobody; 22:05 one person; 22:10 nobody. Summarize what the camera detected. Can you tell who the person was?”

This was a made-up test log supplied in the prompt, not a real camera recording.

Model: qwen3.5:0.8b  
Time: 10.6 seconds

Answer:
“The night watchman, a single person, arrived at the residence around 22:05 to check on the house. There were no other occupants present during this period.”

The model invented the person's identity and reason for being there. The log only supported saying that one person was detected at 22:05, with nobody detected at 22:00 and 22:10. It could not establish who the person was or whether anyone was outside the camera view.

### What I learned

The models could produce fluent answers while adding unsupported details. For my observant system, I would give the model a narrow task and explicitly ask it not to infer identities, intentions, or events missing from the log. I would also keep the original readings available so users can check the summary.

<img width="500" height="300" alt="截屏2026-10-25 中午12 08 01" src="https://github.com/user-attachments/assets/243c3a3f-4492-4789-9ef6-62f2921feb9a" />



## Part E. 
### Connect: from YOLO readings to Qwen reasoning

An observant system is a pipeline: a **detector** turns pixels into boxes, an **interpreter** turns boxes into readings in words ("one person, left, close"), the readings pile up in a **log**, and a **reasoner** answers a question about the log. The language model never sees pixels, only the words you chose in the interpreter. That makes the interpreter the most important design decision in the system.

`yolo_to_qwen.py` is the pipeline in one file, one function per stage. Read it before you run it:

* `interpret(r)` is the interpreter. It takes one YOLO result and returns one reading. A person is *left*, *center* or *right* by which third of the frame the middle of their box is in, and *close* if the box is taller than 60% of the frame, *far* otherwise. The reading is a string like `1 person(s) at center/close`, or `nobody`. Fifteen lines, and they decide everything the model can know.
* `watch(seconds)` is the detector and the log. Twice a second it reads a frame, runs YOLO on it and calls `interpret()`. A time-stamped reading goes into the log **only when it differs from the previous one**, so a minute of sitting still is one line, not 120.
* `ask(log, question)` is the reasoner. It pastes the log and your question into one prompt, tells Qwen to answer in at most three sentences using only what is in the log, and sends it to Ollama with thinking off.

Run it through VNC and a window opens with YOLO's boxes, the current reading and the seconds left. Press q to stop watching early. Over plain ssh add `--headless` and you get the same thing minus the window.

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python yolo_to_qwen.py
```

It watches for a minute, saves the log to `watch_log.txt` and asks Qwen the default question. The terminal looks something like this:

```
14:02:11 nobody
14:02:19 1 person(s) at right/far
14:02:24 1 person(s) at center/close
14:02:51 nobody

4 lines saved to watch_log.txt
asking Qwen...

Qwen (18.4 s):
One person came in from the right, moved close to the camera, and left after about half a minute. ...
```

### Connecting YOLO to Qwen

I ran `yolo_to_qwen.py` for approximately one minute and tested moving across the frame, approaching the camera, and leaving its view. The program saved 20 readings to `watch_log.txt`. Qwen then took 53.2 seconds to generate a summary.

The pipeline used YOLO to detect people, converted the boxes into readings such as left/close or center/close, and logged changes with timestamps. Qwen received these text readings rather than the camera images.

### Checking the summary

Most readings showed one person or nobody. At 12:17:29, the detector reported two people at center/close and left/far. The next reading returned to one person.

Qwen claimed that the number of people increased from one to four. No reading recorded four people, so this claim was unsupported. Changes in position also do not establish that different people entered, since this log does not track individual identities.

This test showed that getting the pipeline to run does not guarantee an accurate summary. For my overnight system, I would calculate the maximum detected count directly from the log and keep the original readings available for checking. A reading of “nobody” would mean no person was detected in the camera view, rather than proof that the room was empty.

[View the recorded log](legacy/watch_log.txt)

<img width="500" height="300" alt="截屏2026-10-25 中午12 19 22" src="https://github.com/user-attachments/assets/26c04d60-f3e8-44c1-bfaa-2b9e1f2bbefe" />

<img width="500" height="300" alt="截屏2026-10-25 中午12 21 07" src="https://github.com/user-attachments/assets/2b5330ba-d6e0-4512-bc32-2f9aa2b535f1" />

---

# Lab 5 Part 2: Overnight Sensation

For Part 2, you will use the observant system from Part 1 to design a night-time interaction. On-device AI is slow, so let it work while you sleep. The person meets the device twice: **before bed**, when they hand the night over, and **when awake**, when the device gives something back. In between, the pipeline from Part E runs on its own.

Two flavors, pick one or mix them:

* **Sense all night.** The Pi watches, listens or measures from bedtime until morning and keeps a log.
* **Process all night.** You already have the data (a day of phone photos, a long recording) and the Pi needs hours to get through it.

Two house rules. Sample rather than stream: one look every 5 to 30 seconds is plenty, and it keeps the Pi cool. And keep everything on the Pi: tell the people you live with, point the camera at things rather than at beds, and delete the snapshots after the demo.

## Part F. 
### Read Part 2 and storyboard your night-time interaction

Storyboard a night-time interaction built on your observant system, in three panels:

1. **Before bed.** How does the person hand the night over, and how does the device acknowledge it?
2. **While asleep.** What does the device watch or work through?
3. **When awake.** What is the one thing the person learns, and in what medium?

Stuck? A kitchen that tells you who raided the fridge. A desk that reports whether you actually went to bed. A window that names the quietest hour. A plant that describes its night. Find something better.

Use storyboards and/or [Verplank diagrams](https://ccrma.stanford.edu/courses/250a-fall-2004/IDSketchbok.pdf).

\*\*\***Insert ideas, sketches, Verplank diagrams and storyboards for your night-time interaction here.**\*\*\*

<img width="500" height="300" alt="3591793459625_ pic" src="https://github.com/user-attachments/assets/54fb161d-f1ae-45f4-ada3-8e72e946697c" />
feedback: The three-step interaction is easy to follow. One concern is whether the camera can recognize the book and cup in low light. I should test the lighting before the overnight run. Missed detections could also look like an object was removed, so the morning report should avoid treating every missed detection as a real change. If nothing changes, it should simply say that no changes were detected.

Planned revisions: I will keep the camera in a fixed position and test which objects it can recognize reliably. The morning report will describe detected changes and mention uncertainty when the readings are inconsistent.

## Prep for Part 2

1. Look at and give feedback on the Part F storyboards.
   **Put the feedback for your ideas here.**
2. [Update your Lab Hub](prep.md#get-the-latest-content) to get the latest content for Part 2.
3. Decide where the device will spend the night and who else lives there. Get their OK before the first run.
4. Revise your storyboard with the feedback and with what you learned in Part E about where the pipeline breaks.

\*\*\***Post your revised storyboard here.**\*\*\*

## Part G. 
### Design the interaction before

The hand-off: the person tells the device what to watch tonight, and the device acknowledges it. Keep it to a thirty-second ritual. A button or a touch (Lab 4), a spoken sentence (Lab 3), a wave or a Quiet Coyote at the camera (Part C). The acknowledgement can be a line on the display, a tone, or an LED that dims rather than lights up. At its simplest, the hand-off just sets the question that the morning will answer.

\*\*\***Describe the interaction before.**\*\*\*

## Part H. 
### Incorporate the observant system

The Part E pipeline becomes the night shift. `overnight.py` runs your `interpret()` from `yolo_to_qwen.py` every few seconds, people only unless you pass `--all`, and writes the readings to `night_log.jsonl`; the reasoning waits for the morning. Start it inside `tmux` so it keeps running after you close your laptop, and stop it with Ctrl-C in the morning:

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ tmux new -s night
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python overnight.py
```

Fake a night first: run it for thirty seconds while you walk around, stop it, and run `morning.py` from Part I. When that looks right, run a real night. If your storyboard needs a sensor rather than the camera, swap in the Lab 4 example code and log its reading the same way.

\*\*\***Screenshots or videos of the running system.**\*\*\*

## Part I. 
### Design the interaction after

The reveal. The night produced a log; the morning turns it into something a half-awake person can take in. `morning.py` is the smallest version: it asks Qwen for a three-sentence report.

```
(.venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 5 $ python morning.py
```

Make it yours: show the report on the Mini PiTFT, read it aloud with Piper from Lab 3, plot the night as a timeline, or ask for JSON (`--json`, Part D) and move a servo. Whatever you pick, make sure it is honest about a night in which nothing happened.

## Final documentation

Document all the prototypes and iterations you have designed and worked on. The deliverables for this lab are writings, sketches, photos, and videos that show what your system:

* "Looks like": how the device sits in the room at night, and what it looks like at bedtime and in the morning.
* "Works like": the pipeline from detector to interpreter to log to reasoner, with a real night's data.
* "Acts like": how a person hands the night over and what they get back.

\*\*\***Include a short video of the whole system**\*\*\*

As always, make sure you document contributions and ideas from others (and AI) explicitly in your writeup.

You are permitted (but not required) to work in groups and share a turn in; you are expected to make equal contribution on any group work you do, and N people's group project should look like N times the work of a single person's lab. Make sure the page for the group turn in is linked to your personal Interactive Lab Hub page.

## Deliverables & Submission for Lab 5

For submission, the readme.md page for this lab should be edited to include the work you have done:
* Upload any materials that explain what you did, including your code and night log, into your Lab 5 repository, and link them in your Lab 5 readme.md.
* Labs are due on Sundays, make sure to submit your Lab 5 readme.md to Canvas.

<details>
  <summary><strong>Submission Cleanup Reminder (Click to Expand)</strong></summary>

  **Before submitting your README.md:**
  - This readme.md file has a lot of extra text for guidance.
  - Remove all instructional text and example prompts from this file.
  - You may either delete these sections or use the toggle/hide feature in VS Code to collapse them for a cleaner look.
  - Your final submission should be neat, focused on your own work, and easy to read for grading.
</details>
