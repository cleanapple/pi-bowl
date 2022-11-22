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

#sound1Location="/home/pi/sound1.wav"
#sound2Location="/home/pi/sound2.wav"
soundpath1=path.abspath("$HOME/Python/frog.wav")
soundpath2=path.abspath("$HOME/Python/peacock.wav")
timepath=path.abspath("time.wav")
team1color="#88ff88"
team2color="#aaaaff"
team3color="#fcb900"
team4color="#eb9694"
team5color="#fff000"
team6color="#bed3f3"



#STATE VARIABLES
inGame=False
timing=False			#Currently counting down the timer
deciding=False			#Right/Wrong decision
buzzable=0			#Can be zero for no one, 1 for team 1, 2 for team 2, or -1 for all
buzzedIn=-1			#-1 for none, 0-9 for buzzers
interrupted=False
firstWrong=False
wrongLimit=0
question=0
buzzed_in_queue = []

if virtualized==False:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    for i in range(0, len(pins)):
        GPIO.setup(pins[i], GPIO.IN, GPIO.PUD_UP)

while True:
    print("Welcome to Knowledge Bowl")
    print("Selct Response Time in Seconds: Ne[X]t=5, Edit [S]core=10, [Y]es=15 ")
    with keyboard.Events() as events:
        # Block for as much as possible
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
# input number of teams
print((TIMELIMIT)," seconds selected")

print('Buzz in to select number of teams.')
while True:
    with keyboard.Events() as events:
        # Block for as much as possible
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
        # Block for as much as possible
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


print("test")



def espeak(string):
	threading.Thread(target=system, args=("espeak "+string, )).start()

def timer():
	global timestart, timeString, TIMELIMIT, timeLeft, locked, \
		   inGame, timing, buzzable, timeLabel, question, \
		   timepath
	while True:
		sleep(.01)
		if (timing):
			delta = time()-timestart
			if delta > timeLeft:
				#os.system("espeak time.")
				threading.Thread(target=playsound, args=(timepath,)).start()
				#espeak("time.")
				buzzable=0
				setButtons()
				setTimeString("00")
				changeQuestion(1)
				sleep(3)
				reset(True)
			elif delta%1<.1:
				string=str(int(timeLeft+1-delta))
				#print("before")
				try:
					setTimeString(string) #TODO Why does this throw an error?
				except AttributeError:
					print("failed")
				#timeString.
				#print("commented")
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
				if (GPIO.input(pins[i])==False):
					virtualPress(i)
		else:
			sleep(.1)


def virtualPress(i):
	global locked, soundLocation, buttons, timeLeft, timeLabel, buzzedIn, buzzed_in_queue, buzzed_in_queue, deciding, \
		state, bigLabel, bigString, team1color, team2color, team3color, team4color, team5color, team6color, inGame, timing, buzzable, interrupted
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
		threading.Thread(target=playsound, args=(i,)).start()
				#state=i
		#print("state"+str(i))
		buzzedIn=i
		setButtons()
		if i in range(0,1):
			buzzed_in_queue.append(1)			
			bigLabel.config(bg=team1color)
			print(buzzed_in_queue)
		if i in range(1,2):
			buzzed_in_queue.append(2)			
			bigLabel.config(bg=team2color)
			print(buzzed_in_queue)
		if i in range(2,3):
			buzzed_in_queue.append(3)			
			bigLabel.config(bg=team3color)
			print(buzzed_in_queue)            
		if i in range(3,4):
			buzzed_in_queue.append(4)			
			bigLabel.config(bg=team4color)
			print(buzzed_in_queue)            
		if i in range(4,5):
			buzzed_in_queue.append(5)			
			bigLabel.config(bg=team5color)
			print(buzzed_in_queue)		
		if i in range(5,6):
			buzzed_in_queue.append(6)			
			bigLabel.config(bg=team6color)
			print(buzzed_in_queue)
		bigString.set(buzzed_in_queue)	
            
def flashLock(i):
	global locked, buttons, buzzedIn, buzzed_in_queue
	colorb = buttons[i].cget('bg')
	flashb = buttons[i].cget('activebackground')
	while i in buzzed_in_queue:
		buttons[i].config(bg=flashb)
		sleep(.4)
		buttons[i].config(bg=colorb)
		sleep(.4)

