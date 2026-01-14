#!/usr/bin/env python3
"""
🐬 FreeVR Overlay - Cyber Watch v9
Por Dolphin Engineering

USA OPENGL TEXTURES - SIN FLICKER
"""

import openvr
import time
import ctypes
import numpy as np
import pyautogui
import asyncio
import psutil
import os
import json
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import calendar as cal_module

# OpenGL
import glfw
from OpenGL.GL import *

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_DIR = Path.home() / ".freevr_overlay"
CONFIG_DIR.mkdir(exist_ok=True)

THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk", "primary": (138, 43, 226), "secondary": (0, 191, 255),
        "accent": (255, 0, 128), "success": (0, 255, 136), "warning": (255, 193, 7),
        "error": (255, 61, 87), "text": (255, 255, 255), "text_dim": (150, 150, 170),
        "panel": (20, 16, 35, 230), "btn": (45, 38, 70),
    },
    "dark": {
        "name": "Oscuro", "primary": (100, 100, 100), "secondary": (80, 80, 80),
        "accent": (120, 120, 120), "success": (100, 200, 100), "warning": (200, 180, 80),
        "error": (200, 80, 80), "text": (220, 220, 220), "text_dim": (120, 120, 120),
        "panel": (15, 15, 15, 245), "btn": (35, 35, 35),
    },
    "light": {
        "name": "Claro", "primary": (70, 130, 180), "secondary": (100, 149, 237),
        "accent": (255, 105, 180), "success": (60, 179, 113), "warning": (255, 165, 0),
        "error": (220, 20, 60), "text": (30, 30, 30), "text_dim": (100, 100, 100),
        "panel": (245, 245, 250, 240), "btn": (220, 220, 230),
    },
    "neon": {
        "name": "Neon", "primary": (255, 0, 255), "secondary": (0, 255, 255),
        "accent": (255, 255, 0), "success": (0, 255, 0), "warning": (255, 165, 0),
        "error": (255, 0, 0), "text": (255, 255, 255), "text_dim": (200, 200, 200),
        "panel": (10, 0, 20, 220), "btn": (30, 0, 50),
    },
    "cyan": {
        "name": "Cyan", "primary": (0, 255, 255), "secondary": (0, 200, 200),
        "accent": (0, 150, 150), "success": (0, 255, 200), "warning": (255, 200, 0),
        "error": (255, 100, 100), "text": (255, 255, 255), "text_dim": (150, 200, 200),
        "panel": (0, 30, 40, 235), "btn": (0, 50, 60),
    },
    "matrix": {
        "name": "Matrix", "primary": (0, 255, 65), "secondary": (0, 200, 50),
        "accent": (0, 150, 40), "success": (0, 255, 100), "warning": (200, 255, 0),
        "error": (255, 50, 50), "text": (0, 255, 65), "text_dim": (0, 150, 40),
        "panel": (0, 10, 0, 240), "btn": (0, 30, 0),
    },
}

class Config:
    def __init__(self):
        self.theme = "cyberpunk"
        self._load()
    
    def get_theme(self): return THEMES.get(self.theme, THEMES["cyberpunk"])
    def set_theme(self, n):
        if n in THEMES: self.theme = n; self._save()
    def next_theme(self):
        k = list(THEMES.keys())
        self.theme = k[(k.index(self.theme)+1) % len(k)] if self.theme in k else k[0]
        self._save()
    def _save(self):
        try:
            with open(CONFIG_DIR/"config.json",'w') as f: json.dump({'theme':self.theme},f)
        except: pass
    def _load(self):
        try:
            with open(CONFIG_DIR/"config.json",'r') as f: self.theme = json.load(f).get('theme','cyberpunk')
        except: pass

# ═══════════════════════════════════════════════════════════════════════════════
# UTILS
# ═══════════════════════════════════════════════════════════════════════════════

def mat34_to_numpy(m): return np.array([[m.m[r][c] for c in range(4)] for r in range(3)] + [[0,0,0,1]])
def numpy_to_mat34(m):
    v = openvr.HmdMatrix34_t()
    for r in range(3):
        for c in range(4): v.m[r][c] = float(m[r][c])
    return v

_fc = {}
def get_font(s, b=False):
    k = (s,b)
    if k not in _fc:
        try:
            n = "arialbd.ttf" if b else "arial.ttf"
            _fc[k] = ImageFont.truetype(os.path.join(os.environ['WINDIR'],'Fonts',n),s) if os.name=='nt' else ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",s)
        except: _fc[k] = ImageFont.load_default()
    return _fc[k]

def get_emoji_font(s):
    k = ('e',s)
    if k not in _fc:
        try:
            _fc[k] = ImageFont.truetype(os.path.join(os.environ['WINDIR'],'Fonts','seguiemj.ttf'),s) if os.name=='nt' else get_font(s)
        except: _fc[k] = get_font(s)
    return _fc[k]

def trunc(t, m): return t[:m-2]+".." if len(t)>m else t

# ═══════════════════════════════════════════════════════════════════════════════
# MANAGERS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MediaInfo:
    title: str = ""; artist: str = ""; is_playing: bool = False; source: str = ""

class MediaDetector:
    def __init__(self):
        self.current = MediaInfo()
        self._lock = threading.Lock()
        self._running = True
        if os.name == 'nt': threading.Thread(target=self._loop, daemon=True).start()
    
    def _loop(self):
        while self._running:
            try:
                import asyncio
                from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MM
                async def get():
                    mgr = await MM.request_async()
                    s = mgr.get_current_session()
                    if s:
                        info = await s.try_get_media_properties_async()
                        pb = s.get_playback_info()
                        app = (s.source_app_user_model_id or "").lower()
                        src = "Media"
                        for n,k in [("Spotify","spotify"),("Chrome","chrome"),("Firefox","firefox")]:
                            if k in app: src=n; break
                        with self._lock: self.current = MediaInfo(info.title or "", info.artist or "", pb.playback_status==4, src)
                    else:
                        with self._lock: self.current = MediaInfo()
                loop = asyncio.new_event_loop()
                try: loop.run_until_complete(get())
                finally: loop.close()
            except: pass
            time.sleep(1.5)
    
    def get(self):
        with self._lock: return MediaInfo(self.current.title, self.current.artist, self.current.is_playing, self.current.source)
    def play_pause(self): pyautogui.press('playpause')
    def next_track(self): pyautogui.press('nexttrack')
    def prev_track(self): pyautogui.press('prevtrack')
    def stop(self): self._running = False

@dataclass
class Notification:
    id: str; icon: str; title: str; message: str; app: str = ""; time: float = field(default_factory=time.time); read: bool = False

