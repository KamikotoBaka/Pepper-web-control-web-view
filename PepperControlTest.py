# -*- coding: utf-8 -*-
import sys
sys.path.append("/home/dan/Downloads/pynaoqi-python2.7-2.8.7.4-linux64-20210819_141148/lib/python2.7/site-packages/")
import time
import qi
import threading
import requests
import urllib2
import json
import signal
from naoqi import ALProxy
#Wartezeit einbauen
last_command_time = 0
last_phrase = ""
COMMAND_DELAY = 3  # Sekunden warten zwischen zwei Befehlen
PHRASE_RESET_DELAY = 5 
def getState(baseURL, itemName, auth):
    url = "http://{}/rest/items/{}".format(baseURL, itemName)
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        data = response.json()
        return data.get("state", "UNDEFINED")
    except Exception as e:
        print("[Error] Initial state for {} could not be retrieved:".format(itemName), e)
        return "UNDEFINED"

def sendCommand(baseURL, itemName, command, auth):
    url = "http://{}/rest/items/{}".format(baseURL, itemName)
    headers = {"Content-Type": "text/plain"}

    try:
        response = requests.post(url, headers=headers, auth=auth, data=command)
        if response.status_code == 202:
            print("[sendCommand] {} and {}".format(itemName, command))
        else:
            print("[Error] when sendCommand for {}. Status code:".format(itemName), response.status_code)
            print("Answer:", response.text)
    except Exception as e:
        print("[Connection error] for sendCommand {}:".format(itemName), e)

def postUpdate(baseURL, itemName, state, auth):
    url = "http://{}/rest/items/{}/state".format(baseURL, itemName)
    headers = {"Content-Type": "text/plain"}

    try:
        response = requests.put(url, headers=headers, auth=auth, data=state)
        if response.status_code == 202:
            print("[postUpdate] {} and {}".format(itemName, state))
        else:
            print("[Error] when postUpdate for {}. Status code:".format(itemName), response.status_code)
            print("Answer:", response.text)
    except Exception as e:
        print("[Connection error] for postUpdate {}:".format(itemName), e)

def ItemStateEvent(baseURL, itemName, memory, auth):
    url = "http://{}/rest/events?topics=openhab/items/{}/state".format(baseURL, itemName)
    headers = {"Accept": "text/event-stream"}

    print("[Connect] Start event listener (SSE) for: {}".format(itemName))

    try:
        response = requests.get(url, headers=headers, auth=auth, stream=True)
        for line in response.iter_lines():
            if line.startswith(b"data: "):
                try:
                    payload = json.loads(line[6:])
                    if payload.get("type") == "ItemStateEvent":
                        state = json.loads(payload["payload"])["value"]
                        memory.insertData("{}_status".format(itemName), state)
                        memory.raiseEvent("{}_statusChanged".format(itemName), state)
                        print("[Event] {} and {}".format(itemName, state))
                except Exception as e:
                    print("[Error] when processing event for {}:".format(itemName), e)
    except Exception as e:
        print("[Error] Connection to event stream for {} failed:".format(itemName), e)

# OpenHAB Command
def send_openhab_command(item, command):
    url = "http://192.168.0.5:8080/rest/items/" + item
    req = urllib2.Request(url, data=command)
    req.add_header("Content-Type", "text/plain")
    try:
        response = urllib2.urlopen(req)
        return response.getcode() == 202
    except Exception as e:
        print("Fehler beim Senden:", e)
        return False
#Multipple Commands
def send_multipple_commands(items, command):
    success = True
    for item in items:
        if not send_openhab_command(item, command):
            print("Fehler beim Item:", item)
            success = False
    return success

#Ligt Controll
def all_lights_on():
    lampen = [   
    "iKueche_Hue_Lampen_Schalter","iKueche_Osram_LEDStreifen_Schalter","iBad_Hue_Lampen_Schalter",
    "iBad_Osram_LEDStreifen_Schalter","iBad_Hue_BloomLampen_Schalter","iIoT_Hue_Lampen_Schalter",
    "iIoT_Hue_LEDStreifen_Schalter","iIoT_Hue_IrisLampen_Schalter","iMultimedia_Hue_Lampen_Schalter",
    "iMultimedia_Hue_LEDStreifen_Schalter","iMultimedia_Hue_GOLampen_Schalter"
    ]
    send_multipple_commands(lampen, "ON")
    
