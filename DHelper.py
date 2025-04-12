from phBot import *
import QtBind
from threading import Timer
import random
from time import sleep
import sqlite3
import json
import struct
import random
import os

pVersion = '0.0.1'
pName = 'DHelper'

# ______________________________ Initializing ______________________________ #

DIMENSIONAL_COOLDOWN_DELAY = 10800 
WAIT_DROPS_DELAY_MAX = 10 
COUNT_MOBS_DELAY = 1.0 

ExistingPillars = []
PillarUID = []
liste1 = []
PillarKey = False


character_data = None
itemUsedByPlugin = None
dimensionalItemActivated = None
Continue = 0
Count = 0
timer = None
SkipCommand = False
DimensionalActivated = False
noNDimensionalHole = False
Inside = False



gui = QtBind.init(__name__,pName)

lbl = QtBind.createLabel(gui,'<font color="blue">#ForFreeUse<font>',580,273)
lbl = QtBind.createLabel(gui,'<font color="red">#DC:_recep<font>',625,293)
lblMobs = QtBind.createLabel(gui,'#   Add monster names to ignore    #\n#          from Monster Counter         #',31,6)
tbxMobs = QtBind.createLineEdit(gui,"",31,35,100,20)
lstMobs = QtBind.createList(gui,31,56,176,203)
lstMobsData = []
btnAddMob = QtBind.createButton(gui,'btnAddMob_clicked',"    Add    ",132,34)
btnRemMob = QtBind.createButton(gui,'btnRemMob_clicked',"Remove Monster",119,258)

def Settings():
	Leader = LeaderSelection()
	if Leader == True :
		x = get_position()['x']
		y = get_position()['y']
		HolyWaterTemple = x > 7298 and x < 12095 and y > 4026 and y < 6534 
		ForgottenWorld = x > 16316 and x < 22659 and y > 2310 and y < 4997
		OnlyCountUnique = 24
		OnlyCountUnique2 = 8
		if HolyWaterTemple :
			if not str(QtBind.text(gui,lblSettings)) == "Holy Water Temple" :
				str(QtBind.setText(gui,lblSettings,str("Holy Water Temple")))
				addCount = lstOnlyCount.append
				if (OnlyCountUnique not in lstOnlyCount) or (OnlyCountUnique2 not in lstOnlyCount) :
					lstOnlyCount.clear()
					addCount(OnlyCountUnique)
					addCount(OnlyCountUnique2)
					QtBind.setChecked(gui,cbxOnlyCountUnique2,True)
					QtBind.setChecked(gui,cbxOnlyCountUnique,True)
					QtBind.setChecked(gui,cbxOnlyCountGeneral,False)
					QtBind.setChecked(gui,cbxOnlyCountChampion,False)
					QtBind.setChecked(gui,cbxOnlyCountGiant,False)
					QtBind.setChecked(gui,cbxOnlyCountTitan,False)
					QtBind.setChecked(gui,cbxOnlyCountStrong,False)
					QtBind.setChecked(gui,cbxOnlyCountElite,False)
					QtBind.setChecked(gui,cbxOnlyCountParty,False)
					QtBind.setChecked(gui,cbxOnlyCountChampionParty,False)
					QtBind.setChecked(gui,cbxOnlyCountGiantParty,False)
					saveConfigs()
					log("Plugin: DHelper'ın Ayarları [ Holy Water Temple ] için ayarlandı.")
		elif ForgottenWorld :
			if not str(QtBind.text(gui,lblSettings)) == "Forgotten World":
				str(QtBind.setText(gui,lblSettings,str("Forgotten World")))
				IgnoreMobs = 'Ghost Curse'
				addName = lstMobsData.append
				if (OnlyCountUnique in lstOnlyCount) or (OnlyCountUnique2 in lstOnlyCount) :
					lstOnlyCount.clear()
					QtBind.setChecked(gui,cbxOnlyCountUnique,False)
					QtBind.setChecked(gui,cbxOnlyCountUnique2,False)
					QtBind.setChecked(gui,cbxOnlyCountGeneral,False)
					QtBind.setChecked(gui,cbxOnlyCountChampion,False)
					QtBind.setChecked(gui,cbxOnlyCountGiant,False)
					QtBind.setChecked(gui,cbxOnlyCountTitan,False)
					QtBind.setChecked(gui,cbxOnlyCountStrong,False)
					QtBind.setChecked(gui,cbxOnlyCountElite,False)
					QtBind.setChecked(gui,cbxOnlyCountUnique,False)
					QtBind.setChecked(gui,cbxOnlyCountParty,False)
					QtBind.setChecked(gui,cbxOnlyCountChampionParty,False)
					QtBind.setChecked(gui,cbxOnlyCountGiantParty,False)
					saveConfigs()
				if IgnoreMobs not in lstMobsData:
					addName(IgnoreMobs)
					QtBind.append(gui,lstMobs,IgnoreMobs)
					saveConfigs()
				log("Plugin: DHelper'ın Ayarları [ Forgotten World ] için ayarlandı.")

