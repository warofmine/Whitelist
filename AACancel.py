from phBot import *
import QtBind
import struct
from threading import Timer
import os

pName = 'AACancel'
pVersion = '0.0.1'
gui = QtBind.init(__name__, pName)

Skill_ID = 9944  

try:
    skill_file_path = os.path.join(get_config_dir(), 'skill.txt')
    if not os.path.exists(skill_file_path):
        with open(skill_file_path, 'w') as f:
            f.write(str(Skill_ID))
        #log(f"[AACancel] oluşturuldu.")
    else:
        with open(skill_file_path, 'r') as f:
            content = f.readline().strip()
            if content.isdigit():
                Skill_ID = int(content)
                #log(f"[AACancel]  yüklendi. ")
            else:
                log(f"Terorist")
except Exception as e:
    log(f"Terorist")

# --- Global değişkenler ---
timer = None
timer2 = None
timer3 = None
PackedCharged1 = '0101010101'
PackedCharged2 = '0101010101'
PackedCharged3 = '0101010101'

# Ayar değişkenleri
sAttack = False
sClientAttack = False
sUseSkill = False
sDelayText = '40'

# UI Elemanları
cbxCancelAA = QtBind.createCheckBox(gui, 'cbxCancel_clicked',' Cancel Auto Attack (Server)',5,5)
cbxUseSkill = QtBind.createCheckBox(gui, 'cbxUseSkill_clicked',' Use Skill',170,5)
cbxCancelAA2 = QtBind.createCheckBox(gui, 'cbxCancel2_clicked',' Cancel Auto Attack (Client)  Delay :               ms ',5,22)
cleDelay = QtBind.createLineEdit(gui,"40",200,20,35,20)

# Callback fonksiyonları
def cbxCancel_clicked(checked):
    global sAttack
    if QtBind.isChecked(gui, cbxCancelAA2):
        QtBind.setChecked(gui, cbxCancelAA2, False)
    sAttack = checked

def cbxCancel2_clicked(checked):
    global sClientAttack
    if QtBind.isChecked(gui, cbxCancelAA):
        QtBind.setChecked(gui, cbxCancelAA, False)
    sClientAttack = checked

def cbxUseSkill_clicked(checked):
    global sUseSkill
    sUseSkill = checked

def cleDelay_changed(text):
    global sDelayText
    sDelayText = text.strip()

# --- sadece uniq filtre ---
def _is_unique_target_from_packet(data):
    try:
        target_id = None
        if len(data) >= 23:
            target_id = struct.unpack_from('<I', data, 19)[0]
        elif len(data) >= 20:
            target_id = struct.unpack_from('<I', data, 15)[0]

        if target_id is not None:
            monsters = get_monsters()
            mob = monsters.get(target_id, None)
            if mob:
                #log(f"Target ID: {target_id} | Mob: {mob['name']} | Type: {mob['type']}")
                if mob.get('type') == 3:  # 3 = Unique
                    return True
    except Exception as e:
        log(f"Hata (uniq kontrol): {str(e)}")
    return True

def handle_joymax(opcode, data):
    global timer, timer2, timer3, PackedCharged1, PackedCharged2, PackedCharged3
    global sAttack, sUseSkill, sDelayText

    if sAttack and opcode == 0xB070:
        if len(data) >= 14:
            packet_player_id = struct.unpack_from('<I', data, 7)[0]
            current_player_id = get_character_data()['player_id']
            if packet_player_id != current_player_id:
                #log(f'[AACancel] Player ID uyuşmuyor → current_player_id: {current_player_id} | packet_player_id: {packet_player_id}')
                return True
        
        if not _is_unique_target_from_packet(data):
            return True

        formattedData = ''.join('{:02X}'.format(x) for x in data)
        Player_ID = get_character_data()['player_id']
        Packed_PlayerID = struct.pack('<I', Player_ID)
        Packed_SkillID = struct.pack('<I', Skill_ID)
        playerID_Data = ''.join('{:02X}'.format(x) for x in Packed_PlayerID)
        SkillID_Data = ''.join('{:02X}'.format(x) for x in Packed_SkillID)

        if formattedData[14:22] == playerID_Data and formattedData[6:14] == SkillID_Data:
            inject_joymax(0x7074, b'\x02', False)

            if sUseSkill:
                skills = get_skills()
                if len(data) >= 23:
                    offset = 38
                elif len(data) >= 20:
                    offset = 30
                else:
                    offset = None

                if offset is not None:
                    try:
                        bytes_data = bytes.fromhex(formattedData[offset:offset+8])
                        #log(f"bytes_data: {bytes_data.hex()}")
                    except Exception as e:
                        log(f"bytes_data alınamadı: {str(e)}")
                    for skill_id, skill_info in skills.items():
                        Frozen = skill_info['name'] in ["Frozen Spear", "Donmuş Mızrak"]
                        Charged = skill_info['name'] in ["Charged Squall", "Yüklü Fırtına"]
                        if timer is None or not Timer.is_alive(timer):
                            if Charged:
                                Skill_ID1 = struct.pack('<I', skill_id)
                                packet = b'\x01\x04' + Skill_ID1 + b'\x01' + bytes_data
                                PackedCharged2 = ''.join('{:02X}'.format(x) for x in Skill_ID1)
                                #log("Gönderilen packet (str): " + packet.hex().upper())
                                inject_joymax(0x7074, packet, False)
                            if Frozen:
                                Skill_ID2 = struct.pack('<I', skill_id)
                                packet = b'\x01\x04' + Skill_ID2 + b'\x01' + bytes_data
                                PackedCharged1 = ''.join('{:02X}'.format(x) for x in Skill_ID2)
                                #log("Gönderilen packet (str): " + packet.hex().upper())
                                inject_joymax(0x7074, packet, False)

    return True

def handle_silkroad(opcode, data):
    global sClientAttack, sDelayText

    Delay = (int(sDelayText) / 1000 if sDelayText else 0.04)  # 40 ms default

    if sClientAttack:
        if opcode == 0x7074:
            formattedData = ''.join('{:02X}'.format(x) for x in data)
            if formattedData[0:6] == '010101':
                if _is_unique_target_from_packet(data):
                    def CancelAutoAttack():
                        inject_joymax(0x7074, b'\x02', False)
                    Timer(Delay, CancelAutoAttack).start()
    return True

def IfCheckBox_Server():
    return not sAttack

def ActiveAA_Server():
    global sAttack
    if not sAttack:
        sAttack = True
        QtBind.setChecked(gui, cbxCancelAA, True)

def IfCheckBox_Client():
    return not sClientAttack

def ActiveAA_Client():
    global sClientAttack
    if not sClientAttack:
        sClientAttack = True
        QtBind.setChecked(gui, cbxCancelAA2, True)

# Başlangıçta UI’dan değerleri oku
sAttack = QtBind.isChecked(gui, cbxCancelAA)
sClientAttack = QtBind.isChecked(gui, cbxCancelAA2)
sUseSkill = QtBind.isChecked(gui, cbxUseSkill)
sDelayText = QtBind.text(gui, cleDelay).strip()

log('Plugin: '+pName+' v'+pVersion+' succesfully loaded')