def playsound(i):
	if i < 100:
		system("aplay recognize"+str(i)+".wav")
	#if i==1:
	#	system("aplay "+soundpath1)
	#elif i==2:
	#	system("aplay "+soundpath2)
	else:
		system("aplay "+str(i))

#reset for the next question
def reset(openall):
	global state, locked, timestart, timeLeft, TIMELIMIT, deciding, buzzedIn, buzzed_in_queue, timing, timeLeft, \
		correctButton, wrongButton, timeString, bigString, bigLabel, top, buzzable, firstWrong
   # global locked
	#global timestart
	if openall:
		buzzable=-1
		timeLeft = TIMELIMIT
	buzzerString.set("Ready to Start Countdown!")
	bigString.set("")
	bigLabel.config(bg=top.cget('bg'))
	setTimeString(str(timeLeft))
	timing=False
	buzzed_in_queue = []
	deciding=False
	#if state!=-3:
	#	state=-2
	setButtons()

def open():
	global inGame, locked, timeString, state, buzzable, buzzedIn, buzzed_in_queue, deciding
	#inGame=False

	#If ingame, the buzzin was either a challenge or a mistake.
	if not inGame:
		setTimeString("00")
	#timeString.zfill
	#print("open")
	buzzable=-1
#	buzzedIn=-1
	deciding=False
	bigString.set("")
	bigLabel.config(bg=top.cget('bg'))
	setButtons()


def setButtons(): #AND LABELS TOO
	global state, buttons, correctButton, wrongButton, timerButton, openButton, timing, interrupted,\
		bigString, bigLabel, top, inGame, buzzable, deciding, newGameButton, timerButton

	#False til proven true
	newGameButton.config(state=DISABLED)
	timerButton.config(state=DISABLED)
	correctButton.config(state=DISABLED)
	wrongButton.config(state=DISABLED)
	wrong2Button.config(state=DISABLED)
	openButton.config(state=NORMAL)
	for i in range(0,6): #MCCALLUM DISABLED LAST 4 INPUTS. NEEDED FOR SCOREKEEPER BUTTONS
		buttons[i].config(state=DISABLED)

	if buzzable==-1:
		#print(2)
		for i in range(0,6):  #MCCALLUM disabled the last four inputs
			buttons[i].config(state=NORMAL)

	if buzzable==1:
		for i in range(0,6):
				buttons[i].config(state=NORMAL)
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

			if interrupted:
			 wrong2Button.config(state=NORMAL)
		elif timing==False:
			timerButton.config(state=NORMAL)





def startCountdown():
	global locked, timestart, state, timing, buzzable
	timestart = time()
	#locked = False
	timing = True
	#inGame=True
	#buzzable=-1

	print("Starting Count")
	setButtons()

def falseStart():
	global timing, timestart, timeLeft
	timing=False
	timeLeft= 10
	timestart=time()
	setTimeString(str(timeLeft))
	setButtons()

def correct():
	global scores, buzzedIn, buzzed_in_queue, plus10, question, wrongLimit, firstWrong

	scores[buzzed_in_queue[0]-1][question].config(bg="#77ff77")
	setLabel(scores[buzzed_in_queue[0]-1][question], "+1")
	wrongLimit=0
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
	global timeLeft, locked, timestart, state, timing, timeString, minus5, \
		deciding, buzzedIn, buzzed_in_queue, TIMELIMIT, interrupted, firstWrong, wrongLimit, scores, question, buzzable
    

	
	if wrongLimit == (TEAMS)-1:		#This is the second wrong answer, so proceed to next question
		setLabel(scores[buzzed_in_queue[0]-1][question], "0")
		firstWrong=False
		print("Next question")
		changeQuestion(1)
		addScores()
		wrongLimit=0
		buzzed_in_queue = []
		reset(True)
	else:
		wrongLimit = ((wrongLimit)+1)
		

#		buzzable=int(buzzedIn/6)+1
#		buzzable=-1
#		if buzzable == 1:
#			buzzable=-1 #MCCALLUM - This used to be two. There are only two lock states in the game. We need more.
#		else:
#			buzzable=-1