def all_lights_off():
    lampen = [   
    "iKueche_Hue_Lampen_Schalter","iKueche_Osram_LEDStreifen_Schalter","iBad_Hue_Lampen_Schalter",
    "iBad_Osram_LEDStreifen_Schalter","iBad_Hue_BloomLampen_Schalter","iIoT_Hue_Lampen_Schalter",
    "iIoT_Hue_LEDStreifen_Schalter","iIoT_Hue_IrisLampen_Schalter","iMultimedia_Hue_Lampen_Schalter",
    "iMultimedia_Hue_LEDStreifen_Schalter","iMultimedia_Hue_GOLampen_Schalter"
    ]
    send_multipple_commands(lampen, "OFF")

def iKueche_lights_on():
    lampen = [
    "iKueche_Hue_Lampen_Schalter","iKueche_Osram_LEDStreifen_Schalter"
    ]
    send_multipple_commands(lampen, "ON")

def iKueche_lights_off():
    lampen = [   
    "iKueche_Hue_Lampen_Schalter","iKueche_Osram_LEDStreifen_Schalter"
    ]
    send_multipple_commands(lampen, "OFF")

def iBad_lights_on():
    lampen = [   
    "iBad_Hue_Lampen_Schalter","iBad_Osram_LEDStreifen_Schalter","iBad_Hue_BloomLampen_Schalter"
    ]
    send_multipple_commands(lampen, "ON")

def iBad_lights_off():
    lampen = [   
    "iBad_Hue_Lampen_Schalter","iBad_Osram_LEDStreifen_Schalter","iBad_Hue_BloomLampen_Schalter"
    ]
    send_multipple_commands(lampen, "OFF")

def iIOT_lights_on():
    lampen = [   
    "iIoT_Hue_Lampen_Schalter","iIoT_Hue_IrisLampen_Schalter","iIoT_Hue_LEDStreifen_Schalter"
    ]
    send_multipple_commands(lampen, "ON")
    
def iIOT_lights_off():
    lampen = [   
    "iIoT_Hue_Lampen_Schalter","iIoT_Hue_IrisLampen_Schalter","iIoT_Hue_LEDStreifen_Schalter"
    ]
    send_multipple_commands(lampen, "OFF")

def iMultimedia_lights_on():
    lampen = [   
    "iMultimedia_Hue_Lampen_Schalter","iMultimedia_Hue_GOLampen_Schalter","iMultimedia_Hue_LEDStreifen_Schalter"
    ]
    send_multipple_commands(lampen, "ON")

def iMultimedia_lights_off():
    lampen = [   
    "iMultimedia_Hue_Lampen_Schalter","iMultimedia_Hue_GOLampen_Schalter","iMultimedia_Hue_LEDStreifen_Schalter"
    ]
    send_multipple_commands(lampen, "OFF")
#Jalousie Controll
def iKonferenz_Rolladen_down(baseURL, auth, memory, tts=None):
    jalousItem = "iKonferenz_Somfy_Rollladen2_Steuerung"
    windowsSensorKonferenz = [  
    "iKonferenz_Homematic_Fenster4_Position","iKonferenz_Homematic_Fenster5_Position","iKonferenz_Homematic_Fenster6_Position",
    ]
    # Check all sensors
    for sensor in windowsSensorKonferenz:
        state = getState(baseURL, sensor, auth)
        print("[Sensor Check] {}: {}".format(sensor, state))
        if state == "OPEN":
            if tts:
                tts.say("Ein Fenster ist offen. Ich kann den Rollladen nicht herunterfahren.")
            else:
                print("Ein Fenster ist offen. Rollladen wird nicht bewegt.")
            return False
    # If all closed, send command
    send_openhab_command(jalousItem, "DOWN")
    if tts:
        tts.say("Ich fahre den Rollladen herunter.")
    return True
    
