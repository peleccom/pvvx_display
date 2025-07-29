#coding: utf-8
from __future__ import annotations

import voluptuous as vol
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import HomeAssistant, Context
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import config_validation as cv
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

# 你要提供的动作类型
ACTION_TYPES = {"show"}

UNIT_VALUES = ["none", "deg_c", "deg_f", "minus", "lines", "lowdash", "deg_ghe", "deg_e"]

# 基础 schema + 可选的“额外字段”
ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend({
    vol.Required(CONF_TYPE): vol.In(ACTION_TYPES),
    
    vol.Optional("big_number"): vol.Coerce(float),
    vol.Optional("small_number"): vol.Coerce(int),
    vol.Optional("unit"): vol.In(UNIT_VALUES),

    vol.Optional("happy"): cv.boolean,
    vol.Optional("sad"): cv.boolean,
    vol.Optional("bracket"): cv.boolean,
    vol.Optional("percent"): cv.boolean,
    vol.Optional("battery"): cv.boolean,

    vol.Optional("validity"): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
})

def _address_from_device(hass: HomeAssistant, device_id: str) -> str:
    """从 device_id 查 BLE 地址（connections 里的 bluetooth）。"""
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)
    if not device:
        raise HomeAssistantError(f"Device {device_id} not found")

    for conn in device.connections:
        if conn[0] == dr.CONNECTION_BLUETOOTH:
            return conn[1]

    # 允许用 identifiers 兜底（你在 __init__ 里也写了 (DOMAIN, address)）
    for ident in device.identifiers:
        if ident[0] == DOMAIN:
            return ident[1]

    raise HomeAssistantError(
        "This device has no Bluetooth address associated. "
        "Re-add the device or move it closer to a Bluetooth proxy."
    )

# ② 给到 UI 的“这个设备有哪些动作”列表
async def async_get_actions(hass: HomeAssistant, device_id: str) -> list[dict]:
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)
    if not device:
        return []

    # 仅当该 device 由本集成的某个 config_entry 提供时才暴露动作
    entry_ids = {e.entry_id for e in hass.config_entries.async_entries(DOMAIN)}
    if not (entry_ids & set(device.config_entries)):
        return []

    actions = []
    for typ in ACTION_TYPES:
        actions.append({
            CONF_DOMAIN: DOMAIN,
            "device_id": device_id,
            CONF_TYPE: typ,
        })
    return actions

# ③ 执行动作：把 device_id 解析为地址，转成你现有的服务调用即可
async def async_call_action_from_config(
    hass: HomeAssistant, config: dict, variables: dict, context: Context | None
) -> None:
    config = ACTION_SCHEMA(config)  # 让核心套用 schema
    device_id = config[CONF_DEVICE_ID]
    action_type = config[CONF_TYPE]

    address = _address_from_device(hass, device_id)

    if action_type == "show":
        # 允许在动作里直接填写额外字段（都可选）
        data = {"address": address}
        # 从 config 里拷贝用户填写的“额外字段”（如果有）
        for key in (
            "big_number", "small_number", "unit",
            "happy", "sad", "bracket", "percent", "battery",
            "validity",
        ):
            if key in config:
                data[key] = config[key]

        await hass.services.async_call(
            DOMAIN, "show", data, blocking=True, context=context
        )
        return

    raise HomeAssistantError(f"Unknown device action type: {action_type}")

# ④（可选）给 UI 提供“额外字段”的能力/表单（不同动作展示不同字段）
async def async_get_action_capabilities(hass: HomeAssistant, config: dict) -> dict:
    action_type = config.get(CONF_TYPE)
    if action_type == "show":
        return {
            "extra_fields": vol.Schema({
                vol.Optional("big_number"): vol.Coerce(float),
                vol.Optional("small_number"): vol.Coerce(int),
                vol.Optional("unit"): vol.In([
                    "none", "deg_c", "deg_f", "minus", "lines", "lowdash", "deg_ghe", "deg_e"
                ]),
                vol.Optional("happy"): cv.boolean,
                vol.Optional("sad"): cv.boolean,
                vol.Optional("bracket"): cv.boolean,
                vol.Optional("percent"): cv.boolean,
                vol.Optional("battery"): cv.boolean,
                vol.Optional("validity"): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            })
        }
    
    return {}  # 默认无额外字段
