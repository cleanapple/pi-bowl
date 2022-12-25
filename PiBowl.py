#!/usr/bin/env python3

from time import sleep, time
from tkinter import *
from tkinter import messagebox
import threading
from pynput import keyboard
from os import path, system

#Constants
virtualized=True
pins=[4, 27, 22, 23, 24, 25, 0] #Teams
pins2=[5, 6, 12, 26] #Hardware buttons fot Yes, No, New Game, Open/Reset

#STATE VARIABLES
inGame=True
timing=False			#Currently counting down the timer
deciding=False			#Right/Wrong decision
buzzable=-1			#Can be zero for no one, 1 for team 1, 2 for team 2, or -1 for all
interrupted=False
firstWrong=False
wrongLimit=0
question=0
buzzed_in_queue = []
buzzlock = []
buzzer=19
teamcolors = ["#37d67a", "#fcb900", "#9979d2", "#ffff00", "#79abd2", "#f78da7"]
TEAMS=3
TIMELIMIT=15
sq = 1
sqscore=("+1")
inGame=True
locked = True

if virtualized==True:
    h=DISABLED

if virtualized==False:
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
	for i in range(0, len(pins)):
		GPIO.setup(pins[i], GPIO.IN, GPIO.PUD_UP)
	for h in range (0, len(pins2)):
		GPIO.setup(pins2[h], GPIO.IN, GPIO.PUD_UP)
	GPIO.setup(buzzer,GPIO.OUT)

print("Starting Game")

def count(timemod):
    global TIMELIMIT, timeLeft
    TIMELIMIT=TIMELIMIT+timemod
    setTimeString(TIMELIMIT)

def teamadd(teammod):
    global TEAMS, teamString
    TEAMS = TEAMS+teammod
    if TEAMS > 6:
        TEAMS-=6
    if TEAMS < 1:
        TEAMS+=1
    teamString.set(TEAMS)

def superQuiz():
    global scores, plus, sqLevel, sq, sqString, sqscore
    if sq==1:
        plus.set("+1")
        sqscore=("+1")
        sqString.set("Freshman")	
    if sq==2:
        plus.set("+2")
        sqscore=("+2")
        sqString.set("Graduate")		
    if sq== 3:
        plus.set("+3")
        sqscore=("+3")
        sqString.set("Ph.D")

def sqadd(sqmod):
    global sq
    sq = sq+sqmod
    if sq > 3:
        sq -= 3
    if sq < 1:
        sq +=1
    superQuiz()

def timer():
	global timestart, timeString, TIMELIMIT, timeLeft, locked, \
		   inGame, timing, buzzable, timeLabel, question
	while True:
		sleep(.01)
		if (timing):
			delta = time()-timestart
			if delta > timeLeft:
				setTimeString("00")
				threading.Thread(target=timeout).start()
				sleep (1)
				setTimeString(TIMELIMIT)
				timing=False

			elif delta%1<.1:
				string=str(int(timeLeft+1-delta))
				try:
					setTimeString(string) #TODO Why does this throw an error?
				except AttributeError:
					print("failed")
		else:
			sleep(.05)

def setTimeString(string):
	global timeString, timeLabel

	try:
		timeString.set(string) #TODO Why does this throw an error?
	except AttributeError:
		print("failed to set to: "+string)
		timeString=StringVar(timeLabel)
		timeLabel.config(textvariable=timeString)
		setTimeString(string)

def buzzercheck():
	global locked, pins, pins2, buzzable

	while True:
		if buzzable!=0:
			sleep(.02)
			for i in range(0, len(pins)):
				if (GPIO.input(pins[i])==False) and i not in buzzlock:
					virtualPress(i)
			for h in range (0, len(pins2)):
				if (GPIO.input(pins2[h])==False):
					hardware(h) 
		else:
			sleep(.1)

def hardware(h):
	global locked, buttons, timeLeft, timeLabel, TEAMS, buzzedIn, buzzed_in_queue, deciding, \
		state, bigLabel, bigString, buzzlock, teamcolors, inGame, timing, buzzable, newGame, interrupted
	if h == 0:
		if len(buzzed_in_queue) > 0:
			correct()
	if h == 1:
		if len(buzzed_in_queue) > 0:
			wrong()
	if h == 2:
		newGame()
	if h == 3:
		buzzed_in_queue = []
		buzzlock = []
		open()

