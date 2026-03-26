from typing import Optional


def detect_signals_of_interest(
    summary: list[dict],
    spike_threshold_db: float = -15.0,
) -> list[dict]:
    signals: list[dict] = []

    for item in summary:
        if item["max_power_db"] >= spike_threshold_db:
            signals.append(
                {
                    "frequency_mhz": item["frequency_mhz"],
                    "hits": item["hits"],
                    "max_power_db": item["max_power_db"],
                    "avg_power_db": item["avg_power_db"],
                    "reason": f"Max power met or exceeded threshold ({spike_threshold_db} dB)",
                }
            )

    return signals


def find_auto_target(summary: list[dict], threshold_db: float) -> Optional[dict]:
    for item in summary:
        if item["max_power_db"] >= threshold_db:
            return item
    return None


def snap_frequency_to_channels(
    detected_freq_mhz: float,
    channels_mhz: list[float],
    max_delta_mhz: float = 0.015,
) -> Optional[float]:
    nearest = None
    nearest_delta = None

    for channel in channels_mhz:
        delta = abs(detected_freq_mhz - channel)

        if nearest is None or delta < nearest_delta:
            nearest = channel
            nearest_delta = delta

    if nearest is None:
        return None

    if nearest_delta is not None and nearest_delta <= max_delta_mhz:
        return nearest

    return None


def find_channel_aware_auto_target(
    summary: list[dict],
    threshold_db: float,
    channels_mhz: list[float],
    max_delta_mhz: float = 0.015,
) -> Optional[dict]:
    best_candidate = None

    for item in summary:
        if item["max_power_db"] < threshold_db:
            continue

        snapped = snap_frequency_to_channels(
            detected_freq_mhz=item["frequency_mhz"],
            channels_mhz=channels_mhz,
            max_delta_mhz=max_delta_mhz,
        )

        if snapped is None:
            continue

        candidate = {
            "detected_frequency_mhz": item["frequency_mhz"],
            "frequency_mhz": snapped,
            "hits": item["hits"],
            "max_power_db": item["max_power_db"],
            "avg_power_db": item["avg_power_db"],
            "reason": (
                f"Detected near known channel {snapped:.4f} MHz "
                f"(threshold {threshold_db:+.2f} dB)"
            ),
        }

        if best_candidate is None or candidate["max_power_db"] > best_candidate["max_power_db"]:
            best_candidate = candidate

    return best_candidate
