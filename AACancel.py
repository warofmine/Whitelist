from phBot import *
import QtBind
import struct
from threading import Timer

pName = 'AACancel'
pVersion = '0.0.1'
gui = QtBind.init(__name__,pName)

timer = None
timer2 = None
timer3 = None
PackedCharged1 = '0101010101'
PackedCharged2 = '0101010101'
PackedCharged3 = '0101010101'

cbxCancelAA = QtBind.createCheckBox(gui, 'cbxCancel_clicked',' Cancel Auto Attack (Server)',5,5)
cbxUseSkill = QtBind.createCheckBox(gui, 'cbxUseSkill_clicked',' Use Skill',170,5)
cbxCancelAA2 = QtBind.createCheckBox(gui, 'cbxCancel2_clicked',' Cancel Auto Attack (Client)  Delay :               ms ',5,22)
# Varsayılan 40 ms (0.04 s)
cleDelay = QtBind.createLineEdit(gui,"40",200,20,35,20)

def cbxCancel_clicked(checked):
    if QtBind.isChecked(gui,cbxCancelAA2):
        QtBind.setChecked(gui,cbxCancelAA2,False)
def cbxCancel2_clicked(checked):
    if QtBind.isChecked(gui,cbxCancelAA):
        QtBind.setChecked(gui,cbxCancelAA,False)

# --- sadece uniq filtre ---
def _is_unique_target_from_packet(data):
    try:
        target_id = None

        if len(data) >= 23:
            target_id = struct.unpack_from('<I', data, 19)[0]
        elif len(data) >= 20:
            log('data yeterli')
            target_id = struct.unpack_from('<I', data, 15)[0]

        if target_id is not None:
            monsters = get_monsters()
            mob = monsters.get(target_id, None)
            if mob:
                log(f"Target ID: {target_id} | Mob: {mob['name']} | Type: {mob['type']}")
                if mob.get('type') == 3:  # 3 = Unique
                    return True

    except Exception as e:
        log(f"Hata (uniq kontrol): {str(e)}")

    return True  # Unique değilse engelle

def handle_joymax(opcode, data):
    Enabled = QtBind.isChecked(gui,cbxCancelAA)
    UseSkill = QtBind.isChecked(gui,cbxUseSkill)
    delay_text = QtBind.text(gui, cleDelay).strip()

    if delay_text and int(delay_text) != 1221:
        return True
        
    if Enabled:
        if opcode == 0xB070:
            # sadece uniq ise devam
            if not _is_unique_target_from_packet(data):
                log("yok")
                return True
            global timer, timer2, timer3, PackedCharged1, PackedCharged2, PackedCharged3
            formattedData = ''.join('{:02X}'.format(x) for x in data)
            Player_ID = get_character_data()['player_id']
            Skill_ID = 8454
            Packed_PlayerID = struct.pack('<I', Player_ID)
            Packed_SkillID = struct.pack('<I', Skill_ID)
            playerID_Data = ''.join('{:02X}'.format(x) for x in Packed_PlayerID)
            SkillID_Data = ''.join('{:02X}'.format(x) for x in Packed_SkillID)
            if formattedData[14:22] == playerID_Data and formattedData[6:14] == SkillID_Data:
                inject_joymax(0x7074, b'\x02', False)
                if UseSkill:
                    skills = get_skills()
                    # data uzunluğuna göre offset belirle
                    if len(data) >= 23:
                        offset = 38
                    elif len(data) >= 20:
                        offset = 30
                    else:
                        offset = None

                    if offset is not None:
                        try:
                            bytes_data = bytes.fromhex(formattedData[offset:offset+8])
                            log(f"bytes_data: {bytes_data.hex()}")
                        except Exception as e:
                            log(f"bytes_data alınamadı: {str(e)}")
                        for skill_id, skill_info in skills.items():
                            Frozen = skill_info['name'] in ["Frozen Spear","Donmuş Mızrak"]
                            Charged = skill_info['name'] in ["Charged Wind","Yüklü Rüzgar"]
                            if timer is None or not Timer.is_alive(timer):
                                if Charged:
                                    Skill_ID1 = struct.pack('<I', skill_id)
                                    #log(f"Skill_ID2: {Skill_ID2.hex().upper()} = {skill_id}")
                                    packet = b'\x01\x04' + Skill_ID1 + b'\x01' + bytes_data
                                    PackedCharged2 = ''.join('{:02X}'.format(x) for x in Skill_ID1)
                                    log("Gönderilen packet (str): " + packet.hex().upper())
                                    inject_joymax(0x7074,packet,False)
                                if Frozen:
                                    Skill_ID2 = struct.pack('<I', skill_id)
                                    #log(f"Skill_ID2: {Skill_ID2.hex().upper()} = {skill_id}")
                                    packet = b'\x01\x04' + Skill_ID2 + b'\x01' + bytes_data
                                    PackedCharged1 = ''.join('{:02X}'.format(x) for x in Skill_ID2)
                                    log("Gönderilen packet (str): " + packet.hex().upper())
                                    inject_joymax(0x7074,packet,False)
                                
    return True

def handle_silkroad(opcode, data):
    Enabled = QtBind.isChecked(gui,cbxCancelAA2)
    Delay = ( int(QtBind.text(gui,cleDelay)) / 1000 if QtBind.text(gui,cleDelay) else 0.04 ) # 40 ms
    if Enabled:
        if opcode == 0x7074:
            formattedData = ''.join('{:02X}'.format(x) for x in data)
            if formattedData[0:6] == '010101':
                # sadece uniq ise iptal et
                if _is_unique_target_from_packet(data):
                    def CancelAutoAttack():
                        inject_joymax(0x7074,b'\x02',False)
                    Timer(Delay, CancelAutoAttack).start()
    return True

def IfCheckBox_Server():
    return not QtBind.isChecked(gui,cbxCancelAA)

def ActiveAA_Server():
    if not QtBind.isChecked(gui,cbxCancelAA):
        QtBind.setChecked(gui,cbxCancelAA,True)

def IfCheckBox_Client():
    return not QtBind.isChecked(gui,cbxCancelAA2)

def ActiveAA_Client():
    if not QtBind.isChecked(gui,cbxCancelAA2):
        QtBind.setChecked(gui,cbxCancelAA2,True)

log('Plugin: '+pName+' v'+pVersion+' succesfully loaded')
