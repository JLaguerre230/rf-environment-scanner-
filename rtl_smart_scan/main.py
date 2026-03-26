import argparse
import sys
import time

from scanner.rtl_power_runner import run_rtl_power_scan
from scanner.band_presets import BAND_PRESETS, list_band_presets
from scanner.channel_presets import CHANNEL_PRESETS
from analysis.activity_mapper import load_rtl_power_csv, summarize_activity
from analysis.signal_detector import (
    detect_signals_of_interest,
    find_auto_target,
    find_channel_aware_auto_target,
)
from reports.summary_report import save_text_summary

try:
    from listener.rtl_listener import listen_frequency
except ImportError:
    listen_frequency = None


def format_db(value: float) -> str:
    return f"{value:+.2f} dB"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a user-defined RF range or preset band, summarize activity, and optionally auto-follow signals."
    )

    parser.add_argument("--start", type=float, help="Start frequency in MHz, e.g. 462.5625")
    parser.add_argument("--end", type=float, help="End frequency in MHz, e.g. 462.7125")
    parser.add_argument("--band", type=str, help="Preset band name, e.g. frs, murs, air, 2m")
    parser.add_argument("--list-bands", action="store_true", help="Show available preset bands and exit")

    parser.add_argument("--gain", type=float, default=20.0, help="RTL-SDR tuner gain in dB")
    parser.add_argument("--duration", type=int, default=15, help="Scan duration in seconds for one cycle")
    parser.add_argument("--interval", type=int, default=10, help="rtl_power reporting interval in seconds")
    parser.add_argument("--bin-size", type=int, default=12500, help="FFT bin size in Hz")
    parser.add_argument("--top", type=int, default=10, help="Number of top frequencies to display")

    parser.add_argument("--live", action="store_true", help="Run continuously until stopped with Ctrl+C")

    parser.add_argument(
        "--spike-threshold",
        type=float,
        default=-15.0,
        help="Minimum max power in dB to mark a signal as a signal of interest in reports",
    )

    parser.add_argument("--listen", action="store_true", help="Enable listening mode")
    parser.add_argument("--auto", action="store_true", help="When used with --listen, auto-follow detected activity")
    parser.add_argument(
        "--threshold",
        type=float,
        default=-35.0,
        help="Minimum max power in dB required for auto-follow listening",
    )
    parser.add_argument(
        "--listen-mode",
        type=str,
        default="nfm",
        help="rtl_fm demod mode for listening, e.g. nfm, am, wfm",
    )
    parser.add_argument(
        "--listen-gain",
        type=float,
        default=35.0,
        help="Gain used in listen mode",
    )
    parser.add_argument(
        "--audio-device",
        type=str,
        default="hw:2,0",
        help="Audio output device for aplay, e.g. hw:2,0",
    )

    args = parser.parse_args()

    if args.list_bands:
        return args

    if args.band:
        if args.band not in BAND_PRESETS:
            parser.error(f"Unknown band preset: {args.band}")
    else:
        if args.start is None or args.end is None:
            parser.error("You must provide either --band OR both --start and --end")

        if args.start >= args.end:
            parser.error("--start must be lower than --end")

    if args.duration <= 0:
        parser.error("--duration must be greater than 0")

    if args.interval <= 0:
        parser.error("--interval must be greater than 0")

    if args.bin_size <= 0:
        parser.error("--bin-size must be greater than 0")

    if args.top <= 0:
        parser.error("--top must be greater than 0")

    if args.auto and not args.listen:
        parser.error("--auto requires --listen")

    return args


def resolve_scan_range(args: argparse.Namespace) -> tuple[float, float, str | None]:
    if args.band:
        info = BAND_PRESETS[args.band]
        return info["start_mhz"], info["end_mhz"], args.band

    return args.start, args.end, None


def print_summary(summary: list[dict], top_n: int) -> None:
    print("\n[+] Top detected frequencies")
    print("-" * 72)
    print(
        f"{'#':<4}"
        f"{'Frequency (MHz)':<18}"
        f"{'Hits':<8}"
        f"{'Max Power':<18}"
        f"{'Avg Power':<18}"
    )
    print("-" * 72)

    if not summary:
        print("No data parsed.")
        return

    for idx, item in enumerate(summary[:top_n], start=1):
        print(
            f"{idx:<4}"
            f"{item['frequency_mhz']:<18.6f}"
            f"{item['hits']:<8}"
            f"{format_db(item['max_power_db']):<18}"
            f"{format_db(item['avg_power_db']):<18}"
        )


