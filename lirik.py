import tkinter as tk
import time
import threading
import random
import os
import sys


#  KONFIGURASI - Ganti lirik, timing, dan kecepatan ketik di sini


# Format: (waktu_muncul_detik, "teks lirik", kecepatan_mengetik_opsional)
# - Jika kecepatan_mengetik tidak diisi, akan menggunakan default TYPING_SPEED (0.05)
# Nilai kiri (kemunculan lirik): semakin besar → lirik muncul lebih lama.
# Nilai kanan (kecepatan lirik): semakin kecil → lirik berjalan lebih cepat.
LYRICS = [
    (0.9, "Lirik 1", 0.05),                           
    (2.5, "Lirik 2", 0.05),
    (3.5, "Lirik 3", 0.05),

]

# Durasi setiap window lirik bertahan di layar (detik)
DISPLAY_DURATION = 8.0

# Kecepatan mengetik DEFAULT (detik per karakter) jika tidak diatur per lirik
TYPING_SPEED = 0.05

# Skema Warna Modern & Border Berwarna-warni (Vibrant & Clean)
COLOR_PALETTES = [
    {"bg": "#181825", "text": "#ffffff", "border": "#cba6f7", "accent": "#b4befe"},  # Violet Lavender
    {"bg": "#1e1e2e", "text": "#ffffff", "border": "#f38ba8", "accent": "#f5e0dc"},  # Rose Pink
    {"bg": "#0f172a", "text": "#f8fafc", "border": "#38bdf8", "accent": "#7dd3fc"},  # Sky Blue
    {"bg": "#0a192f", "text": "#e6f1ff", "border": "#64ffda", "accent": "#a7f3d0"},  # Emerald Mint
    {"bg": "#1a102f", "text": "#f3e8ff", "border": "#c084fc", "accent": "#e9d5ff"},  # Soft Purple
    {"bg": "#1f1924", "text": "#fff7ed", "border": "#fb923c", "accent": "#ffedd5"},  # Sunset Orange
    {"bg": "#111827", "text": "#f3f4f6", "border": "#ec4899", "accent": "#fbcfe8"},  # Vibrant Magenta
    {"bg": "#0f172a", "text": "#ffffff", "border": "#a855f7", "accent": "#e9d5ff"},  # Royal Violet
]

# Ukuran window per lirik
WINDOW_WIDTH = 520
WINDOW_HEIGHT = 95
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 18

# ═══════════════════════════════════════════════════════════════


