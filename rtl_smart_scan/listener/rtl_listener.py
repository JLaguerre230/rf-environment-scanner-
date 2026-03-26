import subprocess


def listen_frequency(
    freq_mhz: float,
    mode: str = "nfm",
    gain: float = 35.0,
    audio_device: str = "hw:2,0",
) -> None:
    print(f"[+] Listening on {freq_mhz:.6f} MHz")
    print(f"[*] Demod mode: {mode}")
    print(f"[*] Gain: {gain:.2f} dB")
    print(f"[*] Audio device: {audio_device}")
    print("[*] Press Ctrl+C to stop listening and return.")

    rtl_cmd = [
        "rtl_fm",
        "-M", mode,
        "-f", f"{freq_mhz}M",
        "-s", "50k",
        "-g", str(gain),
        "-r", "48000",
        "-l", "0",
        "-",
    ]

    aplay_cmd = [
        "aplay",
        "-r", "48000",
        "-f", "S16_LE",
        "-D", audio_device,
    ]

    rtl_proc = None
    aplay_proc = None

    try:
        rtl_proc = subprocess.Popen(
            rtl_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        aplay_proc = subprocess.Popen(
            aplay_cmd,
            stdin=rtl_proc.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if rtl_proc.stdout is not None:
            rtl_proc.stdout.close()

        aplay_proc.wait()

    except KeyboardInterrupt:
        print("\n[!] Listening stopped by user.")
    finally:
        if aplay_proc and aplay_proc.poll() is None:
            aplay_proc.terminate()
            try:
                aplay_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                aplay_proc.kill()

        if rtl_proc and rtl_proc.poll() is None:
            rtl_proc.terminate()
            try:
                rtl_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                rtl_proc.kill()