def iMultimedia_Rolladen_down(baseURL, auth, memory, tts=None):
    jalousItem = "iMultimedia_Somfy_Rollladen_Steuerung"
    windowsSensorMultimedia = [ 
    "iMultimedia_Homematic_Fenster1_Position","iMultimedia_Homematic_Fenster2_Position","iMultimedia_Homematic_Fenster3_Position",
    ]
    # Check all sensors
    for sensor in windowsSensorMultimedia:
        state = getState(baseURL, sensor, auth)
        print("[Sensor Check] {}: {}".format(sensor, state))
        if state != "CLOSED":
            if tts:
                tts.say("Ein Fenster ist offen. Ich kann den Rollladen nicht herunterfahren.")
            else:
                print("Ein Fenster ist offen. Rollladen wird nicht bewegt.")
            return False
    # If all closed, send command
    send_openhab_command(jalousItem, "DOWN")
    if tts:
        tts.say("Ich fahre den Rollladen herunter.")
    return True

def all_Rolladen_down(baseURL, auth, memory, tts=None):
    jalousItems = [ 
    "iKonferenz_Somfy_Rollladen2_Steuerung","iKonferenz_Somfy_Rollladen1_Steuerung","iMultimedia_Somfy_Rollladen_Steuerung"
    ]
    windowsSensorsAll = [   
    "iKonferenz_Homematic_Fenster1_Position","iKonferenz_Homematic_Fenster2_Position","iKonferenz_Homematic_Fenster3_Position",
    "iKonferenz_Homematic_Fenster4_Position","iKonferenz_Homematic_Fenster5_Position","iKonferenz_Homematic_Fenster6_Position",
    "iMultimedia_Homematic_Fenster1_Position","iMultimedia_Homematic_Fenster2_Position","iMultimedia_Homematic_Fenster3_Position",
    ]
    
    # Check all sensors
    for sensor in windowsSensorsAll:
        state = getState(baseURL, sensor, auth)
        print("[Sensor Check] {}: {}".format(sensor, state))
        if state == "OPEN":
            if tts:
                tts.say("Ein Fenster ist offen. Ich kann die Jalousien nicht herunterfahren.")
            else:
                print("Ein Fenster ist offen. Jalousien werden nicht bewegt.")
            return False
    # If all closed, send command to all Jalousie
    for jalousItem in jalousItems:
        send_openhab_command(jalousItem, "DOWN")
    if tts:
        tts.say("Ich fahre alle Jalousien herunter.")
    return True

def all_Rolladen_up(baseURL, auth, memory, tts=None):
    jalousItems = [ 
    "iKonferenz_Somfy_Rollladen2_Steuerung","iKonferenz_Somfy_Rollladen1_Steuerung","iMultimedia_Somfy_Rollladen_Steuerung"
    ]
    for jalousItem in jalousItems:
        send_openhab_command(jalousItem, "UP")
    if tts:
        tts.say("Ich fahre alle Jalousien hoch.")
    return True

def all_Rolladen_stop(baseURL, auth, memory, tts=None):
    jalousItems = [ 
    "iKonferenz_Somfy_Rollladen2_Steuerung","iKonferenz_Somfy_Rollladen1_Steuerung","iMultimedia_Somfy_Rollladen_Steuerung"
    ]
    for jalousItem in jalousItems:
        send_openhab_command(jalousItem, "STOP")
    if tts:
        tts.say("Ich habe alle Jalousien gestoppt.")
    return True
    
#Labor Light Color
def iLabor_light_color(color, baseURL, auth):
    laborLightColor = [ 
    "iMultimedia_Hue_Lampen_Farbe","iKueche_Hue_Lampen_Farbe","iBad_Hue_Lampen_Farbe",
    "iIoT_Hue_Lampen_Farbe"
    ]
    for item in laborLightColor:
        send_openhab_command(item, color)
#Labor Light Brightness
def iLabor_light_brightness(value,baseURL, auth):
    laborLightBrightness = [    
    "iKueche_Hue_Lampen_Helligkeit","iBad_Hue_Lampen_Helligkeit","iIoT_Hue_Lampen_Helligkeit",
    "iMultimedia_Hue_Lampen_Helligkeit"
    ]
    for item in laborLightBrightness:
        send_openhab_command(item, value)
    
