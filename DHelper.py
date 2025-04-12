from phBot import *
import QtBind
from threading import Timer
from time import sleep
import sqlite3
import json
import random
import os

# Globals
pVersion, pName = '0.0.1', 'DHelper'
Continue, Count = 0, 0
timer, Inside, DimensionalActivated = None, False, False
noNDimensionalHole, SkipCommand = False, False
gui = QtBind.init(__name__, pName)

# UI Setup
lbl = [QtBind.createLabel(gui, label, x, y) for label, x, y in [
    ('#less is more flexible', 580, 273),  
    ('#İletişim için DC: _recep', 625, 293),
    ('# Add monster names to ignore #\n# from Monster Counter #', 31, 6)
]]

tbxMobs = QtBind.createLineEdit(gui, "", 31, 35, 100, 20)
lstMobs = QtBind.createList(gui, 31, 56, 176, 203)
btnAddMob = QtBind.createButton(gui, 'btnAddMob_clicked', " Add ", 132, 34)
btnRemMob = QtBind.createButton(gui, 'btnRemMob_clicked', "Remove Monster", 119, 258)

# Ayar Fonksiyonu Düzenlemesi
def Settings():
    Leader = LeaderSelection()
    x, y = get_position().values()
    conditions = [
        (x > 7298 and x < 12095 and y > 4026 and y < 6534, "Holy Water Temple"),
        (x > 16316 and x < 22659 and y > 2310 and y < 4997, "Forgotten World")
    ]
    for cond, label in conditions:
        if cond:
            updateSettings(label)

def updateSettings(label):
    QtBind.setText(gui, lblSettings, label)
    saveConfigs()
    log(f"Plugin: DHelper'ın Ayarları [ {label} ] için ayarlandı.")

# Profil Senkronizasyonu Düzenlemesi
def SyncProfile():
    Profile = get_profile()
    ProfileFGW = "FGW"
    DefaultProfile = str(QtBind.text(gui, txtFGWPROFILE)) or ProfileFGW
    if Profile == DefaultProfile:
        return 1
    return 0

# Lider ve Parti Sayımı Düzenlemesi
def LeaderSelection():
    name = get_character_data()['name']
    return any(
        player['leader'] and player['name'] == name for player in get_party().values()
    )

def party_count():
    return sum(1 for _ in get_party().values())

# Zamanlayıcı Düzenlemesi
def onSaveButtonClicked():
    global timer
    if timer is None or not timer.is_alive():
        timer = Timer(0.5, saveConfigs)
        timer.start()
        log('Plugin: Your Profile Name has been saved.')
