#coding: utf-8

from __future__ import annotations
import struct
from datetime import datetime, timezone

import asyncio
import logging
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth
from homeassistant.exceptions import HomeAssistantError
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache, BleakNotFoundError
from bleak import BleakError

from .const import PVVX_SERVICE_UUID, PVVX_CHAR_UUID

_LOGGER = logging.getLogger(__name__)

# 映射 unit 到位图（与 ESPHome pvvx_display 一致：单位占 cfg 的 bit5..7）
UNIT_BITS = {
    "none": 0,
    "deg_ghe": 1,
    "minus": 2,
    "deg_f": 3,
    "lowdash": 4,
    "deg_c": 5,
    "lines": 6,
    "deg_e": 7,
}

def _build_cfg(unit, happy, sad, bracket, percent, battery):
    cfg = 0
    if happy:   cfg |= 1 << 0
    if sad:     cfg |= 1 << 1
    if bracket: cfg |= 1 << 2
    if percent: cfg |= 1 << 3
    if battery: cfg |= 1 << 4
    u = UNIT_BITS.get(unit or "none", 0) & 0x7
    cfg = (cfg & 0x1F) | (u << 5)
    return cfg

async def _connect(hass: HomeAssistant, address: str) -> BleakClientWithServiceCache:
    # 从 HA 获取可连接的 BLEDevice，再用 bleak-retry-connector 稳定建立连接
    ble_device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
    if not ble_device:
        if bluetooth.async_address_present(hass, address, connectable=False):
            raise HomeAssistantError(
                f"Device {address} is present via passive scan but no connectable path is available. "
                f"Bring an active Bluetooth proxy/adapter closer, or wait for a free connection slot."
            )
        raise HomeAssistantError(
            f"Device {address} is not currently present. Wake the device (tap its button), "
            f"move it closer to a proxy/adapter, then try again."
        )
    try:
        client: BleakClientWithServiceCache = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            name=f"pvvx_display:{address}",
            timeout=10
        )
        return client
    except BleakNotFoundError as e:
        # 常见于后端没有空闲连接槽/瞬时走丢
        _LOGGER.debug("BleakNotFoundError while connecting to %s: %s", address, e)
        raise HomeAssistantError(
            f"Failed to connect to {address}: no backend path available right now. "
            f"Retry in a few seconds or reduce concurrent BLE connections."
        ) from e
    except BleakError as e:
        _LOGGER.debug("BleakError while connecting to %s: %s", address, e)
        raise HomeAssistantError(f"Bluetooth error while connecting to {address}: {e}") from e
    except asyncio.TimeoutError as e:
        raise HomeAssistantError(f"Timed out connecting to {address} (10s)") from e

async def async_show_display(
    hass: HomeAssistant,
    address: str,
    big: float, small: int, unit: str,
    happy: bool, sad: bool, bracket: bool, percent: bool, battery: bool,
    validity: int
):
    client = await _connect(hass, address)
    try:
        # 按 ESPHome 实现：首字节 0x22，随后 bignum(×10, uint16 LE)、smallnum(uint16 LE)、
        # 有效期(uint16 LE)、cfg(uint8)
        bign = int(round((big or 0) * 10))
        smal = int(small or 0) & 0xFFFF
        vali = int(validity or 300) & 0xFFFF
        cfg  = _build_cfg(unit, happy, sad, bracket, percent, battery) & 0xFF

        payload = struct.pack("<BHHHB", 0x22, bign & 0xFFFF, smal, vali, cfg)
        await client.write_gatt_char(PVVX_CHAR_UUID, payload, response=False)
    finally:
        await client.disconnect()
