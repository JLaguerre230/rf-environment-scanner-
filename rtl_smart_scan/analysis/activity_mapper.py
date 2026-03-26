import csv
from pathlib import Path


def load_rtl_power_csv(csv_path: str) -> list[dict]:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    measurements: list[dict] = []

    with path.open("r", newline="") as f:
        reader = csv.reader(f)

        for row in reader:
            if len(row) < 7:
                continue

            date_str = row[0].strip()
            time_str = row[1].strip()
            start_hz = float(row[2])
            step_hz = float(row[4])
            powers = row[6:]

            timestamp = f"{date_str} {time_str}"
            current_hz = start_hz

            for power_str in powers:
                try:
                    power_db = float(power_str)
                except ValueError:
                    current_hz += step_hz
                    continue

                measurements.append(
                    {
                        "timestamp": timestamp,
                        "frequency_mhz": round(current_hz / 1_000_000, 6),
                        "power_db": power_db,
                    }
                )
                current_hz += step_hz

    return measurements


def summarize_activity(measurements: list[dict]) -> list[dict]:
    grouped: dict[float, dict] = {}

    for item in measurements:
        freq = item["frequency_mhz"]
        power = item["power_db"]

        if freq not in grouped:
            grouped[freq] = {
                "frequency_mhz": freq,
                "hits": 0,
                "max_power_db": power,
                "total_power_db": 0.0,
            }

        grouped[freq]["hits"] += 1
        grouped[freq]["total_power_db"] += power
        grouped[freq]["max_power_db"] = max(grouped[freq]["max_power_db"], power)

    summary: list[dict] = []
    for freq_data in grouped.values():
        avg_power = freq_data["total_power_db"] / freq_data["hits"]
        summary.append(
            {
                "frequency_mhz": freq_data["frequency_mhz"],
                "hits": freq_data["hits"],
                "max_power_db": round(freq_data["max_power_db"], 2),
                "avg_power_db": round(avg_power, 2),
            }
        )

    summary.sort(key=lambda x: x["max_power_db"], reverse=True)
    return summary



def find_active_frequencies(summary, threshold_db=-35):
    """
    Returns list of frequencies where activity is stronger than threshold
    """
    active = []

    for freq, power in summary.items():
        if power >= threshold_db:
            active.append((freq, power))

    # sort strongest first
    active.sort(key=lambda x: x[1], reverse=True)

    return active