def virtualPress(i):
	global locked, soundLocation, buttons, h, TEAMS, timeLeft, timeLabel, buzzedIn, buzzed_in_queue, deciding, \
		state, bigLabel, bigString, buzzlock, teamcolors, inGame, timing, buzzable, interrupted
	print("buzzable=",buzzable)
	if buzzable==-1 or buzzable==int(i/9)+1:
		if inGame:
			buzzable=-1
			deciding=True
			timeLeft=int(timeString.get())
		buzzable=-1
		humanBuzzerNum=i
		if humanBuzzerNum>9:
			humanBuzzerNum-=9
		interrupted=not timing
		timing=False
		buzzerString.set("Locked: Buzzer "+str(humanBuzzerNum))
		threading.Thread(target=flashLock, args=(i,)).start()

		if i not in buzzlock:
			if i == 0 and i not in buzzlock:
				buzzed_in_queue.append(1)
				buzzlock.append(i)
				startCountdown
			if i == 1 and i not in buzzlock:
				buzzed_in_queue.append(2)
				buzzlock.append(i)
				startCountdown
			if i == 2 and i not in buzzlock:
				buzzed_in_queue.append(3)
				buzzlock.append(i)
				startCountdown
			if i == 3 and i not in buzzlock:
				buzzed_in_queue.append(4)
				buzzlock.append(i)
				startCountdown                
			if i == 4 and i not in buzzlock:
				buzzed_in_queue.append(5)
				buzzlock.append(i)
				startCountdown                
			if i == 5 and i not in buzzlock:
				buzzed_in_queue.append(6)
				buzzlock.append(i)
				startCountdown                
		setButtons()
		if len(buzzed_in_queue) > 0:
			bigLabel.config(bg=teamcolors[buzzed_in_queue[0]-1])
			bigString.set(buzzed_in_queue)
		threading.Thread(target=playsound, args=(i,)).start()
		if len(buzzed_in_queue) > 0:
			startCountdown()

def flashLock(i):
	global locked, buttons, buzzedIn, buzzed_in_queue
	for i in range (0,5):
		colorb = buttons[i].cget('bg')
		flashb = buttons[i].cget('activebackground')
		while i in buzzlock:
			buttons[i].config(bg=flashb)
			sleep(.4)
			buttons[i].config(bg=colorb)
			sleep(.4)

def playsound(i):
	global buzzlock
	if i in buzzlock:
		GPIO.output(buzzer,GPIO.HIGH)
		sleep(0.075)
		GPIO.output(buzzer,GPIO.LOW)
	else:
		GPIO.output(buzzer,GPIO.LOW)

def timeout():
    GPIO.output(buzzer,GPIO.HIGH)
    sleep(0.5)
    GPIO.output(buzzer,GPIO.LOW)

def reset(openall): #reset for the next question
	global state, locked, timestart, timeLeft, TIMELIMIT, deciding, buzzedIn, buzzed_in_queue, timing, timeLeft, \
		correctButton, wrongButton, timeString, bigString, bigLabel, top, buzzable, firstWrong
	if openall:
		buzzable=-1
		timeLeft = TIMELIMIT
	bigString.set("")
	bigLabel.config(bg=top.cget('bg'))
	setTimeString(str(timeLeft))
	timing=False
	deciding=False
	setButtons()

def open(): #reset buzzers
	global inGame, wrongLimit, locked, timing, h, hardware, falseStart, timeString, state, buzzlock, buzzable, buzzedIn, buzzed_in_queue, deciding

	if not inGame:
		falseStart()
	buzzed_in_queue=[]
	buzzlock =[]
	wrongLimit = 0
	buzzable=-1
	buzzedIn=-1
	falseStart()
	timing=False
	deciding=False
	bigString.set("")
	bigLabel.config(bg=top.cget('bg'))
	setButtons()