class NotificationManager:
    def __init__(self):
        self.items: List[Notification] = []
        self._lock = threading.Lock()
        self._running = True
        self._load()
    
    def add(self, n):
        with self._lock:
            if not any(x.id==n.id for x in self.items):
                self.items.insert(0,n); self.items=self.items[:50]; self._save()
    def add_simple(self, i, t, m): self.add(Notification(f"m_{time.time()}", i, t, m))
    def get_unread(self):
        with self._lock: return sum(1 for n in self.items if not n.read)
    def get_recent(self, c=10):
        with self._lock: return list(self.items[:c])
    def mark_all_read(self):
        with self._lock:
            for n in self.items: n.read=True
            self._save()
    def clear(self):
        with self._lock: self.items.clear(); self._save()
    def _save(self):
        try:
            with open(CONFIG_DIR/"notifs.json",'w',encoding='utf-8') as f: json.dump([vars(n) for n in self.items[:30]],f)
        except: pass
    def _load(self):
        try:
            with open(CONFIG_DIR/"notifs.json",'r',encoding='utf-8') as f:
                for d in json.load(f): self.items.append(Notification(**d))
        except: pass
    def stop(self): self._running = False

@dataclass
class Event:
    id: str; title: str; date: str; time_str: str = ""; yearly: bool = False; reminded: bool = False

class CalendarManager:
    def __init__(self, notifs):
        self.events: List[Event] = []
        self.notifs = notifs
        self._load()
        threading.Thread(target=self._reminder_loop, daemon=True).start()
    
    def _reminder_loop(self):
        while True:
            try:
                now = datetime.now()
                today_str = now.strftime("%Y-%m-%d")
                ct = now.strftime("%H:%M")
                for e in self.events:
                    if e.reminded: continue
                    ed = e.date
                    if e.yearly: ed = f"{now.year}-{e.date[5:]}"
                    if ed == today_str:
                        if e.time_str:
                            if ct == e.time_str:
                                self.notifs.add_simple("📅", f"¡Es hora! {e.title}", f"Evento: {e.time_str}")
                                e.reminded = True; self._save()
                        elif ct == "09:00":
                            self.notifs.add_simple("📅", f"Hoy: {e.title}", "Evento de hoy")
                            e.reminded = True; self._save()
            except: pass
            time.sleep(30)
    
    def get_events_for_date(self, d):
        md = d[5:]
        return [e for e in self.events if e.date==d or (e.yearly and e.date[5:]==md)]
    
    def get_upcoming(self, days=7):
        today = datetime.now()
        result = []
        for e in self.events:
            try:
                d = datetime.strptime(e.date, "%Y-%m-%d")
                if e.yearly:
                    d = d.replace(year=today.year)
                    if d < today - timedelta(days=1): d = d.replace(year=today.year+1)
                if today - timedelta(days=1) <= d <= today + timedelta(days=days):
                    result.append(e)
            except: pass
        return sorted(result, key=lambda x: x.date)[:10]
    
    def add_event(self, title, date, time_str="", yearly=False):
        e = Event(f"ev_{time.time()}", title, date, time_str, yearly, False)
        self.events.append(e); self._save()
        return e
    
    def _save(self):
        try:
            with open(CONFIG_DIR/"calendar.json",'w',encoding='utf-8') as f:
                json.dump([{'id':e.id,'title':e.title,'date':e.date,'time_str':e.time_str,'yearly':e.yearly,'reminded':e.reminded} for e in self.events],f)
        except: pass
    
    def _load(self):
        try:
            with open(CONFIG_DIR/"calendar.json",'r',encoding='utf-8') as f:
                for d in json.load(f): self.events.append(Event(d['id'],d['title'],d['date'],d.get('time_str',''),d.get('yearly',False),d.get('reminded',False)))
        except:
            now = datetime.now()
            self.events = [Event("e1","🎂 Cumpleaños",f"{now.year}-06-15","",True,False)]
            self._save()

class Calculator:
    def __init__(self):
        self.display = "0"; self.current = ""; self.op = ""; self.prev = ""
    
    def press(self, k):
        if k in "0123456789":
            if self.display in ["0","Error"]: self.display = k
            else: self.display += k
            self.current = self.display
        elif k == ".":
            if "." not in self.display: self.display += "."; self.current = self.display
        elif k in "+-×÷":
            if self.current: self.prev = self.current; self.op = k; self.display = "0"; self.current = ""
        elif k == "=":
            if self.prev and self.current and self.op:
                try:
                    a,b = float(self.prev), float(self.current)
                    if self.op == "+": r = a+b
                    elif self.op == "-": r = a-b
                    elif self.op == "×": r = a*b
                    elif self.op == "÷": r = a/b if b else 0
                    else: r = b
                    self.display = str(int(r)) if r==int(r) else f"{r:.4f}".rstrip('0').rstrip('.')
                    self.current = self.display; self.prev = ""; self.op = ""
                except: self.display = "Error"
        elif k == "C": self.display = "0"; self.current = self.prev = self.op = ""
        elif k == "⌫": self.display = self.display[:-1] if len(self.display)>1 else "0"; self.current = self.display

class ScreenCapture:
    def __init__(self):
        self.monitors = []
        try:
            import mss
            with mss.mss() as sct: self.monitors = sct.monitors[1:]
        except: pass
    
    def capture(self, idx=0):
        try:
            import mss
            with mss.mss() as sct:
                if idx < len(sct.monitors)-1:
                    shot = sct.grab(sct.monitors[idx+1])
                    img = Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')
                    return img.resize((1280,720), Image.Resampling.LANCZOS).convert('RGBA')
        except: pass
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# OPENGL TEXTURE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class GLTextureManager:
    """Maneja texturas OpenGL para overlays sin flicker"""
    
    def __init__(self):
        # Inicializar GLFW (ventana oculta para contexto GL)
        if not glfw.init():
            raise RuntimeError("No se pudo inicializar GLFW")
        
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        self.window = glfw.create_window(1, 1, "GL Context", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("No se pudo crear ventana GLFW")
        
        glfw.make_context_current(self.window)
        self.textures = {}
        print("  ✓ Contexto OpenGL inicializado")
    
    def create_texture(self, name: str, width: int, height: int) -> int:
        """Crea una textura OpenGL"""
        glfw.make_context_current(self.window)
        
        tex_id = int(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, tex_id)
        
        # Configurar parámetros
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        # Crear textura vacía
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
        self.textures[name] = {'id': int(tex_id), 'w': width, 'h': height}
        return int(tex_id)
    
    def update_texture(self, name: str, img: Image.Image):
        """Actualiza una textura existente con nuevos datos"""
        if name not in self.textures:
            return
        
        glfw.make_context_current(self.window)
        
        tex = self.textures[name]
        
        # Convertir imagen a RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Asegurar mismo tamaño
        if img.size != (tex['w'], tex['h']):
            img = img.resize((tex['w'], tex['h']), Image.Resampling.NEAREST)  # NEAREST es más rápido
        
        # Flip vertical para OpenGL
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        # Obtener bytes
        data = img.tobytes()
        
        # Actualizar textura
        glBindTexture(GL_TEXTURE_2D, int(tex['id']))
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, tex['w'], tex['h'], GL_RGBA, GL_UNSIGNED_BYTE, data)
        glFlush()
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def get_texture_id(self, name: str) -> int:
        if name in self.textures:
            return int(self.textures[name]['id'])
        return 0
    
    def destroy(self):
        glfw.make_context_current(self.window)
        for name, tex in self.textures.items():
            glDeleteTextures(1, [int(tex['id'])])
        glfw.destroy_window(self.window)
        glfw.terminate()

