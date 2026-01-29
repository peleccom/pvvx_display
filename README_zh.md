# PVVX Display 控制集成 for Home Assistant

🌡️ *通过 Home Assistant 控制 PVVX 固件温湿度计的自定义显示内容*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python 3.13.2+](https://img.shields.io/badge/Python-3.13.2%2B-yellow.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![HomeAssistant 2025.6.0+](https://img.shields.io/badge/HomeAssistant-2025.6.0%2B-blue.svg?style=for-the-badge)](https://www.home-assistant.io/)

(English version available in [README.md](README.md))

## 🕊️ 简介

本集成为 Home Assistant 用户提供了对 **PVVX 固件版小米蓝牙温湿度计** 的 **显示内容控制能力**。
支持通过自动化、脚本等方式，发送GATT自定义显示命令，自定义设备上的：

* 主显示数字（`BigNumber`）
* 次显示数字（`SmallNumber`）
* 图标（`Icons`）
* 显示有效期（`Validity`）

*✨ 本集成基于 Home Assistant 自带的 Bluetooth Framework（`habluetooth`、`bleak`），*
*兼容官方 `BTHome` 被动广播数据接收方式，集成并存运行，不产生冲突。*


## 📦 安装

> 推荐使用 Git 克隆到自定义组件目录：

```bash
cd /config/custom_components
git clone https://github.com/peleccom/pvvx_display.git
```

或将本仓库打包为 `.zip` 后解压至 `custom_components/pvvx_display` 目录下。

然后重启 Home Assistant 即可。


## ⚙️ 配置

本集成支持两种配置方式：

### 1. 自动蓝牙发现（推荐）

* 系统启动后，Home Assistant 会自动扫描附近的 PVVX 设备（需开启蓝牙或配置蓝牙代理）
* 在“设置 > 设备与服务 > 已发现”中点击“配置”
* 确认设备后，即可完成配置

🎯 支持通过 ESPHome 设备作为 BLE Proxy 发现设备、控制设备

### 2. 手动添加

若设备未被自动发现，可手动添加：

* 打开“设置 > 设备与服务 > 添加集成”
* 选择 `PVVX Display`
* 输入设备的 MAC 地址（大写，如：`A4:C1:38:12:34:56`）

## 🛠️ 使用方式

### 1. 服务调用

* 集成将注册一个名为 `pvvx_display.show` 的服务，
* 可在`开发者工具 > 服务`中调用，或用于脚本 / 自动化中。

> 💡 支持的参数详见 `services.yaml` ，
> 或者在`开发者工具 > 服务`中搜索 `pvvx_display.show` ，查看详情.

### 2. 自动化动作

当设备被添加后，将自动注册一个 **“设备动作”** ：

* 可在自动化界面中直接选择设备和显示内容，无需手动填写地址
* 图形化编辑器将提供完整字段填写提示


## 🧊 兼容性说明

* ✅ 本集成不会与官方 `BTHome` 集成冲突，可同时使用
* ✅ 支持通过 ESPHome Bluetooth Proxy 使用，无需蓝牙适配器
* ⚠️ 连接与写入过程耗时约 **5\~10 秒**，推荐用于非实时显示（如状态提示、环境提醒等）


## 📜 许可
本集成遵循 [MIT 许可](LICENSE).