def linkinpark(value):
    linkinparkItems =[
    "iKueche_Audio_Medialib_Morgenroutine_WhatIveDoneLinkinPark", "iBad_Audio_Medialib_Morgenroutine_WhatIveDoneLinkinPark", "iIoT_Audio_Medialib_Morgenroutine_WhatIveDoneLinkinPark", 
    "iMultimedia_Audio_Medialib_Morgenroutine_WhatIveDoneLinkinPark", "iKonferenz_Audio_Medialib_Morgenroutine_WhatIveDoneLinkinPark"
    ]
    for item in linkinparkItems:
        send_openhab_command(item, value)
    
# Speech Commands
def handle_command(phrase, tts, baseURL, auth, memory):
    
    global last_command_time, last_phrase
    now = time.time()
    if (now - last_command_time < COMMAND_DELAY) and (phrase == last_phrase):
        print("Zu schnell hintereinander, Befehl ignoriert.")
        return  # Ignore command if called too quickly

    last_command_time = now
    last_phrase = phrase
    if "Radio EIN" in phrase:
        if send_openhab_command("iKonferenz_Audio_Medialib_BuenaVistaSocialClub_BuenaVistaSocialClubDosGardenias", "ON"):
            tts.say("Ich hab das Radio Angeschaltet.")
        return
    elif "Radio AUS" in phrase:
        if send_openhab_command("iKonferenz_Audio_Medialib_BuenaVistaSocialClub_BuenaVistaSocialClubDosGardenias", "OFF"):
            tts.say("Ich hab das Radio Ausgeschaltet.")
        return
    #Light
    elif "Labor Licht EIN" in phrase:
        all_lights_on()
        tts.say("Ich hab das Licht Angeschaltet.")
        return
    elif "Labor Licht AUS" in phrase:
        all_lights_off()
        tts.say("Ich hab das Licht Ausgeschaltet.")
        return
    elif "Küche Licht EIN" in phrase:
        iKueche_lights_on()
        tts.say("Ich hab das Licht Angeschaltet.")
        return
    elif "Küche Licht AUS" in phrase:
        iKueche_lights_off()
        tts.say("Ich hab das Licht Ausgeschaltet.")
        return
    elif "Bad Licht EIN" in phrase:
        iBad_lights_on()
        tts.say("Ich hab das Licht Angeschaltet.")
        return
    elif "Bad Licht AUS" in phrase:
        iBad_lights_off()
        tts.say("Ich hab das Licht Ausgeschaltet.")
        return
    elif "IoT Licht EIN" in phrase:
        iIOT_lights_on()
        tts.say("Ich hab das Licht Angeschaltet.")
        return
    elif "IoT Licht AUS" in phrase:
        iIOT_lights_off()
        tts.say("Ich hab das Licht Ausgeschaltet.")
        return
    elif "Multimedia Licht EIN" in phrase:
        iMultimedia_lights_on()
        tts.say("Ich hab das Licht Angeschaltet.")
        return
    elif "Multimedia Licht AUS" in phrase:
        iMultimedia_lights_off()
        tts.say("Ich hab das Licht Ausgeschaltet.")
        return
    #Jalousie
    elif "Konferenz Rolladen STOPP" in phrase:
        send_openhab_command("iKonferenz_Somfy_Rollladen2_Steuerung", "STOP")
        return
    elif "Konferenz Rolladen HOCH" in phrase:
        send_openhab_command("iKonferenz_Somfy_Rollladen2_Steuerung", "UP")
        return
    elif "Konferenz Rolladen RUNTER" in phrase:                           
        iKonferenz_Rolladen_down(baseURL, auth, memory, tts)
        return
    elif "Multimedia Rolladen Runter" in phrase:
        iMultimedia_Rolladen_down(baseURL, auth, memory, tts)
        return
    elif "Multimedia Rolladen Hoch" in phrase:    
        send_openhab_command("iMultimedia_Somfy_Rollladen_Steuerung", "UP")
        return
    elif "Multimedia Rolladen Stopp" in phrase:
        send_openhab_command("iMultimedia_Somfy_Rollladen_Steuerung", "STOP") 
        return 
    elif "Alle Rolladen RUNTER" in phrase:
        all_Rolladen_down(baseURL, auth, memory, tts)
        return 
    elif "Alle Rolladen STOPP" in phrase:
        all_Rolladen_stop(baseURL, auth, memory, tts)
        return 
    elif "Alle Rolladen HOCH" in phrase:
        all_Rolladen_up(baseURL, auth, memory, tts)
        return 
    #Light Color
    elif "Multimedia Licht Farbe Rot" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Farbe", "0,100,100") 
        return
    elif "Multimedia Licht Farbe Blau" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Farbe", "240,100,100")
        return 
    elif "Multimedia Licht Farbe Grün" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Farbe", "120,100,100")
        return 
    elif "Multimedia Licht Farbe Pink" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Farbe", "330,100,100")
        return 
    elif "Multimedia Licht Farbe Gelb" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Farbe", "60,100,100")
        return 
    elif "Multimedia Licht Farbe Weiß" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Farbe", "0,0,100")
        return 
    elif "Küche Licht Farbe Rot" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Farbe", "0,100,100")
        return 
    elif "Küche Licht Farbe Blau" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Farbe", "240,100,100")
        return 
    elif "Küche Licht Farbe Grün" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Farbe", "120,100,100")
        return 
    elif "Küche Licht Farbe Pink" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Farbe", "330,100,100")
        return 
    elif "Küche Licht Farbe Gelb" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Farbe", "60,100,100")
        return 
    elif "Küche Licht Farbe Weiß" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Farbe", "0,0,100")
        return 
    elif "Bad Licht Farbe Rot" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Farbe", "0,100,100")
        return 
    elif "Bad Licht Farbe Blau" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Farbe", "240,100,100")
        return 
    elif "Bad Licht Farbe Grün" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Farbe", "120,100,100")
        return 
    elif "Bad Licht Farbe Pink" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Farbe", "330,100,100")
        return 
    elif "Bad Licht Farbe Gelb" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Farbe", "60,100,100")
        return 
    elif "Bad Licht Farbe Weiß" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Farbe", "0,0,100")
        return 
    elif "IoT Licht Farbe Rot" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Farbe", "0,100,100")
        return 
    elif "IoT Licht Farbe Blau" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Farbe", "240,100,100")
        return 
    elif "IoT Licht Farbe Grün" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Farbe", "120,100,100")
        return 
    elif "IoT Licht Farbe Pink" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Farbe", "330,100,100")
        return 
    elif "IoT Licht Farbe Gelb" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Farbe", "60,100,100")
        return 
    elif "IoT Licht Farbe Weiß" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Farbe", "0,0,100")
        return 
    elif "Labor Licht Farbe Rot" in phrase:
        iLabor_light_color("0,100,100", baseURL, auth)
        tts.say("Ich habe die Laborlichter auf Rot gestellt.")
        return
    elif "Labor Licht Farbe Blau" in phrase:
        iLabor_light_color("240,100,100", baseURL, auth)
        tts.say("Ich habe die Laborlichter auf Blau gestellt.")
        return
    elif "Labor Licht Farbe Grün" in phrase:
        iLabor_light_color("120,100,100", baseURL, auth)
        tts.say("Ich habe die Laborlichter auf Grün gestellt.")
        return
    elif "Labor Licht Farbe Pink" in phrase:
        iLabor_light_color("330,100,100", baseURL, auth)
        tts.say("Ich habe die Laborlichter auf Pink gestellt.")
        return
    elif "Labor Licht Farbe Gelb" in phrase:
        iLabor_light_color("60,100,100", baseURL, auth)
        tts.say("Ich habe die Laborlichter auf Gelb gestellt.")
        return
    elif "Labor Licht Farbe Weiß" in phrase:
        iLabor_light_color("0,0,100", baseURL, auth)
        tts.say("Ich habe die Laborlichter auf Weiß gestellt.")
        return
    #Light Brightness
    elif "Multimedia Licht Helligkeit 25" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Helligkeit", "25")
        tts.say("Ich habe die Helligkeit in Multimedia auf 25 prozent gestellt.")
        return 
    elif "Multimedia Licht Helligkeit 50" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Helligkeit", "50")
        tts.say("Ich habe die Helligkeit in Multimedia auf 50 prozent gestellt.")
        return 
    elif "Multimedia Licht Helligkeit 75" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Helligkeit", "75")
        tts.say("Ich habe die Helligkeit in Multimedia auf 75 prozent gestellt.")
        return 
    elif "Multimedia Licht Helligkeit 100" in phrase:    
        send_openhab_command("iMultimedia_Hue_Lampen_Helligkeit", "100")
        tts.say("Ich habe die Helligkeit in Multimedia auf 100 prozent gestellt.")
        return 
    elif "Küche Licht Helligkeit 25" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Helligkeit", "25")
        tts.say("Ich habe die Helligkeit in die Küche auf 25 prozent gestellt.")
        return 
    elif "Küche Licht Helligkeit 50" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Helligkeit", "50")
        tts.say("Ich habe die Helligkeit in die Küche auf 50 prozent gestellt.")
        return 
    elif "Küche Licht Helligkeit 75" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Helligkeit", "75")
        tts.say("Ich habe die Helligkeit in die Küche auf 75 prozent gestellt.")
        return 
    elif "Küche Licht Helligkeit 100" in phrase:    
        send_openhab_command("iKueche_Hue_Lampen_Helligkeit", "100")
        tts.say("Ich habe die Helligkeit in die Küche auf 100 prozent gestellt.")
        return 
    elif "Bad Licht Helligkeit 25" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Helligkeit", "25")
        tts.say("Ich habe die Helligkeit in Bad auf 25 prozent gestellt.")
        return 
    elif "Bad Licht Helligkeit 50" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Helligkeit", "50")
        tts.say("Ich habe die Helligkeit in Bad auf 50 prozent gestellt.")
        return 
    elif "Bad Licht Helligkeit 75" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Helligkeit", "75")
        tts.say("Ich habe die Helligkeit in Bad auf 75 prozent gestellt.")
        return 
    elif "Bad Licht Helligkeit 100" in phrase:    
        send_openhab_command("iBad_Hue_Lampen_Helligkeit", "100")
        tts.say("Ich habe die Helligkeit in Bad auf 100 prozent gestellt.")
        return 
    elif "IoT Licht Helligkeit 25" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Helligkeit", "25")
        tts.say("Ich habe die Helligkeit in IoT auf 25 prozent gestellt.")
        return 
    elif "IoT Licht Helligkeit 50" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Helligkeit", "50")
        tts.say("Ich habe die Helligkeit in IoT auf 50 prozent gestellt.")
        return 
    elif "IoT Licht Helligkeit 75" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Helligkeit", "75")
        tts.say("Ich habe die Helligkeit in IoT auf 75 prozent gestellt.")
        return 
    elif "IoT Licht Helligkeit 100" in phrase:    
        send_openhab_command("iIoT_Hue_Lampen_Helligkeit", "100")
        tts.say("Ich habe die Helligkeit in IoT auf 100 prozent gestellt.")
        return 
    elif "Labor Licht Helligkeit 25" in phrase:
        iLabor_light_brightness("25", baseURL, auth)
        tts.say("Ich habe die Laborlicht Helligkeit auf 25 Prozent gestellt.")
        return
    elif "Labor Licht Helligkeit 50" in phrase:
        iLabor_light_brightness("50", baseURL, auth)
        tts.say("Ich habe die Laborlicht Helligkeit auf 50 Prozent gestellt.")
        return
    elif "Labor Licht Helligkeit 75" in phrase:
        iLabor_light_brightness("75", baseURL, auth)
        tts.say("Ich habe die Laborlicht Helligkeit auf 75 Prozent gestellt.")
        return
    elif "Labor Licht Helligkeit 100" in phrase:
        iLabor_light_brightness("100", baseURL, auth)
        tts.say("Ich habe die Laborlicht Helligkeit auf 100 Prozent gestellt.")
        return
    elif "Kaffemaschiene EIN" in phrase:
        send_openhab_command("iKueche_Miele_Kaffeemaschine_Start", "ON")
        tts.say("Ich hab die Kaffeemaschine Angeschaltet.")
        return
    elif "Kaffemaschiene AUS" in phrase:    
        send_openhab_command("iKueche_Miele_Kaffeemaschine_Start", "OFF")
        tts.say("Ich hab die Kaffeemaschine Ausgeschaltet.")
        return
    elif "Lüfter EIN" in phrase:
        send_openhab_command("iKonferenz_RaumluftreinigerMQTT2_Schalten", "ON")
        tts.say("Ich hab den Lüfter Angeschaltet.")
        return
    elif "Lüfter AUS" in phrase:
        send_openhab_command("iKonferenz_RaumluftreinigerMQTT2_Schalten", "OFF")
        tts.say("Ich hab den Lüfter Ausgeschaltet.")
        return
    elif "Spiele Linkin Park" in phrase:
        linkinpark("ON")
        tts.say("Ich spiele Linkin Park.")
        return
    elif "Linkin Park AUS" in phrase:
        linkinpark("OFF")
        return
    elif "Filmabend Starten" in phrase:
        send_openhab_command("iMultimedia_SmartTV_Power", "ON")
        return
    elif "Filmabend Beenden" in phrase:
        send_openhab_command("iMultimedia_SmartTV_Power", "OFF")
        return
    else:
        tts.say("")