txtFGWPROFILE = QtBind.createLineEdit(gui,'',155,291,70,20)
lbl = QtBind.createLabel(gui,'<font color="red">Profile Name : ( Default FGW ) <font>',5,297)
btnSaveConfig = QtBind.createButton(gui,'onSaveButtonClicked',"Save",5,275)

def SyncProfile():
	Profile = get_profile()
	ProfileFGW = "FGW"
	VariableProfile = str(QtBind.text(gui,txtFGWPROFILE))
	DefaultProfile = (VariableProfile if VariableProfile else ProfileFGW)
	if Profile == DefaultProfile :
		return 1
	return 0

def onSaveButtonClicked():
    global timer  
    ProfileFGW = "FGW"
    VariableProfile = str(QtBind.text(gui,txtFGWPROFILE))
    DefaultProfile = (VariableProfile if VariableProfile else ProfileFGW)
    if timer is None or not timer.is_alive():
        
        timer = Timer(0.5, saveConfigs)
        timer.start()
        log('Plugin: Your Profile Name (%s) have been saved.'%(DefaultProfile))
    else:
        pass


def LeaderSelection():
	count = party_count()
	getpartys = get_party()
	name = get_character_data()['name']
	if getpartys and count >= 2 :
		for oyuncu_id, oyuncu_verisi in getpartys.items():
			if oyuncu_verisi['leader'] == True :
				if	oyuncu_verisi['name'] == name :
					return True
				else :
					return False

def party_count():
	pt = get_party()
	count = 0
	if pt:
		for key, char in pt.items():
			count += 1
		return count

def event_loop():
	global Continue
	global Count
	Enabled = QtBind.isChecked(gui,cbxFGWHWT)
	if Enabled and Count == 0:
		Continue += 0.5
		if Continue % 3 == 0 :
			Count += 1
			Settings()

def WhereAmI():
	x = get_position()['x']
	y = get_position()['y']
	ForgottenWorld3 = x > 16317 and x < 19388 and y > 2298 and y < 4991
	if ForgottenWorld3 :
		return 1
	return 0

def teleported():
	global Count,noNDimensionalHole,Inside
	if Inside == True :
		Timer(5,StartBotFGW).start()
	if noNDimensionalHole == True :
		noNDimensionalHole = False
	if not Count == 0 :	
		Count = 0

def StartBotFGW():
	global Inside
	if Inside == True :
		ins = WhereAmI()
		if ins == 1 :
			Inside = False
			start_bot()
		else :
			Inside = False

lblMonsterCounter = QtBind.createLabel(gui,"#                 Monster Counter                 #",520,6)
lstMonsterCounter = QtBind.createList(gui,520,23,197,237)
QtBind.append(gui,lstMonsterCounter,'Name (Type)') 

lblPreferences = QtBind.createLabel(gui,"#             Monster Counter preferences            #",240,6)
lstIgnore = []
lstOnlyCount = []

