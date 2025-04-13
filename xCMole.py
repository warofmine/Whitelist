from phBot import *
import phBotChat
import struct
import os
import json
import threading
import urllib.request
from time import sleep

pName = 'xCMole'
pVersion = '0.0.1'

Times = 0
Process = False
Working = True
Done = False
unique_name = None
allowplugin = False

def CheckWhitelist():
	whitelist_url = 'https://raw.githubusercontent.com/warofmine/Whitelist/refs/heads/main/whitelist'
	with urllib.request.urlopen(whitelist_url) as response:
		dosya_icerigi = response.read().decode('utf-8')

	icerik_listesi = [item.strip() for item in dosya_icerigi.split(',')]

	return icerik_listesi

def allow():
	global allowplugin
	icerik_listesi = CheckWhitelist()
	nickname = get_character_data()['name']
	if 'FreePlugin' in icerik_listesi :
		allowplugin = True
	elif nickname in icerik_listesi :
		allowplugin = True
	else :
		if allowplugin == True :
			allowplugin = False
			
		else :
			pass

def define_unique_name():
	global unique_name
	region = get_position()['region']

	if region == -32754 :
		unique_name = "Haroeris"
	elif region == -32753 :
		unique_name = "Seth"
	else :
		pass

def DoOwner():
	global Working

	if Working == False :
		Working = True

	else :
		return False

def IfOwner():
	global Working

	if Working == False :
		return True
	
	else:
		return False

def IfGate():
	if allowplugin :
		Npcs = get_npcs()
		if Npcs :
			for npc in Npcs:
				Isis = Npcs[npc]['servername'] == "INS_TEMPLE_TELEPORT"
				Seth = Npcs[npc]['servername'] == "INS_TEMPLE_SETH_TELEPORT"
				if Isis or Seth :
					return True
			else :
				return False
			
def GoInside():
	if allowplugin :
		Npcs = get_npcs()
		if Npcs :
			for npc in Npcs:
				Isis = Npcs[npc]['servername'] == "INS_TEMPLE_TELEPORT"
				Seth = Npcs[npc]['servername'] == "INS_TEMPLE_SETH_TELEPORT"
				if Isis or Seth :
					global Process
					opcode = 0x705A
					data = struct.pack('<IBB', npc , 3 , 0)
					inject_joymax(opcode,data,False)
					Process = False
			else :
				return False

def FastInside():
	global Process

	while Process == True :
		sleep(0.014)
		if IfGate() == True and Process == True :
			threading.Thread(target=GoInside).start()
			log('Plugin: Sonic giriş deaktif edildi.')
		else :
			if Process == False :
				break 

def SS_FastInside():
	global Process

	if Process == False :
		Process = True
		threading.Thread(target=FastInside).start()
		log('Plugin: Sonic giriş aktif edildi.')
	else :
		Process = False
		log('Plugin: Sonic giriş deaktif edildi.')

def event_loop():
	global Times,Working,Done,unique_name

	if unique_name in ["Haroeris","Seth"] :

		if Working == True and Times == 0 :
			drops = get_drops()
			if drops:
				for drop in drops:
					if drops[drop]['servername'] == "ITEM_ETC_SD_TOKEN_04" :
						if drops[drop]['can_pick'] == True :
							Times += 1
				else :
					return False

		elif Working == True and Times >= 1 and Done == False:
			Done = True
			jobnickname = get_character_data()['job_name']
			Owner = "Gold Coin(s) are owned by [" + str(jobnickname) + "] from [" + str(unique_name) + "]"
			phBotChat.Party(Owner)
			phBotChat.ClientNotice(Owner)
		else :
			pass

def handle_chat(t, player, msg):
	global Working,Done

	if Working == True and Done == False:
		Me = get_character_data()['job_name']
		if not Me == player :
			if t == 4 :
				if msg.startswith("Gold Coin(s) are owned by") :
					phBotChat.ClientNotice(msg)
					Done = True

	if t != 0 :
		if player == "xKocakurt" or player == "UP_xKocakurt" or player == "ObIomov" :
			Own = get_character_data()['name']
			if Own != player :
				if msg == "#CHECK" : # feedback
					global allowplugin
					if allowplugin == True :
						Approval = True
					else :
						Approval = False
					Message = "Plugin Name : [ " + str(pName) + " ] : Plugin Version : [ " + str(pVersion) + " ] : Plugin Approval : [ " + str(Approval) + " ] ."
					phBotChat.Private(player,Message)
					phBotChat.ClientNotice(Message)
			else :
				pass

	else :
		pass

def teleported():
	global Times,Done,unique_name
	region_character = get_position()['region']

	if region_character < 0 :
		threading.Thread(target=define_unique_name).start()

	if Done == True :

		if Times >= 1 :
			Times = 0
			Done = False

		elif Times == 0 :
			Done = False

	else :
		pass

def saveConfigs():
	# Save if data has been loaded
	if isJoined():
		# Save all data
		data = {}

		# Overrides
		with open(getConfig(),"w") as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))

# Return folder path
def getPath():
	return get_config_dir()+pName+"\\"

# Return character configs path (JSON)
def getConfig():
	return getPath()+inGame['server'] + "_" + inGame['name'] + ".json"

# Check if character is ingame
def isJoined():
	global inGame
	inGame = get_character_data()
	if not (inGame and "name" in inGame and inGame["name"]):
		inGame = None
	return inGame

# Loads all config previously saved
def loadConfigs():
	if isJoined():
		# Check config exists to load
		threading.Thread(target=allow).start()
		if os.path.exists(getConfig()):
			data = {}
			with open(getConfig(),"r") as f:
				data = json.load(f)

# Called when the bot successfully connects to the game server
def connected():
	global inGame
	inGame = None

# Called when the character enters the game world
def joined_game():
	loadConfigs()

# Plugin loaded
log('Plugin: '+pName+' v'+pVersion+' succesfully loaded')

if os.path.exists(getPath()):
	# Adding RELOAD plugin support
	loadConfigs()
else:
	# Creating configs folder
	os.makedirs(getPath(), exist_ok=True)
