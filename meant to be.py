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
    (0.9, "Light blue eyes", 0.05),                           
    (2.5, "Didn't show surprise", 0.05),                      
    (4.2, "when i explain the fact ", 0.05),                   
    (5.8, "that im satisfied move", 0.05),                     
    (7.7, "the butterflies", 0.05),          
    (9.7, " in my tummy", 0.07),            
    (11.2, "float around", 0.08),
    (12.7, "and make me fell really funny", 0.05),
    (14.8, "you disagree", 0.08),
    (16.2, "with my self-esteem", 0.07),
    (18.5, "did i mention", 0.06),
    (19.7, "you were in my dreams?", 0.06),
    (21.9, "we could walk", 0.07),
    (22.9, "on the ceiling..", 0.07),
    (25.1, "and we thought that", 0.06),
    (26.8, "nothing would go", 0.07),
    (28.5, "wrongggggggggggg", 0.08),
]

# Durasi setiap window lirik bertahan di layar (detik)
DISPLAY_DURATION = 8.0

# Kecepatan mengetik DEFAULT (detik per karakter) jika tidak diatur per lirik
TYPING_SPEED = 0.05

# Karakater Glitch untuk efek hacker/typewriter
GLITCH_CHARS = ['⚡', '░', '▒', '▓', '█', 'Ø', 'X', '!', '@', '#', '$', '%', '&', '*', '0', '1', 'ø', 'µ', '§']

# Atur warna border disini
COLOR_PALETTES = [
    {"bg": "#0a0a0a", "text": "#ffffff", "border": "#ffffff"},  
    {"bg": "#121212", "text": "#f0f0f0", "border": "#888888"},  
    {"bg": "#000000", "text": "#ffffff", "border": "#cccccc"},  
    {"bg": "#1a1a1a", "text": "#e0e0e0", "border": "#ffffff"},  
    {"bg": "#050505", "text": "#ffffff", "border": "#666666"},  
]

# Ukuran window per lirik
WINDOW_WIDTH = 520
WINDOW_HEIGHT = 95
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 18

# ═══════════════════════════════════════════════════════════════