_y = 26
lblGeneral = QtBind.createLabel(gui,'General (0)',240,_y)
cbxIgnoreGeneral = QtBind.createCheckBox(gui,'cbxIgnoreGeneral_clicked','Ignore',345,_y)
cbxOnlyCountGeneral = QtBind.createCheckBox(gui,'cbxOnlyCountGeneral_clicked','Only Count',405,_y)
_y+=20
lblChampion = QtBind.createLabel(gui,'Champion (1)',240,_y)
cbxIgnoreChampion = QtBind.createCheckBox(gui,'cbxIgnoreChampion_clicked','Ignore',345,_y)
cbxOnlyCountChampion = QtBind.createCheckBox(gui,'cbxOnlyCountChampion_clicked','Only Count',405,_y)
_y+=20
lblGiant = QtBind.createLabel(gui,'Giant (4)',240,_y)
cbxIgnoreGiant = QtBind.createCheckBox(gui,'cbxIgnoreGiant_clicked','Ignore',345,_y)
cbxOnlyCountGiant = QtBind.createCheckBox(gui,'cbxOnlyCountGiant_clicked','Only Count',405,_y)
_y+=20
lblTitan = QtBind.createLabel(gui,'Titan (5)',240,_y)
cbxIgnoreTitan = QtBind.createCheckBox(gui,'cbxIgnoreTitan_clicked','Ignore',345,_y)
cbxOnlyCountTitan = QtBind.createCheckBox(gui,'cbxOnlyCountTitan_clicked','Only Count',405,_y)
_y+=20
lblStrong = QtBind.createLabel(gui,'Strong (6)',240,_y)
cbxIgnoreStrong = QtBind.createCheckBox(gui,'cbxIgnoreStrong_clicked','Ignore',345,_y)
cbxOnlyCountStrong = QtBind.createCheckBox(gui,'cbxOnlyCountStrong_clicked','Only Count',405,_y)
_y+=20
lblElite = QtBind.createLabel(gui,'Elite (7)',240,_y)
cbxIgnoreElite = QtBind.createCheckBox(gui,'cbxIgnoreElite_clicked','Ignore',345,_y)
cbxOnlyCountElite = QtBind.createCheckBox(gui,'cbxOnlyCountElite_clicked','Only Count',405,_y)
_y+=20
lblUnique = QtBind.createLabel(gui,'Unique (8)',240,_y)
cbxIgnoreUnique = QtBind.createCheckBox(gui,'cbxIgnoreUnique_clicked','Ignore',345,_y)
cbxOnlyCountUnique = QtBind.createCheckBox(gui,'cbxOnlyCountUnique_clicked','Only Count',405,_y)
_y+=20
lblParty = QtBind.createLabel(gui,'Party (16)',240,_y)
cbxIgnoreParty = QtBind.createCheckBox(gui,'cbxIgnoreParty_clicked','Ignore',345,_y)
cbxOnlyCountParty = QtBind.createCheckBox(gui,'cbxOnlyCountParty_clicked','Only Count',405,_y)
_y+=20
lblChampionParty = QtBind.createLabel(gui,'ChampionParty (17)',240,_y)
cbxIgnoreChampionParty = QtBind.createCheckBox(gui,'cbxIgnoreChampionParty_clicked','Ignore',345,_y)
cbxOnlyCountChampionParty = QtBind.createCheckBox(gui,'cbxOnlyCountChampionParty_clicked','Only Count',405,_y)
_y+=20
lblGiantParty = QtBind.createLabel(gui,'GiantParty (20)',240,_y)
cbxIgnoreGiantParty = QtBind.createCheckBox(gui,'cbxIgnoreGiantParty_clicked','Ignore',345,_y)
cbxOnlyCountGiantParty = QtBind.createCheckBox(gui,'cbxOnlyCountGiantParty_clicked','Only Count',405,_y)
_y+=20
lblUnique2 = QtBind.createLabel(gui,'Unique2 (24)',240,_y)
cbxIgnoreUnique2 = QtBind.createCheckBox(gui,'cbxIgnoreUnique2_clicked','Ignore',345,_y)
cbxOnlyCountUnique2 = QtBind.createCheckBox(gui,'cbxOnlyCountUnique2_clicked','Only Count',405,_y)


