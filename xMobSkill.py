from phBot import *
from threading import Timer
from time import sleep
import struct
import random
import binascii
import QtBind

# Plugin bilgisi
allowplugin = False
pName = 'xMobSkill'

# GUI oluşturma
gui = QtBind.init(__name__, pName)
lineedit1 = QtBind.createLineEdit(gui, "Yaratığın adını yaz", 150, 200, 100, 16)

def handle_joymax(opcode, data):
    if opcode == 0xB070 and data:

        # Güvenlik: Veri boyutunu kontrol et
        if len(data) >= 18:  # 14 + 4 byte okunacak
            test = struct.unpack_from("<I", data, 7)[0]     # Muhtemelen mob unique ID
            kim = struct.unpack_from("<I", data, 14)[0]     # Muhtemelen skill caster

            # Tüm yaratıkları al
            for uID, srth in get_monsters().items():
                if uID == test:
                    # Kullanıcının GUI'den girdiği yaratık adını al
                    user_input = QtBind.text(gui, lineedit1).strip()

                    if user_input and srth['name'] == user_input:
                        log(f"[xMobSkill] Eşleşen yaratık bulundu: {srth['name']}")
                        log(f"[xMobSkill] Data Dump: {' '.join('{:02X}'.format(x) for x in data)}")
                        log(f"[xMobSkill] data[0] = {data[0]}")
                        log(f"[xMobSkill] data[1] = {data[1]}")
                        log(f"[xMobSkill] data[2] = {data[2]}")
                        log(f"[xMobSkill] data[3] = {data[3]}")
                        log(f"[xMobSkill] data[4] = {data[4]}")
        else:
            log(f"[xMobSkill] Uyarı: 0xB070 paketi yeterli uzunlukta değil. Uzunluk: {len(data)}")
            log(f"[xMobSkill] Paket: {' '.join('{:02X}'.format(x) for x in data)}")

    return True

log('[xMobSkill] Plugin yüklendi - By TheWorstOne')
