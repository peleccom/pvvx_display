# PVVX Display Control Integration for Home Assistant

🌡️ *Control custom display content on PVVX firmware Xiaomi BLE thermometers directly from Home Assistant*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python 3.13.2+](https://img.shields.io/badge/Python-3.13.2%2B-yellow.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![HomeAssistant 2025.6.0+](https://img.shields.io/badge/HomeAssistant-2025.6.0%2B-blue.svg?style=for-the-badge)](https://www.home-assistant.io/)

[中文版本请点击这里](README_zh.md)


## 🕊️ Introduction

This custom integration enables Home Assistant users to **send custom display content** to Xiaomi thermometers flashed with the **PVVX firmware**.

You can send GATT write commands to display:

* `BigNumber` (Main value)
* `SmallNumber` (Secondary text)
* `Icon` (Emoji or symbol)
* `Validity` (Display timeout duration in seconds)

✨ Built upon Home Assistant’s native Bluetooth Framework (`habluetooth`, `bleak`),
this integration **coexists perfectly with the official `BTHome` passive broadcast receiver** -- no conflict, seamless coexistence.


## 📦 Installation

### HACS (Recommended)

Install in HACS with button:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=peleccom&repository=pvvx_display&category=integration)

or

1. Open HACS in Home Assistant
1. Go to "Integrations"
1. Click the three dots in the top right and select "Custom repositories"
1. Add this repository URL: https://github.com/Angelic47/pvvx_display
Select category "Integration"
Click "Install"
Restart Home Assistant

# Manual installation

> Recommended: Clone directly into your Home Assistant custom components directory

```bash
cd /config/custom_components
git clone https://github.com/Angelic47/pvvx_display.git
```

Alternatively, you may download this repo as `.zip` and extract it to:
`/config/custom_components/pvvx_display`

Then restart Home Assistant.


## ⚙️ Configuration

This integration supports two setup methods:

### 1. Automatic Bluetooth Discovery (Recommended)

* Home Assistant will automatically scan for nearby PVVX devices (requires Bluetooth enabled or configured BLE proxy)
* Navigate to *Settings > Devices & Services > Discovered* and click **Configure**
* Confirm the device to finish setup

🎯 Supports ESPHome Bluetooth Proxy for remote discovery and control

### 2. Manual Entry

If the device is not auto-discovered:

* Go to *Settings > Devices & Services > Add Integration*
* Search for `PVVX Display`
* Enter the device MAC address in uppercase (e.g., `A4:C1:38:12:34:56`)


## 🛠️ Usage

### 1. Service Call

This integration registers a service called `pvvx_display.show`.

* Can be used via *Developer Tools > Services* or within automations and scripts
* You can specify the device address and display contents directly

> 💡 Supported parameters are listed in `services.yaml`,
> or search for `pvvx_display.show` in the Developer Tools UI for schema details.

### 2. Automation Action

Once a device is configured, it also provides a **device action**:

* Can be used in automations via UI without entering the MAC address manually
* The graphical editor provides field hints and full support


## 🧊 Compatibility Notes

* ✅ Fully compatible with the official `BTHome` integration (no conflict)
* ✅ Works with ESPHome Bluetooth Proxy (no onboard adapter required)
* ⚠️ Connection and write typically take **5–10 seconds**,
  suitable for status messages, ambient updates, or light display tasks (not for real-time switching)


## 📜 License

This project is licensed under the [MIT License](LICENSE).