_y+=25
cbxAcceptForgottenWorld = QtBind.createCheckBox(gui,'cbxAcceptForgottenWorld_checked','Accept Forgotten World invitations',240,_y)
_y+=20
cbxFGWHWT = QtBind.createCheckBox(gui,'cbxFGWHWT_checked','Auto Configuration ( Forgotten World ) and ( Holy Water Temple )',240,_y)
_y+=20
cbx3star = QtBind.createCheckBox(gui,'cbx3star_checked','',240,298)
_y+=2
lbl = QtBind.createLabel(gui,'Configuration: ',460,_y)
lblSettings = QtBind.createLabel(gui,"Default",530,_y)
txtDimensionalHole = QtBind.createCombobox(gui,260,291,190,20)


# Methods #

def cbxIgnoreGeneral_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",0) 
def cbxOnlyCountGeneral_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",0)

def cbxIgnoreChampion_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",1) 
def cbxOnlyCountChampion_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",1)

def cbxIgnoreGiant_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",4) 
def cbxOnlyCountGiant_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",4)

def cbxIgnoreTitan_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",5)
def cbxOnlyCountTitan_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",5)

def cbxIgnoreStrong_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",6) 
def cbxOnlyCountStrong_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",6)

def cbxIgnoreElite_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",7) 
def cbxOnlyCountElite_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",7)

def cbxIgnoreUnique_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",8) 
def cbxOnlyCountUnique_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",8)

def cbxIgnoreParty_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",16) 
def cbxOnlyCountParty_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",16)

def cbxIgnoreChampionParty_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",17) 
def cbxOnlyCountChampionParty_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",17)

def cbxIgnoreGiantParty_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",20) 
def cbxOnlyCountGiantParty_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",20)

def cbxIgnoreUnique2_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",24) 
def cbxOnlyCountUnique2_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",24)

def cbxAcceptForgottenWorld_checked(checked):
	saveConfigs()
def cbxFGWHWT_checked(checked):
	saveConfigs()
def cbx3star_checked(checked):
	saveConfigs()


def Checkbox_Checked(checked,gListName,mobType):
	gListReference = globals()[gListName]
	if checked:
		gListReference.append(mobType)
	else:
		gListReference.remove(mobType)
	saveConfigs()


def getPath():
	return get_config_dir()+pName+"\\"


def getConfig():
	return getPath()+character_data['server'] + "_" + character_data['name'] + ".json"


def loadDefaultConfig():
	
	global lstMobsData,lstIgnore,lstOnlyCount

	lstMobsData = []
	QtBind.clear(gui,lstMobs)

	lstIgnore = []
	QtBind.setChecked(gui,cbxIgnoreGeneral,False)
	QtBind.setChecked(gui,cbxIgnoreChampion,False)
	QtBind.setChecked(gui,cbxIgnoreGiant,False)
	QtBind.setChecked(gui,cbxIgnoreTitan,False)
	QtBind.setChecked(gui,cbxIgnoreStrong,False)
	QtBind.setChecked(gui,cbxIgnoreElite,False)
	QtBind.setChecked(gui,cbxIgnoreUnique,False)
	QtBind.setChecked(gui,cbxIgnoreParty,False)
	QtBind.setChecked(gui,cbxIgnoreChampionParty,False)
	QtBind.setChecked(gui,cbxIgnoreGiantParty,False)
	QtBind.setChecked(gui,cbxIgnoreUnique2,False)

	lstOnlyCount = []
	QtBind.setChecked(gui,cbxOnlyCountGeneral,False)
	QtBind.setChecked(gui,cbxOnlyCountChampion,False)
	QtBind.setChecked(gui,cbxOnlyCountGiant,False)
	QtBind.setChecked(gui,cbxOnlyCountTitan,False)
	QtBind.setChecked(gui,cbxOnlyCountStrong,False)
	QtBind.setChecked(gui,cbxOnlyCountElite,False)
	QtBind.setChecked(gui,cbxOnlyCountUnique,False)
	QtBind.setChecked(gui,cbxOnlyCountParty,False)
	QtBind.setChecked(gui,cbxOnlyCountChampionParty,False)
	QtBind.setChecked(gui,cbxOnlyCountGiantParty,False)
	QtBind.setChecked(gui,cbxOnlyCountUnique2,False)

	QtBind.setChecked(gui,cbxAcceptForgottenWorld,False)
	QtBind.setChecked(gui,cbxFGWHWT,False)
	QtBind.setChecked(gui,cbx3star,False)
	QtBind.setChecked(gui,txtDimensionalHole,False)