# ═══════════════════════════════════════════════════════════════════════════════
# OVERLAY
# ═══════════════════════════════════════════════════════════════════════════════

class View(Enum):
    MAIN = 0; NOTIFICATIONS = 1; CALENDAR = 2; SCREENS = 3
    TIMER = 4; CALCULATOR = 5; SETTINGS = 6; ADD_EVENT = 7

class CyberWatch:
    W, H = 600, 400
    SIZE_M = 0.20
    POPUP_W, POPUP_H = 700, 550
    POPUP_SIZE_M = 0.55
    
    def __init__(self):
        # OpenGL primero
        self.gl = GLTextureManager()
        
        # OpenVR
        openvr.init(openvr.VRApplication_Overlay)
        self.vr = openvr.VRSystem()
        self.ov = openvr.IVROverlay()
        
        self.config = Config()
        
        # Crear texturas GL
        self.gl.create_texture("main", self.W, self.H)
        self.gl.create_texture("ptr", 64, 64)
        self.gl.create_texture("popup", self.POPUP_W, self.POPUP_H)
        self.gl.create_texture("screen", 1280, 720)
        
        # Overlays
        self.main_h = self.ov.createOverlay("dolph_main", "CyberWatch")
        self.ov.setOverlayWidthInMeters(self.main_h, self.SIZE_M)
        self.ov.setOverlaySortOrder(self.main_h, 1)
        
        self.ptr_h = self.ov.createOverlay("dolph_ptr", "Pointer")
        self.ov.setOverlayWidthInMeters(self.ptr_h, 0.012)
        self.ov.setOverlaySortOrder(self.ptr_h, 100)
        
        self.popup_h = self.ov.createOverlay("dolph_popup", "Popup")
        self.ov.setOverlayWidthInMeters(self.popup_h, self.POPUP_SIZE_M)
        self.ov.setOverlaySortOrder(self.popup_h, 2)
        self.popup_visible = False
        self.popup_type = ""
        self.popup_transform = np.identity(4)
        self.popup_transform[2, 3] = -0.45
        
        self.screen_h = self.ov.createOverlay("dolph_screen", "Screen")
        self.ov.setOverlayWidthInMeters(self.screen_h, 1.2)
        self.screen_visible = False
        self.screen_idx = 0
        self.screen_transform = np.identity(4)
        self.screen_transform[2, 3] = -1.2
        
        # Managers
        self.media = MediaDetector()
        self.notifs = NotificationManager()
        self.calendar = CalendarManager(self.notifs)
        self.capture = ScreenCapture()
        self.calc = Calculator()
        
        # State
        self.cal_selected = datetime.now().strftime("%Y-%m-%d")
        self.cal_offset = 0
        self.timer_running = False
        self.timer_start = 0
        self.timer_elapsed = 0
        self.new_event_title = ""
        self.new_event_time = ""
        self.new_event_yearly = False
        self.keyboard_target = ""
        self.keyboard_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ⌫"
        
        self.state = {
            "hora": "", "fecha": "",
            "cpu": 0, "ram": 0, "gpu": 0, "bat": 100, "bat_plug": False,
            "media_title": "", "media_artist": "", "media_playing": False, "media_source": "",
            "unread": 0, "view": View.MAIN,
        }
        self.last_minute = ""
        self.last_hash = ""
        
        # Transform
        self.transform = np.identity(4)
        self.transform[1, 3] = 0.05
        self.transform[2, 3] = 0.02
        
        self.last_left_valid = False
        self.is_visible = True
        self.ptr_visible = False
        
        self.main_world_matrix = np.identity(4)
        self.popup_world_matrix = np.identity(4)
        self.screen_world_matrix = np.identity(4)
        
        self.gpu_timer = 0  # Para no chequear GPU tan seguido
        
        # Init pointer
        self._init_pointer()
        
        self.notifs.add_simple("🐬", "FreeVR Overlay", "¡Sistema iniciado!")
        print("═" * 50)
        print("  🐬 Cyber Watch v9 - Dolphin Engineering")
        print("  🎮 OpenGL Textures - Sin Flicker")
        print("═" * 50)
    
    def _init_pointer(self):
        img = Image.new('RGBA', (64, 64), (0,0,0,0))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, 60, 60], fill=(255,255,255,220), outline=(0,200,255), width=4)
        d.ellipse([18, 18, 46, 46], fill=(0,200,255))
        self._set_gl_texture("ptr", img)
    
    def _set_gl_texture(self, name: str, img: Image.Image):
        """Actualiza textura GL y la asigna al overlay"""
        self.gl.update_texture(name, img)
        
        tex_id = self.gl.get_texture_id(name)
        
        # Crear estructura Texture_t para OpenVR
        texture = openvr.Texture_t()
        texture.handle = ctypes.c_void_p(tex_id)  # tex_id ya es int
        texture.eType = openvr.TextureType_OpenGL
        texture.eColorSpace = openvr.ColorSpace_Gamma
        
        # Asignar al overlay correspondiente
        if name == "main":
            self.ov.setOverlayTexture(self.main_h, texture)
        elif name == "ptr":
            self.ov.setOverlayTexture(self.ptr_h, texture)
        elif name == "popup":
            self.ov.setOverlayTexture(self.popup_h, texture)
        elif name == "screen":
            self.ov.setOverlayTexture(self.screen_h, texture)
    
    def _t(self, key): return self.config.get_theme().get(key, (128,128,128))
    
    def _get_hash(self):
        return f"{self.state['hora']}|{self.state['view'].value}|{self.state['unread']}|{self.config.theme}"
    
    def _update_state(self) -> bool:
        cm = time.strftime("%H:%M")
        self.state["hora"] = cm
        self.state["fecha"] = time.strftime("%A %d %b").upper()
        self.state["cpu"] = int(psutil.cpu_percent(interval=None))  # Non-blocking
        self.state["ram"] = int(psutil.virtual_memory().percent)
        
        bat = psutil.sensors_battery()
        if bat:
            self.state["bat"] = int(bat.percent)
            self.state["bat_plug"] = bat.power_plugged
        
        # GPU solo cada 5 segundos (subprocess es lento)
        now = time.time()
        if now - self.gpu_timer > 5:
            self.gpu_timer = now
            try:
                r = subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu','--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=0.5)
                if r.returncode == 0: self.state["gpu"] = int(r.stdout.strip().split('\n')[0])
            except: pass
        
        m = self.media.get()
        self.state["media_title"] = m.title
        self.state["media_artist"] = m.artist
        self.state["media_playing"] = m.is_playing
        self.state["media_source"] = m.source
        self.state["unread"] = self.notifs.get_unread()
        
        nh = self._get_hash()
        if nh != self.last_hash or cm != self.last_minute:
            self.last_hash = nh
            self.last_minute = cm
            return True
        return False
    
    def _draw_btn(self, d, x, y, w, h, text, color=None, text_color=None):
        if color is None: color = self._t("btn")
        if text_color is None: text_color = self._t("text")
        d.rounded_rectangle([x, y, x+w, y+h], radius=10, fill=color)
        ie = any(ord(c) > 0x1F00 for c in text)
        fs = int(h * 0.45) if ie else int(h * 0.35)
        font = get_emoji_font(fs) if ie else get_font(fs, True)
        d.text((x + w//2, y + h//2), text, fill=text_color, font=font, anchor="mm")
    
    def _render(self) -> Image.Image:
        img = Image.new('RGBA', (self.W, self.H), (0,0,0,0))
        d = ImageDraw.Draw(img)
        v = self.state["view"]
        if v == View.MAIN: self._draw_main(d)
        elif v == View.NOTIFICATIONS: self._draw_notifs(d)
        elif v == View.CALENDAR: self._draw_calendar_mini(d)
        elif v == View.SCREENS: self._draw_screens(d)
        elif v == View.TIMER: self._draw_timer_mini(d)
        elif v == View.CALCULATOR: self._draw_calculator(d)
        elif v == View.SETTINGS: self._draw_settings(d)
        elif v == View.ADD_EVENT: self._draw_add_event(d)
        return img
    
    def _draw_main(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 280, 170], radius=18, fill=T("panel"), outline=T("primary"), width=2)
        d.text((145, 65), self.state["hora"], fill=T("text"), font=get_font(70, True), anchor="mm")
        d.text((145, 120), self.state["fecha"], fill=T("primary"), font=get_font(13, True), anchor="mm")
        d.text((145, 155), "DOLPHIN ENGINEERING", fill=T("text_dim"), font=get_font(9), anchor="mm")
        
        d.rounded_rectangle([290, 10, 590, 170], radius=18, fill=T("panel"), outline=T("secondary"), width=2)
        d.text((440, 28), "SYSTEM", fill=T("secondary"), font=get_font(11, True), anchor="mm")
        
        stats = [("CPU", self.state["cpu"], T("success")), ("RAM", self.state["ram"], T("warning")), ("GPU", self.state["gpu"], T("accent"))]
        y = 48
        for label, val, color in stats:
            d.text((305, y+8), label, fill=T("text_dim"), font=get_font(11))
            d.rounded_rectangle([345, y, 545, y+18], radius=9, fill=(30,25,45))
            if val > 0:
                w = int(200 * min(val,100) / 100)
                d.rounded_rectangle([345, y, 345+w, y+18], radius=9, fill=(*color[:3],200))
            d.text((565, y+8), f"{val}%", fill=color, font=get_font(11,True))
            y += 28
        
        bi = "⚡" if self.state["bat_plug"] else "🔋"
        bc = T("success") if self.state["bat"] > 25 else T("error")
        d.text((440, y+12), f"{bi} {self.state['bat']}%", fill=bc, font=get_emoji_font(14), anchor="mm")
        
        d.rounded_rectangle([10, 180, 420, 295], radius=16, fill=T("panel"), outline=T("accent"), width=2)
        if self.state["media_title"]:
            icon = "▶" if self.state["media_playing"] else "⏸"
            ic = T("success") if self.state["media_playing"] else T("warning")
            d.text((28, 200), icon, fill=ic, font=get_font(18))
            d.text((55, 198), trunc(self.state["media_title"], 26), fill=T("text"), font=get_font(15, True))
            if self.state["media_artist"]:
                d.text((55, 222), trunc(self.state["media_artist"], 30), fill=T("text_dim"), font=get_font(11))
        else:
            d.text((215, 215), "Sin reproducción", fill=T("text_dim"), font=get_font(13), anchor="mm")
        
        self._draw_btn(d, 55, 248, 80, 40, "⏮")
        self._draw_btn(d, 150, 248, 80, 40, "⏯")
        self._draw_btn(d, 245, 248, 80, 40, "⏭")
        
        d.rounded_rectangle([430, 180, 590, 295], radius=14, fill=T("panel"), outline=T("error"), width=2)
        d.text((510, 198), "NOTIFS", fill=T("error"), font=get_font(11, True), anchor="mm")
        if self.state["unread"] > 0:
            d.ellipse([555, 188, 582, 215], fill=T("error"))
            d.text((568, 201), str(min(self.state["unread"],99)), fill=T("text"), font=get_font(12,True), anchor="mm")
        
        y = 218
        for n in self.notifs.get_recent(3):
            d.text((445, y), f"{n.icon} {trunc(n.title, 10)}", fill=T("text") if not n.read else T("text_dim"), font=get_font(10))
            y += 22
        
        d.rounded_rectangle([10, 305, 590, 390], radius=14, fill=T("panel"), outline=T("primary"), width=1)
        nav = [("🏠", View.MAIN), ("🔔", View.NOTIFICATIONS), ("📅", View.CALENDAR),
               ("🖥", View.SCREENS), ("⏱", View.TIMER), ("🔢", View.CALCULATOR), ("⚙", View.SETTINGS)]
        bw, sp = 75, 6
        tw = len(nav) * bw + (len(nav) - 1) * sp
        sx = (600 - tw) // 2
        for i, (icon, view) in enumerate(nav):
            x = sx + i * (bw + sp)
            ia = self.state["view"] == view
            color = T("primary") if ia else T("btn")
            self._draw_btn(d, x, 315, bw, 65, icon, color=color)
    
    def _draw_notifs(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 590, 390], radius=18, fill=T("panel"), outline=T("error"), width=2)
        d.text((300, 35), f"🔔 NOTIFICACIONES ({self.state['unread']})", fill=T("error"), font=get_font(16, True), anchor="mm")
        y = 60
        for n in self.notifs.get_recent(6):
            bg = (*T("btn")[:3], 200) if not n.read else (*T("btn")[:3], 100)
            d.rounded_rectangle([20, y, 580, y+45], radius=10, fill=bg)
            d.text((40, y+14), n.icon, font=get_emoji_font(16), anchor="mm")
            d.text((60, y+10), trunc(n.title, 28), fill=T("text") if not n.read else T("text_dim"), font=get_font(13,True))
            d.text((60, y+28), trunc(n.message, 45), fill=T("text_dim"), font=get_font(10))
            y += 52
        self._draw_btn(d, 20, 340, 130, 45, "✓ Leer todo")
        self._draw_btn(d, 160, 340, 130, 45, "🗑 Limpiar")
        self._draw_btn(d, 460, 340, 120, 45, "← Volver", T("primary"))
    
    def _draw_calendar_mini(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 590, 390], radius=18, fill=T("panel"), outline=T("warning"), width=2)
        d.text((300, 35), "📅 CALENDARIO", fill=T("warning"), font=get_font(16, True), anchor="mm")
        y = 65
        for e in self.calendar.get_upcoming(4):
            d.rounded_rectangle([30, y, 570, y+40], radius=10, fill=T("btn"))
            d.text((50, y+12), e.title[:25], fill=T("text"), font=get_font(12, True))
            dt = e.date[5:] + (f" {e.time_str}" if e.time_str else "")
            d.text((550, y+12), dt, fill=T("warning"), font=get_font(11), anchor="rm")
            y += 46
        self._draw_btn(d, 30, 250, 260, 45, "📅 Abrir Calendario", T("warning"), (20,20,20))
        self._draw_btn(d, 310, 250, 260, 45, "➕ Agregar Evento", T("success"), (20,20,20))
        self._draw_btn(d, 460, 340, 120, 45, "← Volver", T("primary"))
    
    def _draw_add_event(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 590, 390], radius=18, fill=T("panel"), outline=T("success"), width=2)
        d.text((300, 35), "➕ NUEVO EVENTO", fill=T("success"), font=get_font(16, True), anchor="mm")
        d.text((30, 65), "Título:", fill=T("text"), font=get_font(12))
        tbg = T("secondary") if self.keyboard_target == "title" else T("btn")
        d.rounded_rectangle([30, 85, 570, 120], radius=8, fill=tbg)
        d.text((40, 95), self.new_event_title or "Toca para escribir...", fill=T("text"), font=get_font(14))
        d.text((30, 135), f"Fecha: {self.cal_selected}", fill=T("text"), font=get_font(12))
        d.text((300, 135), "Hora:", fill=T("text"), font=get_font(12))
        tmbg = T("secondary") if self.keyboard_target == "time" else T("btn")
        d.rounded_rectangle([350, 130, 450, 160], radius=8, fill=tmbg)
        d.text((360, 138), self.new_event_time or "HH:MM", fill=T("text"), font=get_font(12))
        yc = T("success") if self.new_event_yearly else T("btn")
        d.rounded_rectangle([480, 130, 570, 160], radius=8, fill=yc)
        d.text((525, 145), "Anual", fill=T("text"), font=get_font(11), anchor="mm")
        if self.keyboard_target:
            chars = self.keyboard_chars
            cols = 10
            bw, bh = 52, 40
            stx, sty = 20, 175
            for i, c in enumerate(chars):
                row, col = i // cols, i % cols
                x = stx + col * (bw + 4)
                y = sty + row * (bh + 4)
                self._draw_btn(d, x, y, bw, bh, c)
        self._draw_btn(d, 30, 340, 170, 45, "✓ Guardar", T("success"), (20,20,20))
        self._draw_btn(d, 220, 340, 170, 45, "✕ Cancelar", T("error"))
        self._draw_btn(d, 460, 340, 120, 45, "← Volver", T("primary"))
    
    def _draw_screens(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 590, 390], radius=18, fill=T("panel"), outline=T("secondary"), width=2)
        d.text((300, 35), "🖥 PANTALLAS", fill=T("secondary"), font=get_font(16, True), anchor="mm")
        for i, mon in enumerate(self.capture.monitors[:4]):
            y = 65 + i * 60
            isel = self.screen_visible and self.screen_idx == i
            color = T("secondary") if isel else T("btn")
            d.rounded_rectangle([30, y, 420, y+52], radius=12, fill=color)
            d.text((55, y+17), f"🖥 Monitor {i+1}", fill=T("text"), font=get_font(15, True))
            d.text((400, y+18), f"{mon['width']}x{mon['height']}", fill=T("text_dim"), font=get_font(12), anchor="rm")
        if self.screen_visible:
            self._draw_btn(d, 440, 65, 140, 50, "✕ Cerrar", T("error"))
        self._draw_btn(d, 460, 340, 120, 45, "← Volver", T("primary"))
    
    def _draw_timer_mini(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 590, 390], radius=18, fill=T("panel"), outline=T("accent"), width=2)
        d.text((300, 35), "⏱ CRONÓMETRO", fill=T("accent"), font=get_font(16, True), anchor="mm")
        t = self.timer_elapsed + (time.time() - self.timer_start if self.timer_running else 0)
        display = f"{int(t//60):02d}:{int(t%60):02d}"
        d.rounded_rectangle([100, 70, 500, 160], radius=18, fill=(15,12,25), outline=T("accent"), width=2)
        d.text((300, 115), display, fill=T("text"), font=get_font(60, True), anchor="mm")
        bt = "⏸ Pausar" if self.timer_running else "▶ Iniciar"
        bc = T("warning") if self.timer_running else T("success")
        self._draw_btn(d, 100, 180, 180, 55, bt, bc, (20,20,20))
        self._draw_btn(d, 300, 180, 180, 55, "⏹ Reset")
        self._draw_btn(d, 150, 260, 300, 50, "⏱ Abrir Grande", T("accent"))
        self._draw_btn(d, 460, 340, 120, 45, "← Volver", T("primary"))
    
    def _draw_calculator(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 590, 390], radius=18, fill=T("panel"), outline=T("success"), width=2)
        d.text((300, 32), "🔢 CALCULADORA", fill=T("success"), font=get_font(16, True), anchor="mm")
        d.rounded_rectangle([30, 55, 570, 100], radius=10, fill=(15,12,25), outline=T("success"), width=2)
        d.text((555, 77), trunc(self.calc.display, 16), fill=T("text"), font=get_font(32, True), anchor="rm")
        buttons = [["C","⌫","÷","×"],["7","8","9","-"],["4","5","6","+"],["1","2","3","="],["0",".","←",""]]
        bw, bh = 125, 48
        stx, sty = 35, 112
        gx, gy = 8, 6
        for ri, row in enumerate(buttons):
            for ci, key in enumerate(row):
                if not key: continue
                if key == "←": key = "← Volver"
                x = stx + ci * (bw + gx)
                y = sty + ri * (bh + gy)
                if key in "÷×-+=": color = T("accent")
                elif key in "C⌫": color = T("error")
                elif key == "← Volver": color = T("primary")
                else: color = T("btn")
                w = bw * 2 + gx if key == "0" else bw
                self._draw_btn(d, x, y, w, bh, key, color)
    
    def _draw_settings(self, d):
        T = self._t
        d.rounded_rectangle([10, 10, 590, 390], radius=18, fill=T("panel"), outline=T("primary"), width=2)
        d.text((300, 35), "⚙ CONFIGURACIÓN", fill=T("primary"), font=get_font(16, True), anchor="mm")
        tn = self.config.get_theme()["name"]
        d.rounded_rectangle([30, 70, 570, 120], radius=12, fill=T("btn"))
        d.text((50, 87), "Tema:", fill=T("text"), font=get_font(14))
        d.text((550, 87), tn, fill=T("secondary"), font=get_font(14, True), anchor="rm")
        self._draw_btn(d, 30, 135, 540, 50, "🎨 Cambiar Tema", T("secondary"))
        d.text((300, 205), "Temas disponibles:", fill=T("text_dim"), font=get_font(11), anchor="mm")
        tl = list(THEMES.keys())
        cols = 4
        bw, bh = 125, 35
        stx = 35
        for i, tname in enumerate(tl):
            row, col = i // cols, i % cols
            x = stx + col * (bw + 10)
            y = 220 + row * (bh + 8)
            ic = tname == self.config.theme
            color = T("primary") if ic else T("btn")
            self._draw_btn(d, x, y, bw, bh, THEMES[tname]["name"], color)
        d.text((300, 320), "🐬 FreeVR Overlay v9.0", fill=T("text_dim"), font=get_font(12), anchor="mm")
        self._draw_btn(d, 460, 340, 120, 45, "← Volver", T("primary"))
    
    # Popups
    def _render_popup(self):
        if self.popup_type == "calendar": return self._render_calendar_big()
        elif self.popup_type == "timer": return self._render_timer_big()
        return Image.new('RGBA', (self.POPUP_W, self.POPUP_H), (0,0,0,0))
    
    def _render_calendar_big(self):
        T = self._t
        img = Image.new('RGBA', (self.POPUP_W, self.POPUP_H), (0,0,0,0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, self.POPUP_W-1, self.POPUP_H-1], radius=20, fill=T("panel"), outline=T("warning"), width=3)
        now = datetime.now()
        target = now + timedelta(days=self.cal_offset * 30)
        year, month = target.year, target.month
        months = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        self._draw_btn(d, 30, 20, 70, 50, "◀")
        d.text((350, 45), f"{months[month-1]} {year}", fill=T("warning"), font=get_font(26, True), anchor="mm")
        self._draw_btn(d, 600, 20, 70, 50, "▶")
        days = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        for i, day in enumerate(days):
            d.text((65 + i*90, 90), day, fill=T("text_dim"), font=get_font(14, True), anchor="mm")
        fd = datetime(year, month, 1)
        swd = fd.weekday()
        dim = cal_module.monthrange(year, month)[1]
        cw, ch = 90, 55
        stx, sty = 65, 112
        for day in range(1, dim + 1):
            idx = swd + day - 1
            col, row = idx % 7, idx // 7
            x = stx + col * cw
            y = sty + row * ch
            ds = f"{year}-{month:02d}-{day:02d}"
            it = ds == now.strftime("%Y-%m-%d")
            isel = ds == self.cal_selected
            he = len(self.calendar.get_events_for_date(ds)) > 0
            if isel: color, tc = T("warning"), (20,20,20)
            elif it: color, tc = T("primary"), T("text")
            else: color, tc = T("btn"), T("text")
            d.rounded_rectangle([x-35, y-16, x+35, y+26], radius=10, fill=color)
            d.text((x, y+2), str(day), fill=tc, font=get_font(18, True), anchor="mm")
            if he: d.ellipse([x-5, y+14, x+5, y+24], fill=T("accent"))
        d.rounded_rectangle([20, 450, 680, 535], radius=12, fill=T("btn"))
        events = self.calendar.get_events_for_date(self.cal_selected)
        d.text((350, 468), f"📅 {self.cal_selected}", fill=T("secondary"), font=get_font(14, True), anchor="mm")
        if events:
            x = 40
            for e in events[:3]:
                d.text((x, 490), f"• {e.title[:16]}", fill=T("text"), font=get_font(11))
                if e.time_str: d.text((x, 510), f"  {e.time_str}", fill=T("text_dim"), font=get_font(10))
                x += 200
        else:
            d.text((350, 505), "Sin eventos", fill=T("text_dim"), font=get_font(12), anchor="mm")
        self._draw_btn(d, 560, 485, 110, 42, "✕ Cerrar", T("error"))
        return img
    
    def _render_timer_big(self):
        T = self._t
        img = Image.new('RGBA', (self.POPUP_W, self.POPUP_H), (0,0,0,0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, self.POPUP_W-1, self.POPUP_H-1], radius=20, fill=T("panel"), outline=T("accent"), width=3)
        d.text((350, 45), "⏱ CRONÓMETRO", fill=T("accent"), font=get_font(24, True), anchor="mm")
        t = self.timer_elapsed + (time.time() - self.timer_start if self.timer_running else 0)
        display = f"{int(t//60):02d}:{int(t%60):02d}.{int((t%1)*100):02d}"
        d.rounded_rectangle([80, 100, 620, 240], radius=20, fill=(15,12,25), outline=T("accent"), width=3)
        d.text((350, 170), display, fill=T("text"), font=get_font(75, True), anchor="mm")
        bt = "⏸ PAUSAR" if self.timer_running else "▶ INICIAR"
        bc = T("warning") if self.timer_running else T("success")
        self._draw_btn(d, 100, 270, 200, 65, bt, bc, (20,20,20))
        self._draw_btn(d, 320, 270, 200, 65, "⏹ RESET")
        self._draw_btn(d, 220, 360, 200, 50, "+1 MINUTO", T("secondary"))
        self._draw_btn(d, 540, 480, 130, 50, "✕ Cerrar", T("error"))
        return img
    
    def _update_popup(self):
        img = self._render_popup()
        self._set_gl_texture("popup", img)
    
    # Clicks (simplificado)
    def _handle_click(self, px, py):
        v = self.state["view"]
        if v == View.MAIN:
            if 248 <= py <= 288:
                if 55 <= px <= 135: self.media.prev_track()
                elif 150 <= px <= 230: self.media.play_pause()
                elif 245 <= px <= 325: self.media.next_track()
            if 180 <= py <= 295 and 430 <= px <= 590: self.state["view"] = View.NOTIFICATIONS
            if 315 <= py <= 380:
                views = [View.MAIN, View.NOTIFICATIONS, View.CALENDAR, View.SCREENS, View.TIMER, View.CALCULATOR, View.SETTINGS]
                bw, sp = 75, 6
                tw = len(views) * bw + (len(views) - 1) * sp
                sx = (600 - tw) // 2
                for i, view in enumerate(views):
                    x = sx + i * (bw + sp)
                    if x <= px <= x + bw: self.state["view"] = view; break
        elif v == View.NOTIFICATIONS:
            if 340 <= py <= 385:
                if 20 <= px <= 150: self.notifs.mark_all_read()
                elif 160 <= px <= 290: self.notifs.clear()
                elif 460 <= px <= 580: self.state["view"] = View.MAIN
        elif v == View.CALENDAR:
            if 250 <= py <= 295:
                if 30 <= px <= 290:
                    self.popup_type = "calendar"; self.popup_visible = True
                    self._update_popup(); self.ov.showOverlay(self.popup_h)
                elif 310 <= px <= 570:
                    self.state["view"] = View.ADD_EVENT
                    self.new_event_title = ""; self.new_event_time = ""
                    self.new_event_yearly = False; self.keyboard_target = ""
            elif 340 <= py <= 385 and 460 <= px <= 580: self.state["view"] = View.MAIN
        elif v == View.ADD_EVENT:
            if 85 <= py <= 120 and 30 <= px <= 570: self.keyboard_target = "title"
            elif 130 <= py <= 160 and 350 <= px <= 450: self.keyboard_target = "time"
            elif 130 <= py <= 160 and 480 <= px <= 570: self.new_event_yearly = not self.new_event_yearly
            elif self.keyboard_target and 175 <= py <= 330:
                chars = self.keyboard_chars
                cols = 10
                bw, bh = 52, 40
                stx, sty = 20, 175
                for i, c in enumerate(chars):
                    row, col = i // cols, i % cols
                    x = stx + col * (bw + 4)
                    y = sty + row * (bh + 4)
                    if x <= px <= x + bw and y <= py <= y + bh:
                        if c == "⌫":
                            if self.keyboard_target == "title" and self.new_event_title: self.new_event_title = self.new_event_title[:-1]
                            elif self.keyboard_target == "time" and self.new_event_time: self.new_event_time = self.new_event_time[:-1]
                        else:
                            if self.keyboard_target == "title" and len(self.new_event_title) < 30: self.new_event_title += c
                            elif self.keyboard_target == "time" and len(self.new_event_time) < 5: self.new_event_time += c
                        break
            elif 340 <= py <= 385:
                if 30 <= px <= 200:
                    if self.new_event_title:
                        self.calendar.add_event(self.new_event_title, self.cal_selected, self.new_event_time, self.new_event_yearly)
                        self.notifs.add_simple("✅", "Evento creado", self.new_event_title)
                    self.state["view"] = View.CALENDAR
                elif 220 <= px <= 390: self.state["view"] = View.CALENDAR
                elif 460 <= px <= 580: self.state["view"] = View.MAIN
        elif v == View.SCREENS:
            for i in range(len(self.capture.monitors[:4])):
                y = 65 + i * 60
                if y <= py <= y + 52 and 30 <= px <= 420:
                    if self.screen_visible and self.screen_idx == i:
                        self.screen_visible = False; self.ov.hideOverlay(self.screen_h)
                    else:
                        self.screen_idx = i; self.screen_visible = True; self.ov.showOverlay(self.screen_h)
                    break
            if 65 <= py <= 115 and 440 <= px <= 580 and self.screen_visible:
                self.screen_visible = False; self.ov.hideOverlay(self.screen_h)
            if 340 <= py <= 385 and 460 <= px <= 580: self.state["view"] = View.MAIN
        elif v == View.TIMER:
            if 180 <= py <= 235:
                if 100 <= px <= 280:
                    if self.timer_running:
                        self.timer_elapsed += time.time() - self.timer_start; self.timer_running = False
                    else: self.timer_start = time.time(); self.timer_running = True
                elif 300 <= px <= 480: self.timer_running = False; self.timer_elapsed = 0
            if 260 <= py <= 310 and 150 <= px <= 450:
                self.popup_type = "timer"; self.popup_visible = True
                self._update_popup(); self.ov.showOverlay(self.popup_h)
            if 340 <= py <= 385 and 460 <= px <= 580: self.state["view"] = View.MAIN
        elif v == View.CALCULATOR:
            buttons = [["C","⌫","÷","×"],["7","8","9","-"],["4","5","6","+"],["1","2","3","="],["0",".","back",""]]
            bw, bh = 125, 48
            stx, sty = 35, 112
            gx, gy = 8, 6
            for ri, row in enumerate(buttons):
                for ci, key in enumerate(row):
                    if not key: continue
                    x = stx + ci * (bw + gx)
                    y = sty + ri * (bh + gy)
                    w = bw * 2 + gx if key == "0" else bw
                    if x <= px <= x + w and y <= py <= y + bh:
                        if key == "back": self.state["view"] = View.MAIN
                        else: self.calc.press(key)
                        return
        elif v == View.SETTINGS:
            if 135 <= py <= 185 and 30 <= px <= 570: self.config.next_theme()
            tl = list(THEMES.keys())
            cols = 4
            bw, bh = 125, 35
            stx = 35
            for i, tname in enumerate(tl):
                row, col = i // cols, i % cols
                x = stx + col * (bw + 10)
                y = 220 + row * (bh + 8)
                if x <= px <= x + bw and y <= py <= y + bh: self.config.set_theme(tname); break
            if 340 <= py <= 385 and 460 <= px <= 580: self.state["view"] = View.MAIN
        self.last_hash = ""
    
    def _handle_popup_click(self, px, py):
        if self.popup_type == "calendar":
            if 20 <= py <= 70:
                if 30 <= px <= 100: self.cal_offset -= 1
                elif 600 <= px <= 670: self.cal_offset += 1
            if 485 <= py <= 527 and 560 <= px <= 670:
                self.popup_visible = False; self.ov.hideOverlay(self.popup_h); return
            if 96 <= py <= 430:
                now = datetime.now()
                target = now + timedelta(days=self.cal_offset * 30)
                year, month = target.year, target.month
                swd = datetime(year, month, 1).weekday()
                dim = cal_module.monthrange(year, month)[1]
                cw, ch = 90, 55
                stx, sty = 65, 112
                for day in range(1, dim + 1):
                    idx = swd + day - 1
                    col, row = idx % 7, idx // 7
                    x = stx + col * cw
                    y = sty + row * ch
                    if x - 35 <= px <= x + 35 and y - 16 <= py <= y + 26:
                        self.cal_selected = f"{year}-{month:02d}-{day:02d}"; break
        elif self.popup_type == "timer":
            if 270 <= py <= 335:
                if 100 <= px <= 300:
                    if self.timer_running:
                        self.timer_elapsed += time.time() - self.timer_start; self.timer_running = False
                    else: self.timer_start = time.time(); self.timer_running = True
                elif 320 <= px <= 520: self.timer_running = False; self.timer_elapsed = 0
            if 360 <= py <= 410 and 220 <= px <= 420: self.timer_elapsed += 60
            if 480 <= py <= 530 and 540 <= px <= 670:
                self.popup_visible = False; self.ov.hideOverlay(self.popup_h); return
        self._update_popup()
    
    # Main loop
    async def run(self):
        last_trigger = False
        popup_timer = 0
        screen_timer = 0
        render_timer = 0
        state_timer = 0
        
        # Renderizar inicial
        img = self._render()
        self._set_gl_texture("main", img)
        
        while True:
            try:
                now = time.time()
                
                poses = (openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount)()
                self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0, poses)
                
                l_id = self.vr.getTrackedDeviceIndexForControllerRole(openvr.TrackedControllerRole_LeftHand)
                r_id = self.vr.getTrackedDeviceIndexForControllerRole(openvr.TrackedControllerRole_RightHand)
                hmd_valid = poses[openvr.k_unTrackedDeviceIndex_Hmd].bPoseIsValid
                
                left_valid = l_id != openvr.k_unTrackedDeviceIndexInvalid and poses[l_id].bPoseIsValid
                
                if left_valid and not self.last_left_valid: self.last_hash = ""
                self.last_left_valid = left_valid
                
                hmd_m = np.identity(4)
                if hmd_valid:
                    hmd_m = mat34_to_numpy(poses[openvr.k_unTrackedDeviceIndex_Hmd].mDeviceToAbsoluteTracking)
                
                if left_valid:
                    ml = mat34_to_numpy(poses[l_id].mDeviceToAbsoluteTracking)
                    self.main_world_matrix = ml @ self.transform
                    v_mat = numpy_to_mat34(self.transform)
                    self.ov.setOverlayTransformTrackedDeviceRelative(self.main_h, l_id, v_mat)
                    
                    if r_id != openvr.k_unTrackedDeviceIndexInvalid and poses[r_id].bPoseIsValid:
                        mr = mat34_to_numpy(poses[r_id].mDeviceToAbsoluteTracking)
                        r_pos = mr[:3, 3]
                        _, state = self.vr.getControllerState(r_id)
                        grip = bool(state.ulButtonPressed & (1 << openvr.k_EButton_Grip))
                        
                        p_local_main = (np.linalg.inv(self.main_world_matrix) @ np.append(r_pos, 1))[:3]
                        hw = self.SIZE_M / 2
                        hh = hw * self.H / self.W
                        in_main = (abs(p_local_main[0]) < hw * 1.1 and abs(p_local_main[1]) < hh * 1.1 and abs(p_local_main[2]) < 0.08)
                        
                        in_popup = False
                        p_local_popup = np.zeros(3)
                        if self.popup_visible and hmd_valid:
                            self.popup_world_matrix = hmd_m @ self.popup_transform
                            p_local_popup = (np.linalg.inv(self.popup_world_matrix) @ np.append(r_pos, 1))[:3]
                            phw = self.POPUP_SIZE_M / 2
                            phh = phw * self.POPUP_H / self.POPUP_W
                            in_popup = (abs(p_local_popup[0]) < phw * 1.1 and abs(p_local_popup[1]) < phh * 1.1 and abs(p_local_popup[2]) < 0.1)
                        
                        in_screen = False
                        p_local_screen = np.zeros(3)
                        if self.screen_visible and hmd_valid:
                            self.screen_world_matrix = hmd_m @ self.screen_transform
                            p_local_screen = (np.linalg.inv(self.screen_world_matrix) @ np.append(r_pos, 1))[:3]
                            shw = 1.2 / 2
                            shh = shw * 720 / 1280
                            in_screen = (abs(p_local_screen[0]) < shw * 1.1 and abs(p_local_screen[1]) < shh * 1.1 and abs(p_local_screen[2]) < 0.15)
                        
                        show_ptr = in_main or in_popup or in_screen
                        
                        if show_ptr:
                            if in_popup:
                                ptr_m = self.popup_world_matrix.copy()
                                ptr_m[:3, 3] = (self.popup_world_matrix[:3, 3] + 
                                               self.popup_world_matrix[:3, 0] * p_local_popup[0] + 
                                               self.popup_world_matrix[:3, 1] * p_local_popup[1] + 
                                               self.popup_world_matrix[:3, 2] * (-0.005))
                            elif in_screen:
                                ptr_m = self.screen_world_matrix.copy()
                                ptr_m[:3, 3] = (self.screen_world_matrix[:3, 3] + 
                                               self.screen_world_matrix[:3, 0] * p_local_screen[0] + 
                                               self.screen_world_matrix[:3, 1] * p_local_screen[1] + 
                                               self.screen_world_matrix[:3, 2] * (-0.005))
                            else:
                                ptr_m = self.main_world_matrix.copy()
                                ptr_m[:3, 3] = (self.main_world_matrix[:3, 3] + 
                                               self.main_world_matrix[:3, 0] * p_local_main[0] + 
                                               self.main_world_matrix[:3, 1] * p_local_main[1] + 
                                               self.main_world_matrix[:3, 2] * (-0.005))
                            
                            self.ov.setOverlayTransformAbsolute(self.ptr_h, openvr.TrackingUniverseStanding, numpy_to_mat34(ptr_m))
                            
                            if not self.ptr_visible: self.ov.showOverlay(self.ptr_h); self.ptr_visible = True
                            
                            trigger = bool(state.ulButtonPressed & (1 << openvr.k_EButton_SteamVR_Trigger))
                            if not trigger and last_trigger:
                                if in_popup:
                                    phw = self.POPUP_SIZE_M / 2
                                    phh = phw * self.POPUP_H / self.POPUP_W
                                    ppx = int(((p_local_popup[0] / phw) + 1) * self.POPUP_W / 2)
                                    ppy = int((1 - (p_local_popup[1] / phh)) * self.POPUP_H / 2)
                                    self._handle_popup_click(ppx, ppy)
                                elif in_main:
                                    px = int(((p_local_main[0] / hw) + 1) * self.W / 2)
                                    py = int((1 - (p_local_main[1] / hh)) * self.H / 2)
                                    px = max(0, min(self.W - 1, px))
                                    py = max(0, min(self.H - 1, py))
                                    self._handle_click(px, py)
                                # Forzar re-render después de click
                                render_timer = 0
                            last_trigger = trigger
                        else:
                            if self.ptr_visible: self.ov.hideOverlay(self.ptr_h); self.ptr_visible = False
                            last_trigger = False
                        
                        if grip:
                            if in_main: self.transform = np.linalg.inv(ml) @ mr
                            elif in_popup: self.popup_transform = np.linalg.inv(hmd_m) @ mr
                            elif in_screen: self.screen_transform = np.linalg.inv(hmd_m) @ mr
                    
                    # Visibilidad (cada 100ms)
                    if hmd_valid and now - state_timer > 0.1:
                        state_timer = now
                        hmd_pos = hmd_m[:3, 3]
                        vec = hmd_pos - self.main_world_matrix[:3, 3]
                        dot = np.dot(self.main_world_matrix[:3, 2], vec / np.linalg.norm(vec))
                        should_show = dot >= 0.10 or self.ov.isDashboardVisible()
                        if should_show != self.is_visible:
                            if should_show: self.ov.showOverlay(self.main_h)
                            else: self.ov.hideOverlay(self.main_h)
                            self.is_visible = should_show
                    
                    # Actualizar estado y renderizar (cada 500ms para main, o cuando hay cambio)
                    if now - render_timer > 0.5:
                        render_timer = now
                        if self._update_state():
                            img = self._render()
                            self._set_gl_texture("main", img)
                
                # Popup transform (siempre)
                if self.popup_visible and hmd_valid:
                    self.popup_world_matrix = hmd_m @ self.popup_transform
                    self.ov.setOverlayTransformAbsolute(self.popup_h, openvr.TrackingUniverseStanding, numpy_to_mat34(self.popup_world_matrix))
                    
                    # Timer popup actualiza más frecuente cuando corre
                    if self.popup_type == "timer" and self.timer_running and now - popup_timer > 0.033:
                        popup_timer = now
                        self._update_popup()
                
                # Screen mirror
                if self.screen_visible and hmd_valid:
                    self.screen_world_matrix = hmd_m @ self.screen_transform
                    self.ov.setOverlayTransformAbsolute(self.screen_h, openvr.TrackingUniverseStanding, numpy_to_mat34(self.screen_world_matrix))
                    
                    if now - screen_timer > 0.066:
                        screen_timer = now
                        screen_img = self.capture.capture(self.screen_idx)
                        if screen_img:
                            self._set_gl_texture("screen", screen_img)
                
            except Exception as e:
                pass
            
            await asyncio.sleep(0.004)  # 250Hz para tracking suave
    
    def shutdown(self):
        print("\n🐬 Cerrando...")
        self.media.stop()
        self.notifs.stop()
        try:
            self.ov.destroyOverlay(self.main_h)
            self.ov.destroyOverlay(self.ptr_h)
            self.ov.destroyOverlay(self.popup_h)
            self.ov.destroyOverlay(self.screen_h)
            openvr.shutdown()
        except: pass
        self.gl.destroy()

def main():
    w = None
    try:
        w = CyberWatch()
        asyncio.run(w.run())
    except KeyboardInterrupt:
        pass
    finally:
        if w: w.shutdown()

if __name__ == "__main__":
    main()
