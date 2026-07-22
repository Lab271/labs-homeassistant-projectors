"""Pure helpers for the Vivitek "op" ASCII control protocol.

This module is deliberately free of Home Assistant (and any network) imports
so the reply-parsing logic can be unit-tested without the HA runtime. See
coordinator.py for how these are used against a live projector.
"""

ILLEGAL = "*Illegal format#"
# Values the projector reports when a reading is not yet available.
UNAVAILABLE_VALUES = {"", "NA"}

# Query commands -> key used in the coordinator's data dict.
# "op proj.runtime ?" is the only usage-hours counter the DU4371Z-ST exposes
# (lamp1.hours / light.hour etc. all return *Illegal format#).
QUERIES = {
    "power": "op status ?",
    "source_info": "op source.info ?",
    "light_mode": "op light.mode ?",
    "runtime_hours": "op proj.runtime ?",
    "input": "op input.sel ?",
}

# Input source codes reported/accepted by "op input.sel" (verified against the
# DU4371Z-ST; matches the DU7195Z laser communication manual).
INPUT_SOURCES = {
    1: "VGA1",
    6: "HDMI 1",
    9: "HDMI 2",
    15: "HDBaseT",
}


def parse_reply(key, raw):
    """Turn a raw ASCII reply into a usable value.

    Replies look like "OP STATUS = 2" or "OP SOURCE.INFO = 1920 x 1200 ...".
    During power transitions the projector may return "NA" (not yet
    available), the padded "*Illegal format#", or a stray framing byte with
    no "=" — all of which become None here.
    """
    if not raw or raw == ILLEGAL or "=" not in raw:
        return None
    value = raw.split("=", 1)[-1].strip()
    if value in UNAVAILABLE_VALUES:
        return None
    if key == "power":
        # Observed states: 0 = off/standby; 2 = on; 4/5 = warming.
        # Any non-zero numeric state means the projector is powered on.
        return value.isdigit() and value != "0"
    if key in ("light_mode", "runtime_hours"):
        try:
            return int(value)
        except ValueError:
            return None
    if key == "input":
        # Map the numeric code to a source name; unknown codes -> None.
        try:
            return INPUT_SOURCES.get(int(value))
        except ValueError:
            return None
    if key == "source_info":
        # Collapse the projector's padded spacing: "1920  x  1200  @  59.94 Hz".
        return " ".join(value.split())
    return value
