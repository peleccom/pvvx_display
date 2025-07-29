#coding: utf-8

from __future__ import annotations
from typing import Any

import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_ADDRESS

class PVVXDisplayFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    _discovery: BluetoothServiceInfoBleak | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            address = user_input[CONF_ADDRESS].upper()
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"PVVX {address}", data={CONF_ADDRESS: address})

        data_schema = vol.Schema({
            vol.Required(CONF_ADDRESS): cv.string
        })
        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> ConfigFlowResult:
        address = discovery_info.address.upper()

        # 1) 先绑定 unique_id（用 MAC），并防重入
        await self.async_set_unique_id(address, raise_on_progress=False)
        self._abort_if_unique_id_configured()  # 已配置或已忽略 -> 直接终止

        # 2) 可选：只处理可连接路径，避免“被动广播”反复发现
        if not discovery_info.connectable:
            return self.async_abort(reason="not_connectable")
        
        # 3) 继续到确认页
        self._discovery = discovery_info
        name = discovery_info.name or discovery_info.address

        self.context["title_placeholders"] = {"name": name}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            # 已在 bluetooth 步设置过 unique_id，这里只需创建条目
            return self.async_create_entry(
                title=self.context.get("title_placeholders", {}).get("name", "PVVX"),
                data={CONF_ADDRESS: self.unique_id},
            )
        
        address = self._discovery.address.upper()
        name = self._discovery.name or address
        return self.async_show_form(step_id="bluetooth_confirm", description_placeholders={"name": name, "address": address}, data_schema=vol.Schema({}))
