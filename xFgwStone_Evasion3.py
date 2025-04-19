from phBot import *
from threading import Timer
import random
import QtBind

pName = 'xFgwStone_Evasion3'

# GUI başlat
gui = QtBind.init(__name__, pName)

# Data kontrol GUI
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

# Radio button benzeri seçim alanı
QtBind.createLabel(gui, "Seviye Seçimi:", 430, 0)
rb1Star = QtBind.createCheckBox(gui, '', '101-110 lvl 1*', 430, 20)
rb2Star = QtBind.createCheckBox(gui, '', '101-110 lvl 2*', 430, 40)
rb3Star = QtBind.createCheckBox(gui, '', '101-110 lvl 3*', 430, 60)
rb4Star = QtBind.createCheckBox(gui, '', '101-110 lvl 4*', 430, 80)

selected_star = None

# Hedef konum ve işlem bayrakları
target_position = None
retry_count = 0
max_retry = 3
evading = False

# Etki kontrolü
from enum import IntFlag
class BadEffect(IntFlag):
    None_ = 0
    Poison = 1 << 0
    Burn = 1 << 1
    Frostbite = 1 << 2
    Zombie = 1 << 11
    Petrify = 1 << 12

previous_effect = BadEffect.None_

def handle_joymax(opcode, data):
    global evading
    if opcode == 0xB070 and len(data) >= 5:
        try:
            d0 = int(QtBind.text(gui, tbxData0))
            d1 = int(QtBind.text(gui, tbxData1))
            d3 = int(QtBind.text(gui, tbxData3))
            d4 = int(QtBind.text(gui, tbxData4))

            if data[0] == d0 and data[1] == d1 and data[3] == d3 and data[4] == d4:
                if evading:
                    return True
                log('[%s] Sereness taş saldırısı algılandı, kaçış başlatılıyor...' % pName)
                stop_bot()
                evading = True
                evade_from_stone()
        except Exception as ex:
            log('[%s] Data karşılaştırmasında hata: %s' % (pName, str(ex)))
    return True

def evade_from_stone(radius=5):
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
        move_to(new_x, new_y, pos['z'])
        sleep(1.5)
        move_to(new_x, new_y, pos['z'])        
        log('[%s] Kaçış → Yeni konum: (X:%d, Y:%d)' % (pName, new_x, new_y))
        Timer(3.0, check_if_arrived).start()
    else:
        log('[%s] Konum alınamadı, kaçış başarısız.' % pName)

def check_if_arrived():
    global target_position, retry_count, evading
    current = get_position()
    if not current or not target_position:
        return
    current_x = int(round(current['x']))
    current_y = int(round(current['y']))
    if (current_x, current_y) == target_position:
        delay = get_start_delay()
        log('[%s] Yeni konuma ulaşıldı. Bot %.1f saniye sonra yeniden başlatılacak.' % (pName, delay))
        Timer(delay, restart_bot_from_evade).start()
        target_position = None
    else:
        retry_count += 1
        if retry_count >= max_retry:
            log('[%s] Konuma ulaşamadı. Alternatif kaçış başlatılıyor...' % pName)
            force_alternate_escape()
        else:
            Timer(3.0, check_if_arrived).start()

def restart_bot_from_evade():
    global evading
    evading = False
    start_bot()
    log('[%s] Bot tekrar başlatıldı.' % pName)

def force_alternate_escape():
    global target_position
    pos = get_position()
    if pos:
        new_x = int(round(pos['x'] + random.randint(-5, 5)))
        new_y = int(round(pos['y'] + random.randint(-5, 5)))
        target_position = (new_x, new_y)
        move_to(new_x, new_y, pos['z'])
        log('[%s] Alternatif kaçış denemesi: (X:%d, Y:%d)' % (pName, new_x, new_y))
        Timer(3.0, check_if_arrived).start()
    else:
        log('[%s] Alternatif konum alınamadı. Bot güvenli şekilde başlatılıyor...' % pName)
        restart_bot_from_evade()

def get_start_delay():
    try:
        delay = float(QtBind.text(gui, tbxDelay))
        return max(0.5, delay)
    except:
        return 2.0

def get_stone_delay():
    try:
        delay = float(QtBind.text(gui, tbxStoneDelay))
        return max(0.5, delay)
    except:
        return 4.0

def event_loop():
    global previous_effect, selected_star

    # RADIO BUTTON TAKİBİ
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

    # TAŞ OLMA DURUMU KONTROLÜ
    effect_flag = get_character_data().get("bad_effects", 0)
    current_effect = BadEffect(effect_flag)
    started = ~previous_effect & current_effect

    if (started & BadEffect.Petrify) == BadEffect.Petrify:
        delay = get_stone_delay()
        log('[%s] Taş olundu. %.1f saniye beklenip sonra bot tekrar başlatılacak.' % (pName, delay))
        stop_bot()
        Timer(delay, start_bot).start()

    previous_effect = current_effect

log('[%s] Plugin yüklendi. Taş kaçışı, stun bekleme ve tekli seviye seçimi aktif.' % pName)
