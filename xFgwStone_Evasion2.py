from phBot import *
from threading import Timer
import random
import QtBind

pName = 'xFgwStone_Evasion'

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

# Delay ayarı
QtBind.createLabel(gui, "Kaçıştan sonra başlatma süresi (sn):", 15, 45)
tbxDelay = QtBind.createLineEdit(gui, "2", 220, 43, 30, 16)

# Hedef konum
target_position = None
retry_count = 0
max_retry = 3

def handle_joymax(opcode, data):
    if opcode == 0xB070 and len(data) >= 5:
        try:
            d0 = int(QtBind.text(gui, tbxData0))
            d1 = int(QtBind.text(gui, tbxData1))
            d3 = int(QtBind.text(gui, tbxData3))
            d4 = int(QtBind.text(gui, tbxData4))

            if data[0] == d0 and data[1] == d1 and data[3] == d3 and data[4] == d4:
                log('[%s] Sereness taş saldırısı algılandı, kaçış başlatılıyor...' % pName)
                stop_bot()
                evade_from_stone()
        except Exception as ex:
            log('[%s] Data karşılaştırmasında hata: %s' % (pName, str(ex)))
    return True

def evade_from_stone(radius=5):
    global target_position, retry_count
    retry_count = 0
    pos = get_position()
    if pos:
        base_x = round(pos['x'])
        base_y = round(pos['y'])

        offset_x = random.uniform(-radius, radius)
        offset_y = random.uniform(-radius, radius)

        new_x = round(base_x + offset_x, 1)
        new_y = round(base_y + offset_y, 1)

        target_position = (new_x, new_y)
        move_to(new_x, new_y, pos['z'])
        log('[%s] Kaçış → Yeni konum: (X:%.1f, Y:%.1f)' % (pName, new_x, new_y))

        Timer(4.0, check_if_arrived).start()
    else:
        log('[%s] Konum alınamadı, kaçış başarısız.' % pName)

def check_if_arrived():
    global target_position, retry_count
    current = get_position()
    if not current or not target_position:
        return

    current_x = round(current['x'], 1)
    current_y = round(current['y'], 1)

    if (current_x, current_y) == target_position:
        delay = get_start_delay()
        log('[%s] Yeni konuma ulaşıldı. Bot %.1f saniye sonra yeniden başlatılacak.' % (pName, delay))
        Timer(delay, start_bot).start()
        target_position = None
    else:
        retry_count += 1
        if retry_count >= max_retry:
            log('[%s] Konuma ulaşamadı (muhtemelen stun oldu). Alternatif kaçış başlatılıyor...' % pName)
            force_alternate_escape()
        else:
            Timer(4.0, check_if_arrived).start()

def force_alternate_escape():
    global target_position
    pos = get_position()
    if pos:
        new_x = round(pos['x'] + random.uniform(-5, 5), 1)
        new_y = round(pos['y'] + random.uniform(-5, 5), 1)
        target_position = (new_x, new_y)
        move_to(new_x, new_y, pos['z'])
        log('[%s] Alternatif kaçış denemesi: (X:%.1f, Y:%.1f)' % (pName, new_x, new_y))
        Timer(4.0, check_if_arrived).start()
    else:
        log('[%s] Alternatif konum alınamadı, botu güvenli şekilde başlatıyor...' % pName)
        start_bot()

# GUI'den bekleme süresini oku
def get_start_delay():
    try:
        delay = float(QtBind.text(gui, tbxDelay))
        return max(0.5, delay)
    except:
        return 2.0

log('[%s] Plugin yüklendi. GUI aktif. Data ve bekleme süresi kullanıcı tarafından ayarlanabilir.' % pName)
