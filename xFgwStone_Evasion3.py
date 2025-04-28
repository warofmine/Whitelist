from phBot import *
from threading import Timer
import random
import QtBind
from time import sleep
import struct
import math
import phBotChat
import re

pName = 'xFgwStone_Evasion'
gui = QtBind.init(__name__, pName)

# GUI Alanlar
QtBind.createLabel(gui, "Data[0]:", 15, 15)
tbxData0 = QtBind.createLineEdit(gui, "1", 70, 13, 30, 16)

QtBind.createLabel(gui, "Data[1]:", 110, 15)
tbxData1 = QtBind.createLineEdit(gui, "0", 170, 13, 30, 16)

QtBind.createLabel(gui, "Data[3]:", 210, 15)
tbxData3 = QtBind.createLineEdit(gui, "82", 270, 13, 30, 16)

QtBind.createLabel(gui, "Data[4]:", 310, 15)
tbxData4 = QtBind.createLineEdit(gui, "128", 370, 13, 30, 16)

QtBind.createLabel(gui, "Kaçıştan sonra başlatma süresi (sn):", 15, 45)
tbxDelay = QtBind.createLineEdit(gui, "2", 220, 43, 30, 16)

QtBind.createLabel(gui, "TAŞ Delay (saniye):", 15, 70)
tbxStoneDelay = QtBind.createLineEdit(gui, "4", 140, 68, 30, 16)

QtBind.createLabel(gui, "Takip Edilecek Kişi:", 15, 100)
tbxTraceName = QtBind.createLineEdit(gui, "MerVa", 140, 98, 100, 16)

QtBind.createLabel(gui, "Yaratık İsmi:", 15, 125)
tbxTargetMob = QtBind.createLineEdit(gui, "Mangyang", 100, 123, 120, 16)

# Yeni GUI elemanları (Party Chat Dinleme Checkbox)
cbxListenPartyChat = QtBind.createCheckBox(gui, 'toggle_listen_party_chat', 'Party chati dinle', 15, 150)



QtBind.createLabel(gui, "Seviye Seçimi:", 430, 0)
rb1Star = QtBind.createCheckBox(gui, '', '101-110 lvl 1*', 430, 20)
rb2Star = QtBind.createCheckBox(gui, '', '101-110 lvl 2*', 430, 40)
rb3Star = QtBind.createCheckBox(gui, '', '101-110 lvl 3*', 430, 60)
rb4Star = QtBind.createCheckBox(gui, '', '101-110 lvl 4*', 430, 80)

selected_star = None
target_position = None
retry_count = 0
max_retry = 3
evading = False

def get_trace_target_name():
    return QtBind.text(gui, tbxTraceName).strip()

def get_start_delay():
    try:
        return max(0.5, float(QtBind.text(gui, tbxDelay)))
    except:
        return 2.0

def get_stone_delay():
    try:
        return max(0.5, float(QtBind.text(gui, tbxStoneDelay)))
    except:
        return 4.0

def is_listen_party_chat_enabled():
    return QtBind.isChecked(gui, cbxListenPartyChat)


def handle_joymax(opcode, data):
    global evading

    if opcode == 0xB070 and len(data) >= 5:
        try:
            yerim = get_position()
            anlik_x = int(round(yerim['x']))
            anlik_y = int(round(yerim['y']))
            kordinat = f"{anlik_x}, {anlik_y}"
            d0 = int(QtBind.text(gui, tbxData0))
            d1 = int(QtBind.text(gui, tbxData1))
            d3 = int(QtBind.text(gui, tbxData3))
            d4 = int(QtBind.text(gui, tbxData4))
            if data[0] == d0 and data[1] == d1 and data[3] == d3 and data[4] == d4:
                if evading:
                    return True
                phBotChat.Party(kordinat)
                evading = True
                evade_from_stone()
        except Exception as ex:
            log(f"[{pName}] Data karşılaştırmasında hata: {str(ex)}")

    elif opcode == 0x3057 and data and len(data) >= 11:
        try:
            player_id = get_character_data()['player_id']
            player_bytes = struct.pack('<I', player_id)
            if data[:3] == player_bytes[:3] and data[5] == 0x01:
                effect_byte = data[9]
                if effect_byte == 0x0A:
                    delay = get_stone_delay()
                    log(f"[{pName}] Karakter TAŞ oldu! ({delay:.1f} sn beklenip bot yeniden başlatılacak)")
                    stop_bot()
                    Timer(delay, start_bot).start()
        except Exception as e:
            log(f"[{pName}] 0x3057 analiz hatası: {str(e)}")

    return True

