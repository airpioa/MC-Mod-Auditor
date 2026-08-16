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
git clone [https://github.com/airpioa/mc-mod-auditor.git](https://github.com/your-username/mc-mod-auditor.git)
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

---

## 🤝 Contributing & Making Changes

Contributions are welcome! If you'd like to report a bug, suggest a feature, or submit code improvements, follow these steps:

### 1. Fork & Clone
1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/MC-Mod-Auditor.git](https://github.com/YOUR_USERNAME/MC-Mod-Auditor.git)
   cd MC-Mod-Auditor
   
2. Create a Feature Branch

Create a branch specifically for your changes:

```Bash
git checkout -b feature/your-feature-name
3. Local Testing
Since mc_mod_auditor.py is a standalone single-file script:
```
Run the modified script against a local Prism Launcher instance to verify changes:

```Bash
python3 mc_mod_auditor.py
Test configuration menu interactions via python3 mc_mod_auditor.py --config.
```
Ensure terminal ANSI formatting renders cleanly across different shell setups.

4. Submit a Pull Request
Commit your changes with clear, concise messages:

```Bash
git commit -m "feat: add support for custom JVM server args"
Push to your forked branch:
```
```Bash
git push origin feature/your-feature-name
Open a Pull Request against the main branch of the official repository (airpioa/MC-Mod-Auditor). Describe your changes and reference any related issues.
```
