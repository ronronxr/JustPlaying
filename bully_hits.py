"""Bully Hits - whack-a-mole style game. Run: python bully_hits.py"""
import json
import random
import tkinter as tk
from pathlib import Path

ROUND = 30
BEST_FILE = Path.home() / ".bully_hits_best.json"
BULLIES = ["😈", "👹", "😠", "🤬"]
FRIENDS = ["🙂", "😊", "🤓"]

BG, HOLE, ACCENT = "#1e2a44", "#12192b", "#ffcc33"


def load_best():
    try:
        return int(json.loads(BEST_FILE.read_text()))
    except (OSError, ValueError):
        return 0


def save_best(value):
    try:
        BEST_FILE.write_text(json.dumps(value))
    except OSError:
        pass


class Game:
    def __init__(self, root):
        self.root = root
        root.title("Bully Hits")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.score = 0
        self.time_left = 0
        self.running = False
        self.best = load_best()
        self.state = [None] * 9      # None, "bully" or "friend"
        self.hide_jobs = [None] * 9
        self.spawn_job = None
        self.tick_job = None

        tk.Label(root, text="BULLY HITS", font=("Helvetica", 24, "bold"),
                 fg=ACCENT, bg=BG).pack(pady=(10, 0))
        tk.Label(root, text="Bonk the bullies 😈 — don't hit the friendly kids 🙂",
                 fg="white", bg=BG).pack()

        self.hud = tk.Label(root, font=("Helvetica", 14), fg="white", bg=BG)
        self.hud.pack(pady=8)

        board = tk.Frame(root, bg=BG)
        board.pack(padx=14)
        self.buttons = []
        for i in range(9):
            b = tk.Button(board, text="", width=4, height=1, bd=0,
                          font=("Helvetica", 36), bg=HOLE, activebackground=HOLE,
                          command=lambda i=i: self.whack(i))
            b.grid(row=i // 3, column=i % 3, padx=6, pady=6)
            self.buttons.append(b)

        self.msg = tk.Label(root, text="", fg="white", bg=BG)
        self.msg.pack(pady=6)
        self.start_btn = tk.Button(root, text="Start", font=("Helvetica", 14, "bold"),
                                   bg=ACCENT, command=self.start)
        self.start_btn.pack(pady=(0, 14))
        self.update_hud()

    def update_hud(self):
        self.hud.config(text=f"Score: {self.score}    Time: {self.time_left}    Best: {self.best}")

    def start(self):
        self.score = 0
        self.time_left = ROUND
        self.running = True
        self.msg.config(text="")
        self.start_btn.config(state="disabled")
        self.update_hud()
        self.tick_job = self.root.after(1000, self.tick)
        self.spawn()

    def tick(self):
        self.time_left -= 1
        self.update_hud()
        if self.time_left <= 0:
            self.end()
        else:
            self.tick_job = self.root.after(1000, self.tick)

    def spawn(self):
        if not self.running:
            return
        free = [i for i, s in enumerate(self.state) if s is None]
        if free:
            i = random.choice(free)
            friend = random.random() < 0.25
            self.state[i] = "friend" if friend else "bully"
            self.buttons[i].config(text=random.choice(FRIENDS if friend else BULLIES))
            elapsed = ROUND - self.time_left
            stay = max(450, 1000 - elapsed * 18)
            self.hide_jobs[i] = self.root.after(stay, lambda: self.hide(i))
        gap = max(300, 800 - (ROUND - self.time_left) * 15)
        self.spawn_job = self.root.after(gap, self.spawn)

    def hide(self, i):
        if self.hide_jobs[i]:
            self.root.after_cancel(self.hide_jobs[i])
            self.hide_jobs[i] = None
        self.state[i] = None
        self.buttons[i].config(text="", bg=HOLE, activebackground=HOLE)

    def whack(self, i):
        if not self.running or self.state[i] is None:
            return
        if self.state[i] == "bully":
            self.score += 10
            flash = "#a33"
        else:
            self.score = max(0, self.score - 15)
            flash = "#36a"
        self.state[i] = None
        self.buttons[i].config(bg=flash, activebackground=flash)
        if self.hide_jobs[i]:
            self.root.after_cancel(self.hide_jobs[i])
        self.hide_jobs[i] = self.root.after(250, lambda: self.hide(i))
        self.update_hud()

    def end(self):
        self.running = False
        if self.spawn_job:
            self.root.after_cancel(self.spawn_job)
        for i in range(9):
            self.hide(i)
        text = f"Time's up! Final score: {self.score}."
        if self.score > self.best:
            self.best = self.score
            save_best(self.best)
            text += " New best! 🏆"
        self.msg.config(text=text)
        self.start_btn.config(state="normal", text="Play again")
        self.update_hud()


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