def loadConfigs():
	loadDefaultConfig()
	if isJoined() and os.path.exists(getConfig()):
		data = {}
		with open(getConfig(),"r") as f:
			data = json.load(f)
		
		if "Ignore Names" in data:
			global lstMobsData
			lstMobsData = data["Ignore Names"]
			
			for name in lstMobsData:
				QtBind.append(gui,lstMobs,name)
		
		if "Ignore Types" in data:
			global lstIgnore
			for t in data["Ignore Types"]:
				if t == 24:
					QtBind.setChecked(gui,cbxIgnoreUnique2,True)
				elif t == 8:
					QtBind.setChecked(gui,cbxIgnoreUnique,True)
				elif t == 7:
					QtBind.setChecked(gui,cbxIgnoreElite,True)
				elif t == 6:
					QtBind.setChecked(gui,cbxIgnoreStrong,True)
				elif t == 5:
					QtBind.setChecked(gui,cbxIgnoreTitan,True)
				elif t == 4:
					QtBind.setChecked(gui,cbxIgnoreGiant,True)
				elif t == 1:
					QtBind.setChecked(gui,cbxIgnoreChampion,True)
				elif t == 0:
					QtBind.setChecked(gui,cbxIgnoreGeneral,True)
				elif t == 16:
					QtBind.setChecked(gui,cbxIgnoreParty,True)
				elif t == 17:
					QtBind.setChecked(gui,cbxIgnoreChampionParty,True)
				elif t == 20:
					QtBind.setChecked(gui,cbxIgnoreGiantParty,True)
				else:
					
					continue
				lstIgnore.append(t)

		if "OnlyCount Types" in data:
			global lstOnlyCount
			for t in data["OnlyCount Types"]:
				if t == 24:
					QtBind.setChecked(gui,cbxOnlyCountUnique2,True)
				if t == 8:
					QtBind.setChecked(gui,cbxOnlyCountUnique,True)
				elif t == 7:
					QtBind.setChecked(gui,cbxOnlyCountElite,True)
				elif t == 6:
					QtBind.setChecked(gui,cbxOnlyCountStrong,True)
				elif t == 5:
					QtBind.setChecked(gui,cbxOnlyCountTitan,True)
				elif t == 4:
					QtBind.setChecked(gui,cbxOnlyCountGiant,True)
				elif t == 1:
					QtBind.setChecked(gui,cbxOnlyCountChampion,True)
				elif t == 0:
					QtBind.setChecked(gui,cbxOnlyCountGeneral,True)
				elif t == 16:
					QtBind.setChecked(gui,cbxOnlyCountParty,True)
				elif t == 17:
					QtBind.setChecked(gui,cbxOnlyCountChampionParty,True)
				elif t == 20:
					QtBind.setChecked(gui,cbxOnlyCountGiantParty,True)
				else:
					
					continue
				lstOnlyCount.append(t)

		if 'Accept ForgottenWorld' in data and data['Accept ForgottenWorld']:
			QtBind.setChecked(gui,cbxAcceptForgottenWorld,True)
		if 'hwtandfgw' in data and data['hwtandfgw']:
			QtBind.setChecked(gui,cbxFGWHWT,True)
		if '3StarFgw' in data and data['3StarFgw']:
			QtBind.setChecked(gui,cbx3star,True)
		if 'fgwprofile' in data and data['fgwprofile']:
			QtBind.setText(gui,txtFGWPROFILE,str(data["fgwprofile"]))
		if 'DimensionalHole' in data and data['DimensionalHole']:
			QtBind.setText(gui,txtDimensionalHole,str(data["DimensionalHole"]))



def saveConfigs():
	if isJoined():
		data = {}

		data['OnlyCount Types'] = lstOnlyCount
		data['Ignore Types'] = lstIgnore
		data['Ignore Names'] = lstMobsData
		data['Accept ForgottenWorld'] = QtBind.isChecked(gui,cbxAcceptForgottenWorld)
		data['hwtandfgw'] = QtBind.isChecked(gui,cbxFGWHWT)
		data['3StarFgw'] = QtBind.isChecked(gui,cbx3star)
		data["fgwprofile"] = QtBind.text(gui,txtFGWPROFILE)
		data["DimensionalHole"] = QtBind.text(gui,txtDimensionalHole)
	
		with open(getConfig(),"w") as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))

