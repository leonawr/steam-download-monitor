# steam_monitor.py
import time
import os
import re
import winreg

def get_steam_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        return steam_path
    except Exception as e:
        print(f"Не удалось найти путь Steam в реестре: {e}")
        return None

def parse_download_log(steam_path):
    log_file = os.path.join(steam_path, "logs", "content_log.txt")
    if not os.path.exists(log_file):
        return None

    current_game = None
    download_speed = 0
    status = "Unknown"

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-50:]
        for line in reversed(lines):
            match = re.search(r"Downloading app (\d+) : (.+?) : ([\d\.]+) ([KMG]B)/s", line)
            if match:
                _, game_name, speed, unit = match.groups()
                current_game = game_name
                speed_value = float(speed)
                if unit == "KB":
                    download_speed = speed_value / 1024
                elif unit == "GB":
                    download_speed = speed_value * 1024
                else:
                    download_speed = speed_value
                status = "Downloading"
                break
            if "Download paused" in line:
                status = "Paused"
                break
    return current_game, download_speed, status

def main():
    steam_path = get_steam_path()
    if not steam_path:
        return

    print(f"Steam path: {steam_path}")
    print("Отслеживание скорости загрузки игр...")

    for i in range(5):
        result = parse_download_log(steam_path)
        if result:
            game, speed, status = result
            if game:
                print(f"[{i+1}] Игра: {game}, Статус: {status}, Скорость: {speed:.2f} MB/s")
            else:
                print(f"[{i+1}] Нет активной загрузки.")
        else:
            print(f"[{i+1}] Не удалось получить данные о загрузке.")
        time.sleep(60)

if __name__ == "__main__":
    main()
