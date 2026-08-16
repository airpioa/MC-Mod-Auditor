# 🛠️ MC Mod Auditor

Automated testing harness for Prism Launcher modpacks. MC-Mod-Auditor validates .jar stability, bisects crashes to isolate mod conflicts, auto-fetches dependencies from Modrinth, and scales RAM for shaders—keeping configs intact for easy export.

---

## ✨ Features

* ⚡ **Headless Fast-Boot Server:** Boots a local, lightweight test server (`view-distance=3`, flat-world default, G1GC tuning) with sub-second log polling for rapid handoffs.
* 📈 **Dynamic RAM Auto-Scaler:** Starts at a lightweight baseline (2GB) and automatically increases client heap space up to 8GB if Out-Of-Memory (OOM) or shader pipeline heap allocation errors occur.
* 🔍 **Automatic Conflict Bisecting:** Isolates failing mods and runs a binary-search routine against your verified mod pool to pinpoint exact mod-on-mod conflicts.
* 📦 **Auto Dependency Fetching:** Scans startup crash logs for missing library IDs (Fabric, Forge, NeoForge) and auto-downloads required dependencies directly from Modrinth.
* 🎮 **Native Shader & Config Compatibility:** Operates directly within standard Prism Launcher instance structures so options, keybinds, shader configurations, and configs carry over seamlessly.
* 📁 **Export-Ready Output:** Moves verified mods back into your primary instance `.minecraft/mods` directory and cleans up temporary sandboxes upon completion.

---

## 🛠️ Prerequisites

* **Python:** `3.8` or higher
* **Launcher:** [Prism Launcher](https://prismlauncher.org/)
* **Java:** JDK 21 installed (or let the tool automatically fetch a local sandbox JDK runtime)
* **Python Libraries:** `requests` (installed automatically on first run if missing)

---

## 🚀 How to Run

### 1. Download / Clone
Clone the repository to your local machine:
```bash
git clone [https://github.com/your-username/mc-mod-auditor.git](https://github.com/your-username/mc-mod-auditor.git)
cd mc-mod-auditor
```
2. Make Executable (Linux / macOS)
Grant execution permissions to the Python script:

```Bash
chmod +x mc_mod_auditor.py
```
3. Launching the Auditor
Run the script using Python 3:

```Bash
python3 mc_mod_auditor.py
```
