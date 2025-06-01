from phBot import *
import QtBind
import struct
import math
import json
import threading
import os

pName = 'xFollowPartyMaster-revitalized'
pVersion = '0.0.2'

# ______________________________ ' Initializing ' ______________________________ #

# Graphic user interface
gui = QtBind.init(__name__,pName)

btnSaveConfig = QtBind.createButton(gui,'onSaveButtonClicked',"Save Config",350,35)
txtLineEdit1 = QtBind.createLineEdit(gui,"0",125,35,60,20)
txtLineEdit2 = QtBind.createLineEdit(gui,"0",200,35,60,20)
txtLineEdit3 = QtBind.createLineEdit(gui,"0",275,35,60,20)
cbxLogMessage = QtBind.createCheckBox(gui, 'logMessage_checked','Log Inject Message',10,35)

def handle_silkroad(opcode, data) :
	if QtBind.isChecked(gui,cbxLogMessage) :
		if opcode == 0x705A :
			first_int, = struct.unpack('<I', data[0:4])
			item_data = f'{first_int}'
			pos_data = get_position()
			character = (pos_data['x'], pos_data['y'])
			for name, pos in npcs.items():
				result = is_npc_in_range(character, pos)
				if result :
					if name == "npc1" :
						QtBind.setText(gui, txtLineEdit1,item_data)
					elif name == "npc2" :
						QtBind.setText(gui, txtLineEdit2,item_data)
					elif name == "npc3" :
						QtBind.setText(gui, txtLineEdit3,item_data) 
					saveConfigs()

def onSaveButtonClicked():
	if QtBind.isChecked(gui,cbxLogMessage) :
		QtBind.setChecked(gui, cbxLogMessage, False)
	saveConfigs()

npcs = {
	"npc1": (-133, 773),
	"npc2": (38, 813),
	"npc3": (181, 856),
}

npcs2 = {
	"npc1": (-12670, -6610),
	"npc2": (-12479, -6605),
	"npc3": (-12287, -6608),
	"npc4": (-12095, -6617),
}

def letsfuckingo():
	for name2, pos2 in npcs2.items():
		leader = WhereIsLeader()
		if is_npc_in_range(leader, pos2) and get_character_data().get('zone_name', '') in {'Kuzey Hotan', 'Northern Hotan'} :
			return True

def is_npc_in_range(character_pos, npc_pos, max_distance=70):
	x1, y1 = character_pos
	x2, y2 = npc_pos
	distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
	return distance <= max_distance

def which_kale_kapilari():
    npcs = get_npcs()
    result = []
    if npcs:
        for UniqueID, NPC in npcs.items():
            if NPC['name'].startswith('Hotan Kale Kapısı '):
                log(f"Bulundu: {NPC['name']} - ID: {UniqueID}")
                result.append(UniqueID)
    return result
                    
                    
                    

def WhereIsLeader():
	getpartys = get_party()
	name = get_character_data().get('name', '')
	if getpartys :
		for oyuncu_id, oyuncu_verisi in getpartys.items():
			if oyuncu_verisi['leader']:
				if oyuncu_verisi.get('name') != name :
					return (oyuncu_verisi['x'], oyuncu_verisi['y'])
	return (0,0)

def Goddamnbro():
    leader = WhereIsLeader()
    pos_data = get_position()
    character = (pos_data['x'], pos_data['y'])
    for name, pos in npcs.items():
        result = is_npc_in_range(character, pos)
        kapilar = which_kale_kapilari()
        if result:
            if name == "npc1":
                for name2, pos2 in npcs2.items():
                    result2 = is_npc_in_range(leader, pos2)
                    if result2:
                        npc_uid1 = kapilar
                        if name2 == "npc1":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid1, 2, 153), False)
                        if name2 == "npc2":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid1, 2, 154), False)
                        if name2 == "npc3":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid1, 2, 155), False)
                        if name2 == "npc4":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid1, 2, 156), False)
            elif name == "npc2":
                for name2, pos2 in npcs2.items():
                    result2 = is_npc_in_range(leader, pos2)
                    if result2:
                        npc_uid2 = kapilar
                        if name2 == "npc1":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid2, 2, 153), False)
                        if name2 == "npc2":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid2, 2, 154), False)
                        if name2 == "npc3":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid2, 2, 155), False)
                        if name2 == "npc4":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid2, 2, 156), False)
            elif name == "npc3":
                for name2, pos2 in npcs2.items():
                    result2 = is_npc_in_range(leader, pos2)
                    if result2:
                        npc_uid3 = kapilar
                        if name2 == "npc1":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid3, 2, 153), False)
                        if name2 == "npc2":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid3, 2, 154), False)
                        if name2 == "npc3":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid3, 2, 155), False)
                        if name2 == "npc4":
                            inject_joymax(0x705A, struct.pack('<IBI', npc_uid3, 2, 156), False)


# Return folder path

def isJoined():
	global inGame
	inGame = get_character_data()
	if not (inGame and "name" in inGame and inGame["name"]):
		inGame = None
	return inGame

def loadConfigs():
	if isJoined() :
		if os.path.exists(getConfig()):
			data = {}
			with open(getConfig(),"r", encoding='utf-8') as f:
				data = json.load(f)
			# Check to load config
			if 'npc1' in data and data['npc1']:
				QtBind.setText(gui,txtLineEdit1,str(data["npc1"]))
			if 'npc2' in data and data['npc2']:
				QtBind.setText(gui,txtLineEdit2,str(data["npc2"]))
			if 'npc3' in data and data['npc3']:
				QtBind.setText(gui,txtLineEdit3,str(data["npc3"]))
		else:
			saveConfigs()
			threading.Timer(0.5, loadConfigs).start()

def saveConfigs():
	if isJoined():
		data = {}
		data["npc1"] = QtBind.text(gui,txtLineEdit1) or "0"
		data["npc2"] = QtBind.text(gui,txtLineEdit2) or "0"
		data["npc3"] = QtBind.text(gui,txtLineEdit3) or "0"
		with open(getConfig(),"w") as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))

def getPath():
	return get_config_dir()+pName+"\\"

def connected():
	global inGame
	inGame = None

def getConfig():
	return getPath()+inGame['server'] + "_" + inGame['name'] + ".json"

# Called when the character enters the game world
def joined_game():
	loadConfigs()

# Plugin loaded
log('Plugin: '+pName+' v'+pVersion+' başarıyla yüklendi.')

if os.path.exists(getPath()):
	try:
		loadConfigs()
	except:
		log(f"Plugin: {pName} yapılandırma dosyası yüklenirken hata oluştu.")
else:
	os.makedirs(getPath())
	log(f"Plugin: {pName} klasörü oluşturuldu.")
