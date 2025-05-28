# Smart Home Web Control for Pepper Robot

This project enables full control of a smart home lab environment using both **voice recognition** and a **web-based interface** displayed on the **Pepper robot's tablet**.

The system is designed to interact with **OpenHAB** via REST API, allowing synchronized actions via:
- Voice commands through Pepper's speech recognition system
- A responsive UI running in a WebView on Pepper’s tablet

## 🔧 Features

- 🔊 **Voice-Controlled Automation**  
  Use Pepper's voice recognition to trigger smart home actions such as turning on lights, lowering blinds, starting a meeting, etc.

- 📱 **Tablet UI Integration**  
  A fully integrated web UI is shown on Pepper’s tablet using WebView, offering manual control and feedback in real time.

- 🔄 **Synchronized Voice + Touch Control**  
  Both the UI and voice commands can control the same devices, keeping the system consistent.

- 🔐 **Login !!** 
  Change the Login and the Password for th OpenHAB

  📦 Requirements
  Pepper Robot (with Android 5.1 tablet and WebView ≤ 48)

  OpenHAB with REST API enabled

  SSH access to Pepper for file upload

  Python 2.7 installed on your development machine

  naoqi Python SDK installed (naoqi module required for ALTabletService)

  🛠️ Launch PepperControl.py
  Use your Python control script to open the WebView with the correct file path:

  ALTabletService.showWebView("HTML PATH")


  🙋
  Created by KamikotoBaka
  Smart Home Lab – Hochschule Furtwangen
