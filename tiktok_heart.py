import time
import random
import threading
import tkinter as tk
from tkinter import ttk
import pyautogui
from pynput import keyboard as kb
from pynput import mouse as ms

# Fix DPI scaling trên màn hình laptop/HiDPI
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

pyautogui.PAUSE = 0

# ── State ──────────────────────────────────────────────
HEART_BREAK_AT = 500   # nghỉ sau mỗi X tim
BREAK_MIN      = 5     # nghỉ tối thiểu (giây)
BREAK_MAX      = 10    # nghỉ tối đa (giây)

running    = False
paused     = False
last_key   = 0
count      = 0
start_t    = 0
listener       = None
mouse_listener = None
pressing_l = False
is_pinned  = False
is_compact = False

# ── Keyboard listener ──────────────────────────────────
def on_press(key):
    global paused, last_key
    if key == kb.Key.f8:
        stop()
        return False
    try:
        if key.char == 'l' and pressing_l:
            return
    except AttributeError:
        pass
    last_key = time.time()
    paused = True

def on_click(x, y, button, pressed):
    """Click chuột = rời ô chat → resume"""
    global paused
    if pressed and paused:
        paused = False

def resume_watcher():
    global paused
    while running:
        time.sleep(0.2)

# ── Main loop ──────────────────────────────────────────
def heart_loop():
    global count, running, pressing_l
    mn = float(var_min.get())
    mx = float(var_max.get())
    if mx <= mn:
        mx = mn + 0.1

    threading.Thread(target=resume_watcher, daemon=True).start()

    delay = float(var_delay.get())
    steps = int(delay * 10)
    for i in range(steps, 0, -1):
        if not running:
            return
        lbl_status.config(text=f"Chuẩn bị... {i/10:.1f}s")
        time.sleep(0.1)

    lbl_status.config(text="Đang thả tim ❤️")
    batch = 0  # đếm tim trong đợt hiện tại
    while running:
        if not paused:
            pressing_l = True
            pyautogui.press('l')
            pressing_l = False
            count += 1
            batch += 1

            # Dừng hẳn khi đạt giới hạn
            limit = var_limit.get()
            if limit > 0 and count >= limit:
                lbl_status.config(text=f"Đã đạt {limit:,} tim ✅")
                stop()
                return

            # Nghỉ sau mỗi HEART_BREAK_AT tim
            if batch >= HEART_BREAK_AT:
                batch = 0
                break_time = random.uniform(BREAK_MIN, BREAK_MAX)
                lbl_status.config(text=f"Nghỉ {break_time:.0f}s... ⏳")
                pause_end = time.time() + break_time
                while time.time() < pause_end and running:
                    time.sleep(0.1)
                if running:
                    lbl_status.config(text="Đang thả tim ❤️")

        time.sleep(0.1 if paused else random.uniform(mn, mx))

# ── UI actions ─────────────────────────────────────────
def start():
    global running, paused, count, start_t, listener
    if running:
        return
    if var_limit.get() < 1:
        lbl_status.config(text="⚠️ Vui lòng chọn giới hạn tim!")
        return
    running  = True
    paused   = False
    count    = 0
    start_t  = time.time()
    listener = kb.Listener(on_press=on_press)
    listener.start()
    mouse_listener = ms.Listener(on_click=on_click)
    mouse_listener.start()
    btn_start.config(state="disabled")
    btn_stop.config(state="normal")
    threading.Thread(target=heart_loop, daemon=True).start()
    update_ui()

def stop():
    global running, listener, mouse_listener
    running = False
    if listener:
        try: listener.stop()
        except: pass
    if mouse_listener:
        try: mouse_listener.stop()
        except: pass
    btn_start.config(state="normal")
    btn_stop.config(state="disabled")
    lbl_status.config(text="Đã dừng")

def update_ui():
    if not running:
        return
    elapsed = int(time.time() - start_t)
    m, s = divmod(elapsed, 60)
    lbl_count.config(text=str(count))
    lbl_time.config(text=f"{m:02d}:{s:02d}")
    lbl_pause.config(text="⏸ Đang chat..." if paused else "")
    lbl_compact_info.config(
        text=f"❤️ {count}   ⏱ {m:02d}:{s:02d}"
    )
    # Compact: ẩn/hiện nút tùy trạng thái chat
    if is_compact:
        if paused:
            cf_btn.pack_forget()
            cf_chat.pack(side="right", padx=8)
        else:
            cf_chat.pack_forget()
            cf_btn.pack(side="right", padx=8)
    root.after(200, update_ui)