#		print(buzzable)
		if interrupted:
			scores[buzzed_in_queue[0]-1][question].config(bg="#ff7777")
			scores[buzzed_in_queue[0]-1][question].config(textvariable=minus5)
			reset(False)
			buzzed_in_queue.pop(0)
			print(buzzed_in_queue)                       
			#print("Resetting...")
		else:
			setLabel(scores[buzzed_in_queue[0]-1][question], "0")
			startCountdown()			
			print("Resuming Countdown...")
			timeLeft = timeLeft+5
		setTimeString(timeLeft)
#		buzzedIn=-1
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
			if i < 5:
				e = Entry(leftframe, text="", width=4, bd=1, bg=rightframe.cget('bg'), justify="center")
			else:
				e = Entry(rightframe, text="", width=4, bd=1, bg=rightframe.cget('bg'), justify="center")
			scores[i].append(e)
			e.grid(row=question, column=i%5, pady=0, padx=0)
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
	global scores, score1Label, score2Label, score3Label, score4Label, score4Label, score5Label, score6Label,leftFrame, rightFrame
	#Left side scores MCCALLUM - I need to find how to display more score boxes in frames.
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

		setLabel(score1Label, "Team A: "+str(sum))
	except IndexError:
		print("IndexError")
	#Right side scores
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
		setLabel(score2Label, "Team B: "+str(sum))
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

		setLabel(score3Label, "Team C: "+str(sum))
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
		setLabel(score4Label, "Team D: "+str(sum))
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

		setLabel(score5Label, "Team E: "+str(sum))
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

		setLabel(score6Label, "Team F: "+str(sum))
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


def time_plus():
	global timeLeft
	timeLeft = timeLeft+5
	setTimeString(str(int(timeLeft)))

def time_minus():
	global timeLeft
	timeLeft = timeLeft-5
	setTimeString(str(int(timeLeft)))

def configure():
	print("configuring")


def addIndividualScores():
	print("Nothing here yet")


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
Label(timeFrame, text="Time:", justify="right", font=mediumfont).grid(row=0, column=0, sticky='e')
minusButton=Button(timeFrame, text="-", width=1, command=time_minus)
minusButton.grid(row=0, column=1, padx=10)
timeLabel=Label(timeFrame, textvariable=timeString, width=2, justify="center", font=mediumfont)
timeLabel.grid(row=0, column=2)
plusButton=Button(timeFrame, text="+", width=1, command=time_plus)
plusButton.grid(row=0, column=3, padx=10)
falseStartButton=Button(timeFrame, text="Reset", width=2, command=falseStart)
falseStartButton.grid(row=0, column=4)
#timeLabel.pack()


buzzerString=StringVar()
buzzerString.set("Buzzers Closed")
buzzerLabel=Label(top, textvariable=buzzerString, justify="center")
#buzzerLabel.grid(row=1, column=5)
#buzzerLabel.pack()

newGameButton = Button(top, text="START NEW GAME", command=newGame, bg="#00ffff", width=30)
newGameButton.grid(row=2, column=5)
#newGameButton.pack()buttons[i].grid(row=20, column=i)

timerButton = Button(top, text="Start Countdown", command=startCountdown, state=DISABLED)
timerButton.grid(row=3, column=5)
#timerButton.pack()

correctButton = Button(top, text="Correct!", command=correct, background="#22ff22",)
correctButton.grid(row=4, column=5)
#correctButton.pack()

wrongFrame = Frame(top)
wrongFrame.grid(row=5, column=5)
wrongButton = Button(wrongFrame, text="Wrong", command=wrong, bg="#ff6666")
wrongButton.grid(row=0, column=0, padx=0)
wrong2Button = Button(wrongFrame, width=14, text="(but not interrupted)", command=wrong_no_interrupt, bg="#ff6666")
wrong2Button.grid(row=0, column=1, padx=0)
#wrongButton.pack()

#Label(top).pack()

openButton = Button(top, text="Open buzzer, Ignore buzz-in\n(e.g. buzzer checks, challenges)", command=open, bg="#00ffff", width=25)
openButton.grid(row=6, column=5)
#openButton.pack()


#Label dispaying question # and associated buttons
questionFrame= Frame(top)
questionFrame.grid(row=7, column=5)
Label(questionFrame, text="Question:", justify="center").grid(row=0, column=0)
qminusButton=Button(questionFrame, text="-", width=1, command=lambda i=-1: changeQuestion(i))
qminusButton.grid(row=0, column=1, padx=20)
questionString=StringVar()
questionLabel=Label(questionFrame, textvariable=questionString, justify="center")
questionLabel.grid(row=0, column=2)
qplusButton=Button(questionFrame, text="+", width=1, command=lambda i=1: changeQuestion(i))
qplusButton.grid(row=0, column=3, padx=20)