def setButtons(): #AND LABELS TOO
	global state, buttons, h, hardware, correctButton, wrongButton, timerButton, openButton, timing, interrupted,\
		bigString, bigLabel, top, inGame, buzzlock, buzzed_in_queue, buzzable, deciding, timerButton

	correctButton.config(state=DISABLED)
	wrongButton.config(state=DISABLED)
	openButton.config(state=NORMAL)
	for i in range(0,5): 
		buttons[i].config(state=NORMAL)

	if buzzable==-1:
		for i in range(0,5):  
			if i in buzzlock and virtualized == True:
				buttons[i].config(state=NORMAL)
			elif i in buzzlock and virtualized == False:
				buttons[i].config(state=NORMAL)				

	if buzzable==1:
		for i in range(0,5):
				buttons[i].config(state=NORMAL)

	if inGame==False:
		openButton.config(state=NORMAL)
	else:
		if deciding:
			correctButton.config(state=NORMAL)
			wrongButton.config(state=NORMAL)

def startCountdown():
	global locked, timestart, state, timing, buzzable
	timestart = time()
	timing = True
	print("Starting Count")
	setButtons()

def falseStart():
	global timing, timestart, timeLeft
	timing=False
	timeLeft= TIMELIMIT
	timestart=time()
	setTimeString(str(timeLeft))
	setButtons()

def correct():
	global scores, plus, buzzedIn, h, hardware, sqscore, buzzlock, buzzed_in_queue, question, wrongLimit, firstWrong

	scores[buzzed_in_queue[0]-1][question].config(bg="#77ff77")
	setLabel(scores[buzzed_in_queue[0]-1][question], sqscore)
	wrongLimit=0
	buzzlock = []
	buzzed_in_queue = []
	changeQuestion(1)
	firstWrong=False
	reset(True)

def wrong():
	global timeLeft, locked, h, TEAMS, pins2, timestart, state, hardware, timing, timeString, minus0, bigString, bigLabel, \
		deciding, buzzedIn, buzzlock, addScores, changeQuestion, buzzed_in_queue, TIMELIMIT, interrupted, firstWrong, wrongLimit, scores, question, buzzable

	if wrongLimit == (TEAMS)-1:		#All teams gave a wrong answer, so proceed to next question
		setLabel(scores[buzzed_in_queue[0]-1][question], "0")
		firstWrong=False
		print("Next question")
		changeQuestion(1)
		addScores()
		wrongLimit=0
		buzzed_in_queue = []
		buzzlock = []
		timing=False
		timeLeft = TIMELIMIT
		reset(True)
	else:
		wrongLimit = ((wrongLimit)+1)
		setLabel(scores[buzzed_in_queue[0]-1][question], "0")
		if len (buzzed_in_queue) == 1:
			buzzed_in_queue.pop(0)			
			bigLabel.config(bg="#ffffff"), bigString.set("Reread")
			timeLeft = TIMELIMIT
			timing=False			
			setTimeString(timeLeft)
			deciding=True
			addScores()
			setButtons()           
		else: 
			buzzed_in_queue.pop(0)
			bigLabel.config(bg=teamcolors[buzzed_in_queue[0]-1]), bigString.set(buzzed_in_queue)
			timeLeft = TIMELIMIT
			startCountdown()			
			setTimeString(timeLeft)
			deciding=True
			addScores()
			setButtons()

def changeQuestion(amount):
	global question, scores, questionLabel, questionnum
	question+=amount
	setLabel(questionLabel, question+1)
	if question >= questionnum:
		for i in range(0,len(scores)):
			scores[i][question-questionnum].grid_remove()
			if i < 6:
				e = Entry(leftframe, text="", width=4, bd=1, bg=leftframe.cget('bg'), justify="center")
			else:
				e = Entry(leftframe, text="", width=4, bd=1, bg=leftframe.cget('bg'), justify="center")
			scores[i].append(e)
			e.grid(row=question, column=i%6, pady=0, padx=0)
	for i in range(0,len(scores)):
		setLabel(scores[i][question], "")
		scores[i][question].config(bg="#eeeeee")

def newGame(): #reset everything and prepare for a new game
	global locked, inGame, state, question, TEAMS, scores, buttons, TIMELIMIT, sq, buzzlock, buzzed_in_queue, sqscore, scores, buttons, questionnum, leftframe
	print(newGame)
# Destroy all widgets in the leftframe
	for widget in leftframe.winfo_children():
		widget.destroy()
