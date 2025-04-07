from phBot import *
from threading import Timer
from time import sleep
import struct
import random
import binascii
import QtBind

allowplugin = False
pName = 'xMobSkill' 

def CheckWhitelist():
	whitelist_url = 'https://raw.githubusercontent.com/iNacya/Whitelist/main/xCaveHelper_Whitelist'
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

def handle_joymax(opcode, data):
  if opcode == 0xB070 :
    #log("Server: (Opcode) 0x" + '{:02X}'.format(opcode) + " (Data) "+ ("None" if not data else ' '.join('{:02X}'.format(x) for x in data)))
    kim=struct.unpack_from("<I",data,14)[0]
    if kim>0:
        test=struct.unpack_from("<I",data,7)[0]
        for uID, srth in get_monsters().items():
            if uID==test:
                if srth['name']=='Ghost Sereness':
                    can = srth['hp']
                    anlik = srth['max_hp']
                    gerekli = (int(anlik) * 50) /100
                    if  int(can) <= gerekli:
                        log(str(srth['hp']))
                        log('can değeri üstte')
                        log(str(data[0]))
                        log(str(data[1]))
                        log(str(data[3]))
                        log(str(data[4]))
  return True

log('LongTimeNoSee')