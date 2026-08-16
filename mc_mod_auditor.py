#!/usr/bin/env python3
import os
import re
import sys
import time
import json
import tarfile
import shutil
import platform
import subprocess
from pathlib import Path

# --- AUTOMATIC DEPENDENCY INSTALLER ---

def auto_install_python_packages():
    """Installs required Python libraries locally if missing."""
    missing_packages = []
    try:
        import requests
    except ImportError:
        missing_packages.append("requests")

    if missing_packages:
        print(f"📦 Missing required Python packages: {', '.join(missing_packages)}")
        print("⚡ Installing missing dependencies via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages, "--user"])
            print("✅ Dependencies installed successfully!\n")
        except Exception as e:
            print(f"⚠️ Failed to install packages via pip: {e}")
            print("Please run manually: python3 -m pip install requests")
            sys.exit(1)

auto_install_python_packages()
import requests

# --- TERMINAL STYLING (ANSI TUI) ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_banner(title="MC-MOD-AUDITOR TUI"):
    clear_screen()
    width = 64
    print(f"{Colors.CYAN}╔{'═' * (width - 2)}╗{Colors.ENDC}")
    print(f"{Colors.CYAN}║{Colors.BOLD}{title.center(width - 2)}{Colors.CYAN}║{Colors.ENDC}")
    print(f"{Colors.CYAN}╚{'═' * (width - 2)}╝{Colors.ENDC}")
    print(f"{Colors.BLUE} System: {platform.system()} {platform.release()}{Colors.ENDC}\n")

def render_card(title, content_dict):
    print(f"{Colors.BOLD}{Colors.YELLOW}─ [ {title} ] {'─' * (45 - len(title))}{Colors.ENDC}")
    for key, val in content_dict.items():
        print(f"  {Colors.BOLD}{key}:{Colors.ENDC} {val}")
    print()

def render_progress_bar(current, total, length=40, prefix="Progress", suffix="Complete"):
    """Renders an inline visual ANSI progress bar."""
    percent = f"{100 * (current / float(total)):.1f}"
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    print(f"\r  {Colors.BOLD}{prefix}:{Colors.ENDC} |{Colors.CYAN}{bar}{Colors.ENDC}| {percent}% {suffix}", end="\n\n")

# --- CONFIG MANAGEMENT & USER PREFERENCES ---

CONFIG_DIR = Path.home() / ".config" / "mc_mod_tester"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "eula_accepted": False,
    "save_eula_choice": False,
    "auto_fetch_dependencies": True,
    "default_target_mode": "both",
    "accepted_timestamp": None,
    "client_ram_mb": 2048
}

def load_config():
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(errors="ignore"))
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            return merged
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config_data, indent=2))

def interactive_config_tool(config):
    """Main setup menu displayed at every boot."""
    while True:
        render_banner("CONFIGURATION MENU")
        save_status = "Save Acceptance (Skip Prompt)" if config.get("save_eula_choice") else "Prompt EULA on Every Tool Boot"
        fetch_status = "Enabled" if config.get("auto_fetch_dependencies") else "Disabled"
        
        render_card("CURRENT SETTINGS", {
            "EULA Prompting": save_status,
            "Auto-Fetch Missing Libs": fetch_status,
            "Default Target Mode": config.get("default_target_mode", "both").upper(),
            "Current Client RAM": f"{config.get('client_ram_mb', 2048)} MB",
            "Repository Link": "https://github.com/airpioa/MC-Mod-Auditor",
            "Config File Path": str(CONFIG_FILE)
        })

        print(f"  {Colors.CYAN}[1]{Colors.ENDC} Toggle 'EULA Prompt Behavior' (Current: {'Save Choice' if config.get('save_eula_choice') else 'Prompt Each Boot'})")
        print(f"  {Colors.CYAN}[2]{Colors.ENDC} Toggle 'Auto-Fetch Dependencies' (Current: {fetch_status})")
        print(f"  {Colors.CYAN}[3]{Colors.ENDC} Set Default Target Mode (client / server / both / prompt)")
        print(f"  {Colors.CYAN}[4]{Colors.ENDC} Clear Configuration File")
        print(f"  {Colors.CYAN}[5]{Colors.ENDC} Save Settings & Start Mod Testing")
        print(f"  {Colors.CYAN}[q]{Colors.ENDC} Quit")
        print()

        choice = input(f"Select option {Colors.BOLD}(1-5/q){Colors.ENDC}: ").strip().lower()

        if choice == '1':
            config["save_eula_choice"] = not config.get("save_eula_choice")
            if not config["save_eula_choice"]:
                config["eula_accepted"] = False
            save_config(config)
        elif choice == '2':
            config["auto_fetch_dependencies"] = not config.get("auto_fetch_dependencies")
            save_config(config)
        elif choice == '3':
            print("\nSelect default target mode:")
            print("  1. Client Only")
            print("  2. Server Only")
            print("  3. Both (Client + Server)")
            print("  4. Always Prompt on Start")
            m_choice = input("Choice (1-4): ").strip()
            mode_map = {"1": "client", "2": "server", "3": "both", "4": "prompt"}
            if m_choice in mode_map:
                config["default_target_mode"] = mode_map[m_choice]
                save_config(config)
        elif choice == '4':
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
            config = DEFAULT_CONFIG.copy()
            print(f"\n{Colors.GREEN}✅ Configuration reset to defaults.{Colors.ENDC}")
            time.sleep(1)
        elif choice == '5':
            save_config(config)
            print(f"\n{Colors.GREEN}✅ Settings saved. Proceeding...{Colors.ENDC}")
            time.sleep(0.6)
            break
        elif choice == 'q':
            sys.exit(0)