def get_target_monster():
    name_filter = QtBind.text(gui, tbxTargetMob).strip().lower()
    for mob in get_monsters():
        if isinstance(mob, dict) and 'name' in mob and mob['name'].lower() == name_filter:
            log("var")
            return mob
    return None



def evade_from_stone(radius=8):
    global target_position, retry_count
    retry_count = 0
    pos = get_position()
    if pos:
        base_x = int(round(pos['x']))
        base_y = int(round(pos['y']))
        offset_x = random.randint(-radius, radius)
        offset_y = random.randint(-radius, radius)
        new_x = base_x + offset_x
        new_y = base_y + offset_y
        target_position = (new_x, new_y)

        status = get_status()
        if status == "botting":
            stop_bot()
            log(f"[{pName}] Bot durduruldu. Kaçılıyor...")
        elif status == "tracing":
            stop_trace()
            log(f"[{pName}] Takip durduruldu. Kaçılıyor...")
        else:
            log(f"[{pName}] Bot pasif durumda, sadece kaçış uygulanıyor...")

        move_to(new_x, new_y, pos['z'])
        sleep(1.5)
        move_to(new_x, new_y, pos['z'])
        log(f"[{pName}] Kaçış → Yeni konum: (X:{new_x}, Y:{new_y})")

        Timer(2.0, check_if_arrived_status_aware, [status]).start()
    else:
        log(f"[{pName}] Konum alınamadı, kaçış başarısız.")

def check_if_arrived_status_aware(status):
    global target_position, retry_count, evading
    current = get_position()
    if not current or not target_position:
        return

    current_x = int(round(current['x']))
    current_y = int(round(current['y']))

    if (current_x, current_y) == target_position:
        delay = get_start_delay()
        log(f"[{pName}] Yeni konuma ulaşıldı. Bot {delay:.1f} saniye sonra yeniden başlatılacak.")
        if status == "botting":
            Timer(delay, start_bot).start()
        elif status == "tracing":
            trace_name = get_trace_target_name()
            if trace_name:
                Timer(delay, lambda: start_trace(trace_name)).start()
            else:
                log(f"[{pName}] Takip edilecek karakter ismi girilmemiş.")
        target_position = None
        evading = False
    else:
        retry_count += 1
        if retry_count >= max_retry:
            log(f"[{pName}] Konuma ulaşılamadı. Alternatif kaçış başlatılıyor...")
            force_alternate_escape()
        else:
            Timer(2.0, check_if_arrived_status_aware, [status]).start()

def force_alternate_escape():
    global target_position, evading
    pos = get_position()
    if pos:
        new_x = int(round(pos['x'] + random.randint(-5, 5)))
        new_y = int(round(pos['y'] + random.randint(-5, 5)))
        target_position = (new_x, new_y)
        move_to(new_x, new_y, pos['z'])
        log(f"[{pName}] Alternatif kaçış denemesi: (X:{new_x}, Y:{new_y})")
        Timer(2.0, check_if_arrived_status_aware, [get_status()]).start()
    else:
        log(f"[{pName}] Konum alınamadı. Bot güvenli şekilde başlatılıyor...")
        evading = False

def point_line_distance(x0, y0, x1, y1, x2, y2):
    numerator = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1)
    denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    return numerator / denominator if denominator != 0 else float('inf')

def evade_from_threat_line(x, y):
    global target_position, retry_count, evading
    retry_count = 0

    offset_x = random.choice([-10, 10])
    offset_y = random.choice([-10, 10])
    new_x = int(x + offset_x)
    new_y = int(y + offset_y)
    pos = get_position()
    if not pos:
        log(f"[{pName}] Kaçış pozisyonu alınamadı.")
        return

    z = pos['z']
    target_position = (new_x, new_y)

    # Mevcut bot durumu
    status = get_status()
    if status == "botting":
        stop_bot()
        log(f"[{pName}] Bot modu durduruldu. Kaçış başlatılıyor...")
    elif status == "tracing":
        stop_trace()
        log(f"[{pName}] Takip modu durduruldu. Kaçış başlatılıyor...")
    else:
        log(f"[{pName}] Bot zaten pasif. Kaçış uygulanıyor...")

    log(f"[{pName}] Tehlike → Kaçış pozisyonu: X:{new_x}, Y:{new_y}")
    move_to(new_x, new_y, z)

    Timer(2.0, check_if_arrived_status_aware, [status]).start()