def isJoined():
	global character_data
	character_data = get_character_data()
	if not (character_data and "name" in character_data and character_data["name"]):
		character_data = None
	return character_data

def btnAddMob_clicked():
	global lstMobsData
	
	text = QtBind.text(gui,tbxMobs)
	if text and not ListContains(text,lstMobsData):
		lstMobsData.append(text)
		
		QtBind.append(gui,lstMobs,text)
		QtBind.setText(gui,tbxMobs,"")
		saveConfigs()
		log('Plugin: Monster added ['+text+']')

def btnRemMob_clicked():
	global lstMobsData
	
	selected = QtBind.text(gui,lstMobs)
	if selected:
		lstMobsData.remove(selected)
		
		QtBind.remove(gui,lstMobs,selected)
		saveConfigs()
		log('Plugin: Monster removed ['+selected+']')

def ListContains(text,lst):
	text = text.lower()
	for i in range(len(lst)):
		if lst[i].lower() == text:
			return True
	return False

def QtBind_ItemsContains(text,lst):
	return ListContains(text,QtBind.getItems(gui,lst))

def AttackMobs(wait,isAttacking,position,radius):
	count = getMobCount(position,radius)
	if count > 0:
		
		if not isAttacking:
			start_bot()
			log("Plugin: Starting to kill ("+str(count)+") mobs at this area. Radius: "+(str(radius) if radius != None else "Max."))
		
		Timer(wait,AttackMobs,[wait,True,position,radius]).start()
	else:
		log("Plugin: All mobs killed!")
		
		conn = GetFilterConnection()
		cursor = conn.cursor()
		WaitPickableDrops(cursor)
		conn.close()
		
		stop_bot()
		
		set_training_position(0,0,0,0)
		
		log("Plugin: Getting back to the script...")
		Timer(2.5,move_to,[position['x'],position['y'],position['z']]).start()
		
		Timer(5.0,start_bot).start()


def getMobCount(position,radius):
	
	QtBind.clear(gui,lstMonsterCounter)
	QtBind.append(gui,lstMonsterCounter,'Name (Type)') 
	count = 0
	
	p = position if radius != None else None
	
	monsters = get_monsters()
	if monsters:
		for key, mob in monsters.items():
			
			if mob['type'] in lstIgnore:
				continue
			
			if len(lstOnlyCount) > 0:
				
				if not mob['type'] in lstOnlyCount:
					continue
			
			elif ListContains(mob['name'],lstMobsData):
				continue
			
			if radius != None:
				if round(GetDistance(p['x'], p['y'],mob['x'],mob['y']),2) > radius:
					continue
			
			QtBind.append(gui,lstMonsterCounter,mob['name']+' ('+str(mob['type'])+')')
			count+=1
	return count


def GetDistance(ax,ay,bx,by):
	return ((bx-ax)**2 + (by-ay)**2)**(0.5)


def GetFilterConnection():
	
	path = get_config_dir()+character_data['server']+'_'+character_data['name']+'.db3'
	
	return sqlite3.connect(path)

def IsPickable(filterCursor,ItemID):
	
	return filterCursor.execute('SELECT EXISTS(SELECT 1 FROM pickfilter WHERE id=? AND pick=1 LIMIT 1)',(ItemID,)).fetchone()[0]


def WaitPickableDrops(filterCursor,waiting=0):
	
	if waiting >= WAIT_DROPS_DELAY_MAX:
		log("Plugin: Timeout for picking up drops!")
		return
	
	drops = get_drops()
	if drops:
		
		drop = None
		for key in drops:
			value = drops[key]
			if IsPickable(filterCursor,value['model']):
				drop = value
				break
		if drop:
			log('Plugin: Waiting for picking up "'+drop['name']+'"...')
			
			sleep(1.0)
			
			WaitPickableDrops(filterCursor,waiting+1)


