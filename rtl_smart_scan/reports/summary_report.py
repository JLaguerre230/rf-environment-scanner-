from datetime import datetime
from pathlib import Path


def format_db(value: float) -> str:
    return f"{value:+.2f} dB"


def save_text_summary(
    summary: list[dict],
    signals_of_interest: list[dict],
    start_mhz: float,
    end_mhz: float,
    duration_seconds: int,
    output_dir: str = "output",
    mode_label: str = "Single Run",
    band_label: str | None = None,
) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "latest_summary.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = []
    lines.append("RTL Smart Scan Report")
    lines.append("=" * 72)
    lines.append(f"Generated : {timestamp}")
    lines.append(f"Mode      : {mode_label}")
    if band_label:
        lines.append(f"Band      : {band_label}")
    lines.append(f"Range     : {start_mhz:.6f} MHz -> {end_mhz:.6f} MHz")
    lines.append(f"Duration  : {duration_seconds} seconds")
    lines.append("")

    lines.append("Top Detected Frequencies")
    lines.append("-" * 72)
    lines.append(
        f"{'#':<4}"
        f"{'Frequency (MHz)':<18}"
        f"{'Hits':<8}"
        f"{'Max Power':<18}"
        f"{'Avg Power':<18}"
    )
    lines.append("-" * 72)

    if not summary:
        lines.append("No frequency activity parsed.")
    else:
        for idx, item in enumerate(summary[:20], start=1):
            lines.append(
                f"{idx:<4}"
                f"{item['frequency_mhz']:<18.6f}"
                f"{item['hits']:<8}"
                f"{format_db(item['max_power_db']):<18}"
                f"{format_db(item['avg_power_db']):<18}"
            )

    lines.append("")
    lines.append("Signals of Interest")
    lines.append("-" * 72)

    if not signals_of_interest:
        lines.append("None above threshold.")
    else:
        lines.append(
            f"{'#':<4}"
            f"{'Frequency (MHz)':<18}"
            f"{'Hits':<8}"
            f"{'Max Power':<18}"
            f"{'Avg Power':<18}"
            f"Reason"
        )
        lines.append("-" * 72)

        for idx, item in enumerate(signals_of_interest, start=1):
            lines.append(
                f"{idx:<4}"
                f"{item['frequency_mhz']:<18.6f}"
                f"{item['hits']:<8}"
                f"{format_db(item['max_power_db']):<18}"
                f"{format_db(item['avg_power_db']):<18}"
                f"{item['reason']}"
            )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