# Reset the scores and buttons lists
	scores = []
	buttons = []
  # Create new widgets with the same layout as the original ones
	for i in range(0,6):
		buttons.append(Button(leftframe, text=str(i+1), bg=teamcolors[i],
			command=lambda i=i: virtualPress(i)))
		buttons[i].grid(row=200, column=i)
		scores.append([])
		for j in range(0,questionnum):
			string=StringVar()
			#string.set(str(i)+str(j))
			e = Entry(leftframe, textvariable=string, width=4, bd=1,  bg=leftframe.cget('bg'), justify="center")
			scores[i].append(e)
			e.grid(row=j, column=i, pady=0, padx=0)
	question=0
	changeQuestion(0)
	TIMELIMIT=15
	TEAMS=3
	inGame=True
	sq==1
	plus.set("+1")
	sqscore=("+1")
	sqString.set("Freshman")	
	open()
	reset(True)

def setLabel(label, text):
	string = StringVar()
	string.set(text)
	label.config(textvariable=string)

def monitorScoresThread():
	while True:
		sleep(.5)
		addScores()

def addScores():
    global scores, score1Label, score2Label, score3Label, score4Label, score4Label, score5Label, score6Label, leftframe, rightframe

    labels = [score1Label, score2Label, score3Label, score4Label, score5Label, score6Label]
    for y in range(len(scores)):
        sum = 0
        for x in range(len(scores[y])):
            try:
                if x != question:
                    colorCell(scores[y][x])
                sum += int(scores[y][x].get())
            except ValueError:
                sum += 0
        setLabel(labels[y], f"Team {y+1}: {sum}") 

def colorCell(cell):
	global leftframe
	try:
		firstchar=cell.get()[0]
		if firstchar=='-':
			cell.config(bg="#ff7777", fg="#000000")
		elif firstchar=='0':
			cell.config(bg=leftframe.cget('bg'), fg="#000000")
		elif firstchar=='+':
			cell.config(bg="#77ff77", fg="#000000")
		else:
			cell.config(bg=leftframe.cget('bg'))
	except IndexError:
		cell.config(bg=leftframe.cget('bg'))

def configure():
	print("configuring")

def dumpScores():
	global scores
	message=""
	for x in range(0,len(scores[0])):
		message+=str(x+1)+"\t"
		for y in range(0,6):
			message+=make3String(scores[y][x].get())
		message=message+"      "
		message+="\n"
	print(message)
	messagebox.showinfo("Scores Dump", message)

def make3String(string):
	if string == "":
		return "__ "
	if string == "+1":
		return "1 "
	if string == "0":
		return "0  "
	if string =="0":
		return "0 "
	if string =="+2":
		return "2 "	
	if string =="+3":
		return "3 "		
	else:
		return "__ "

top=Tk()

top.option_add('*Dialog.msg.font', 'Sans 10')

bigfont=("Sans", 24)
mediumfont=("Sans", 16)

timeString=StringVar()
setTimeString("Ready to Start Countdown!")

#Label displaying time, and associated buttons
timeFrame = Frame(top)
timeFrame.grid(row=0, column=5)
minusButton=Button(timeFrame, text="-", width=1, command=lambda timemod=-1: count(timemod), font=mediumfont)
minusButton.grid(row=0, column=1, padx=10)
timeLabel=Label(timeFrame, textvariable=timeString, width=2, justify="center", font=bigfont)
timeLabel.grid(row=0, column=2)
plusButton=Button(timeFrame, text="+", width=1, command=lambda timemod=+1: count(timemod), font=mediumfont)
plusButton.grid(row=0, column=3, padx=10)
falseStartButton=Button(timeFrame, text="New Game", width=8, command=newGame)
falseStartButton.grid(row=1, column=2)

buzzerString=StringVar()
#buzzerString.set("Buzzers Closed")
#buzzerLabel=Label(top, textvariable=buzzerString, justify="center")

correctFrame = Frame(top)
correctFrame.grid(row=2, column=5)
correctButton = Button(top, text="Right!", justify="center", command=correct, background="#47e749", font=bigfont)
correctButton.grid(row=2, column=5)

wrongFrame = Frame(top)
wrongFrame.grid(row=3, column=5)
wrongButton = Button(wrongFrame, text="Wrong", justify="center", command=wrong, bg="#ff6666", font=bigfont)
wrongButton.grid(row=0, column=1, padx=0)

openFrame = Frame(top)
openFrame.grid(row=4, column=5)
openButton = Button(openFrame, text="Open buzzers", justify="center", command=open, bg="#00ffff", width=10)
openButton.grid(row=0, column=0)