# Webanzeige auf Tablet # Ich hab dich nicht verstanden. Bitte wiederhol noch man
"""def show_tablet_webview(tablet_session):
    tablet_service = tablet_session.service("ALTabletService")
    try:
        url = "http://192.168.0.246:80/homecontrol.html"
        tablet_service.showWebview(url)
        print("Tablet-Webview gestartet.")
        # Aktiv lassen, bis man beendet
        

    except Exception as e:
        print("Tablet Fehler:", e)"""
    

# Speech recognition
def start_speech_recognition(speech_session, stop_event):
    ip = "192.168.0.41"
    port = 9559
    tts = speech_session.service("ALTextToSpeech")
    asr = speech_session.service("ALSpeechRecognition")
    memory = speech_session.service("ALMemory")
    #Two-stage speech recognition#
    WAKE_WORD = "Pepper"
    command_vocabulary = [
        "Radio EIN", "Radio AUS", "Labor Licht EIN", "Labor Licht AUS",
        "Küche Licht EIN", "Küche Licht AUS", "Bad Licht EIN", "Bad Licht AUS",
        "IoT Licht EIN", "IoT Licht AUS", "Multimedia Licht EIN", "Multimedia Licht AUS",
        "Konferenz Rolladen HOCH", "Konferenz Rolladen STOPP", "Konferenz Rolladen RUNTER",
        "Multimedia Rolladen Runter", "Multimedia Rolladen Stopp", "Multimedia Rolladen Hoch",
        "Multimedia Licht Farbe Rot", "Multimedia Licht Farbe Blau", "Multimedia Licht Farbe Grün",
        "Multimedia Licht Farbe Pink", "Multimedia Licht Farbe Gelb", "Multimedia Licht Farbe Weiß",
        "Labor Licht Farbe Rot", "Labor Licht Farbe Blau", "Labor Licht Farbe Grün", "Labor Licht Farbe Pink",
        "Labor Licht Farbe Gelb", "Labor Licht Farbe Weiß", "Multimedia Licht Helligkeit 25", "Multimedia Licht Helligkeit 50",
        "Multimedia Licht Helligkeit 75", "Multimedia Licht Helligkeit 100", "Küche Licht Helligkeit 25", "Küche Licht Helligkeit 50",
        "Küche Licht Helligkeit 75", "Küche Licht Helligkeit 100", "Bad Licht Helligkeit 25", "Bad Licht Helligkeit 50", "Bad Licht Helligkeit 75",
        "Bad Licht Helligkeit 100", "IoT Licht Helligkeit 25", "IoT Licht Helligkeit 50", "IoT Licht Helligkeit 75", "IoT Licht Helligkeit 100", "Küche Licht Farbe Rot",
        "Küche Licht Farbe Blau", "Küche Licht Farbe Grün", "Küche Licht Farbe Pink", "Küche Licht Farbe Gelb", "Küche Licht Farbe Weiß", "Bad Licht Farbe Rot", "Bad Licht Farbe Blau", 
        "Bad Licht Farbe Grün", "Bad Licht Farbe Pink", "Bad Licht Farbe Gelb", "Bad Licht Farbe Weiß", "IoT Licht Farbe Rot", "IoT Licht Farbe Blau", "IoT Licht Farbe Grün", "IoT Licht Farbe Pink", 
        "IoT Licht Farbe Gelb", "IoT Licht Farbe Weiß", "Alle Rolladen RUNTER", "Alle Rolladen STOPP", "Alle Rolladen HOCH", "Labor Licht Helligkeit 25", "Labor Licht Helligkeit 50", "Labor Licht Helligkeit 75",
        "Labor Licht Helligkeit 100", "Kaffemaschiene EIN", "Kaffemaschiene AUS", "Lüfter EIN", "Lüfter AUS", "Spiele Linkin Park", "Linkin Park AUS", "Filmabend Starten", "Filmabend Beenden"
    ]

    def set_vocabulary(vocab):
        asr.pause(True)
        asr.setVocabulary(vocab, False)
        asr.pause(False)
    
    set_vocabulary([WAKE_WORD])
    asr.subscribe("PepperSpeechControl")
    print("Spracherkennung gestartet. Drücke CTRL + C zum Beenden.")
    baseURL = "192.168.0.5:8080"
    auth = requests.auth.HTTPBasicAuth("openHABAdmin", "hJem2jz6")

    try:
        while not stop_event.is_set():
            try:
                data = memory.getData("WordRecognized")
            except Exception:
                time.sleep(0.1)
                continue
            if isinstance(data, list) and len(data) > 1 and data[1] > 0.4:
                print("[Spracherkennung] erkannt:", data[0])
                if data[0] == WAKE_WORD:
                    tts.say("Ja?")
                    set_vocabulary(command_vocabulary)
                    memory.removeData("WordRecognized")
                    command_start = time.time()
                    while time.time() - command_start < 7:
                        try:
                            cmd_data = memory.getData("WordRecognized")
                        except Exception:
                            time.sleep(0.1)
                            continue
                        if isinstance(cmd_data, list) and len(cmd_data) > 1 and cmd_data[1] > 0.4:
                            print("[Spracherkennung] erkannt (Befehl):", cmd_data[0])
                            asr.pause(True)
                            try:
                                handle_command(cmd_data[0], tts, baseURL, auth, memory)
                                memory.removeData("WordRecognized")
                            finally:
                                time.sleep(COMMAND_DELAY)
                                asr.pause(False)
                            break
                        time.sleep(0.1)
                    set_vocabulary([WAKE_WORD])
                    print("Sag 'Pepper', um einen Befehl zu geben.")
                else:
                    memory.removeData("WordRecognized")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Beende Spracherkennung.")
        asr.unsubscribe("PepperSpeechControl")
    finally:
        try:
            asr.pause(False)
        except Exception:
            pass

