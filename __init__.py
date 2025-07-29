#coding: utf-8

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN, CONF_ADDRESS

PLATFORMS: list = []  # 这里不挂平台，不创建实体；只注册服务

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # 注册服务：pvvx_display.show 在 setup_entry 里完成（确保有 entry）
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    address: str = entry.data[CONF_ADDRESS]

    # 将此集成“附着”到同一物理设备：使用相同 connections key，避免与 BTHome 产生新的重复设备
    dev_reg = dr.async_get(hass)
    dev_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={(dr.CONNECTION_BLUETOOTH, address)},
        manufacturer="Xiaomi / PVVX",
        name=f"PVVX Display ({address})",
        model="LYWSD03MMC (PVVX)"
    )

    # 延后注册服务，确保至少有一个 entry
    async def _unregister_services():
        try:
            hass.services.async_remove(DOMAIN, "show")
        except Exception:
            pass

    from .client import async_show_display

    async def handle_show_service(call):
        await async_show_display(hass, address=call.data["address"],
                                 big=call.data.get("big_number"),
                                 small=call.data.get("small_number"),
                                 unit=call.data.get("unit", "none"),
                                 happy=call.data.get("happy", False),
                                 sad=call.data.get("sad", False),
                                 bracket=call.data.get("bracket", False),
                                 percent=call.data.get("percent", False),
                                 battery=call.data.get("battery", False),
                                 validity=call.data.get("validity", 300))

    # 只注册一次
    if not hass.services.has_service(DOMAIN, "show"):
        hass.services.async_register(DOMAIN, "show", handle_show_service)

    entry.async_on_unload(_unregister_services)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True