#Label dispaying question # and associated buttons
questionFrame= Frame(top)
questionFrame.grid(row=5, column=5)
Label(questionFrame, text="", justify="center").grid(row=0, column=0)
qminusButton=Button(questionFrame, text="-", width=1, command=lambda i=-1: changeQuestion(i))
qminusButton.grid(row=0, column=0, padx=10)
questionString=StringVar()
questionLabel=Label(questionFrame, font=bigfont, textvariable=questionString, justify="center")
questionLabel.grid(row=0, column=1)
qplusButton=Button(questionFrame, text="+", width=1, command=lambda i=1: changeQuestion(i))
qplusButton.grid(row=0, column=2, padx=10)

bigString=StringVar()
bigString.set("12")
bigLabel=Label(top, textvariable=bigString, bg="#cccccc", padx=10, pady=10, font=bigfont)
bigLabel.grid(row=7, sticky='swen', column=0, columnspan=100)

threading.Thread(target=timer, args=()).start()
if virtualized==False:
	threading.Thread(target=buzzercheck, args=()).start()

scores=[]
buttons=[]
questionnum=6
leftframe=Frame(top)
leftframe.grid(row=0, column=0, rowspan=15, columnspan=4, sticky='n')
for i in range(0,6):
	buttons.append(Button(leftframe, text=str(i+1), bg=teamcolors[i],
		command=lambda i=i: virtualPress(i)))
	buttons[i].grid(row=200, column=i)
	scores.append([])
	for j in range(0,questionnum):
		string=StringVar()
		#string.set(str(i)+str(j))
		e = Entry(leftframe, textvariable=string, width=4, bd=1,  bg=leftframe.cget('bg'), justify="center")
		scores[i].append(e)
		e.grid(row=j, column=i, pady=0, padx=0)

optionsframe=Frame(top)
optionsframe.grid(row=3, column=0, rowspan=15, columnspan=4, sticky='n')
dumpScoresButton=Button(optionsframe, text="Dump Scores", command=dumpScores)
dumpScoresButton.grid(row=0, column=0, pady=5, columnspan=5)

teamString=StringVar()
teamString.set(TEAMS)
teamAdd=Button(optionsframe, text="-", width=1, command=lambda teammod=-1: teamadd(teammod))
teamAdd.grid(row=1, column=1, padx=10)
teamLabel=Label(optionsframe, textvariable=teamString, width=2, justify="center")
teamLabel.grid(row=1, column=2)
teamSub=Button(optionsframe, text="+", width=1, command=lambda teammod=+1: teamadd(teammod))
teamSub.grid(row=1, column=3, padx=10)

sqString=StringVar()
sqString.set("Freshman")
teamAdd=Button(optionsframe, text="-", width=1, command=lambda sqmod=-1: sqadd(sqmod))
teamAdd.grid(row=2, column=1, padx=10)
teamLabel=Label(optionsframe, textvariable=sqString, width=7, justify="center")
teamLabel.grid(row=2, column=2)
teamSub=Button(optionsframe, text="+", width=1, command=lambda sqmod=+1: sqadd(sqmod))
teamSub.grid(row=2, column=3, padx=10)

rightframe=Frame(top)
rightframe.grid(row=0, column=7, rowspan=6, columnspan=100)
score1Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=teamcolors[0], bg="#222222")
score1Label.grid(row=1, column=6, columnspan=5, pady=5)
score2Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=teamcolors[1], bg="#222222")
score2Label.grid(row=2, column=6, columnspan=5, pady=5)
score3Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=teamcolors[2], bg="#222222")
score3Label.grid(row=3, column=6, columnspan=5, pady=5)
score4Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=teamcolors[3], bg="#222222")
score4Label.grid(row=4, column=6, columnspan=5, pady=5)
score5Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=teamcolors[4], bg="#222222")
score5Label.grid(row=5, column=6, columnspan=5, pady=5)
score6Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=teamcolors[5], bg="#222222")
score6Label.grid(row=6, column=6, columnspan=5, pady=5)

minus0=StringVar()
minus0.set("0")

plus=StringVar()
plus.set("+1")

reset(True)
buzzable=-1
setButtons()

threading.Thread(target=monitorScoresThread, args=()).start()

print("Starting loop...")

top.mainloop()