def print_signals_of_interest(signals: list[dict]) -> None:
    print("\n[+] Signals of interest")
    print("-" * 72)

    if not signals:
        print("None above threshold.")
        return

    print(
        f"{'#':<4}"
        f"{'Frequency (MHz)':<18}"
        f"{'Hits':<8}"
        f"{'Max Power':<18}"
        f"{'Avg Power':<18}"
        f"Reason"
    )
    print("-" * 72)

    for idx, item in enumerate(signals, start=1):
        print(
            f"{idx:<4}"
            f"{item['frequency_mhz']:<18.6f}"
            f"{item['hits']:<8}"
            f"{format_db(item['max_power_db']):<18}"
            f"{format_db(item['avg_power_db']):<18}"
            f"{item['reason']}"
        )


def maybe_auto_listen(args: argparse.Namespace, summary: list[dict], band_label: str | None) -> None:
    if not args.listen or not args.auto:
        return

    if listen_frequency is None:
        print("\n[!] Listen mode requested, but listener/rtl_listener.py is missing.")
        return

    target = None

    if band_label and band_label in CHANNEL_PRESETS:
        target = find_channel_aware_auto_target(
            summary=summary,
            threshold_db=args.threshold,
            channels_mhz=CHANNEL_PRESETS[band_label],
            max_delta_mhz=0.015,
        )

        if target is not None:
            print(
                f"\n[AUTO] Channel-aware target selected -> "
                f"detected {target['detected_frequency_mhz']:.6f} MHz, "
                f"snapped to {target['frequency_mhz']:.6f} MHz"
            )

    if target is None:
        target = find_auto_target(summary, args.threshold)

        if target is not None:
            print(
                f"\n[AUTO] Generic target selected -> "
                f"{target['frequency_mhz']:.6f} MHz "
                f"(max={format_db(target['max_power_db'])})"
            )

    if target is None:
        print(f"\n[AUTO] No signal met the auto-follow threshold ({args.threshold:+.2f} dB).")
        return

    listen_frequency(
        freq_mhz=target["frequency_mhz"],
        mode=args.listen_mode,
        gain=args.listen_gain,
        audio_device=args.audio_device,
    )


def run_once(args: argparse.Namespace) -> None:
    start_mhz, end_mhz, band_label = resolve_scan_range(args)

    csv_path = run_rtl_power_scan(
        start_mhz=start_mhz,
        end_mhz=end_mhz,
        bin_size_hz=args.bin_size,
        integration_seconds=args.interval,
        gain=args.gain,
        output_dir="data/raw",
        duration_seconds=args.duration,
    )

    measurements = load_rtl_power_csv(str(csv_path))
    summary = summarize_activity(measurements)
    signals = detect_signals_of_interest(summary, spike_threshold_db=args.spike_threshold)

    print(f"\n[*] Raw CSV saved to: {csv_path}")
    print(f"[*] Measurements parsed: {len(measurements)}")
    print(f"[*] Unique frequency bins summarized: {len(summary)}")

    print_summary(summary, args.top)
    print_signals_of_interest(signals)

    report_path = save_text_summary(
        summary=summary,
        signals_of_interest=signals,
        start_mhz=start_mhz,
        end_mhz=end_mhz,
        duration_seconds=args.duration,
        output_dir="output",
        mode_label="Live Monitoring" if args.live else "Single Run",
        band_label=band_label,
    )

    print(f"\n[+] Summary report saved to: {report_path}")

    maybe_auto_listen(args, summary, band_label)


def main() -> int:
    args = parse_args()

    if args.list_bands:
        print(list_band_presets())
        return 0

    start_mhz, end_mhz, band_label = resolve_scan_range(args)

    print("[*] RTL Smart Scan")
    if band_label:
        print(f"[*] Band preset: {band_label}")
        if band_label in CHANNEL_PRESETS:
            print("[*] Channel-aware follow: enabled")
        else:
            print("[*] Channel-aware follow: generic mode")
    print(f"[*] Range: {start_mhz:.6f} MHz -> {end_mhz:.6f} MHz")
    print(f"[*] Gain: {args.gain:.2f} dB")
    print(f"[*] Duration: {args.duration} seconds")
    print(f"[*] Interval: {args.interval} seconds")
    print(f"[*] Bin size: {args.bin_size} Hz")
    print(f"[*] Mode: {'live' if args.live else 'single run'}")

    if args.listen:
        print("[*] Listen mode enabled: yes")
        print(f"[*] Auto-follow: {'yes' if args.auto else 'no'}")
        print(f"[*] Auto threshold: {args.threshold:+.2f} dB")
        print(f"[*] Listen demod mode: {args.listen_mode}")
        print(f"[*] Listen gain: {args.listen_gain:.2f} dB")
        print(f"[*] Audio device: {args.audio_device}")

    try:
        if args.live:
            cycle = 1
            while True:
                print(f"\n{'=' * 72}")
                print(f"[*] Live cycle #{cycle}")
                run_once(args)
                cycle += 1
                time.sleep(1)
        else:
            run_once(args)

    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
        return 0
    except Exception as exc:
        print(f"\n[!] Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