class SingleLyricWindow:
    """Class untuk mengelola 1 window lirik dengan efek Glitch & Typewriter."""

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

        # Canvas untuk border box & glitch line
        self.canvas = tk.Canvas(
            self.win,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=self.colors["bg"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Border box
        self.border_rect = self.canvas.create_rectangle(
            2, 2, WINDOW_WIDTH - 2, WINDOW_HEIGHT - 2,
            outline=self.colors["border"],
            width=2
        )

        # Container Frame untuk Label Lirik agar bisa tumpuk RGB shadow
        self.text_container = tk.Frame(self.win, bg=self.colors["bg"])
        self.text_container.place(relx=0.5, rely=0.5, anchor="center")

        # 1. Monochrome Glitch Shadow Label - Pure White (geser kiri atas)
        self.label_cyan = tk.Label(
            self.text_container,
            text="",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg="#ffffff",
            bg=self.colors["bg"],
            wraplength=WINDOW_WIDTH - 50,
            justify="center"
        )
        self.label_cyan.place(x=-2, y=-1)

        # 2. Monochrome Glitch Shadow Label - Dark Grey (geser kanan bawah)
        self.label_pink = tk.Label(
            self.text_container,
            text="",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg="#555555",
            bg=self.colors["bg"],
            wraplength=WINDOW_WIDTH - 50,
            justify="center"
        )
        self.label_pink.place(x=2, y=1)

        # 3. Label Lirik Utama
        self.label_main = tk.Label(
            self.text_container,
            text="",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"],
            wraplength=WINDOW_WIDTH - 50,
            justify="center"
        )
        self.label_main.pack()

        # State animasi
        self.alpha = 0.0
        self.char_idx = 0
        self.is_alive = True
        self.glitching = False

        # Drag support
        self._drag_data = {"x": 0, "y": 0}
        self.win.bind("<Button-1>", self._on_drag_start)
        self.win.bind("<B1-Motion>", self._on_drag_motion)
        self.win.bind("<Button-3>", lambda e: self.close())

        # Mulai animasi ketik & melayang & glitch loop
        self._start_typewriter()
        self._animate_float_and_fade_in()
        self._schedule_glitch_pulse()

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        self.x = self.win.winfo_x() + event.x - self._drag_data["x"]
        self.current_y = self.win.winfo_y() + event.y - self._drag_data["y"]
        self.win.geometry(f"+{self.x}+{int(self.current_y)}")

    # ═══════════════════════════════════════════════════════════════
    #  EFEK GLITCH UI (MONOCHROME HITAM-PUTIH)
    # ═══════════════════════════════════════════════════════════════

    def _schedule_glitch_pulse(self):
        """Menjadwalkan efek glitch acak secara berkala."""
        if not self.is_alive:
            return

        # Glitch akan terjadi setiap 350ms - 1500ms sekali
        next_glitch_ms = random.randint(350, 1500)
        self.win.after(next_glitch_ms, self._trigger_glitch_pulse)

    def _trigger_glitch_pulse(self):
        """Menjalankan efek glitch hitam-putih (jitter posisi, border flash, & noise text)."""
        if not self.is_alive:
            return

        self.glitching = True

        # 1. Jitter posisi window sedikit (1-4 pixel offset)
        offset_x = random.choice([-5, -3, 3, 5])
        offset_y = random.choice([-4, -2, 2, 4])
        glitch_x = self.x + offset_x
        glitch_y = int(self.current_y) + offset_y
        self.win.geometry(f"+{glitch_x}+{glitch_y}")

        # 2. Border flash hitam / putih / abu-abu terang
        glitch_border_color = random.choice(["#ffffff", "#aaaaaa", "#000000", "#777777"])
        self.canvas.itemconfig(self.border_rect, outline=glitch_border_color, width=3)

        # 3. Tampilkan shadow glitch text offset lebih jauh
        self.label_cyan.place(x=random.randint(-6, -2), y=random.randint(-4, -1))
        self.label_pink.place(x=random.randint(2, 6), y=random.randint(1, 4))

        # 4. Jika sedang mengetik / tampil, berikan karakter glitch sesaat pada teks
        if self.label_main.cget("text"):
            current_text = self.label_main.cget("text")
            glitched_chars = list(current_text)
            # Acak 1-3 karakter jadi simbol hacker
            for _ in range(min(3, len(glitched_chars))):
                idx = random.randint(0, len(glitched_chars) - 1)
                if glitched_chars[idx] != ' ':
                    glitched_chars[idx] = random.choice(GLITCH_CHARS)
            glitch_str = "".join(glitched_chars)
            self.label_main.config(text=glitch_str)
            self.label_cyan.config(text=glitch_str)
            self.label_pink.config(text=glitch_str)

        # Kembalikan ke normal setelah 45 - 80 ms
        glitch_duration_ms = random.randint(45, 80)
        self.win.after(glitch_duration_ms, self._restore_from_glitch)

    def _restore_from_glitch(self):
        """Mengembalikan window ke tampilan normal setelah glitch pulse."""
        if not self.is_alive:
            return

        self.glitching = False

        # Kembalikan posisi geometry normal
        self.win.geometry(f"+{self.x}+{int(self.current_y)}")

        # Kembalikan warna border & shadow offset
        self.canvas.itemconfig(self.border_rect, outline=self.colors["border"], width=2)
        self.label_cyan.place(x=-2, y=-1)
        self.label_pink.place(x=2, y=1)

        # Restore teks asli
        current_typed = self.full_text[:self.char_idx]
        if self.char_idx < len(self.full_text):
            text_to_show = current_typed + "❘"
        else:
            text_to_show = self.full_text

        self.label_main.config(text=text_to_show)
        self.label_cyan.config(text=text_to_show)
        self.label_pink.config(text=text_to_show)

        # Jadwalkan glitch berikutnya
        self._schedule_glitch_pulse()

    # ═══════════════════════════════════════════════════════════════
    #  ANIMASI TYPEWRITER & FLOATING
    # ═══════════════════════════════════════════════════════════════

    def _start_typewriter(self):
        """Efek mengetik karakter demi karakter dengan kecepatan individual per lirik."""
        if not self.is_alive:
            return

        if self.char_idx < len(self.full_text):
            self.char_idx += 1
            current_typed = self.full_text[:self.char_idx]

            # Kadang munculkan karakter glitch saat ketik (15% peluang)
            if random.random() < 0.15 and self.char_idx < len(self.full_text):
                display_text = current_typed[:-1] + random.choice(GLITCH_CHARS) + "❘"
            else:
                display_text = current_typed + "❘"

            if not self.glitching:
                self.label_main.config(text=display_text)
                self.label_cyan.config(text=display_text)
                self.label_pink.config(text=display_text)

            delay_ms = int(self.typing_speed * 1000)
            self.win.after(delay_ms, self._start_typewriter)
        else:
            # Selesai mengetik: tampilkan teks penuh tanpa kursor
            if not self.glitching:
                self.label_main.config(text=self.full_text)
                self.label_cyan.config(text=self.full_text)
                self.label_pink.config(text=self.full_text)

    def _animate_float_and_fade_in(self):
        """Animasi melayang ke atas + Fade in dari bawah."""
        if not self.is_alive:
            return

        if self.alpha < 0.95:
            self.alpha = min(1.0, self.alpha + 0.05)
            self.current_y -= 1.5  # Melayang naik ke atas dari bawah
            if not self.glitching:
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
            if not self.glitching:
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
            if not self.glitching:
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
        """Thread pengatur timing penampillan lirik."""
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
    print("  ♪ Multi-Floating Glitch Typewriter Lyrics Player")
    print("=" * 60)

    app = MultiLyricsManager()
    app.run()
