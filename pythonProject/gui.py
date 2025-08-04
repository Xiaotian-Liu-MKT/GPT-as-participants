"""Simple Tkinter GUI for the participant simulator.

This interface wraps :func:`simulate_participants` so that non-technical
users can run the experiment generation without touching the command line.
"""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from simulate import simulate_participants


class SimulatorGUI(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("GPT Participants Simulator")
        self.resizable(False, False)

        # Variables
        self.participants_var = tk.StringVar(value="200")
        self.model_var = tk.StringVar(value="gpt-4o-mini")
        self.output_var = tk.StringVar()
        default_profile = Path(__file__).parent / "profile_config.json"
        self.profile_var = tk.StringVar(
            value=str(default_profile) if default_profile.exists() else ""
        )
        self.status_var = tk.StringVar(value="Ready")

        self._build_widgets()

    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        padding = {"padx": 5, "pady": 5}

        frm = ttk.Frame(self)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Participants:").grid(row=0, column=0, **padding, sticky="e")
        ttk.Entry(frm, textvariable=self.participants_var, width=10).grid(
            row=0, column=1, **padding
        )

        ttk.Label(frm, text="Model:").grid(row=1, column=0, **padding, sticky="e")
        ttk.Entry(frm, textvariable=self.model_var, width=15).grid(
            row=1, column=1, **padding
        )

        ttk.Label(frm, text="Output file:").grid(row=2, column=0, **padding, sticky="e")
        ttk.Entry(frm, textvariable=self.output_var, width=30).grid(
            row=2, column=1, **padding
        )
        ttk.Button(frm, text="Browse", command=self._select_output).grid(
            row=2, column=2, **padding
        )

        ttk.Label(frm, text="Profile config:").grid(
            row=3, column=0, **padding, sticky="e"
        )
        ttk.Entry(frm, textvariable=self.profile_var, width=30).grid(
            row=3, column=1, **padding
        )
        ttk.Button(frm, text="Browse", command=self._select_profile).grid(
            row=3, column=2, **padding
        )

        ttk.Button(frm, text="Start Simulation", command=self._start).grid(
            row=4, column=0, columnspan=3, pady=10
        )

        ttk.Label(frm, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=3, **padding
        )

    # ------------------------------------------------------------------
    def _select_output(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if path:
            self.output_var.set(path)

    def _select_profile(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if path:
            self.profile_var.set(path)

    def _start(self) -> None:
        try:
            count = int(self.participants_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Participants must be an integer")
            return

        model = self.model_var.get().strip()
        output = Path(self.output_var.get().strip()) if self.output_var.get().strip() else None
        profile = (
            Path(self.profile_var.get().strip()) if self.profile_var.get().strip() else None
        )

        self.status_var.set("Running...")
        self.after(100, lambda: self._run_simulation(count, model, output, profile))

    def _run_simulation(
        self, count: int, model: str, output: Path | None, profile: Path | None
    ) -> None:
        def task() -> None:
            try:
                result = simulate_participants(count, model, output, profile)
            except Exception as exc:  # pragma: no cover - GUI feedback
                self.status_var.set("Error")
                messagebox.showerror("Simulation failed", str(exc))
            else:
                self.status_var.set(f"Done: {result}")
                messagebox.showinfo("Simulation complete", f"Results saved to {result}")

        threading.Thread(target=task, daemon=True).start()


def main() -> None:  # pragma: no cover - manual invocation
    app = SimulatorGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