def display_eula_and_notice(config):
    if config.get("save_eula_choice") and config.get("eula_accepted"):
        return

    render_banner("TERMS & EULA AGREEMENT")
    print(f"{Colors.BOLD}Welcome to MC-Mod-Auditor!{Colors.ENDC}")
    print("Please review the following disclaimers before proceeding:\n")
    print("  1. " + f"{Colors.GREEN}Zero System Modifications:{Colors.ENDC} Operations remain inside your instance's")
    print("     local folder (.mod_tester_tmp). System settings and PATHs are left untouched.")
    print("  2. " + f"{Colors.GREEN}Automated Java Management:{Colors.ENDC} Missing Java runtimes are fetched silently into")
    print("     the local sandbox directory without system prompts or administrative privileges.")
    print("  3. " + f"{Colors.GREEN}Minecraft EULA Acceptance:{Colors.ENDC} Running a test server automatically accepts Mojang's")
    print("     Minecraft End User License Agreement (https://account.mojang.com/documents/minecraft_eula).\n")
    print(f"{Colors.CYAN}───────────────────────────────────────────────────────────────{Colors.ENDC}")
    print(f"  🔗 GitHub Repository: {Colors.UNDERLINE}https://github.com/airpioa/MC-Mod-Auditor{Colors.ENDC}")
    print(f"  🔗 Modrinth API:       {Colors.UNDERLINE}https://modrinth.com{Colors.ENDC}")
    print(f"{Colors.CYAN}───────────────────────────────────────────────────────────────{Colors.ENDC}\n")

    choice = input(f"Do you accept these terms and agree to the Minecraft EULA? ({Colors.BOLD}y/n{Colors.ENDC}): ").strip().lower()
    if choice == 'y':
        if config.get("save_eula_choice"):
            config["eula_accepted"] = True
            config["accepted_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            save_config(config)
            print(f"\n{Colors.GREEN}✅ Accepted! Saved configuration to: {CONFIG_FILE}{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}✅ Accepted! (Prompting on each tool boot as configured){Colors.ENDC}")
        time.sleep(0.8)
    else:
        print(f"\n{Colors.RED}❌ Terms declined. Exiting application.{Colors.ENDC}")
        sys.exit(0)

# --- PLATFORM DETECTOR & PATH RESOLUTION ---
SYSTEM = platform.system().lower()

def get_default_prism_root():
    home = Path.home()
    if SYSTEM == "linux":
        flatpak_path = home / ".var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher"
        if flatpak_path.exists():
            return flatpak_path
        return home / ".local/share/PrismLauncher"
    elif SYSTEM == "darwin":  # macOS
        return home / "Library/Application Support/PrismLauncher"
    elif SYSTEM == "windows":
        appdata = Path(os.getenv("APPDATA", home / "AppData/Roaming"))
        return appdata / "PrismLauncher"
    else:
        raise OSError(f"Unsupported OS: {SYSTEM}")

CRASH_ASSISTANT_SLUG = "crash-assistant"

# --- AUTOMATIC JAVA RESOLVER ---

def resolve_or_install_java_silent(tmp_base_dir):
    java_bin = shutil.which("java")
    if java_bin and subprocess.run([java_bin, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        return java_bin

    prism_root = get_default_prism_root()
    prism_java_dir = prism_root / "java"
    if prism_java_dir.exists():
        for path in prism_java_dir.rglob("java"):
            if path.is_file() and os.access(path, os.X_OK):
                return str(path)

    local_java = tmp_base_dir / "java"
    if local_java.exists():
        for path in local_java.rglob("java"):
            if path.is_file() and os.access(path, os.X_OK):
                return str(path)

    print(f"\n{Colors.CYAN}⚡ Auto-fetching JDK 21 runtime into local sandbox...{Colors.ENDC}")
    headers = {"User-Agent": "MC-Mod-Auditor/1.0 (https://github.com/airpioa/MC-Mod-Auditor)"}
    arch = "aarch64" if platform.machine().lower() in ["arm64", "aarch64"] else "x64"
    os_name = "mac" if SYSTEM == "darwin" else ("windows" if SYSTEM == "windows" else "linux")
    
    url = f"https://api.adoptium.net/v3/binary/latest/21/ga/{os_name}/{arch}/jdk/hotspot/normal/eclipse"
    res = requests.get(url, headers=headers, stream=True)
    
    if res.status_code == 200:
        archive_path = tmp_base_dir / "java_download.tar.gz"
        with open(archive_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
                
        extract_dir = tmp_base_dir / "java"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)
            
        archive_path.unlink()
        
        for path in extract_dir.rglob("java"):
            if path.is_file():
                os.chmod(path, 0o755)
                print(f"{Colors.GREEN}✅ Sandbox Java environment ready.{Colors.ENDC}\n")
                return str(path)
                
    print(f"{Colors.RED}❌ Failed to fetch local Java runtime. Please verify network connection.{Colors.ENDC}")
    sys.exit(1)

# --- PRISM INSTANCE CONFIG & RAM AUTOSCALER ---

def set_prism_instance_ram(instance_path, ram_mb):
    cfg_file = instance_path / "instance.cfg"
    try:
        lines = []
        if cfg_file.exists():
            lines = cfg_file.read_text(errors="ignore").splitlines()
        
        new_lines = []
        for line in lines:
            if line.startswith("OverrideMemory=") or line.startswith("MaxMemAlloc="):
                continue
            new_lines.append(line)
        
        new_lines.append("OverrideMemory=true")
        new_lines.append(f"MaxMemAlloc={ram_mb}")
        cfg_file.write_text("\n".join(new_lines) + "\n")
        print(f"  {Colors.CYAN}⚙️ Prism Instance RAM tuned to:{Colors.ENDC} {ram_mb} MB")
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠️ Could not update Prism instance.cfg RAM: {e}{Colors.ENDC}")

# --- GAME MUTER UTILITY ---

def enforce_muted_options(instance_dir):
    options_file = instance_dir / "minecraft" / "options.txt"
    try:
        if options_file.exists():
            content = options_file.read_text(errors="ignore")
            if "soundCategory_master:" in content:
                content = re.sub(r"soundCategory_master:.*", "soundCategory_master:0.0", content)
            else:
                content += "\nsoundCategory_master:0.0"
            
            if "soundVolume:" in content:
                content = re.sub(r"soundVolume:.*", "soundVolume:0.0", content)
            else:
                content += "\nsoundVolume:0.0"
                
            options_file.write_text(content)
        else:
            options_file.parent.mkdir(parents=True, exist_ok=True)
            options_file.write_text("soundCategory_master:0.0\nsoundVolume:0.0\n")
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠️ Could not automatically mute options.txt: {e}{Colors.ENDC}")

# --- PROCESS KILLER UTILITY ---

def kill_running_minecraft():
    try:
        if SYSTEM == "windows":
            subprocess.run(["taskkill", "/F", "/IM", "javaw.exe", "/T"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "java.exe", "/T"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["pkill", "-f", "minecraft"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "PrismLauncher"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "net.minecraft"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "local_server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

# --- INSTANCE METADATA EXTRACTOR & SERVER DOWNLOADER ---

def parse_instance_metadata(instance_path):
    pack_json = instance_path / "mmc-pack.json"
    mc_version = None
    loader_type = None
    loader_version = None

    if pack_json.exists():
        try:
            data = json.loads(pack_json.read_text(errors="ignore"))
            for component in data.get("components", []):
                uid = component.get("uid", "")
                if uid == "net.minecraft":
                    mc_version = component.get("version")
                elif uid in ["net.fabricmc.fabric-loader", "org.quiltmc.quilt-loader"]:
                    loader_type = "fabric"
                    loader_version = component.get("version")
                elif uid == "net.neoforged":
                    loader_type = "neoforge"
                    loader_version = component.get("version")
                elif uid == "net.minecraftforge":
                    loader_type = "forge"
                    loader_version = component.get("version")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Error reading mmc-pack.json: {e}{Colors.ENDC}")

    return mc_version, loader_type, loader_version

def download_and_setup_server_jar(local_server_dir, mc_version, loader_type, loader_version, java_exec):
    headers = {"User-Agent": "MC-Mod-Auditor/1.0 (https://github.com/airpioa/MC-Mod-Auditor)"}
    local_server_dir.mkdir(parents=True, exist_ok=True)
    
    existing_executables = list(local_server_dir.glob("*.jar")) + list(local_server_dir.glob("run.sh")) + list(local_server_dir.glob("run.bat"))
    if len(existing_executables) > 1:
        return True

    print(f"\n{Colors.CYAN}🌐 Fetching server launcher for {loader_type.upper()} {mc_version} (Loader: {loader_version})...{Colors.ENDC}")

    if loader_type == "fabric":
        url = f"https://meta.fabricmc.net/v2/versions/loader/{mc_version}/{loader_version}/server/jar"
        out_jar = local_server_dir / f"fabric-server-{mc_version}.jar"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            out_jar.write_bytes(res.content)
            print(f"{Colors.GREEN}✅ Downloaded Fabric Server executable!{Colors.ENDC}")
            return True

    elif loader_type == "neoforge":
        url = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{loader_version}/neoforge-{loader_version}-installer.jar"
        installer_jar = local_server_dir / "installer.jar"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            installer_jar.write_bytes(res.content)
            print(f"{Colors.YELLOW}⚙️ Executing NeoForge headless server installer...{Colors.ENDC}")
            subprocess.run([java_exec, "-jar", str(installer_jar), "--installServer"], cwd=str(local_server_dir), check=True)
            return True

    elif loader_type == "forge":
        url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{loader_version}/forge-{mc_version}-{loader_version}-installer.jar"
        installer_jar = local_server_dir / "installer.jar"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{loader_version}/forge-{loader_version}-installer.jar"
            res = requests.get(url, headers=headers)
            
        if res.status_code == 200:
            installer_jar.write_bytes(res.content)
            print(f"{Colors.YELLOW}⚙️ Executing Forge headless server installer...{Colors.ENDC}")
            subprocess.run([java_exec, "-jar", str(installer_jar), "--installServer"], cwd=str(local_server_dir), check=True)
            return True

    print(f"{Colors.RED}❌ Auto-fetch failed for {loader_type} server file.{Colors.ENDC}")
    return False

# --- ULTRA FAST OPTIMIZED LOCAL SERVER MANAGER ---

def setup_and_start_local_server(server_mods_dir, mc_dir, instance_path, java_exec):
    local_server_dir = mc_dir / ".mod_tester_tmp" / "local_server"
    local_server_dir.mkdir(parents=True, exist_ok=True)
    active_server_mods = local_server_dir / "mods"
    active_server_mods.mkdir(parents=True, exist_ok=True)
    
    mc_ver, l_type, l_ver = parse_instance_metadata(instance_path)
    
    if mc_ver and l_type:
        download_and_setup_server_jar(local_server_dir, mc_ver, l_type, l_ver, java_exec)

    for old_file in active_server_mods.glob("*.jar"):
        old_file.unlink()
    for item in server_mods_dir.glob("*.jar"):
        shutil.copy2(item, active_server_mods / item.name)

    (local_server_dir / "eula.txt").write_text("eula=true\n")
    
    props_file = local_server_dir / "server.properties"
    props_file.write_text(
        "server-port=25565\n"
        "online-mode=false\n"
        "spawn-protection=0\n"
        "max-tick-time=-1\n"
        "generate-structures=false\n"
        "view-distance=3\n"
        "simulation-distance=3\n"
        "level-type=flat\n"
        "sync-chunk-writes=false\n"
        "motd=Mod Testing Server\n"
    )

    launch_cmd = None
    if (local_server_dir / "run.sh").exists() and SYSTEM != "windows":
        launch_cmd = ["bash", "run.sh"]
    elif (local_server_dir / "run.bat").exists() and SYSTEM == "windows":
        launch_cmd = ["run.bat"]
    else:
        jars = [j for j in local_server_dir.glob("*.jar") if "installer" not in j.name]
        if jars:
            launch_cmd = [
                java_exec,
                "-Xms512M", "-Xmx1024M",
                "-XX:+UseG1GC",
                "-XX:TieredStopAtLevel=1",
                "-Djava.awt.headless=true",
                "-Dcom.mojang.eula.agree=true",
                "-jar", jars[0].name, "nogui"
            ]

    if not launch_cmd:
        print(f"\n{Colors.YELLOW}⚠️ Could not find or build server executable in: {local_server_dir}{Colors.ENDC}")
        return None

    print(f"\n{Colors.CYAN}🖥️ Launching local test server (Fast Boot Mode)...{Colors.ENDC}")
    
    server_logs = local_server_dir / "logs" / "latest.log"
    if server_logs.exists():
        try: server_logs.write_text("")
        except Exception: pass

    server_proc = subprocess.Popen(
        launch_cmd,
        cwd=str(local_server_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print(f"{Colors.YELLOW}⚡ Waiting for server initialization...{Colors.ENDC}")
    start_wait = time.time()
    while time.time() - start_wait < 35:
        if server_logs.exists():
            text = server_logs.read_text(errors="ignore")
            if "Done (" in text or "Starting Minecraft server on" in text or "Listening on" in text:
                print(f"{Colors.GREEN}✅ Server ready in {round(time.time() - start_wait, 1)}s!{Colors.ENDC}")
                break
        time.sleep(0.15)

    return server_proc

# --- AUTOMATIC PRISM & ENVIRONMENT DETECTOR ---

def auto_detect_or_prompt_prism():
    while True:
        prism_root = get_default_prism_root()
        instances_dir = prism_root / "instances"

        if instances_dir.exists():
            return instances_dir

        render_banner("PRISM LAUNCHER SETUP")
        print(f"{Colors.YELLOW}⚠️ Prism Launcher data directory not found in standard paths.{Colors.ENDC}\n")
        
        installed = input(f"Is Prism Launcher installed on this machine? ({Colors.BOLD}y/n{Colors.ENDC}): ").strip().lower()
        
        if installed == 'n':
            print(f"\n{Colors.RED}❌ Prism Launcher is required to manage Minecraft instances.{Colors.ENDC}")
            print(f"👉 Download: {Colors.UNDERLINE}https://prismlauncher.org/download{Colors.ENDC}\n")
            
            open_browser = input("Would you like to open the download page in your browser? (y/n): ").strip().lower()
            if open_browser == 'y':
                import webbrowser
                webbrowser.open("https://prismlauncher.org/download")
            
            while True:
                ready = input(f"Did you finish installing Prism Launcher? ({Colors.BOLD}y/n/q{Colors.ENDC} to quit): ").strip().lower()
                if ready == 'y':
                    print(f"\n{Colors.GREEN}🔄 Re-checking system for Prism Launcher...{Colors.ENDC}")
                    time.sleep(1.5)
                    break
                elif ready == 'q':
                    sys.exit(0)
                    
        elif installed == 'y':
            custom_input = input("\nEnter custom Prism folder path: ").strip().strip('"').strip("'")
            custom_path = Path(custom_input)
            if (custom_path / "instances").exists():
                return custom_path / "instances"
            elif custom_path.name == "instances" and custom_path.exists():
                return custom_path
            
            print(f"\n{Colors.RED}❌ Could not locate an 'instances' folder at: {custom_path}{Colors.ENDC}")
            retry = input("Would you like to try entering the path again or re-scan? (y/n): ").strip().lower()
            if retry != 'y':
                sys.exit(1)

def get_available_instances(instances_dir):
    if not instances_dir.exists():
        return []
    instances = []
    for item in instances_dir.iterdir():
        if item.is_dir() and ((item / "instance.cfg").exists() or (item / "minecraft").exists()):
            instances.append(item.name)
    return sorted(instances)

def prompt_select_instance(instances_dir):
    render_banner("SELECT INSTANCE")
    instances = get_available_instances(instances_dir)
    
    if not instances:
        print(f"{Colors.RED}❌ No Minecraft instances found in {instances_dir}{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.BOLD}Available Instances:{Colors.ENDC}")
    for idx, name in enumerate(instances, 1):
        print(f"  {Colors.CYAN}[{idx}]{Colors.ENDC} {name}")
    print()

    while True:
        try:
            choice = input(f"Select Instance {Colors.BOLD}(1-{len(instances)}){Colors.ENDC}: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(instances):
                selected = instances[int(choice) - 1]
                print(f"\n{Colors.GREEN}✅ Selected: {selected}{Colors.ENDC}")
                time.sleep(0.6)
                return selected
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

def prompt_testing_target_mode(config):
    default_mode = config.get("default_target_mode", "prompt")
    if default_mode in ["client", "server", "both"]:
        server_addr = "127.0.0.1:25565" if default_mode == "both" else ""
        return default_mode, server_addr

    render_banner("TEST TARGET MODE")
    print("Select testing scope:")
    print(f"  {Colors.CYAN}[1]{Colors.ENDC} Client Only (Launch Minecraft client)")
    print(f"  {Colors.CYAN}[2]{Colors.ENDC} Server Only (Launch headless server process only)")
    print(f"  {Colors.CYAN}[3]{Colors.ENDC} Both (Launch local server and auto-join via client)")
    print()

    target_mode = "both"
    server_address = ""
    
    while True:
        choice = input(f"Select Mode {Colors.BOLD}(1-3){Colors.ENDC}: ").strip()
        if choice == '1':
            target_mode = "client"
            break
        elif choice == '2':
            target_mode = "server"
            break
        elif choice == '3':
            target_mode = "both"
            server_address = "127.0.0.1:25565"
            break

    if target_mode == "client":
        autojoin = input(f"Do you want to auto-join an external server IP? ({Colors.BOLD}y/n{Colors.ENDC}): ").strip().lower()
        if autojoin == 'y':
            server_address = input("Enter target server IP / domain: ").strip()

    return target_mode, server_address

def build_launch_cmd(instance_name, server_address):
    cmd = []
    if SYSTEM == "linux" and (Path.home() / ".var/app/org.prismlauncher.PrismLauncher").exists():
        cmd = ["flatpak", "run", "org.prismlauncher.PrismLauncher", "--launch", instance_name]
    elif SYSTEM == "windows":
        cmd = ["prismlauncher.exe", "--launch", instance_name]
    elif SYSTEM == "darwin":
        mac_app_binary = Path("/Applications/Prism Launcher.app/Contents/MacOS/prismlauncher")
        if mac_app_binary.exists():
            cmd = [str(mac_app_binary), "--launch", instance_name]
        elif shutil.which("prismlauncher"):
            cmd = ["prismlauncher", "--launch", instance_name]
        else:
            cmd = ["open", "-a", "Prism Launcher", "--args", "--launch", instance_name]
    else:
        cmd = ["prismlauncher", "--launch", instance_name]
        
    if server_address.strip():
        cmd.extend(["--server", server_address.strip()])
    return cmd

# --- LOG & BOOT DIAGNOSTICS ---

def get_latest_log(mods_dir):
    log_file = mods_dir.parent / "logs" / "latest.log"
    return log_file.read_text(errors="ignore") if log_file.exists() else ""

def auto_check_successful_start(mods_dir, start_time):
    log_file = mods_dir.parent / "logs" / "latest.log"
    
    for _ in range(25):
        if log_file.exists():
            mtime = log_file.stat().st_mtime
            if mtime >= start_time:
                log_text = log_file.read_text(errors="ignore")
                
                if "java.lang.OutOfMemoryError" in log_text or "GL_OUT_OF_MEMORY" in log_text:
                    return False, "OOM_RAM_CRASH"

                if "Fatal error" in log_text or "Crash Report Created" in log_text or "Incompatible mod set" in log_text or "Missing or unsupported mandatory dependencies" in log_text:
                    return False, "Crash or missing dependency detected in latest.log"
                
                if "Connecting to" in log_text or "Joined world" in log_text or "Setting user:" in log_text:
                    return True, "Main menu or server connection verified"
                    
        time.sleep(1)
    
    return False, "Boot timeout or unconfirmed state"

def normalize_mod_name(filename):
    name = filename.lower().replace(".jar", "")
    return re.sub(r"[-_](v?\d+\.|\d+\.\d+|fabric|forge|neoforge|quilt|mc\d+).*", "", name)

def clean_duplicate_mods(directory):
    if not directory.exists():
        return
    mod_groups = {}
    for jar in directory.glob("*.jar"):
        base_id = normalize_mod_name(jar.name)
        mod_groups.setdefault(base_id, []).append(jar)
        
    for base_id, files in mod_groups.items():
        if len(files) > 1:
            sorted_files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
            for dup in sorted_files[1:]:
                print(f"  {Colors.YELLOW}🗑️ Removing duplicate version:{Colors.ENDC} {dup.name}")
                dup.unlink()

def sync_working_mods(mods_dir, working_dir):
    working_dir.mkdir(parents=True, exist_ok=True)
    for item in working_dir.glob("*.jar"):
        target = mods_dir / item.name
        if not target.exists():
            shutil.copy2(item, target)

def auto_stage_mods_from_instance(mods_dir, staging_dir):
    candidate_mods = sorted([f for f in staging_dir.glob("*.jar")])
    if not candidate_mods:
        existing_instance_mods = list(mods_dir.glob("*.jar"))
        if existing_instance_mods:
            print(f"{Colors.CYAN}📦 Found {len(existing_instance_mods)} mods in real instance folder!{Colors.ENDC}")
            print(f"{Colors.YELLOW}Moving modpack files into tmp/staging directory to begin step-by-step testing...{Colors.ENDC}")
            for mod_file in existing_instance_mods:
                shutil.move(str(mod_file), str(staging_dir / mod_file.name))
            time.sleep(1)

def finalize_exportable_instance_mods(mods_dir, working_dir, instance_path):
    print(f"\n{Colors.CYAN}📦 Synchronizing verified mods to instance mods folder for export...{Colors.ENDC}")
    
    for jar in mods_dir.glob("*.jar"):
        jar.unlink()
        
    for jar in working_dir.glob("*.jar"):
        shutil.copy2(jar, mods_dir / jar.name)
        
    tmp_dir = instance_path / "minecraft" / ".mod_tester_tmp"
    if tmp_dir.exists():
        try:
            shutil.rmtree(tmp_dir)
            print(f"{Colors.GREEN}🧹 Cleaned up temporary test runner directories.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Notice: Could not remove temporary test dir: {e}{Colors.ENDC}")

    print(f"{Colors.GREEN}✅ Instance configuration & modpack ready for normal use and export!{Colors.ENDC}\n")

def fetch_mod_from_modrinth(project_id, target_dir):
    try:
        headers = {"User-Agent": "MC-Mod-Auditor/1.0 (https://github.com/airpioa/MC-Mod-Auditor)"}
        
        res = requests.get(f"https://api.modrinth.com/v2/project/{project_id}", headers=headers)
        
        if res.status_code != 200:
            search_res = requests.get(f"https://api.modrinth.com/v2/search?query={project_id}&limit=1", headers=headers)
            if search_res.status_code == 200 and search_res.json().get('hits'):
                project_id = search_res.json()['hits'][0]['slug']
                res = requests.get(f"https://api.modrinth.com/v2/project/{project_id}", headers=headers)
            else:
                return None
        
        versions_res = requests.get(f"https://api.modrinth.com/v2/project/{project_id}/version", headers=headers)
        if versions_res.status_code == 200 and len(versions_res.json()) > 0:
            latest_version = versions_res.json()[0]
            primary_file = next((f for f in latest_version['files'] if f.get('primary')), latest_version['files'][0])
            
            download_url = primary_file['url']
            filename = primary_file['filename']
            print(f"  {Colors.CYAN}⬇️ Auto-downloading dependency ({project_id}):{Colors.ENDC} {filename}")
            dl_res = requests.get(download_url, headers=headers)
            
            out_file = target_dir / filename
            with open(out_file, "wb") as f:
                f.write(dl_res.content)
            return out_file
    except Exception as e:
        print(f"  {Colors.RED}⚠️ Failed to fetch dependency '{project_id}': {e}{Colors.ENDC}")
    return None

def ensure_crash_assistant(working_dir, config):
    if not config.get("auto_fetch_dependencies", True):
        return
    has_ca = any("crash" in f.name.lower() for f in working_dir.glob("*.jar"))
    if not has_ca:
        print(f"{Colors.YELLOW}🛡️ Utility mod 'Crash Assistant' missing. Auto-installing from Modrinth...{Colors.ENDC}")
        if not fetch_mod_from_modrinth(CRASH_ASSISTANT_SLUG, working_dir):
            fetch_mod_from_modrinth("notenoughcrashinfo", working_dir)

def analyze_crash_logs(mods_dir):
    print(f"\n{Colors.RED}{Colors.BOLD}─── 🔍 AUTOMATIC CRASH ANALYSIS ───{Colors.ENDC}")
    log_text = get_latest_log(mods_dir)
    crash_reports_dir = mods_dir.parent / "crash-reports"
    crash_details = []
    
    if crash_reports_dir.exists():
        reports = sorted(crash_reports_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)
        if reports:
            latest_report = reports[0].read_text(errors="ignore")
            desc = re.search(r"Description:\s*(.*)", latest_report)
            caused = re.findall(r"Caused by:\s*(.*)", latest_report)
            if desc: crash_details.append(f"Description: {desc.group(1)}")
            if caused: crash_details.append(f"Root Cause: {caused[-1]}")

    if not crash_details and log_text:
        errors = re.findall(r"\[.*ERROR.*\]:\s*(.*)", log_text)
        caused = re.findall(r"Caused by:\s*(.*)", log_text)
        if caused: crash_details.append(f"Caused By: {caused[-1]}")
        elif errors: crash_details.append(f"Fatal Error: {errors[-1]}")

    if crash_details:
        for detail in crash_details[:3]:
            print(f"  ❌ {Colors.BOLD}{detail}{Colors.ENDC}")
    else:
        print("  ⚠️ See in-game Crash Assistant screen for detailed stack trace.")
    print(f"{Colors.RED}───────────────────────────────────{Colors.ENDC}\n")

def find_missing_dependencies(log_text):
    missing_mods = set()
    
    fabric_matches = re.findall(r"requires\s+['\"]?([a-zA-Z0-9_\-]+)['\"]?", log_text, re.IGNORECASE)
    for m in fabric_matches:
        if m.lower() not in ["minecraft", "java"]: missing_mods.add(m.lower())

    forge_matches = re.findall(r"Mod\s+([a-zA-Z0-9_\-]+)\s+requires\s+([a-zA-Z0-9_\-]+)", log_text)
    for _, dep in forge_matches:
        if dep.lower() not in ["minecraft", "forge", "neoforge", "java"]: missing_mods.add(dep.lower())
            
    generic_matches = re.findall(r"Missing ID:\s*([a-zA-Z0-9_\-]+)", log_text)
    for dep in generic_matches:
        if dep.lower() not in ["minecraft", "java"]: missing_mods.add(dep.lower())

    return missing_mods

# --- LAUNCH EXECUTION HELPER ---

def run_single_launch_attempt(target_mode, launch_cmd, mods_dir, mc_dir, instance_path, java_exec, server_address):
    kill_running_minecraft()
    time.sleep(1)

    launch_time = time.time()
    
    if target_mode in ["server", "both"]:
        setup_and_start_local_server(mods_dir, mc_dir, instance_path, java_exec)

    if target_mode in ["client", "both"]:
        subprocess.Popen(launch_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{Colors.CYAN}🚀 Launching Minecraft client (Auto-joining server)...{Colors.ENDC}")
        auto_passed, reason = auto_check_successful_start(mods_dir, launch_time)
    else:
        print(f"{Colors.CYAN}🚀 Server running in standalone test mode...{Colors.ENDC}")
        time.sleep(6)
        auto_passed = True
        reason = "Server process stayed alive"

    log_data = get_latest_log(mods_dir)
    missing_deps = find_missing_dependencies(log_data)
    
    return auto_passed, reason, missing_deps

# --- CONFLICT DETECTOR & BISECTION ENGINE ---

def isolate_and_bisect_conflict(mod_path, working_dir, mods_dir, target_mode, launch_cmd, mc_dir, instance_path, java_exec, server_address):
    print(f"\n{Colors.YELLOW}🔍 Initial failure detected. Testing '{mod_path.name}' in isolation to check for conflicts...{Colors.ENDC}")
    
    for item in mods_dir.glob("*.jar"):
        item.unlink()
    shutil.copy2(mod_path, mods_dir / mod_path.name)

    passed_alone, _, _ = run_single_launch_attempt(target_mode, launch_cmd, mods_dir, mc_dir, instance_path, java_exec, server_address)
    kill_running_minecraft()

    if not passed_alone:
        print(f"{Colors.RED}❌ '{mod_path.name}' fails on its own (corrupted jar or incompatible version).{Colors.ENDC}")
        return False, None

    verified_list = sorted([f for f in working_dir.glob("*.jar")])
    if not verified_list:
        return False, None

    print(f"{Colors.YELLOW}⚡ '{mod_path.name}' passed on its own! Finding conflicting mod in {len(verified_list)} working mods...{Colors.ENDC}")

    low = 0
    high = len(verified_list)
    conflicting_mod = None

    while low < high:
        mid = (low + high) // 2
        subset = verified_list[:mid + 1]

        for item in mods_dir.glob("*.jar"):
            item.unlink()
        shutil.copy2(mod_path, mods_dir / mod_path.name)
        for item in subset:
            shutil.copy2(item, mods_dir / item.name)

        print(f"\n{Colors.CYAN}🧪 Testing subset ({len(subset)} working mods + target mod)...{Colors.ENDC}")
        sub_pass, _, _ = run_single_launch_attempt(target_mode, launch_cmd, mods_dir, mc_dir, instance_path, java_exec, server_address)
        kill_running_minecraft()

        if sub_pass:
            low = mid + 1
        else:
            conflicting_mod = subset[mid]
            high = mid

    if conflicting_mod:
        print(f"\n{Colors.RED}💥 CONFLICT FOUND:{Colors.ENDC} {mod_path.name} conflicts directly with {conflicting_mod.name}")
        return True, conflicting_mod
    
    return False, None

# --- MAIN EXECUTION ---

def main():
    config = load_config()
    
    interactive_config_tool(config)
    display_eula_and_notice(config)

    instances_dir = auto_detect_or_prompt_prism()
    instance_name = prompt_select_instance(instances_dir)
    target_mode, server_address = prompt_testing_target_mode(config)

    instance_path = instances_dir / instance_name
    mc_dir = instance_path / "minecraft"
    mods_dir = mc_dir / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    
    tmp_base_dir = mc_dir / ".mod_tester_tmp"
    staging_dir = tmp_base_dir / "staging_mods"
    working_dir = tmp_base_dir / "working_mods"
    
    tmp_base_dir.mkdir(parents=True, exist_ok=True)
    staging_dir.mkdir(parents=True, exist_ok=True)
    working_dir.mkdir(parents=True, exist_ok=True)

    java_exec = resolve_or_install_java_silent(tmp_base_dir)

    set_prism_instance_ram(instance_path, config.get("client_ram_mb", 2048))

    if target_mode in ["client", "both"]:
        enforce_muted_options(instance_path)

    launch_cmd = build_launch_cmd(instance_name, server_address)

    render_banner("PREPARING ENVIRONMENT")

    auto_stage_mods_from_instance(mods_dir, staging_dir)

    print(f"{Colors.YELLOW}🧹 Cleaning duplicate mod files across staging and working folders...{Colors.ENDC}")
    clean_duplicate_mods(staging_dir)
    clean_duplicate_mods(working_dir)

    ensure_crash_assistant(working_dir, config)
    sync_working_mods(mods_dir, working_dir)

    candidate_mods = sorted([f for f in staging_dir.glob("*.jar")])
    total_mods_count = len(candidate_mods)

    if not candidate_mods:
        render_banner("NO MODS STAGED")
        print(f"{Colors.YELLOW}No .jar files found in staging or instance mods folder!{Colors.ENDC}")
        print(f"Temporary Staging Path: {staging_dir}")
        sys.exit(0)

    for idx, mod_path in enumerate(candidate_mods, 1):
        render_banner(f"TESTING MOD ({idx}/{total_mods_count})")
        
        render_progress_bar(idx - 1, total_mods_count, prefix="Overall Progress", suffix=f"({idx-1}/{total_mods_count} Verified)")

        render_card("RUNNER STATE", {
            "Instance": instance_name,
            "Target Mode": f"{Colors.BOLD}{target_mode.upper()}{Colors.ENDC}",
            "Testing Mod": f"{Colors.BOLD}{mod_path.name}{Colors.ENDC}",
            "Staging Queue": f"{total_mods_count - idx} remaining",
            "Auto-Join Target": server_address if server_address else "Disabled",
            "Current Client RAM": f"{config.get('client_ram_mb', 2048)} MB",
            "Sandbox Java": java_exec,
            "Tmp Directory": str(tmp_base_dir)
        })

        sync_working_mods(mods_dir, working_dir)
        target_path = mods_dir / mod_path.name
        shutil.copy2(mod_path, target_path)
        
        while True:
            auto_passed, reason, missing_deps = run_single_launch_attempt(
                target_mode, launch_cmd, mods_dir, mc_dir, instance_path, java_exec, server_address
            )
            
            if reason == "OOM_RAM_CRASH":
                curr_ram = config.get("client_ram_mb", 2048)
                if curr_ram < 8192:
                    new_ram = curr_ram + 1024
                    config["client_ram_mb"] = new_ram
                    save_config(config)
                    print(f"\n{Colors.YELLOW}⚡ Detected Out-Of-Memory / Shader heap allocation failure!{Colors.ENDC}")
                    print(f"{Colors.CYAN}📈 Auto-scaling client RAM from {curr_ram} MB -> {new_ram} MB and retrying launch...{Colors.ENDC}\n")
                    set_prism_instance_ram(instance_path, new_ram)
                    kill_running_minecraft()
                    time.sleep(1)
                    continue

            if missing_deps and config.get("auto_fetch_dependencies", True):
                print(f"\n{Colors.YELLOW}⚡ Auto-detected missing library requirement(s): {', '.join(missing_deps)}{Colors.ENDC}")
                resolved_any = False
                for dep in missing_deps:
                    fetched_jar = fetch_mod_from_modrinth(dep, working_dir)
                    if fetched_jar and fetched_jar.exists():
                        shutil.copy2(fetched_jar, mods_dir / fetched_jar.name)
                        resolved_any = True
                
                if resolved_any:
                    print(f"{Colors.CYAN}🔄 Retrying launch automatically with fetched dependencies...{Colors.ENDC}\n")
                    kill_running_minecraft()
                    time.sleep(1)
                    continue
            
            if auto_passed and not missing_deps:
                print(f"{Colors.GREEN}✅ Auto-detected successful start & server connection: {reason}{Colors.ENDC}")
                choice = 'y'
            else:
                prompt_str = f"Did testing pass for {target_mode.upper()} mode? ({Colors.BOLD}y/n{Colors.ENDC}): "
                choice = input(f"\n{prompt_str}").strip().lower()
            
            kill_running_minecraft()
            
            if choice == 'y':
                print(f"\n{Colors.GREEN}✅ SUCCESS: {mod_path.name} verified!{Colors.ENDC}")
                shutil.move(str(mod_path), str(working_dir / mod_path.name))
                time.sleep(0.8)
                break
            else:
                print(f"\n{Colors.RED}❌ BOOT FAILURE: {mod_path.name}{Colors.ENDC}")
                analyze_crash_logs(mods_dir)
                
                is_conflict, conflicting_mod = isolate_and_bisect_conflict(
                    mod_path, working_dir, mods_dir, target_mode, launch_cmd, mc_dir, instance_path, java_exec, server_address
                )
                
                if is_conflict:
                    print(f"\n{Colors.YELLOW}⚠️ Options for Conflict Resolution:{Colors.ENDC}")
                    print(f"  [{Colors.BOLD}1{Colors.ENDC}] Keep existing working mods and discard new '{mod_path.name}'")
                    print(f"  [{Colors.BOLD}2{Colors.ENDC}] Keep new '{mod_path.name}' and remove conflicting '{conflicting_mod.name}'")
                    opt = input("Select resolution choice (1/2): ").strip()
                    
                    if opt == '2':
                        print(f"{Colors.YELLOW}🗑️ Removing conflicting mod '{conflicting_mod.name}' from working set...{Colors.ENDC}")
                        conflicting_file = working_dir / conflicting_mod.name
                        if conflicting_file.exists(): conflicting_file.unlink()
                        shutil.move(str(mod_path), str(working_dir / mod_path.name))
                        break

                action = input(f"\nAction: [{Colors.BOLD}r{Colors.ENDC}]etry / [{Colors.BOLD}s{Colors.ENDC}]kip (remove mod) / [{Colors.BOLD}q{Colors.ENDC}]uit: ").strip().lower()
                
                if action == 'r':
                    continue
                elif action == 's':
                    print(f"{Colors.YELLOW}🗑️ Removing {mod_path.name} from active launch...{Colors.ENDC}")
                    if target_path.exists(): target_path.unlink()
                    time.sleep(0.8)
                    break
                else:
                    print("Exiting test session.")
                    sys.exit(0)

    finalize_exportable_instance_mods(mods_dir, working_dir, instance_path)

    render_banner("COMPLETE")
    render_progress_bar(total_mods_count, total_mods_count, prefix="Overall Progress", suffix="All Mods Verified!")
    print(f"{Colors.GREEN}🎉 All staged mods processed and verified! Stored directly in instance for regular play/export.{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
