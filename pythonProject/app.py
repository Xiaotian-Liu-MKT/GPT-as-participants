"""Modernized Tkinter GUI skeleton for the participant simulator.

This module implements the information architecture proposed in the design
specification.  It focuses on laying out the main navigation frames and
bilingual labels.  Business logic is intentionally minimal – most buttons are
placeholders that can be wired to the existing ``simulate_participants``
function in future work.

Run this module directly to launch the interface:

    python app.py

The UI uses ``ttk`` widgets and optionally styles provided by ``ttkbootstrap``
if it is installed in the environment.  It is safe to run without the extra
package; the appearance will simply fall back to the default Tk theme.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Design tokens (subset)
# ---------------------------------------------------------------------------

FONT_FAMILY = "Inter"
TOKENS = {
    "primary": "#3B82F6",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#6366F1",
    "border": "#E5E7EB",
    "text_primary": "#111827",
    "text_secondary": "#4B5563",
}


# ---------------------------------------------------------------------------
# Helper widgets
# ---------------------------------------------------------------------------

class SidebarButton(ttk.Button):
    """Navigation button with consistent padding and style."""

    def __init__(self, master: tk.Misc, text: str, command) -> None:
        super().__init__(master, text=text, command=command, style="Sidebar.TButton")
        self.pack(fill="x", padx=8, pady=4)


class Placeholder(ttk.Frame):
    """Simple frame used as content placeholder."""

    def __init__(self, master: tk.Misc, title: str) -> None:
        super().__init__(master, padding=20)
        ttk.Label(self, text=title, font=(FONT_FAMILY, 16, "bold")).pack()


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class SimulatorApp(tk.Tk):
    """Top-level application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("GPT Participants – Dashboard")
        self.geometry("900x600")
        self._init_theme()

        self._content: dict[str, ttk.Frame] = {}
        self._build_layout()
        self.show("dashboard")

    # ------------------------------------------------------------------
    def _init_theme(self) -> None:
        """Initialize ``ttkbootstrap`` theme if available."""

        try:  # pragma: no cover - theme loading is cosmetic
            import ttkbootstrap as tb

            style = tb.Style("flatly")
            style.configure("Sidebar.TButton", font=(FONT_FAMILY, 12))
        except Exception:  # pragma: no cover - fallback
            style = ttk.Style()
            style.configure("Sidebar.TButton", font=(FONT_FAMILY, 12))
        finally:
            self.style = style

    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        """Create sidebar navigation and content frames."""

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Sidebar ----------------------------------------------------------------
        sidebar = ttk.Frame(container, width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        SidebarButton(sidebar, "Dashboard / 仪表盘", lambda: self.show("dashboard"))
        SidebarButton(sidebar, "Runs / 运行队列", lambda: self.show("runs"))
        SidebarButton(sidebar, "Results / 结果浏览器", lambda: self.show("results"))
        SidebarButton(sidebar, "Config / 配置与环境", lambda: self.show("config"))

        # Content stack -----------------------------------------------------------
        content = ttk.Frame(container)
        content.pack(side="left", fill="both", expand=True)

        self._content["dashboard"] = self._build_dashboard(content)
        self._content["runs"] = self._build_runs(content)
        self._content["results"] = self._build_results(content)
        self._content["config"] = self._build_config(content)

    # ------------------------------------------------------------------
    def show(self, name: str) -> None:
        """Raise the named content frame."""

        for frame in self._content.values():
            frame.pack_forget()
        self._content[name].pack(fill="both", expand=True)

    # -- Builders ---------------------------------------------------------------
    def _build_dashboard(self, master: tk.Misc) -> ttk.Frame:
        frame = ttk.Frame(master, padding=10)
        ttk.Label(frame, text="Dashboard / 仪表盘", font=(FONT_FAMILY, 20, "bold")).pack(
            anchor="w"
        )
        ttk.Button(frame, text="New Run / 新建运行", command=self._open_new_run).pack(
            pady=20, anchor="w"
        )
        return frame

    def _build_runs(self, master: tk.Misc) -> ttk.Frame:
        return Placeholder(master, "Runs / 运行队列")

    def _build_results(self, master: tk.Misc) -> ttk.Frame:
        return Placeholder(master, "Results / 结果浏览器")

    def _build_config(self, master: tk.Misc) -> ttk.Frame:
        return Placeholder(master, "Config / 配置与环境")

    # ------------------------------------------------------------------
    def _open_new_run(self) -> None:
        """Display a dialog for creating a new Run."""

        dlg = tk.Toplevel(self)
        dlg.title("New Run / 新建运行")
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=10)
        frm.pack(fill="both", expand=True)

        # Basic Info ------------------------------------------------------------
        info = ttk.LabelFrame(frm, text="Basic Info / 基本信息", padding=10)
        info.pack(fill="x", expand=False, pady=5)
        ttk.Label(info, text="Run Name / 名称").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(info, width=30).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(info, text="Project / 项目").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(info, width=30).grid(row=1, column=1, padx=4, pady=4)
        ttk.Label(info, text="Random Seed / 随机种子").grid(row=2, column=0, sticky="e", padx=4, pady=4)
        ttk.Spinbox(info, from_=0, to=999999).grid(row=2, column=1, padx=4, pady=4)

        # Review ----------------------------------------------------------------
        review = ttk.Frame(frm, padding=10)
        review.pack(fill="x", pady=10)
        ttk.Button(
            review, text="Start Simulation / 开始模拟", command=dlg.destroy, style="Accent.TButton"
        ).pack()

    # ------------------------------------------------------------------
    def run(self) -> None:
        self.mainloop()


def main() -> None:  # pragma: no cover - manual execution
    app = SimulatorApp()
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