def handle_party_message(t, player, msg):
    if player == get_character_data()['name']:
        return

    match = re.search(r'(-?\d+),\s*(-?\d+)', msg)
    if not match:
        return

    try:
        x1 = int(match.group(1))
        y1 = int(match.group(2))
        pos = get_position()
        if not pos:
            return
        x0 = pos['x']
        y0 = pos['y']
        mob = get_nearest_monster()
        if not mob:
            log(f"[{pName}] Yakın canavar tespit edilemedi.")
            return
        x2 = mob['x']
        y2 = mob['y']
        d = point_line_distance(x0, y0, x1, y1, x2, y2)
        log(f"[{pName}] Tehlike hattı uzaklığı: {d:.2f}")
        if d <= 2:
            log(f"[{pName}] Tehlike hattındasınız! Kaçış başlatılıyor...")
            evade_from_threat_line(x0, y0)
    except Exception as e:
        log(f"[{pName}] Party mesajı işlenirken hata: {str(e)}")

def event_loop():
    global selected_star

    if QtBind.isChecked(gui, rb1Star) and selected_star != 84:
        selected_star = 84
        QtBind.setChecked(gui, rb2Star, False)
        QtBind.setChecked(gui, rb3Star, False)
        QtBind.setChecked(gui, rb4Star, False)
        QtBind.setText(gui, tbxData3, str(selected_star))
    elif QtBind.isChecked(gui, rb2Star) and selected_star != 85:
        selected_star = 85
        QtBind.setChecked(gui, rb1Star, False)
        QtBind.setChecked(gui, rb3Star, False)
        QtBind.setChecked(gui, rb4Star, False)
        QtBind.setText(gui, tbxData3, str(selected_star))
    elif QtBind.isChecked(gui, rb3Star) and selected_star != 86:
        selected_star = 86
        QtBind.setChecked(gui, rb1Star, False)
        QtBind.setChecked(gui, rb2Star, False)
        QtBind.setChecked(gui, rb4Star, False)
        QtBind.setText(gui, tbxData3, str(selected_star))
    elif QtBind.isChecked(gui, rb4Star) and selected_star != 87:
        selected_star = 87
        QtBind.setChecked(gui, rb1Star, False)
        QtBind.setChecked(gui, rb2Star, False)
        QtBind.setChecked(gui, rb3Star, False)
        QtBind.setText(gui, tbxData3, str(selected_star))

# Party mesajlarını dinle
def handle_chat(t, player, msg):

    if not is_listen_party_chat_enabled():
        return  # Eğer tikli değilse hiç bir şey yapma

    if t not in [2, 4, 5]:  # Party, Union, PM
        return

    if player == get_character_data()['name']:
        return

    match = re.search(r'(-?\d+),\s*(-?\d+)', msg)
    if not match:
        return

    try:
        # Party mesajındaki koordinatlar → saldırıya uğrayan oyuncu
        x2 = int(match.group(1))
        y2 = int(match.group(2))

        # Karakterin pozisyonu
        pos = get_position()
        if not pos:
            log(f"[{pName}] Karakter pozisyonu alınamadı.")
            return
        x0 = round(pos['x'])
        y0 = round(pos['y'])

        # GUI'deki hedef yaratık adına göre boss konumunu bul
        name_filter = QtBind.text(gui, tbxTargetMob).strip().lower()
        boss = None
        for m in get_monsters().values():
            if 'name' in m and m['name'].lower() == name_filter:
                boss = m
                break

        if not boss:
            log(f"[{pName}] '{name_filter}' adlı yaratık haritada bulunamadı.")
            return

        x1 = round(boss['x'])
        y1 = round(boss['y'])

        # Point-line distance hesapla
        d = point_line_distance(x0, y0, x1, y1, x2, y2)
        log(f"[{pName}] Tehlike çizgisine olan uzaklık: {d:.2f}")

        if d <= 2:
            log(f"[{pName}] 🔺 Tehlike hattındasınız, kaçış başlatılıyor...")
            evade_from_threat_line(x0, y0)
        else:
            log(f"[{pName}] ✅ Güvendesiniz, kaçış gerekmez.")
    except Exception as e:
        log(f"[{pName}] handle_chat() hatası: {str(e)}")





log(f"[{pName}] Plugin yüklendi. Taş saldırısı, taş olma ve tehlikeli çizgi kaçışı aktif.")