def toggle_pin():
    global is_pinned
    is_pinned = not is_pinned
    root.attributes("-topmost", is_pinned)
    btn_pin.config(
        text="📌 Bỏ ghim" if is_pinned else "📌 Ghim",
        bg=C_RED if is_pinned else "#e8e8e8",
        fg="white" if is_pinned else C_TEXT,
    )

def toggle_compact():
    global is_compact
    is_compact = not is_compact
    if is_compact:
        frame_main.pack_forget()
        frame_compact.pack(fill="x", padx=8, pady=4)
        root.geometry("400x95")
        btn_collapse.config(text="Mở rộng")
    else:
        frame_compact.pack_forget()
        frame_main.pack(fill="both", expand=True, padx=14, pady=14)
        root.geometry("400x505")
        btn_collapse.config(text="Thu gọn")

def show_help():
    """Hiển thị cửa sổ hướng dẫn nhỏ"""
    win = tk.Toplevel(root)
    win.title("Hướng dẫn")
    win.geometry("380x460")
    win.resizable(False, False)
    win.configure(bg=C_BG)
    win.attributes("-topmost", True)

    # Giữ cửa sổ con luôn trên cửa sổ chính
    win.transient(root)

    # Header
    hd = tk.Frame(win, bg=C_RED, height=44)
    hd.pack(fill="x")
    hd.pack_propagate(False)
    tk.Label(hd, text="❓  Hướng dẫn sử dụng", bg=C_RED, fg="white",
             font=("Segoe UI", 12, "bold")).pack(expand=True)

    # Nội dung scroll với Canvas
    container = tk.Frame(win, bg=C_BG)
    container.pack(fill="both", expand=True, padx=0, pady=0)

    canvas = tk.Canvas(container, bg=C_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    outer = tk.Frame(canvas, bg=C_BG)

    outer.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=outer, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=16, pady=12)
    scrollbar.pack(side="right", fill="y", pady=12)

    # Cuộn bằng chuột
    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

    items = [
        ("📌  Ghim (Always on Top)",
         "Giữ cửa sổ luôn hiển thị trên cùng, kể cả khi bạn đang xem TikTok hoặc thao tác ở tab khác."),
        ("▼  Thu gọn",
         "Thu nhỏ giao diện xuống còn một dòng nhỏ để không chiếm màn hình. Vẫn hiển thị số tim và thời gian theo thời gian thực."),
        ("⏱  Thời gian chờ",
         "Số giây đếm ngược sau khi bấm Bắt đầu. Dùng thời gian này để click vào video TikTok Live trước khi tool bắt đầu nhấn phím."),
        ("🎯  Tối thiểu / Tối đa",
         "Khoảng cách ngẫu nhiên giữa mỗi lần thả tim (giây). Ví dụ: min 0.2s, max 0.8s → mỗi lần tim cách nhau từ 0.2 đến 0.8 giây ngẫu nhiên. Giúp giả lập hành vi tự nhiên hơn."),
        ("💬  Tạm dừng khi chat",
         "Khi bạn gõ bàn phím, tool tự động tạm dừng để không làm nhiễu ô chat. Tool tiếp tục thả tim khi bạn nhấn Enter (gửi chat) hoặc click chuột ra ngoài ô chat."),
        ("⌨️  Phím F8",
         "Dừng tool bất kỳ lúc nào, kể cả khi đang gõ chat hay làm việc khác. Không cần quay lại bấm nút Dừng."),
        ("❤️  Tim có thật không?",
         "Có. Tim được gửi lên server TikTok bình thường. Hiệu ứng tim bay trên màn hình chỉ hiển thị khi tab TikTok đang active — điều này bình thường và không ảnh hưởng đến việc đếm tim thật."),
    ]

    for icon_title, desc in items:
        row = tk.Frame(outer, bg=C_BG)
        row.pack(fill="x", pady=(0, 10))

        tk.Label(row, text=icon_title, bg=C_BG, fg=C_TEXT,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
        tk.Label(row, text=desc, bg=C_BG, fg=C_GRAY,
                 font=("Segoe UI", 9), anchor="w", wraplength=320,
                 justify="left").pack(fill="x", padx=(8, 0))

    tk.Button(win, text="Đóng", bg=C_RED, fg="white",
              font=("Segoe UI", 10, "bold"), bd=0, relief="flat",
              cursor="hand2", pady=8, command=win.destroy
              ).pack(fill="x", padx=16, pady=(0, 12))

# ── UI layout ──────────────────────────────────────────
root = tk.Tk()
root.title("Auto Heart by HoangVi")
root.geometry("400x505")
root.resizable(False, False)
root.configure(bg="#fff")

C_BG   = "#ffffff"
C_CARD = "#f7f7f7"
C_RED  = "#fe2c55"
C_GRAY = "#666666"
C_TEXT = "#111111"

def card(parent, **kw):
    return tk.Frame(parent, bg=C_CARD, bd=0, relief="flat",
                    highlightbackground="#e8e8e8", highlightthickness=1, **kw)

# ── Header ─────────────────────────────────────────────
hdr = tk.Frame(root, bg=C_RED, height=48)
hdr.pack(fill="x")
hdr.pack_propagate(False)

tk.Label(hdr, text="♥  Auto Heart",
         bg=C_RED, fg="white", font=("Segoe UI", 13, "bold")).pack(side="left", padx=12, expand=True)

btn_pin = tk.Button(hdr, text="📌 Ghim", bg="#e8e8e8", fg=C_TEXT,
                    font=("Segoe UI", 8), bd=0, relief="flat",
                    cursor="hand2", padx=6, pady=3, command=toggle_pin)
btn_pin.pack(side="right", padx=(4, 4), pady=8)

btn_collapse = tk.Button(hdr, text="Thu gọn", bg="#e8e8e8", fg=C_TEXT,
                         font=("Segoe UI", 8), bd=0, relief="flat",
                         cursor="hand2", padx=6, pady=3, command=toggle_compact)
btn_collapse.pack(side="right", padx=(0, 4), pady=8)

# ── Compact view ───────────────────────────────────────
frame_compact = tk.Frame(root, bg=C_BG)

lbl_compact_info = tk.Label(frame_compact, text="❤️ 0   ⏱ 00:00",
                             bg=C_BG, fg=C_TEXT, font=("Segoe UI", 13, "bold"))
lbl_compact_info.pack(side="left", padx=10, pady=6)

# Frame chứa nút bình thường
cf_btn = tk.Frame(frame_compact, bg=C_BG)
cf_btn.pack(side="right", padx=8)
cf_start = tk.Button(cf_btn, text="▶ Bắt đầu", bg=C_RED, fg="white",
          font=("Segoe UI", 9, "bold"), bd=0, relief="flat",
          cursor="hand2", padx=8, pady=5, command=start)
cf_start.pack(side="left", padx=(0,4))
cf_stop = tk.Button(cf_btn, text="■ Dừng", bg="#e8e8e8", fg=C_TEXT,
          font=("Segoe UI", 9), bd=0, relief="flat",
          cursor="hand2", padx=8, pady=5, command=stop)
cf_stop.pack(side="left")

# Nút "Đang chat" hiện khi pause
cf_chat = tk.Button(frame_compact, text="💬 Đang chat...", bg="#f5a623", fg="white",
                    font=("Segoe UI", 9, "bold"), bd=0, relief="flat",
                    padx=10, pady=5, state="disabled")
# Không pack mặc định, chỉ hiện khi paused

# ── Full view ──────────────────────────────────────────
frame_main = tk.Frame(root, bg=C_BG)
frame_main.pack(fill="both", expand=True, padx=14, pady=14)

sf = card(frame_main)
sf.pack(fill="x", pady=(0, 10))
tk.Label(sf, text="Cài đặt", bg=C_CARD, fg=C_GRAY,
         font=("Segoe UI", 9)).grid(row=0, column=0, columnspan=3,
                                     sticky="w", padx=10, pady=(8,2))

def _make_setting_row(parent, row, label, var, mn, mx, step, fmt, is_int=False):
    # Column 0: label cố định 140px
    # Column 1: slider fill phần còn lại
    # Column 2: giá trị cố định 60px
    parent.columnconfigure(0, minsize=140)
    parent.columnconfigure(1, weight=1)
    parent.columnconfigure(2, minsize=60)

    tk.Label(parent, text=label, bg=C_CARD, fg=C_TEXT,
             font=("Segoe UI", 10), anchor="w"
             ).grid(row=row, column=0, padx=(10,4), pady=4, sticky="w")

    ttk.Scale(parent, from_=mn, to=mx, variable=var,
              orient="horizontal").grid(row=row, column=1, padx=4, sticky="ew")

    lv = tk.Label(parent, bg=C_CARD, fg=C_RED,
                  font=("Segoe UI", 10, "bold"), anchor="e")
    lv.grid(row=row, column=2, padx=(4,10), sticky="e")

    def upd(*_):
        v = round(float(var.get()) / step) * step
        if is_int:
            v = max(mn, min(mx, int(v)))
            var.set(v)
        lv.config(text=fmt.format(v))
    var.trace_add("write", upd)
    upd()

def setting_row_int(parent, row, label, var, mn, mx, step, fmt):
    _make_setting_row(parent, row, label, var, mn, mx, step, fmt, is_int=True)

def setting_row(parent, row, label, var, mn, mx, step, fmt):
    _make_setting_row(parent, row, label, var, mn, mx, step, fmt, is_int=False)

var_limit  = tk.IntVar(value=3000)
var_min    = tk.DoubleVar(value=0.2)
var_max    = tk.DoubleVar(value=0.8)
var_delay  = tk.DoubleVar(value=5.0)
setting_row_int(sf, 1, "Giới hạn tim",  var_limit,  1, 100000, 1000, "{:,}")
setting_row(sf, 2, "Tối thiểu (giây)",  var_min,    0.1, 2.0,  0.1, "{:.1f}s")
setting_row(sf, 3, "Tối đa (giây)",     var_max,    0.2, 5.0,  0.1, "{:.1f}s")
setting_row(sf, 4, "Thời gian chờ",     var_delay,  1.0, 10.0, 0.1, "{:.1f}s")

stf = card(frame_main)
stf.pack(fill="x", pady=(0, 10))
stf.columnconfigure((0,1), weight=1)

tk.Label(stf, text="Tim đã thả", bg=C_CARD, fg=C_GRAY,
         font=("Segoe UI", 9)).grid(row=0, column=0, pady=(8,0))
tk.Label(stf, text="Thời gian",  bg=C_CARD, fg=C_GRAY,
         font=("Segoe UI", 9)).grid(row=0, column=1, pady=(8,0))

lbl_count = tk.Label(stf, text="0", bg=C_CARD, fg=C_RED,
                     font=("Segoe UI", 24, "bold"))
lbl_count.grid(row=1, column=0, pady=(0,8))

lbl_time = tk.Label(stf, text="00:00", bg=C_CARD, fg=C_TEXT,
                    font=("Segoe UI", 24, "bold"))
lbl_time.grid(row=1, column=1, pady=(0,8))

lbl_status = tk.Label(frame_main, text="Chưa chạy", bg=C_BG, fg=C_GRAY,
                      font=("Segoe UI", 10))
lbl_status.pack()

lbl_pause = tk.Label(frame_main, text="", bg=C_BG, fg="#f5a623",
                     font=("Segoe UI", 9))
lbl_pause.pack()

# Buttons
bf = tk.Frame(frame_main, bg=C_BG)
bf.pack(fill="x", pady=10)

btn_start = tk.Button(bf, text="▶  Bắt đầu", bg=C_RED, fg="white",
                      font=("Segoe UI", 11, "bold"), bd=0, relief="flat",
                      cursor="hand2", padx=16, pady=8, command=start)
btn_start.pack(side="left", expand=True, fill="x", padx=(0,6))

btn_stop = tk.Button(bf, text="■  Dừng (F8)", bg="#e8e8e8", fg=C_TEXT,
                     font=("Segoe UI", 11), bd=0, relief="flat",
                     cursor="hand2", padx=16, pady=8, command=stop,
                     state="disabled")
btn_stop.pack(side="left", expand=True, fill="x")

# Footer: hint + nút hướng dẫn
tk.Label(frame_main, text="Click vào video TikTok Live trước khi bấm Bắt đầu",
         bg=C_BG, fg=C_GRAY, font=("Segoe UI", 8),
         wraplength=280, justify="center").pack()

tk.Button(frame_main, text="❓  Hướng dẫn sử dụng", bg=C_BG, fg=C_GRAY,
          font=("Segoe UI", 8), bd=0, relief="flat",
          cursor="hand2", pady=2, command=show_help).pack()

root.mainloop()
