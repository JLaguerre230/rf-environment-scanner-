BAND_PRESETS = {
    "frs": {
        "start_mhz": 462.5500,
        "end_mhz": 467.7250,
        "description": "FRS/GMRS voice channels",
    },
    "gmrs": {
        "start_mhz": 462.5500,
        "end_mhz": 467.7250,
        "description": "GMRS main and interstitial channels",
    },
    "murs": {
        "start_mhz": 151.8200,
        "end_mhz": 154.6000,
        "description": "MURS VHF walkie-talkie channels",
    },
    "air": {
        "start_mhz": 118.0000,
        "end_mhz": 136.9750,
        "description": "Civil aviation voice band",
    },
    "2m": {
        "start_mhz": 144.0000,
        "end_mhz": 148.0000,
        "description": "2 meter amateur band",
    },
    "70cm": {
        "start_mhz": 420.0000,
        "end_mhz": 450.0000,
        "description": "70 centimeter amateur band",
    },
    "ism_433": {
        "start_mhz": 433.0500,
        "end_mhz": 434.7900,
        "description": "433 MHz ISM devices",
    },
    "adsb": {
        "start_mhz": 1090.0000,
        "end_mhz": 1090.0000,
        "description": "ADS-B centered on 1090 MHz",
    },
}


def list_band_presets() -> str:
    lines = []
    lines.append("Available preset bands")
    lines.append("=" * 72)
    lines.append(f"{'Name':<12} {'Start (MHz)':>12} {'End (MHz)':>12}  Description")
    lines.append("-" * 72)

    for name, info in BAND_PRESETS.items():
        lines.append(
            f"{name:<12} "
            f"{info['start_mhz']:>12.4f} "
            f"{info['end_mhz']:>12.4f}  "
            f"{info['description']}"
        )

    return "\n".join(lines)