def main(session, stop_event):
    memory = session.service("ALMemory")
    tabletService = session.service("ALTabletService")

    baseURL = "192.168.0.5:8080"
    auth = requests.auth.HTTPBasicAuth("openHABAdmin", "hJem2jz6")

    # Hier Items
    items = {
        "lichtToggleKueche": "iKueche_Hue_Lampen_Schalter",
        "lichtToggleBad": "iBad_Hue_Lampen_Schalter",
        "lichtToggleIoT": "iIoT_Hue_Lampen_Schalter", 
        "lichtToggleMultimedia": "iMultimedia_Hue_Lampen_Schalter",
    }

    # Initialzustände setzen
    for buttonId, itemName in items.items():
        initialState = getState(baseURL, itemName, auth)
        memory.insertData("{}_status".format(itemName), initialState)
        print("[Initial] {} and {}".format(itemName, initialState))

    # HTML-UI anzeigen
    htmlFilePath = "http://198.18.0.1/apps/openhab_ui/openhab_ui_pepper/index.html"
    print("[Debug] Loading URL on tablet:", htmlFilePath)
    tabletService.showWebview(htmlFilePath)

    # Event-Listener für jedes Item starten
    for buttonId, itemName in items.items():
        eventThread = threading.Thread(target=ItemStateEvent, args=(baseURL, itemName, memory, auth))
        eventThread.daemon = True
        eventThread.start()
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        tabletService.hideWebview()
        print("\n[Closed] Display closed.")
    # Thread für Tablet
    #tablet_thread = threading.Thread(target=show_tablet_webview, args=(session,))
    #tablet_thread.start()

    # Sprachsteuerung starten
if __name__ == "__main__":
    session = qi.Session()
    session.connect("tcp://192.168.0.41:9559")
    stop_event = threading.Event()
    # Start speech recognition in a separate thread
    speech_thread = threading.Thread(target=start_speech_recognition, args=(session,stop_event))
    speech_thread.start()
    try:
        # Run the main function
        main(session, stop_event)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        speech_thread.join()
        