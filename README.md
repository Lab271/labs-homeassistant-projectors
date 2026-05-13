# labs-homeassistant-projectors

Home Assistant custom integration for controlling networked projectors. Runs on the Lab271 Home Assistant instance and is also installable via HACS.

## Status

WIP. Vivitek is the only vendor wired up today (tested against the DU4371Z-ST; the same TCP control protocol covers the broader Vivitek DU/D series). The integration layout is intended to grow to additional projector vendors.

## Rename history

This repo was previously named `ha-vivitek`. It was renamed to `labs-homeassistant-projectors` to match the [Lab271 naming convention](https://github.com/LAB271/labs-infra-overview/blob/main/CONVENTIONS.md) (`labs-homeassistant-<thing>`) and to reflect the broader scope (multiple projector vendors, not just Vivitek). GitHub auto-redirects keep the old URLs working, but pinned references (HACS custom repo URLs, Ansible inventories, internal docs) should be updated to the new name.

## Scope

**In scope:**

- Home Assistant custom component for projector power control over TCP.
- Vivitek protocol today (`op power.on` / `op power.off` / `op status ?` on port 7000).
- Per-device config flow (host + name).

**Out of scope:**

- Lens / source / picture-mode control — power-only for now.
- Vendor SDKs that require cloud accounts.
- Network/AVR/matrix wiring — see the videowall and audio repos.

Adding a vendor: drop a new platform module under `custom_components/` alongside `vivitek/` and register its config flow. The `manifest.json` `domain` should match the vendor.

## Quick start

Install via HACS as a custom repository, or copy `custom_components/vivitek/` into your Home Assistant `config/custom_components/` directory and restart. Add the integration from **Settings → Devices & Services → Add Integration → Vivitek Projector** and enter the projector's host and a friendly name.

## Inventory / targets

Vivitek projectors on the Lab271 AV network (currently a DU4371Z-ST). Hosts are configured per-instance via the HA UI.

## Dependencies

- Home Assistant 2024.x or newer (config flow + `async_forward_entry_setups`).
- Network reachability from the HA host to each projector on TCP/7000.
- No external secrets or API tokens.

## Naming

Projector hostnames follow the [Lab271 naming convention](https://github.com/Lab271/labs-infra-overview/blob/main/naming.md): the `prj` class with 2-digit zero-padded numbering, e.g. `sbplabprj01`. Applies to Vivitek today and any future projector vendor this integration grows to support.

## Owner

[`@LAB271`](.github/CODEOWNERS).