def GetDimensionalHole(Name):
	searchByName = Name != ''

	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			
			match = False
			if searchByName:
				match = (Name == item['name'])
			else:
				itemData = get_item(item['model'])
				match = (itemData['tid1'] == 3 and itemData['tid2'] == 12 and itemData['tid3'] == 7)

			if match:
				item['slot'] = slot
				return item
	return None

def GetListPillarUID(Name):
	if PillarKey == False :
		ExistingPillars.clear()
		PillarUID.clear()
		npcs = get_npcs()
		if npcs:
			for uid in npcs: 
				ItemInfo = get_item_string(Name)
				NpcModel = npcs[uid]['model']
				ItemModel = ItemInfo['model']
				if NpcModel == ItemModel :
					if not uid in ExistingPillars :
						ExistingPillars.append(int(uid))
						fark_liste2 = list(set(ExistingPillars) - set(liste1))
		return fark_liste2
	else :
		return PillarUID


def GetDimensionalPillarUID(Name):
    global PillarKey
    
    uid = GetListPillarUID(Name)
    
    if not uid:  
        PillarKey = True
        return 0
    
    Max = max(uid)

    if not Max in PillarUID:
        PillarKey = True
        PillarUID.append(int(Max))
        
    for i in range(len(PillarUID)):
        PillarUID[i] = int(PillarUID[i])
        
    return int(PillarUID[i])



def EnterToDimensional(Name):

	uid = GetDimensionalPillarUID(Name)
	Enabled = QtBind.isChecked(gui,cbx3star)
	SyncProfileFGW = SyncProfile()
	global SkipCommand
	if uid != 0 :
		global Inside
        
		log('Plugin: "'+Name+'" Seçiliyor...')
		packet = struct.pack('I',uid)
		inject_joymax(0x7045,packet,False)
		sleep(1.0)
        
		log('Plugin: "'+Name+'" giriliyor...')
		inject_joymax(0x704B,packet,False)
		packet += struct.pack('H',3)
		inject_joymax(0x705A,packet,False)
		Inside = True
		if Enabled and SyncProfileFGW == 1 and SkipCommand == False :
			global DimensionalActivated
			Time = (183 * 60)
			SkipCommand = True
			DimensionalActivated = True
			Timer(Time,fnSkipCommand).start()
			log('Plugin: Tebrikler, 3 Saat sonra "Tekrar Giriş" Aktif edildi.')
		return
	elif uid == 0 :
		if Enabled and SyncProfileFGW == 1 and SkipCommand == False :
			global dimensionalItemActivated
			Time1860 = (31 * 60)
			dimensionalItemActivated = None
			SkipCommand = True
			Timer(Time1860,fnSkipCommand).start()
			log('Plugin: "'+Name+'" Buglandı, 30 Dakika Sonra tekrar deneyecek.')



def fnSkipCommand():
	SyncProfileFGW = SyncProfile()
	global SkipCommand,PillarKey,DimensionalActivated
	SkipCommand = False
	DimensionalActivated = False
	PillarKey = False
	if SyncProfileFGW == 1 :
		Timer(random.uniform(0.5,1),use_return_scroll).start()
		Timer(random.uniform(4,5),start_bot).start()

def CheckDimensionalHole():
	global noNDimensionalHole
	if noNDimensionalHole == True :
		return 1
	return 0


def GoDimensionalThread(Name):
	
	if dimensionalItemActivated:
		Name = dimensionalItemActivated['name']
		log('Plugin: '+( '"'+Name+'"' if Name else 'Dimensional Hole')+' hala Açık!')
		EnterToDimensional(Name)
		return
	
	item = GetDimensionalHole(Name)
	if item:
		global DimensionalActivated
		if DimensionalActivated == False :
			
			log('Plugin: Using "'+item['name']+'"...')
			p = struct.pack('B',item['slot'])
			locale = get_locale()
			if locale == 56 or locale == 18: 
				p += b'\x30\x0C\x0C\x07'
			else: 
				p += b'\x6C\x3E'
			
			global itemUsedByPlugin
			itemUsedByPlugin = item
			inject_joymax(0x704C,p,True)
		else:
			
			stop_bot()
			Timer(random.uniform(0.5,1),use_return_scroll).start()
			log('Plugin: '+( '"'+Name+'"' if Name else 'Dimensional Hole')+' açmak için hala zaman var.')	
	else:
		
		global noNDimensionalHole
		if noNDimensionalHole == False :
			noNDimensionalHole = True
		log('Plugin: '+( '"'+Name+'"' if Name else 'Dimensional Hole')+' Envanterinizde bulunamadı.')
		