class SingleLyricWindow:
    """Class untuk mengelola 1 window lirik dengan animasi ketik & melayang bersih."""

    def __init__(self, master, text, typing_speed=TYPING_SPEED, duration=DISPLAY_DURATION):
        self.master = master
        self.full_text = text
        self.typing_speed = typing_speed
        self.duration = duration

        # Pilih skema warna random
        self.colors = random.choice(COLOR_PALETTES)

        # Buat Toplevel window
        self.win = tk.Toplevel(master)
        self.win.title("Lyric")
        self.win.configure(bg=self.colors["bg"])
        self.win.attributes("-topmost", True)
        self.win.overrideredirect(True)  # Tanpa titlebar
        self.win.attributes("-alpha", 0.0)

        # Tentukan posisi random X di layar
        screen_w = self.win.winfo_screenwidth()
        screen_h = self.win.winfo_screenheight()

        min_x = 40
        max_x = max(min_x + 50, screen_w - WINDOW_WIDTH - 40)
        self.x = random.randint(min_x, max_x)

        # Muncul dari BAWAH LAYAR
        self.start_y = screen_h - WINDOW_HEIGHT - random.randint(20, 60)
        self.current_y = float(self.start_y)

        self.win.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{self.x}+{int(self.current_y)}")

        # Canvas untuk border box & aksen warna
        self.canvas = tk.Canvas(
            self.win,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=self.colors["bg"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Border box luar tebal berwarna
        self.canvas.create_rectangle(
            2, 2, WINDOW_WIDTH - 2, WINDOW_HEIGHT - 2,
            outline=self.colors["border"],
            width=2
        )

        # Border box dalam halus
        self.canvas.create_rectangle(
            5, 5, WINDOW_WIDTH - 5, WINDOW_HEIGHT - 5,
            outline=self.colors["accent"],
            width=1
        )

        # Label lirik utama
        self.label = tk.Label(
            self.win,
            text="",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"],
            wraplength=WINDOW_WIDTH - 50,
            justify="center"
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        # State animasi
        self.alpha = 0.0
        self.char_idx = 0
        self.is_alive = True

        # Drag support
        self._drag_data = {"x": 0, "y": 0}
        self.win.bind("<Button-1>", self._on_drag_start)
        self.win.bind("<B1-Motion>", self._on_drag_motion)
        self.win.bind("<Button-3>", lambda e: self.close())

        # Mulai animasi ketik & melayang
        self._start_typewriter()
        self._animate_float_and_fade_in()

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        self.x = self.win.winfo_x() + event.x - self._drag_data["x"]
        self.current_y = self.win.winfo_y() + event.y - self._drag_data["y"]
        self.win.geometry(f"+{self.x}+{int(self.current_y)}")

    def _start_typewriter(self):
        """Efek mengetik karakter demi karakter secara mulus dan bersih."""
        if not self.is_alive:
            return

        if self.char_idx < len(self.full_text):
            self.char_idx += 1
            current_typed = self.full_text[:self.char_idx]
            self.label.config(text=current_typed + "❘")  # Kursor ketik bersih
            delay_ms = int(self.typing_speed * 1000)
            self.win.after(delay_ms, self._start_typewriter)
        else:
            # Selesai mengetik: tampilkan teks penuh tanpa kursor
            self.label.config(text=self.full_text)

    def _animate_float_and_fade_in(self):
        """Animasi melayang ke atas + Fade in dari bawah."""
        if not self.is_alive:
            return

        if self.alpha < 0.95:
            self.alpha = min(1.0, self.alpha + 0.05)
            self.current_y -= 1.5  # Melayang naik ke atas dari bawah
            self.win.geometry(f"+{self.x}+{int(self.current_y)}")
            self.win.attributes("-alpha", self.alpha)
            self.win.after(25, self._animate_float_and_fade_in)
        else:
            self.alpha = 1.0
            self.win.attributes("-alpha", 1.0)
            self._hold_and_float(start_time=time.time())

    def _hold_and_float(self, start_time):
        """Window terus melayang naik ke atas selama durasi DISPLAY_DURATION."""
        if not self.is_alive:
            return

        elapsed = time.time() - start_time
        if elapsed < self.duration:
            self.current_y -= 1.0  # Terus naik melayang ke atas
            self.win.geometry(f"+{self.x}+{int(self.current_y)}")
            self.win.after(30, lambda: self._hold_and_float(start_time))
        else:
            self._fade_out()

    def _fade_out(self):
        """Animasi fade out sambil melayang naik lebih tinggi lalu ditutup."""
        if not self.is_alive:
            return

        if self.alpha > 0.05:
            self.alpha = max(0.0, self.alpha - 0.05)
            self.current_y -= 2.0  # Melayang naik lebih cepat saat hilang
            self.win.geometry(f"+{self.x}+{int(self.current_y)}")
            self.win.attributes("-alpha", self.alpha)
            self.win.after(25, self._fade_out)
        else:
            self.close()

    def close(self):
        """Tutup window ini."""
        if self.is_alive:
            self.is_alive = False
            try:
                self.win.destroy()
            except Exception:
                pass


class MultiLyricsManager:
    """Manager utama untuk spawning window-window lirik."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Sembunyikan main window utama
        self.running = True
        self.windows = []

    def spawn_lyric(self, text, typing_speed):
        """Buat window lirik baru dengan kecepatan ketik spesifik."""
        win = SingleLyricWindow(self.root, text, typing_speed=typing_speed, duration=DISPLAY_DURATION)
        self.windows.append(win)

    def _lyrics_thread(self):
        """Thread pengatur timing penampilan lirik."""
        start_time = time.time()

        print("\n╔══════════════════════════════════════════════════════╗")
        print("║                                                      ║")
        print("║   ♪                  MEANT TO BE                ♪    ║")
        print("║                                                      ║")
        print("╚══════════════════════════════════════════════════════╝\n")

        for item in LYRICS:
            if not self.running:
                break

            # Ekstrak data (waktu, teks, kecepatan_mengetik)
            trigger_time = item[0]
            text = item[1]
            speed = item[2] if len(item) > 2 else TYPING_SPEED

            # Tunggu hingga waktu lirik tiba
            while self.running:
                elapsed = time.time() - start_time
                if elapsed >= trigger_time:
                    break
                time.sleep(0.02)

            if not self.running:
                break

            print(f"  ♪ [{self._format_time(trigger_time)}] Spawning (speed={speed}s): \"{text}\"")
            self.root.after(0, lambda t=text, s=speed: self.spawn_lyric(t, s))

        # Tunggu sampai semua lirik selesai tampil
        time.sleep(DISPLAY_DURATION + 3)
        if self.running:
            print("\n  ✓ Semua lirik selesai ditampilkan!")
            self.root.after(0, self._quit)

    def _format_time(self, seconds):
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"

    def _quit(self):
        self.running = False
        self.root.quit()

    def run(self):
        # Jalankan thread scheduler lirik
        t = threading.Thread(target=self._lyrics_thread, daemon=True)
        t.start()

        # Mainloop tkinter
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._quit()

#  MAIN
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("  ♪ Multi-Floating Clean Lyrics Player")
    print("=" * 60)

    app = MultiLyricsManager()
    app.run()
