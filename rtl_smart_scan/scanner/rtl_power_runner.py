import subprocess
from datetime import datetime
from pathlib import Path


def run_rtl_power_scan(
    start_mhz: float,
    end_mhz: float,
    bin_size_hz: int,
    integration_seconds: int,
    gain: float,
    output_dir: str = "data/raw",
    duration_seconds: int = 15,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{start_mhz:.6f}_{end_mhz:.6f}_{timestamp}.csv"
    csv_path = output_path / filename

    command = [
        "rtl_power",
        "-f",
        f"{start_mhz}M:{end_mhz}M:{bin_size_hz}",
        "-i",
        str(integration_seconds),
        "-g",
        str(gain),
        str(csv_path),
    ]

    print("\n[*] Running scan...")
    print("[*] Command:", " ".join(command))
    print(f"[*] Scan duration: {duration_seconds} seconds")

    try:
        process = subprocess.Popen(command)
        process.wait(timeout=duration_seconds)
    except subprocess.TimeoutExpired:
        print("[*] Duration reached, stopping rtl_power...")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    except FileNotFoundError as exc:
        raise RuntimeError("rtl_power not found. Install rtl-sdr tools first.") from exc

    if not csv_path.exists():
        raise RuntimeError(f"CSV file was not created: {csv_path}")

    return csv_path