def AttackArea(args):
	
	radius = None
	if len(args) >= 2:
		radius = round(float(args[1]),2)
	
	p = get_position()
	
	if getMobCount(p,radius) > 0:
		
		stop_bot()
		
		set_training_position(p['region'], p['x'], p['y'],p['z'])
		
		if radius != None:
			set_training_radius(radius)
		else:
			set_training_radius(100.0)
		
		Timer(0.001,AttackMobs,[COUNT_MOBS_DELAY,False,p,radius]).start()
	
	else:
		log("Plugin: No mobs at this area. Radius: "+(str(radius) if radius != None else "Max."))
	return 0


def GoDimensional(args):
    stop_bot()
    
    name = ''
    npcs = get_npcs()
    liste1.clear()
    if npcs :
        for uid in npcs:
            liste1.append(uid)
    if len(args) > 1:
        name = args[1]
        Timer(random.uniform(0.5,2),GoDimensionalThread,[name]).start()
    else :
        name = QtBind.text(gui,txtDimensionalHole)
        Timer(random.uniform(0.5,2),GoDimensionalThread,[name]).start()
    return 0

def joined_game():
	loadConfigs()

def handle_joymax(opcode, data):
	
	if opcode == 0x751A:
		if QtBind.isChecked(gui,cbxAcceptForgottenWorld):
			
			packet = data[:4]
			packet += b'\x00\x00\x00\x00'
			packet += b'\x01'
			inject_joymax(0x751C,packet,False)
			log('Plugin: Forgotten World Daveti Kabul edildi.!')
	
	elif opcode == 0xB04C:
		
		global itemUsedByPlugin
		Enabled = QtBind.isChecked(gui,cbx3star)
		SyncProfileFGW = SyncProfile()
		if itemUsedByPlugin:
			
			if data[0] == 1:
				log('Plugin: "'+itemUsedByPlugin['name']+'" Açıldı.')
				
				global dimensionalItemActivated
				dimensionalItemActivated = itemUsedByPlugin
				def DimensionalCooldown():
					global dimensionalItemActivated
					dimensionalItemActivated = None
				Timer(DIMENSIONAL_COOLDOWN_DELAY,DimensionalCooldown).start()
				
				Timer(1.0,EnterToDimensional,[itemUsedByPlugin['name']]).start()
			elif data[0] == 2 and Enabled and SyncProfileFGW == 1 :
				Timer(0.5,ForgottenWorld).start()
			else:
				log('Plugin: "'+itemUsedByPlugin['name']+'" Açılmadı')
			
			itemUsedByPlugin = None
	return True

def ForgottenWorld():
	DimensionalHole = QtBind.text(gui,txtDimensionalHole)
	GoDimensional(["", (DimensionalHole)])

def DimensionalHole(ListDimensionalHole):
	if ListDimensionalHole == 'DimensionalHole':
		DimensionalHoleList = { "Boyut Deliği (Gemi Enkazı-★)": [], "Boyut Deliği (Gemi Enkazı-★★)": [], "Boyut Deliği (Gemi Enkazı-★★★)": [], "Boyut Deliği (Gemi Enkazı-★★★★)": [] }
		for Hole in DimensionalHoleList:
			QtBind.append(gui,txtDimensionalHole,Hole)
	return True
DimensionalHole('DimensionalHole')

# Plugin loaded
log('Plugin: '+pName+' v'+pVersion+' yüklendi')

if os.path.exists(getPath()):
	# Adding RELOAD plugin support
	try:
		loadConfigs()
	except:
		# Just in case omg -_-
		log('Plugin: Error loading '+pName+' config file')
else:
	# Creating configs folder
	os.makedirs(getPath())
	log('Plugin: '+pName+' folder has been created')
