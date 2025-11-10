import tkinter as tk
from tkinter import ttk, messagebox
import math, random

# ----------------------- THEME -----------------------
BG = "#0f1220"           # page background
PANEL = "#151a2e"        # panels/cards
TXT = "#e9ecff"          # primary text
MUTED = "#b8bfe7"        # secondary text
ACCENT = "#5b8cff"       # brand blue
ACCENT_DARK = "#2c5be7"  # darker blue
WIN = "#18c39a"          # win green
LOSS = "#ff6b6b"         # loss red
TIE = "#ffb84d"          # tie amber
TILE_BG = "#232a4a"      # tile background
TILE_ACTIVE = "#2f3a68"  # tile hover/active

FONT_H1 = ("Segoe UI", 18, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_TXT = ("Segoe UI", 10)
FONT_TILE = ("Segoe UI Semibold", 28, "bold")
FONT_BADGE = ("Segoe UI", 10, "bold")


# ----------------------- AI (Minimax + Alpha-Beta) -----------------------
def check_winner(board):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),         # rows
        (0,3,6),(1,4,7),(2,5,8),         # cols
        (0,4,8),(2,4,6)                  # diagonals
    ]
    for a,b,c in wins:
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a], (a,b,c)     # ('X' or 'O', combo)
    if "" not in board:
        return "Tie", None
    return None, None

def minimax(board, depth, is_max, alpha, beta, ai, human):
    winner, _ = check_winner(board)
    if winner == ai:
        return 10 - depth
    if winner == human:
        return depth - 10
    if winner == "Tie":
        return 0

    if is_max:
        best = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = ai
                score = minimax(board, depth+1, False, alpha, beta, ai, human)
                board[i] = ""
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = human
                score = minimax(board, depth+1, True, alpha, beta, ai, human)
                board[i] = ""
                best = min(best, score)
                beta = min(beta, best)
                if beta <= alpha:
                    break
        return best

def best_move(board, ai, human):
    best_score = -math.inf
    best_idx = None
    for i in range(9):
        if board[i] == "":
            board[i] = ai
            score = minimax(board, 0, False, -math.inf, math.inf, ai, human)
            board[i] = ""
            if score > best_score:
                best_score = score
                best_idx = i
    return best_idx


