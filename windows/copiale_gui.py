#!/usr/bin/env python3
"""Simple GUI for Copiale cipher translator."""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

# Add the repo root (parent of this folder) to path so `copiale` is found.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copiale import encode, decode, CopialeError
from copiale.locked import generate_key


class CopialeTranslator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Copiale Cipher Translator")
        self.geometry("750x500")
        self.minsize(650, 450)

        # Mode
        self.mode = tk.StringVar(value="encode")
        self.strict = tk.BooleanVar(value=False)
        self.key_var = tk.StringVar(value="")

        # Top frame - controls
        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill="x")

        ttk.Label(control_frame, text="Mode:").pack(side="left", padx=(0, 5))
        mode_combo = ttk.Combobox(
            control_frame,
            textvariable=self.mode,
            values=("encode", "decode"),
            state="readonly",
            width=20,
        )
        mode_combo.pack(side="left", padx=(0, 10))
        mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

        strict_check = ttk.Checkbutton(
            control_frame, text="Strict mode", variable=self.strict
        )
        strict_check.pack(side="left", padx=(0, 10))

        ttk.Button(control_frame, text="Swap", command=self.swap).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(control_frame, text="Clear", command=self.clear).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(control_frame, text="Translate", command=self.translate).pack(
            side="left", padx=(5, 0)
        )

        # Key frame - optional locked mode
        key_frame = ttk.Frame(self, padding="0 10 10 0")
        key_frame.pack(fill="x")

        ttk.Label(key_frame, text="Key (optional):").pack(side="left", padx=(10, 5))
        key_entry = ttk.Entry(key_frame, textvariable=self.key_var, width=30)
        key_entry.pack(side="left", padx=(0, 5))
        ttk.Button(key_frame, text="New key", command=self.new_key).pack(
            side="left", padx=(0, 5)
        )
        ttk.Label(
            key_frame,
            text="leave empty for normal use",
            foreground="gray",
        ).pack(side="left")

        # Labels
        labels_frame = ttk.Frame(self, padding="5 0 10 0")
        labels_frame.pack(fill="x")

        self.input_label = ttk.Label(labels_frame, text="English (plaintext):")
        self.input_label.pack(side="left", padx=(5, 0))

        ttk.Label(labels_frame, text="Result:").pack(side="right", padx=(0, 5))

        # Text areas
        text_frame = ttk.Frame(self, padding="5 5 10 10")
        text_frame.pack(fill="both", expand=True)

        self.input_text = scrolledtext.ScrolledText(
            text_frame, wrap="word", height=10, font=("Consolas", 10)
        )
        self.input_text.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.input_text.bind("<Control-Return>", lambda e: self.translate())

        self.output_text = scrolledtext.ScrolledText(
            text_frame,
            wrap="word",
            height=10,
            font=("Consolas", 10),
            state="disabled",
        )
        self.output_text.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken")
        status_bar.pack(fill="x", side="bottom")

        self._on_mode_change()

    def _on_mode_change(self, event=None):
        if self.mode.get() == "encode":
            self.input_label.config(text="English (plaintext):")
            self.status_var.set("Type English text to encode → Tokens")
        else:
            self.input_label.config(text="Cipher tokens (space separated):")
            self.status_var.set("Type space-separated tokens to decode → English")

    def swap(self):
        inp = self.input_text.get("1.0", "end-1c")
        out = self._get_output()
        if self.mode.get() == "encode":
            self.mode.set("decode")
        else:
            self.mode.set("encode")
        self._on_mode_change()
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", out)
        self._set_output(inp)

    def clear(self):
        self.input_text.delete("1.0", "end")
        self._set_output("")
        self.status_var.set("Cleared")

    def _get_output(self):
        return self.output_text.get("1.0", "end-1c")

    def _set_output(self, text):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def new_key(self):
        self.key_var.set(generate_key())
        self.status_var.set("Fresh key generated — share it with the recipient")

    def translate(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            self.status_var.set("Enter text to translate")
            return

        mode_strict = "strict" if self.strict.get() else "experimental"
        key = self.key_var.get().strip() or None

        try:
            if self.mode.get() == "encode":
                res = encode(text, mode=mode_strict, key=key)
                tokens = " ".join(res["tokens"])
                self._set_output(tokens)
                notes = " ".join(res["notes"]) if res["notes"] else ""
                if key:
                    self.status_var.set(
                        f"Locked with key ({len(res['tokens'])} tokens) — "
                        f"share the tokens AND the key"
                    )
                elif notes:
                    self.status_var.set(notes)
                else:
                    self.status_var.set(f"Encoded {len(res['tokens'])} tokens")
            else:
                # decode - split by whitespace
                token_str = text
                # handle multiple spaces
                tokens_list = token_str.split()
                res = decode(tokens_list, mode=mode_strict, key=key)
                self._set_output(res["text"])
                notes = " ".join(res["notes"]) if res["notes"] else ""
                if key:
                    self.status_var.set("Unlocked with key")
                elif notes:
                    self.status_var.set(notes)
                else:
                    self.status_var.set("Decoded successfully")
        except CopialeError as e:
            messagebox.showerror("Translation Error", str(e))
            self.status_var.set("Error")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error")


if __name__ == "__main__":
    app = CopialeTranslator()
    app.mainloop()
