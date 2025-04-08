from phBot import *
from threading import Timer
from time import sleep
import struct
import random
import binascii
import QtBind

allowplugin = False
pName = 'xMobSkill' 

# GUI oluşturma
gui = QtBind.init(__name__, "xMobSkill")
lineedit1 = QtBind.createLineEdit(gui, "Yaratığın adını yaz", 150, 200, 100, 16)

def handle_joymax(opcode, data):
    if opcode == 0xB070:
        # log("Server: (Opcode) 0x" + '{:02X}'.format(opcode) + " (Data) "+ ("None" if not data else ' '.join('{:02X}'.format(x) for x in data)))
        kim = struct.unpack_from("<I", data, 14)[0]
        if kim > 0:
            test = struct.unpack_from("<I", data, 7)[0]
            for uID, srth in get_monsters().items():
                if uID == test:
                    # Kullanıcının girdiği yaratık adını al
                    user_input = QtBind.text(gui, lineedit1).strip()

                    # Eğer yaratık adı boş değilse karşılaştır
                    if user_input and srth['name'] == user_input:
                            log(f"1. log = {data[0]}")
                            log(f"2. log = {data[1]}")
                            log(f"4. log = {data[3]}")
                            log(f"5. log = {data[4]}")
    return True

log('By TheWorstOne')
