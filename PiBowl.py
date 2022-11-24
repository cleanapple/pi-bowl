#!/usr/bin/env python3

from time import sleep, time
from tkinter import *
from tkinter import messagebox
import threading
from pynput import keyboard
from os import path, system


#Constants
virtualized=True
pins=[4, 27, 22, 23, 24, 25, 5, 6, 12, 26]
#A, B, C, D, E, F, Yes, No, Edit Score, Next Question


#STATE VARIABLES
inGame=True
timing=False			#Currently counting down the timer
deciding=False			#Right/Wrong decision
buzzable=-1			#Can be zero for no one, 1 for team 1, 2 for team 2, or -1 for all
#buzzedIn=-1			#-1 for none, 0-9 for buzzers
interrupted=False
firstWrong=False
wrongLimit=0
question=0
buzzed_in_queue = []
buzzlock = []
ycybuzzer=19
teamcolors = ["#88ff88", "#aaaaff", "#fcb900", "#eb9694", "#fff000", "#bed3f3"]


if virtualized==False:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    for i in range(0, len(pins)):
        GPIO.setup(pins[i], GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(buzzer,GPIO.OUT)

while True:
    print("Welcome to Knowledge Bowl")
    print("Selct Response Time in Seconds: Ne[X]t=5, Edit [S]core=10, [Y]es=15 ")
    with keyboard.Events() as events:
        event = events.get(1e6)
        if event.key == keyboard.KeyCode.from_char('x'):
            TIMELIMIT=5
            break
        if event.key == keyboard.KeyCode.from_char('s'):
            TIMELIMIT=10
            break
        if event.key == keyboard.KeyCode.from_char('y'):
            TIMELIMIT=15
            break
print((TIMELIMIT)," seconds selected")

print('Buzz in to select number of teams.')
while True:
    with keyboard.Events() as events:
        event = events.get(1e6)
        if event.key == keyboard.KeyCode.from_char('a'):
            TEAMS=1
            break
        if event.key == keyboard.KeyCode.from_char('b'):
            TEAMS=2
            break
        if event.key == keyboard.KeyCode.from_char('c'):
            TEAMS=3
            break
        if event.key == keyboard.KeyCode.from_char('d'):
            TEAMS=4
            break
        if event.key == keyboard.KeyCode.from_char('e'):
            TEAMS=5
            break
        if event.key == keyboard.KeyCode.from_char('f'):
            TEAMS=6
            break   

print(TEAMS, "teams selected. ")


print("Press Yes to continue or No to edit selections.")
while True:
    with keyboard.Events() as events:
        event = events.get(1e6)
        if event.key == keyboard.KeyCode.from_char('n'):
            break
        if event.key == keyboard.KeyCode.from_char('y'):
            break



locked = True
#timestart = 0

#State is used to represent where the buzzer state is. -3 means no game is in progress, nor the buzzers open.
#-2 means closed to all,
#-1 means open for a buzz-in,
#and 0-9 means closed to all as a result of buzzer[i] pressed.
#state=-3


print("Starting Game")

inGame=True
buzzable=-1
interrupted=False
firstWrong=False
wrongLimit=0
question=0
buzzed_in_queue = []
buzzlock = []

def countmore():
    global TIMELIMIT, timeLeft
    TIMELIMIT=TIMELIMIT+1
    setTimeString(TIMELIMIT)

def countless():
    global TIMELIMIT, timeLeft
    TIMELIMIT=TIMELIMIT-1
    setTimeString(TIMELIMIT)   

def teamadd():
   global TEAMS, teamString
   TEAMS = TEAMS+1
   teamString.set(TEAMS)

    

def teamsub():
    global TEAMS, teamString
    TEAMS=TEAMS-1
    teamString.set(TEAMS)

    		

def espeak(string):
	threading.Thread(target=system, args=("espeak "+string, )).start()

def timer():
	global timestart, timeString, TIMELIMIT, timeLeft, locked, \
		   inGame, timing, buzzable, timeLabel, question
	while True:
		sleep(.01)
		if (timing):
			delta = time()-timestart
			if delta > timeLeft:
				buzzable=-1
				setButtons()
				setTimeString("00")
				GPIO.output(buzzer,GPIO.HIGH)
				sleep(0.5)
				GPIO.output(buzzer,GPIO.LOW)
				sleep(30)
				wrong()
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
		#print "successfully set to: "+str(string))
	except AttributeError:
		print("failed to set to: "+string)
		timeString=StringVar(timeLabel)
		timeLabel.config(textvariable=timeString)
		setTimeString(string)


def buzzercheck():
	global locked, pins, buzzable

	while True:
		if buzzable!=0:
			sleep(.02)
			for i in range(0, len(pins)):
				if (GPIO.input(pins[i])==False) and i not in buzzlock:
					virtualPress(i)
		else:
			sleep(.1)


def virtualPress(i):
	global locked, soundLocation, buttons, timeLeft, timeLabel, buzzedIn, buzzed_in_queue, deciding, \
		state, bigLabel, bigString, buzzlock, teamcolors, inGame, timing, buzzable, interrupted
	print("buzzable=",buzzable)
	if buzzable==-1 or buzzable==int(i/6)+1:
		if inGame:
			buzzable=-1
			deciding=True
			timeLeft=int(timeString.get())
		buzzable=-1
		humanBuzzerNum=i+1
		if humanBuzzerNum>7:
			humanBuzzerNum-=7
		interrupted=not timing
		timing=False
		buzzerString.set("Locked: Buzzer "+str(humanBuzzerNum))
		threading.Thread(target=flashLock, args=(i,)).start()

		if i not in buzzlock:
			if i == 0 and i not in buzzlock:
				buzzed_in_queue.append(1)
				buzzlock.append(i)
			if i == 1 and i not in buzzlock:
				buzzed_in_queue.append(2)
				buzzlock.append(i)
			if i == 2 and i not in buzzlock:
				buzzed_in_queue.append(3)
				buzzlock.append(i)
			if i == 3 and i not in buzzlock:
				buzzed_in_queue.append(4)
				buzzlock.append(i)
			if i == 4 and i not in buzzlock:
				buzzed_in_queue.append(5)
				buzzlock.append(i)
			if i == 5 and i not in buzzlock:
				buzzed_in_queue.append(6)
				buzzlock.append(i)
		setButtons()
		bigLabel.config(bg=teamcolors[buzzed_in_queue[0]-1])
		bigString.set(buzzed_in_queue)
		threading.Thread(target=playsound, args=(i,)).start()
		if len(buzzed_in_queue) > 0:
			startCountdown()

		if i == 6:
			correct()
		if i == 7:
			wrong()
		if i == 8:
			changeQuestion(+1)
			buzzed_in_queue = []
			buzzlock=[]
		if i == 9:
			changeQuestion(-1)
			buzzed_in_queue = []
			buzzlock = []            	


def flashLock(i):
	global locked, buttons, buzzedIn, buzzed_in_queue
	for i in range (0,6):
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
		sleep(0.1)
		GPIO.output(buzzer,GPIO.LOW)
	else:
		GPIO.output(buzzer,GPIO.LOW)

#reset for the next question
def reset(openall):
	global state, locked, timestart, timeLeft, TIMELIMIT, deciding, buzzedIn, buzzed_in_queue, timing, timeLeft, \
		correctButton, wrongButton, timeString, bigString, bigLabel, top, buzzable, firstWrong
	if openall:
		buzzable=-1
		timeLeft = TIMELIMIT
	buzzerString.set("Ready to Start Countdown!")
	bigString.set("")
	bigLabel.config(bg=top.cget('bg'))
	setTimeString(str(timeLeft))
	timing=False
	deciding=False
	#if state!=-3:
	#	state=-2
	setButtons()

def open():
	global inGame, locked, timeString, state, buzzlock, buzzable, buzzedIn, buzzed_in_queue, deciding
	#inGame=False

	#If ingame, the buzzin was either a challenge or a mistake.
	if not inGame:
		falseStart()
	buzzed_in_queue=[]
	buzzlock =[]
	buzzable=-1
	buzzedIn=-1
	falseStart()
	deciding=False
	bigString.set("")
	bigLabel.config(bg=top.cget('bg'))
	setButtons()


def setButtons(): #AND LABELS TOO
	global state, buttons, correctButton, wrongButton, timerButton, openButton, timing, interrupted,\
		bigString, bigLabel, top, inGame, buzzlock, buzzed_in_queue, buzzable, deciding, newGameButton, timerButton

	#False til proven true
	newGameButton.config(state=DISABLED)
#	timerButton.config(state=DISABLED)
	correctButton.config(state=DISABLED)
	wrongButton.config(state=DISABLED)
#	wrong2Button.config(state=DISABLED)
	openButton.config(state=NORMAL)
	for i in range(0,6): #MCCALLUM DISABLED LAST 4 INPUTS. NEEDED FOR SCOREKEEPER BUTTONS
		buttons[i].config(state=NORMAL)

	if buzzable==-1:
		#print(2)
		for i in range(0,6):  #MCCALLUM disabled the last four inputs
			if i in buzzlock and virtualized == True:
				buttons[i].config(state=DISABLED)
			elif i in buzzlock and virtualized == False:
				buttons[i].config(state=DISABLED)				

	if buzzable==1:
		for i in range(0,6):
				buttons[i].config(state=NORMAL)

#MCCALLUM NOT SURE WHAT TO DO HERE TO PREVENT ERRORS WITH PINS 6-9
#	if buzzable==2: 
#		for i in range(6,10):
#				buttons[i].config(state=NORMAL)

	if inGame==False:
		newGameButton.config(state=NORMAL)
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
	global scores, buzzedIn, buzzlock, buzzed_in_queue, plus1, question, wrongLimit, firstWrong

	scores[buzzed_in_queue[0]-1][question].config(bg="#77ff77")
	setLabel(scores[buzzed_in_queue[0]-1][question], "+1")
	wrongLimit=0
	buzzlock = []
	buzzed_in_queue = []
	changeQuestion(1)

	firstWrong=False
	reset(True)

def wrong_no_interrupt():
	global interrupted, bigLabel, bigString, firstWrong
	interrupted=False

	bigString.set("")
	bigLabel.config(bg=top.cget('bg'))

	wrong()

def wrong():
	global timeLeft, locked, timestart, state, timing, timeString, minus0, \
		deciding, buzzedIn, buzzlock, buzzed_in_queue, TIMELIMIT, interrupted, firstWrong, wrongLimit, scores, question, buzzable

	if wrongLimit == (TEAMS)-1:		#This is the second wrong answer, so proceed to next question
		setLabel(scores[buzzed_in_queue[0]-1][question], "0")
		firstWrong=False
		print("Next question")
		changeQuestion(1)
		addScores()
		wrongLimit=0
		buzzed_in_queue = []
		buzzlock = []
		timeLeft = TIMELIMIT
		reset(True)
	else:
		wrongLimit = ((wrongLimit)+1)
		setLabel(scores[buzzed_in_queue[0]-1][question], "0")
		if len(buzzed_in_queue) > 0:
		    buzzed_in_queue.pop(0)			
		timeLeft = TIMELIMIT
		bigLabel.config(bg=teamcolors[buzzed_in_queue[0]-1])			
		bigString.set(buzzed_in_queue)			
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
			if i < 7:
				e = Entry(leftframe, text="", width=4, bd=1, bg=rightframe.cget('bg'), justify="center")
			else:
				e = Entry(rightframe, text="", width=4, bd=1, bg=rightframe.cget('bg'), justify="center")
			scores[i].append(e)
			e.grid(row=question, column=i%6, pady=0, padx=0)
	for i in range(0,len(scores)):
		setLabel(scores[i][question], "")
		scores[i][question].config(bg="#eeeeee")

def newGame():
	global locked, inGame, state, question
	print(newGame)
	question=0
	changeQuestion(0)
	inGame=True
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
	try:
		sum=0
		for y in range(0,1):
			for x in range(0,len(scores[y])):
				try:
					if x != question:
						colorCell(scores[y][x])
					sum+= int(scores[y][x].get())
						#print(int(scores[y][x].get()))
				except ValueError:
					sum+=0

		setLabel(score1Label, "Team 1: "+str(sum))
	except IndexError:
		print("IndexError")
	try:
		sum=0
		for y in range(1,2):
			for x in range(0,len(scores[y])):
				try:
					if x != question:
						colorCell(scores[y][x])
					sum+= int(scores[y][x].get())
						#print(int(scores[y][x].get()))
				except ValueError:
					sum+=0
		setLabel(score2Label, "Team 2: "+str(sum))
	except IndexError:
		print("IndexError")              
	try:
		sum=0
		for y in range(2,3):
			for x in range(0,len(scores[y])):
				try:
					if x != question:
						colorCell(scores[y][x])
					sum+= int(scores[y][x].get())
						#print(int(scores[y][x].get()))
				except ValueError:
					sum+=0

		setLabel(score3Label, "Team 3: "+str(sum))
	except IndexError:    
 		print("IndexError")  
	try:
		sum=0
		for y in range(3,4):
			for x in range(0,len(scores[y])):
				try:
					if x != question:
						colorCell(scores[y][x])
					sum+= int(scores[y][x].get())
						#print(int(scores[y][x].get()))
				except ValueError:
					sum+=0
		setLabel(score4Label, "Team 4: "+str(sum))
	except IndexError:
		print("IndexError")              
	try:
		sum=0
		for y in range(4,5):
			for x in range(0,len(scores[y])):
				try:
					if x != question:
						colorCell(scores[y][x])
					sum+= int(scores[y][x].get())
						#print(int(scores[y][x].get()))
				except ValueError:
					sum+=0

		setLabel(score5Label, "Team 5: "+str(sum))
	except IndexError:    
 		print("IndexError")  
	try:
		sum=0
		for y in range(5,6):
			for x in range(0,len(scores[y])):
				try:
					if x != question:
						colorCell(scores[y][x])
					sum+= int(scores[y][x].get())
						#print(int(scores[y][x].get()))
				except ValueError:
					sum+=0

		setLabel(score6Label, "Team 6: "+str(sum))
	except IndexError:    
 		print("IndexError")           
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


#def time_plus():
#	global timeLeft
#	timeLeft = timeLeft+5
#	setTimeString(str(int(timeLeft)))

#def time_minus():
#	global timeLeft
#	timeLeft = timeLeft-5
#	setTimeString(str(int(timeLeft)))

def configure():
	print("configuring")


#def addIndividualScores():
#	print("Nothing here yet")


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
#Label(timeFrame, text="Time:", justify="right", font=mediumfont).grid(row=0, column=0, sticky='e')
minusButton=Button(timeFrame, text="-", width=1, command=countless, font=mediumfont)
minusButton.grid(row=0, column=1, padx=10)
timeLabel=Label(timeFrame, textvariable=timeString, width=2, justify="center", font=bigfont)
timeLabel.grid(row=0, column=2)
plusButton=Button(timeFrame, text="+", width=1, command=countmore, font=mediumfont)
plusButton.grid(row=0, column=3, padx=10)
falseStartButton=Button(timeFrame, text="Reset", width=6, command=falseStart)
falseStartButton.grid(row=1, column=2)



buzzerString=StringVar()
buzzerString.set("Buzzers Closed")
buzzerLabel=Label(top, textvariable=buzzerString, justify="center")
#buzzerLabel.grid(row=2, column=2)
#buzzerLabel.pack()

newGameButton = Button(top, text="START", command=newGame, bg="#00ffff", width=15)
newGameButton.grid(row=1, column=5)
#newGameButton.pack()buttons[i].grid(row=20, column=i)

#timerButton = Button(top, text="Start Countdown", command=startCountdown, state=DISABLED)
#timerButton.grid(row=2, column=5)

correctButton = Button(top, text="Right!", command=correct, background="#99ca9f", font=bigfont)
correctButton.grid(row=2, column=5)

wrongFrame = Frame(top)
wrongFrame.grid(row=3, column=5)
wrongButton = Button(wrongFrame, text="Wrong", justify="center", command=wrong, bg="#ff6666", font=bigfont)
wrongButton.grid(row=0, column=1, padx=0)
#wrong2Button = Button(wrongFrame, width=14, text="(but not interrupted)", command=wrong_no_interrupt, bg="#ff6666")
#wrong2Button.grid(row=1, column=0, padx=0)


openButton = Button(wrongFrame, text="Open buzzers", command=open, bg="#00ffff", width=10)
openButton.grid(row=2, column=1)
#openButton.pack()


#Label dispaying question # and associated buttons
questionFrame= Frame(top)
questionFrame.grid(row=7, column=5)
Label(questionFrame, text="", justify="center").grid(row=0, column=0)
qminusButton=Button(wrongFrame, text="-", width=1, command=lambda i=-1: changeQuestion(i))
qminusButton.grid(row=3, column=0, padx=10)
questionString=StringVar()
questionLabel=Label(wrongFrame, font=bigfont, textvariable=questionString, justify="center")
questionLabel.grid(row=3, column=1)
qplusButton=Button(wrongFrame, text="+", width=1, command=lambda i=1: changeQuestion(i))
qplusButton.grid(row=3, column=2, padx=10)


bigString=StringVar()
bigString.set("12")
bigLabel=Label(top, textvariable=bigString, bg="#cccccc", padx=10, pady=10, font=bigfont)
bigLabel.grid(row=4, sticky='nesw', column=0, columnspan=5)


threading.Thread(target=timer, args=()).start()
if virtualized==False:
	threading.Thread(target=buzzercheck, args=()).start()

scores=[]
buttons=[]
questionnum=6
leftframe=Frame(top)
leftframe.grid(row=0, column=0, rowspan=15, columnspan=4, sticky='n')
#leftframe.grid(row=0, column=0)
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
		#print("created",i,j)


dumpScoresButton=Button(leftframe, text="Dump Scores", command=dumpScores)
dumpScoresButton.grid(row=210, column=0, pady=5, columnspan=5)

teamString=StringVar()
teamString.set(TEAMS)
teamAdd=Button(leftframe, text="-", width=1, command=teamsub)
teamAdd.grid(row=211, column=1, padx=10)
teamLabel=Label(leftframe, textvariable=teamString, width=2, justify="center")
teamLabel.grid(row=211, column=2)
teamSub=Button(leftframe, text="+", width=1, command=teamadd)
teamSub.grid(row=211, column=3, padx=10)

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



#scoreFrame

#not used rightside options
#t = IntVar()
#t.set(1)
#i = IntVar()
#i.set(1)

#configFrame=Frame(top)#, bg="#eeeeee")
#configFrame.grid(row=0, column=100, padx=50)
#timeCheck=Checkbutton(configFrame, text="Display the running timer?", command=configure, variable=t)
#timeCheck.grid(row=0, column=0, sticky='w')
#indivCheck=Checkbutton(configFrame, text="Show individual scores?", command=configure, variable=i)
#indivCheck.grid(row=1, column=0, sticky='w')


minus0=StringVar()
minus0.set("0")

plus1=StringVar()
plus1.set("+1")

reset(True)
buzzable=-1
setButtons()

threading.Thread(target=monitorScoresThread, args=()).start()


print("Starting loop...")


top.mainloop()
