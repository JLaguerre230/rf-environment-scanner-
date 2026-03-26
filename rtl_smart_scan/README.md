_______________________________________________________________
     |                                                               |
     |    ██████╗ ███████╗    ████████╗ ██████╗  ██████╗ ██╗         |
     |    ██╔══██╗██╔════╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║         |
     |    ██████╔╝█████╗         ██║   ██║   ██║██║   ██║██║         |
     |    ██╔══██╗██╔══╝         ██║   ██║   ██║██║   ██║██║         |
     |    ██║  ██║██║            ██║   ╚██████╔╝╚██████╔╝███████╗    |
     |    ╚═╝  ╚═╝╚═╝            ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝    |
     |_______________________________________________________________|
     |                                                               |
     |  [!] LEGAL DISCLAIMER & USAGE WARNING                         |
     |                                                               |
     |  1. MONITORING: Do not intercept or decode private traffic    |
     |     without explicit permission.                              |
     |  2. TRANSMITTING: Ensure you are licensed (Ham/Amateur) and   |
     |     operating within legal frequency/power limits.            |
     |  3. INTENT: This tool is for educational/testing use only.    |
     |                                                               |
     |  "The airwaves are shared, but privacy is a right."           |
     |_______________________________________________________________|

# RTL Smart Scan

**RTL Smart Scan** is an intelligent RF scanning and signal monitoring tool built for RTL-SDR users.

It allows operators to scan preset radio bands or custom frequency ranges, detect signal activity, and automatically tune to active transmissions for live listening.

The tool is designed for real-world SDR exploration, long-duration monitoring sessions, and RF environment awareness.

---

## 🚀 Installation

Clone the repository:

```
git clone https://github.com/JLaguerre230/rf-environment-scanner-.git
cd rtl_smart_scan
```

---

## 📡 Requirements

* RTL-SDR compatible dongle
* Python 3
* rtl-sdr tools
* ALSA audio tools

Install dependencies:

```
sudo apt update
sudo apt install rtl-sdr alsa-utils
```

---

## ⚡ Recommended Workflow (IMPORTANT)

For long scans or remote monitoring (SSH / Raspberry Pi), it is **strongly recommended** to use `tmux`.

Start a tmux session:

```
tmux new -s rtlscan
```

Run your scan.

Detach safely:

```
CTRL + B then D
```

Reconnect later:

```
tmux attach -t rtlscan
```

---

## 🧠 Features

* Preset radio band scanning (FRS, MURS, Airband, etc)
* Custom frequency range scanning
* Smart signal detection using threshold logic
* Automatic jump-to-listen mode
* Continuous adaptive monitoring
* Live scan summaries
* Background scanning support
* Clean readable terminal output
* Designed for Kali Linux / Raspberry Pi SDR setups

---

## 📊 Usage Examples

### List available preset bands

```
python3 main.py --list-bands
```

---

### Scan FRS band for 60 seconds

```
python3 main.py --band frs --duration 60
```

---

### Scan custom frequency range

```
python3 main.py --start 462.0 --end 463.0 --duration 120
```

---

### Adjust detection threshold

```
python3 main.py --band frs --listen --auto --threshold -35
```

Lower threshold → more sensitive
Higher threshold → only strong signals trigger listening

---

Watch summaries live:

```
watch cat output/latest_summary.txt
```

---

## 📡 Supported Preset Bands

* FRS (Family Radio Service)
* MURS (Multi-Use Radio Service)
* Airband
* UHF Business Radio
* VHF Business Radio

More presets can easily be added.

---

## ⚠️ Notes

Reported frequencies may slightly differ from real channel centers due to FFT bin resolution or tuner offset.

This is normal in wideband SDR scanning.

---

## 📜 Disclaimer

This tool is intended for educational SDR use, RF exploration, and lawful spectrum monitoring.

Users must comply with local radio regulations.

---

## 🔮 Future Improvements

* Automatic signal recording
* RF activity heatmaps
* Persistent intelligence database
* Real-time waterfall interface
* Signal classification logic