# ----------------------- APP -----------------------
class TicTacToeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe — CodSoft Task 2 (GUI)")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.player = "X"
        self.ai = "O"
        self.turn = "X"                 # X starts
        self.board = [""]*9
        self.buttons = []
        self.pulse_job = None
        self.pulse_on = False
        self.win_combo = None

        self.score = {"You":0, "AI":0, "Ties":0}
        self.difficulty = tk.StringVar(value="Impossible")  # Easy / Medium / Impossible
        self.status_var = tk.StringVar(value="Your turn (X)")

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(padx=16, pady=(16,8), fill="x")

        title = tk.Label(header, text="Tic Tac Toe", fg=TXT, bg=BG, font=FONT_H1)
        subtitle = tk.Label(header, text="Human vs AI • Dark UI • Difficulty selector • Scoreboard",
                            fg=MUTED, bg=BG, font=FONT_TXT)
        title.pack(anchor="w")
        subtitle.pack(anchor="w", pady=(2,0))

        # Control panel
        panel = tk.Frame(self, bg=PANEL, bd=0, highlightthickness=0)
        panel.pack(padx=16, pady=8, fill="x")

        # Difficulty
        tk.Label(panel, text="Difficulty", bg=PANEL, fg=MUTED, font=FONT_TXT).grid(row=0, column=0, padx=(12,6), pady=12, sticky="w")
        diff = ttk.Combobox(panel, textvariable=self.difficulty, values=["Easy","Medium","Impossible"], state="readonly", width=14)
        diff.grid(row=0, column=1, pady=12, sticky="w")
        self._style_ttk()
        # Buttons
        btn_restart = tk.Button(panel, text="Restart Board", command=self.restart_board,
                                bg=ACCENT, fg="white", activebackground=ACCENT_DARK,
                                relief="flat", padx=14, pady=6, font=FONT_H2)
        btn_new = tk.Button(panel, text="New Match (Reset Score)", command=self.reset_match,
                            bg="#394164", fg=TXT, activebackground="#2c3350",
                            relief="flat", padx=14, pady=6, font=FONT_H2)
        btn_restart.grid(row=0, column=2, padx=(16,8))
        btn_new.grid(row=0, column=3, padx=(8,12))
        panel.grid_columnconfigure(4, weight=1)

        # Scoreboard
        board_panel = tk.Frame(self, bg=PANEL)
        board_panel.pack(padx=16, pady=(8,16))

        self.score_you = self._badge(board_panel, "YOU", self.score["You"], WIN)
        self.score_ai  = self._badge(board_panel, "AI", self.score["AI"], LOSS)
        self.score_tie = self._badge(board_panel, "TIES", self.score["Ties"], TIE)

        self.score_you.grid(row=0, column=0, padx=8, pady=12, sticky="nsew")
        self.score_ai.grid(row=0, column=1, padx=8, pady=12, sticky="nsew")
        self.score_tie.grid(row=0, column=2, padx=8, pady=12, sticky="nsew")

        # Grid (3x3)
        grid = tk.Frame(self, bg=BG)
        grid.pack(padx=16, pady=(0,12))

        for i in range(9):
            btn = tk.Button(
                grid, text="", width=4, height=2,
                font=FONT_TILE, relief="flat",
                bg=TILE_BG, fg=TXT, activebackground=TILE_ACTIVE,
                command=lambda i=i: self.on_tile(i)
            )
            r, c = divmod(i, 3)
            btn.grid(row=r, column=c, padx=8, pady=8, ipadx=8, ipady=8, sticky="nsew")
            self.buttons.append(btn)

        # Status bar
        status_bar = tk.Frame(self, bg=PANEL)
        status_bar.pack(padx=16, pady=(0,16), fill="x")
        self.status = tk.Label(status_bar, textvariable=self.status_var, bg=PANEL, fg=MUTED, font=FONT_H2, anchor="w")
        self.status.pack(fill="x", padx=12, pady=10)

    def _style_ttk(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("TCombobox",
                        fieldbackground=PANEL,
                        background=PANEL,
                        foreground=TXT)
        style.map("TCombobox",
                  fieldbackground=[("readonly", PANEL)],
                  foreground=[("readonly", TXT)])
    
    def _badge(self, parent, label, value, color):
        frame = tk.Frame(parent, bg=PANEL, padx=16, pady=12)
        title = tk.Label(frame, text=label, bg=PANEL, fg=MUTED, font=FONT_TXT)
        num = tk.Label(frame, text=str(value), bg=PANEL, fg=color, font=("Segoe UI", 22, "bold"))
        title.pack()
        num.pack()
        # Store label ref to update later
        frame.value_label = num
        return frame

    # ---------- Game flow ----------
    def on_tile(self, idx):
        if self.board[idx] != "" or self.turn != self.player:
            return
        self._place(idx, self.player)
        winner, combo = check_winner(self.board)
        if winner:
            self._finalize(winner, combo)
            return
        # AI turn
        self.turn = self.ai
        self.status_var.set("AI is thinking…")
        self.after(450, self.ai_move)

    def ai_move(self):
        idx = self._choose_ai_move()
        if idx is not None:
            self._place(idx, self.ai)
        winner, combo = check_winner(self.board)
        if winner:
            self._finalize(winner, combo)
        else:
            self.turn = self.player
            self.status_var.set("Your turn (X)")

    def _choose_ai_move(self):
        empty = [i for i,v in enumerate(self.board) if v == ""]
        if not empty:
            return None
        mode = self.difficulty.get()
        if mode == "Easy":
            # 80% random, 20% best
            return random.choice(empty) if random.random() < 0.8 else best_move(self.board[:], self.ai, self.player)
        elif mode == "Medium":
            # 50% best, 50% random
            return best_move(self.board[:], self.ai, self.player) if random.random() < 0.5 else random.choice(empty)
        else:
            # Impossible = optimal
            return best_move(self.board[:], self.ai, self.player)

    def _place(self, idx, symbol):
        self.board[idx] = symbol
        self.buttons[idx].config(text=symbol, state="disabled")
        # little tap animation
        self._tap(self.buttons[idx])

    def _tap(self, btn):
        # Simple visual press feedback via bg toggle
        orig = btn.cget("bg")
        btn.config(bg=TILE_ACTIVE)
        self.after(90, lambda: btn.config(bg=orig))

    def _finalize(self, winner, combo):
        # Disable tiles
        for b in self.buttons:
            b.config(state="disabled")
        if winner == "Tie":
            self.status_var.set("Game over — Tie")
            self.score["Ties"] += 1
            self._update_score()
            # soft flash all tiles
            self._pulse_tiles([i for i in range(9)], TIE)
            self.after(1200, self.restart_board)
            return

        # Someone won
        if winner == self.player:
            self.status_var.set("You win! 🎉")
            self.score["You"] += 1
            color = WIN
        else:
            self.status_var.set("AI wins! 🤖")
            self.score["AI"] += 1
            color = LOSS

        self._update_score()
        self.win_combo = combo
        self._pulse_tiles(combo, color)
        self.after(1400, self.restart_board)

    def _pulse_tiles(self, indices, color):
        # Pulse winning/tie tiles a couple of times
        def toggle():
            self.pulse_on = not self.pulse_on
            for i in range(9):
                if i in indices:
                    self.buttons[i].config(bg=(color if self.pulse_on else TILE_BG))
                else:
                    self.buttons[i].config(bg=TILE_BG)
        # 4 pulses
        seq = [150, 300, 450, 600, 750, 900]
        for i, delay in enumerate(seq):
            self.after(delay, toggle)

    def _update_score(self):
        self.score_you.value_label.config(text=str(self.score["You"]))
        self.score_ai.value_label.config(text=str(self.score["AI"]))
        self.score_tie.value_label.config(text=str(self.score["Ties"]))

    # ---------- Controls ----------
    def restart_board(self):
        # stop any pulse visuals
        self.pulse_on = False
        self.win_combo = None
        self.board = [""]*9
        for b in self.buttons:
            b.config(text="", state="normal", bg=TILE_BG)
        self.turn = self.player
        self.status_var.set("Your turn (X)")

    def reset_match(self):
        if messagebox.askyesno("Reset Match", "Reset scores and clear the board?"):
            self.score = {"You":0, "AI":0, "Ties":0}
            self._update_score()
            self.restart_board()


if __name__ == "__main__":
    app = TicTacToeApp()
    app.mainloop()
