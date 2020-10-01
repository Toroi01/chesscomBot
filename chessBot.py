#It needs 1920 * 1080 resolution
#Left half of the screen has to be the game in chess.com
#Activate always promote a queen
#Chess.com in english
#cordenates = NONE in chess.com
#TODO: Implement DECLIN a draw / AVOID repetitions
#TODO: Implement a method where each lose increments 0.1 unit in the time engine
#starting in 0 and so on, X wins in a row decrements in 0.05
#TODO:Implement blitz Mode
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import chess
import chess.uci

import pyautogui
import time

import keyboard 

import random


def inGame(chat):
	#Analyze the chat backwards and if we find a NEW GAME before a GAME OVER we are in game 
	#We find the last NEW GAME and the last GAME OVER positions

	#Find the NEW GAME position
	ngpos = chat.rfind("NEW GAME")
	#Find the GAME OVER position
	gopos = chat.rfind("GAME OVER")
	#Find the GAME ABORTED position
	ga = chat.rfind("GAME ABORTED")

	#If not exist NEW GAME
	if ngpos == -1:
		return False
	else:
		if gopos>ngpos:
			return False
		if ga>ngpos:
			return False
		if gopos<ngpos:
			return True

def parseMovesToBoard():
	#Take the moves
	dirtyMoves = driver.find_element_by_class_name('vertical-move-list-component')
	moves = dirtyMoves.text
	#If the game just starts
	if moves == '':
		return chess.Board()
	moves = moves.split("\n")
	finalMoves = []
	#If the move starts with a letter then is a real move
	for m in moves:
		if(m[0].isalpha()):
			finalMoves.append(m)	

	#Create a new board
	board = chess.Board()
	#Parse moves in the board
	for m in finalMoves:
		board.push_san(m)
	return board

def makeAMove(move):
	
	letters = ['a','b','c','d','e','f','g','h']
	#Generate the cordenates of each square
	origin = (1,815)
	sqsize = 64
	keys = []
	cords = []
	
	#If the color is white
	if(color):
		for l in letters:
			for x in range (1,9):		     
			     keys.append(l+str(x))

		for x in range(0,8):
			for y in range(0,8):
				cords.append((origin[0]+x*(sqsize)+sqsize/2,origin[1]-y*sqsize-sqsize/2))

	#If the color is white
	else:
		for l in letters[::-1]:
			for x in range (8,0,-1):		     
			     keys.append(l+str(x))

		for x in range(0,8):
			for y in range(0,8):
				cords.append((origin[0]+x*(sqsize)+sqsize/2,origin[1]-y*sqsize-sqsize/2))

	dictCord = dict( zip( keys, cords))

	pyautogui.click(dictCord[str(move[0:2])])
	pyautogui.click(dictCord[str(move[2:4])])
	
def whichColor(chat):
	#We obtain which color we are
	vspos = chat.rfind("vs")
	isBlack = chat.find(usr, vspos, vspos+len(usr)+5)
	if isBlack == -1:
		return True
	else: 
		return False

def pressNewGame(mode):
	if mode == "normal":
		#For normal games
		newGameButton = driver.find_elements_by_xpath("//button[contains(text(),'New')]")
	if mode == "arena":
		#For arena
		newGameButton = driver.find_elements_by_xpath("//*[contains(text(), 'Next')]")
	if mode == "rematch":
		newGameButton = driver.find_elements_by_xpath("//*[contains(text(), 'Rematch')]")
	newGameButton[0].click()
	#time.sleep(3)

def waitingGame():
	waiting = driver.find_elements_by_xpath("//*[contains(text(), 'Searching')]")
	if waiting == []:
		return False
	else:
		return True

def bulletMoves():
	#Function to play 1 min chess
	print("bulletMode")

	clock = driver.find_element_by_id('main-clock-bottom')
	opClock = driver.find_element_by_id('main-clock-top')
	mySec = float(clock.text[clock.text.find(':')+1:])
	opSec = float(opClock.text[opClock.text.find(':')+1:])
	myMin = float(clock.text[:clock.text.find(':')])
	opMin = float(opClock.text[:opClock.text.find(':')])

	#If we are in the last seconds of the game
	if (mySec<=20):
		return engine.go(movetime=50)
	#If we have a lot of time advantage we will wait
	if (myMin>opMin or (myMin==opMin and (mySec-opSec)>2)):
		time.sleep(1)

	luck = random.random()
	if(luck>0.7):
		time.sleep(0.750)
	if(luck>0.95):
		return engine.go(movetime=25)#Excelent move	
	if(luck>0.90):
		return engine.go(movetime=20)#Good move
	if(luck<0.90):
		return engine.go(movetime=15)#Normal move

def bulletSimple():
	randommovetime = 3+random.random()
	bestMove = engine.go(movetime=randommovetime)
	return bestMove

def godMode():
	bestMove = engine.go(movetime=500)
	return bestMove

def bulletVSmachine():
	luck = random.random()
	if(luck>0.95):
		return engine.go(movetime=250)#Excelent move	
	if(luck>0.90):
		return engine.go(movetime=200)#Good move
	if(luck<0.90):
		return engine.go(movetime=150)#Normal move


#Enter to chess.com
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.chess.com/')

#Log in
usr = 'user'
pwd = 'password'

usr_box = driver.find_element_by_class_name('form-input-input')
usr_box.send_keys(usr)

pwd_box = driver.find_element_by_id('password')
pwd_box.send_keys(pwd)

login_button = driver.find_element_by_css_selector('button.form-button-component.form-button-large.form-button-basic')
login_button.submit()


#Communication with stockfish
engine = chess.uci.popen_engine("C:/Users/joanp/Desktop/ChessComBot/stockfish")

#Update always the moves and the web elements
while(True):
	try:
		if keyboard.is_pressed('w'):#if key 'w' is pressed
			print('WAIT!')
			while True:
				if keyboard.is_pressed('f'):
					print("FOLLOW!")
					break#finishing the loop

		#Test if chat is on and take it
		chat = WebDriverWait(driver, 100).until(
			EC.presence_of_element_located((By.CLASS_NAME ,'chat-stream-component'))
		)

		if(inGame(str(chat.text))):
			color = whichColor(str(chat.text))
			#Parse the moves in the board
			#Create the board with the actual position			
			board = parseMovesToBoard()
			if(board.turn == color):
				engine.position(board)
				bestMove = godMode()
				makeAMove(bestMove[0].uci())
		else:
			if(waitingGame() == False):
				pressNewGame("normal")

	except Exception as e:
		print(e)
	