bigString=StringVar()
bigString.set("12")
bigLabel=Label(top, textvariable=bigString, bg="#cccccc", padx=10, pady=10, font=bigfont)
bigLabel.grid(row=9, sticky='nesw', column=0, columnspan=11)
#bigLabel.pack(side='bottom', fill=BOTH)


threading.Thread(target=timer, args=()).start()
if virtualized==False:
	threading.Thread(target=buzzercheck, args=()).start()

scores=[]
buttons=[]
questionnum=15
leftframe=Frame(top)
leftframe.grid(row=0, column=0, rowspan=15, columnspan=5, sticky='n')
#leftframe.grid(row=0, column=0)
for i in range(0,1):
	buttons.append(Button(leftframe, text=str(i+1), bg=team1color,
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
for i in range(1,2):
	buttons.append(Button(leftframe, text=str(i+1), bg=team2color,
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
for i in range(2,3):
	buttons.append(Button(leftframe, text=str(i+1), bg=team3color,
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
for i in range(3,4):
	buttons.append(Button(leftframe, text=str(i+1), bg=team4color,
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
for i in range(4,5):
	buttons.append(Button(leftframe, text=str(i+1), bg=team5color,
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
for i in range(5,6):
	buttons.append(Button(leftframe, text=str(i+1), bg=team6color,
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
#	buttons[i].pack(side='left')        
#	buttons[i].pack(side='left')
dumpScoresButton=Button(leftframe, text="Dump Scores", command=dumpScores)
dumpScoresButton.grid(row=210, column=0, pady=5, columnspan=5)

rightframe=Frame(top)
rightframe.grid(row=0, column=7, rowspan=6, columnspan=100)
score1Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=team1color, bg="#222222")
score1Label.grid(row=1, column=6, columnspan=5, pady=5)
#score1Label.pack(side="left")
score2Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=team2color, bg="#222222")
score2Label.grid(row=2, column=6, columnspan=5, pady=5)
#score2Label.pack(side="right")
score3Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=team3color, bg="#222222")
score3Label.grid(row=3, column=6, columnspan=5, pady=5)
#score3Label.pack(side="right")
score4Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=team4color, bg="#222222")
score4Label.grid(row=4, column=6, columnspan=5, pady=5)
#score4Label.pack(side="left")
score5Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=team5color, bg="#222222")
score5Label.grid(row=5, column=6, columnspan=5, pady=5)
#score5Label.pack(side="right")
score6Label=Label(rightframe, justify="right", padx=5, font=bigfont, fg=team6color, bg="#222222")
score6Label.grid(row=6, column=6, columnspan=5, pady=5)
#score6Label.pack(side="right")

#for i in range(6,10):
#	buttons.append(Button(rightframe, text=str(i-4), bg=team2color,
#		command=lambda i=i: virtualPress(i)))
#	buttons[i].grid(row=200, column=i-5)
#	scores.append([])
#	for j in range(0,questionnum):
#		string=StringVar()
		#string.set(str(i)+str(j))
#		e = Entry(rightframe, textvariable=string, width=4, bd=1, bg=rightframe.cget('bg'), justify="center")
#		scores[i].append(e)
#		e.grid(row=j, column=i-5, pady=0, padx=0)
		#print("created",i,j)
    
        #for i in [9, 8, 7, 6, 5]:  #NEED TO ADD IN OPPOSITE ORDER TO APPEAR CORRECTLY



#	print("not")
#	buttons[i].pack(side='right')


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

#dumpScoresButton=Button(rightframe, text="Dump Scores", command=dumpScores) #MCCALLUM Moved to Left side 
#dumpScoresButton.grid(row=202, column=0, pady=0, columnspan=5) #MCCALLUM Moved to left side

minus5=StringVar()
minus5.set("0")

plus10=StringVar()
plus10.set("+1")

reset(True)
buzzable=0
setButtons()

threading.Thread(target=monitorScoresThread, args=()).start()


print("Starting loop...")


top.mainloop()
