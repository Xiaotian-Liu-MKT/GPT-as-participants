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

import os
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import requests

from simulate import load_profile_config, simulate_participants

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
        """Recent projects, cost summary and quick run button."""

        frame = ttk.Frame(master, padding=10)
        ttk.Label(frame, text="Dashboard / 仪表盘", font=(FONT_FAMILY, 20, "bold")).pack(
            anchor="w"
        )

        # Recent runs table ----------------------------------------------------
        cols = ("project", "run", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=5)
        tree.heading("project", text="Project / 项目")
        tree.heading("run", text="Run")
        tree.heading("status", text="Status / 状态")
        tree.pack(fill="x", pady=10)

        # Cost summary ---------------------------------------------------------
        summary = ttk.Frame(frame)
        summary.pack(fill="x", pady=5)
        ttk.Label(summary, text="Estimated Cost / 预计成本: $0.00").pack(
            side="left", padx=5
        )
        ttk.Label(summary, text="Tokens Used / 已用 tokens: 0").pack(
            side="left", padx=5
        )

        ttk.Button(frame, text="New Run / 新建运行", command=self._open_new_run).pack(
            pady=10, anchor="e"
        )
        return frame

    def _build_runs(self, master: tk.Misc) -> ttk.Frame:
        """Run queue with detail preview."""

        frame = ttk.Frame(master, padding=10)
        ttk.Label(frame, text="Runs / 运行队列", font=(FONT_FAMILY, 20, "bold")).pack(
            anchor="w"
        )

        cols = ("project", "run", "status", "progress")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col.title())
        tree.pack(fill="both", expand=True)

        # Detail pane ----------------------------------------------------------
        detail = ttk.LabelFrame(frame, text="Detail / 详情", padding=10)
        detail.pack(fill="x", pady=5)
        ttk.Progressbar(detail, mode="determinate", value=40).pack(fill="x", pady=5)
        ttk.Label(detail, text="Log (sample) / 日志示例").pack(anchor="w")
        tk.Text(detail, height=4).pack(fill="x")
        btns = ttk.Frame(detail)
        btns.pack(fill="x", pady=5)
        ttk.Button(btns, text="Pause / 暂停").pack(side="left", padx=2)
        ttk.Button(btns, text="Cancel / 取消").pack(side="left", padx=2)
        ttk.Button(btns, text="Retry Failed Jobs / 仅重试失败项").pack(side="left", padx=2)
        return frame

    def _build_results(self, master: tk.Misc) -> ttk.Frame:
        """Results browser with table and diff placeholder."""

        frame = ttk.Frame(master, padding=10)
        ttk.Label(frame, text="Results / 结果浏览器", font=(FONT_FAMILY, 20, "bold")).pack(
            anchor="w"
        )

        cols = ("participant", "condition", "model", "tokens")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col.title())
        tree.pack(fill="both", expand=True)

        diff = ttk.LabelFrame(frame, text="A/B Diff / A/B 差异", padding=5)
        diff.pack(fill="both", expand=True, pady=5)
        tk.Text(diff, height=6).pack(fill="both", expand=True)

        ttk.Button(frame, text="Export Selected / 导出选中").pack(anchor="e", pady=5)
        return frame

    def _build_config(self, master: tk.Misc) -> ttk.Frame:
        """Environment config and template placeholders."""

        frame = ttk.Frame(master, padding=10)
        ttk.Label(frame, text="Config / 配置与环境", font=(FONT_FAMILY, 20, "bold")).pack(
            anchor="w"
        )
        env = ttk.LabelFrame(frame, text=".env Status / 环境变量", padding=10)
        env.pack(fill="x", pady=5)
        ttk.Entry(env, width=40).pack(side="left", padx=5)
        ttk.Button(env, text="Test Connectivity / 测试连通性").pack(side="left")

        versions = ttk.LabelFrame(frame, text="Versions / 版本信息", padding=10)
        versions.pack(fill="x", pady=5)
        tk.Text(versions, height=4).pack(fill="x")

        templates = ttk.LabelFrame(frame, text="Templates / 模板管理", padding=10)
        templates.pack(fill="x", pady=5)
        ttk.Button(templates, text="Save Template / 保存模板").pack(side="left", padx=2)
        ttk.Button(templates, text="Load Template / 加载模板").pack(side="left", padx=2)
        return frame
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
        run_name = ttk.Entry(info, width=30)
        run_name.grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(info, text="Project / 项目").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        project = ttk.Entry(info, width=30)
        project.grid(row=1, column=1, padx=4, pady=4)
        ttk.Label(info, text="Random Seed / 随机种子").grid(row=2, column=0, sticky="e", padx=4, pady=4)
        seed = ttk.Spinbox(info, from_=0, to=999999)
        seed.grid(row=2, column=1, padx=4, pady=4)

        # Conditions & Prompt ---------------------------------------------------
        cond = ttk.LabelFrame(frm, text="Conditions & Prompt / 条件与提示", padding=10)
        cond.pack(fill="both", expand=True, pady=5)
        a_frame = ttk.Frame(cond)
        a_frame.pack(side="left", fill="both", expand=True, padx=5)
        b_frame = ttk.Frame(cond)
        b_frame.pack(side="left", fill="both", expand=True, padx=5)
        for label, frame in (("A", a_frame), ("B", b_frame)):
            ttk.Label(frame, text=f"Condition {label}").pack(anchor="w")
            btn = ttk.Button(frame, text="Load / 载入", command=lambda f=frame: self._load_file_into_text(f))
            btn.pack(anchor="e")
            txt = tk.Text(frame, width=40, height=6)
            txt.pack(fill="both", expand=True)

            # Preload default condition text from file if available
            try:
                file_path = Path(__file__).with_name(f"condition{label}.txt")
                txt.insert("1.0", file_path.read_text(encoding="utf-8"))
            except OSError:
                # Missing or unreadable file – leave text widget empty
                pass

        ttk.Label(cond, text="Diff (preview) / 差异预览").pack(anchor="w", pady=5)
        tk.Text(cond, height=4).pack(fill="x")

        # Participant Profile ---------------------------------------------------
        profile = ttk.LabelFrame(frm, text="Participant Profile / 参与者画像", padding=10)
        profile.pack(fill="both", expand=True, pady=5)
        mode = tk.StringVar(value="form")
        switch = ttk.Frame(profile)
        switch.pack(anchor="w")
        ttk.Radiobutton(
            switch,
            text="Form / 表单",
            variable=mode,
            value="form",
            command=lambda: self._toggle_profile(profile, mode),
        ).pack(side="left")
        ttk.Radiobutton(
            switch,
            text="JSON",
            variable=mode,
            value="json",
            command=lambda: self._toggle_profile(profile, mode),
        ).pack(side="left")

        form_frame = ttk.Frame(profile)
        form_frame.pack(fill="x")

        # Load trait definitions and build form inputs dynamically
        config_path = Path(__file__).with_name("profile_config.json")
        _, trait_defs = load_profile_config(config_path)
        if not trait_defs:  # fallback to example config
            _, trait_defs = load_profile_config(Path(__file__).with_name("profile_config.example.json"))

        trait_entries: dict[str, ttk.Entry] = {}
        for row, trait in enumerate(trait_defs):
            ttk.Label(form_frame, text=f"{trait} (range)").grid(
                row=row, column=0, sticky="e", padx=4, pady=2
            )
            ent = ttk.Entry(form_frame)
            ent.insert(0, "1-7")
            ent.grid(row=row, column=1, padx=4, pady=2)
            trait_entries[trait] = ent

        json_frame = ttk.Frame(profile)
        json_text = tk.Text(json_frame, height=5)
        json_text.pack(fill="both", expand=True)

        profile.form_frame = form_frame  # type: ignore[attr-defined]
        profile.json_frame = json_frame  # type: ignore[attr-defined]

        # Model Provider -------------------------------------------------------
        participants = tk.IntVar(value=200)
        concurrency = tk.IntVar(value=1)
        budget = tk.DoubleVar(value=0.0)
        cost_var = tk.StringVar(value="$0.00")
        max_tokens_var = tk.IntVar(value=256)

        provider = ttk.LabelFrame(frm, text="Model Provider / 模型供应商", padding=10)
        provider.pack(fill="x", pady=5)
        prov_var = tk.StringVar()
        model_var = tk.StringVar()
        prov_combo = ttk.Combobox(
            provider,
            values=["OpenAI", "Gemini", "GitHub"],
            textvariable=prov_var,
            state="readonly",
        )
        prov_combo.grid(row=0, column=0, padx=4, pady=4)
        model_combo = ttk.Combobox(provider, textvariable=model_var, state="readonly")
        model_combo.grid(row=0, column=1, padx=4, pady=4)

        def fetch_models_for_provider(name: str) -> list[str]:
            try:
                if name == "GitHub":
                    headers = {"X-GitHub-Api-Version": "2022-11-28"}
                    token = os.getenv("GITHUB_TOKEN")
                    if token:
                        headers["Authorization"] = f"Bearer {token}"
                    resp = requests.get(
                        "https://api.github.com/models", headers=headers, timeout=5
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    models: list[str] = []
                    if isinstance(data, dict):
                        items = data.get("data") or data.get("models") or data.get("items")
                        if isinstance(items, list):
                            for item in items:
                                if isinstance(item, dict):
                                    models.append(item.get("id") or item.get("name"))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                models.append(item.get("id") or item.get("name"))
                    return [m for m in models if m]
                if name == "OpenAI":
                    return ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                if name == "Gemini":
                    return ["gemini-1.5-flash", "gemini-1.5-pro"]
            except Exception:
                pass
            return []

        def on_provider_change(event: tk.Event | None = None) -> None:
            models = fetch_models_for_provider(prov_var.get())
            model_combo["values"] = models
            if models:
                model_var.set(models[0])
            else:
                model_var.set("")

        prov_combo.bind("<<ComboboxSelected>>", on_provider_change)
        prov_combo.current(0)
        on_provider_change()

        params = ttk.Frame(provider)
        params.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Label(params, text="temperature").grid(row=0, column=0)
        temp = ttk.Spinbox(params, from_=0.0, to=2.0, increment=0.1)
        temp.grid(row=0, column=1)
        ttk.Label(params, text="top_p").grid(row=0, column=2)
        top_p = ttk.Spinbox(params, from_=0.0, to=1.0, increment=0.05)
        top_p.grid(row=0, column=3)
        ttk.Label(params, text="max_tokens").grid(row=1, column=0)
        max_tokens = ttk.Spinbox(
            params,
            from_=1,
            to=4096,
            textvariable=max_tokens_var,
            command=lambda: self._update_cost(participants, max_tokens_var, cost_var),
        )
        max_tokens.grid(row=1, column=1)
        ttk.Label(params, text="seed").grid(row=1, column=2)
        model_seed = ttk.Spinbox(params, from_=0, to=999999)
        model_seed.grid(row=1, column=3)

        # Run Parameters --------------------------------------------------------
        run_params = ttk.LabelFrame(frm, text="Run Parameters / 运行参数", padding=10)
        run_params.pack(fill="x", pady=5)

        ttk.Label(run_params, text="Participants / 参与者数量").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        ttk.Spinbox(run_params, from_=1, to=10000, textvariable=participants, command=lambda: self._update_cost(participants, max_tokens_var, cost_var)).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(run_params, text="Concurrency / 并发").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        ttk.Spinbox(run_params, from_=1, to=10, textvariable=concurrency, command=lambda: self._concurrency_tip(concurrency)).grid(row=1, column=1, padx=4, pady=2)
        ttk.Label(run_params, text="Budget / 预算上限 ($)").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(run_params, textvariable=budget).grid(row=2, column=1, padx=4, pady=2)
        ttk.Label(run_params, text="Estimated Cost / 预计成本").grid(row=3, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(run_params, textvariable=cost_var).grid(row=3, column=1, sticky="w")

        # Review ----------------------------------------------------------------
        review = ttk.LabelFrame(frm, text="Review / 复核", padding=10)
        review.pack(fill="both", pady=5)
        snapshot = tk.Text(review, height=4)
        snapshot.pack(fill="both", expand=True)

        def start_and_close() -> None:
            data = {
                "run_name": run_name.get(),
                "project": project.get(),
                "seed": seed.get(),
                "provider": prov_var.get(),
                "model": model_var.get(),
                "participants": participants.get(),
            }

            trait_ranges: dict[str, tuple[int, int]] = {}
            for name, entry in trait_entries.items():
                text = entry.get().strip()
                try:
                    lo, hi = [int(x) for x in text.split("-")]
                except Exception:
                    lo, hi = 1, 7
                trait_ranges[name] = (lo, hi)

            snapshot.delete("1.0", tk.END)
            snapshot.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))

            try:
                simulate_participants(
                    participants.get(),
                    model_var.get() or "gpt-4o-mini",
                    traits=trait_ranges,
                )
            except Exception as exc:  # pragma: no cover - UI feedback
                messagebox.showerror("Simulation failed", str(exc))

            dlg.destroy()

        ttk.Button(
            review,
            text="Start Simulation / 开始模拟",
            command=start_and_close,
            style="Accent.TButton",
        ).pack(pady=5)

    # ------------------------------------------------------------------
    def run(self) -> None:
        self.mainloop()

    # Utility callbacks -------------------------------------------------
    def _load_file_into_text(self, frame: ttk.Frame) -> None:
        """Load a text file into the first Text widget of ``frame``."""

        path = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*")])
        if not path:
            return
        widget = next((w for w in frame.winfo_children() if isinstance(w, tk.Text)), None)
        if widget is not None:
            with open(path, "r", encoding="utf-8") as fh:
                widget.delete("1.0", tk.END)
                widget.insert("1.0", fh.read())

    def _toggle_profile(self, frame: ttk.LabelFrame, mode: tk.StringVar) -> None:
        """Switch between profile form and JSON editor."""

        frame.form_frame.pack_forget()
        frame.json_frame.pack_forget()
        if mode.get() == "form":
            frame.form_frame.pack(fill="x")
        else:
            frame.json_frame.pack(fill="both", expand=True)

    def _update_cost(
        self, participants: tk.IntVar, max_tokens: tk.IntVar, cost_var: tk.StringVar
    ) -> None:
        """Very rough cost estimator based on participants and max tokens."""

        cost = participants.get() * max_tokens.get() * 0.000002  # placeholder rate
        cost_var.set(f"${cost:0.2f}")

    def _concurrency_tip(self, var: tk.IntVar) -> None:
        if var.get() > 1:
            messagebox.showinfo(
                "Concurrency Info",
                "High concurrency may hit rate limits. 并发过高可能触发速率限制",
            )


def main() -> None:  # pragma: no cover - manual execution
    app = SimulatorApp()
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
