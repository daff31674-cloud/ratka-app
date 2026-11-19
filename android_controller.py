import json
import os
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput


def load_db_url():
  if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as f:
      data = json.load(f)
      url = data.get("firebase_url", "").rstrip("/")
      if url:
        return url
  return "https://ratka-777f3-default-rtdb.firebaseio.com"


DB_URL = load_db_url()


def send_cmd(nick, payload):
  nick = nick.strip()
  if not nick:
    return "Ошибка: введи ник ПК"
  url = f"{DB_URL}/commands/{nick}.json"
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url,
      data=data,
      headers={"Content-Type": "application/json"},
      method="PUT",
  )
  with urllib.request.urlopen(req, timeout=10) as resp:
    resp.read()
  return f"Отправлено -> {nick}"


class ControllerApp(App):

  def build(self):
    root = BoxLayout(orientation="vertical", padding=16, spacing=12)

    self.status = Label(
        text="Готово к отправке", size_hint_y=None, height=40
    )
    self.nick_input = TextInput(
        hint_text="Ник ПК (как в pc_client.exe)",
        multiline=False,
        size_hint_y=None,
        height=48,
    )

    self.vol_label = Label(
        text="Громкость: 50%", size_hint_y=None, height=32
    )
    self.vol_slider = Slider(
        min=0, max=100, value=50, size_hint_y=None, height=44
    )
    self.vol_slider.bind(
        value=lambda inst, val: setattr(
            self.vol_label, "text", f"Громкость: {int(val)}%"
        )
    )
    btn_vol = Button(
        text="Применить громкость", size_hint_y=None, height=50
    )
    btn_vol.bind(on_press=self.on_volume)

    self.text_input = TextInput(
        hint_text="Текст на экран ПК",
        multiline=False,
        size_hint_y=None,
        height=48,
    )
    self.img_input = TextInput(
        hint_text="Путь к картинке на ПК (необязательно)",
        multiline=False,
        size_hint_y=None,
        height=48,
    )
    btn_overlay = Button(
        text="Показать на экране ПК", size_hint_y=None, height=50
    )
    btn_overlay.bind(on_press=self.on_overlay)

    self.path_input = TextInput(
        hint_text="Путь для Проводника (пусто = домашняя папка)",
        multiline=False,
        size_hint_y=None,
        height=48,
    )
    btn_explorer = Button(
        text="Открыть Проводник", size_hint_y=None, height=50
    )
    btn_explorer.bind(on_press=self.on_explorer)

    for w in [
        self.status,
        self.nick_input,
        self.vol_label,
        self.vol_slider,
        btn_vol,
        self.text_input,
        self.img_input,
        btn_overlay,
        self.path_input,
        btn_explorer,
    ]:
      root.add_widget(w)

    return root

  def on_volume(self, _):
    try:
      self.status.text = send_cmd(
          self.nick_input.text,
          {"action": "volume", "value": int(self.vol_slider.value)},
      )
    except Exception as e:
      self.status.text = f"Ошибка: {e}"

  def on_overlay(self, _):
    try:
      self.status.text = send_cmd(
          self.nick_input.text,
          {
              "action": "overlay",
              "text": self.text_input.text,
              "image_path": self.img_input.text.strip(),
              "duration": 5,
          },
      )
    except Exception as e:
      self.status.text = f"Ошибка: {e}"

  def on_explorer(self, _):
    try:
      payload = {"action": "explorer"}
      p = self.path_input.text.strip()
      if p:
        payload["path"] = p
      self.status.text = send_cmd(self.nick_input.text, payload)
    except Exception as e:
      self.status.text = f"Ошибка: {e}"


if __name__ == "__main__":
  ControllerApp().run()
