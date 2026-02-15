"""Docling Installer (zero-dependency bootstrap).

- Uses only Python standard library in installer process.
- Creates a virtual environment and installs runtime dependencies.
- Writes runnable launcher artifacts.
"""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

APP_NAME = "Docling 설치 관리자"
DEFAULT_DIRNAME = "PDF_Indexer_v43"

RUNNER_SOURCE = r'''import os
import threading
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from docling.document_converter import DocumentConverter


class RunnerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Docling 실행기")
        self.root.geometry("980x700")
        self.root.configure(bg="#f4f6f8")

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.running = False

        self._build_ui()

    def _build_ui(self) -> None:
        wrapper = tk.Frame(self.root, bg="#f4f6f8", padx=16, pady=16)
        wrapper.pack(fill="both", expand=True)

        tk.Label(
            wrapper,
            text="Docling PDF 변환 실행기",
            font=("Malgun Gothic", 18, "bold"),
            fg="#1f3a56",
            bg="#f4f6f8",
        ).pack(anchor="w", pady=(0, 14))

        p1 = tk.Frame(wrapper, bg="#f4f6f8")
        p1.pack(fill="x", pady=(0, 8))
        tk.Label(p1, text="입력 폴더", bg="#f4f6f8", font=("Malgun Gothic", 10, "bold")).pack(side="left", padx=(0, 8))
        tk.Entry(p1, textvariable=self.input_dir, font=("Consolas", 10)).pack(side="left", fill="x", expand=True)
        tk.Button(p1, text="찾아보기", command=self.select_input).pack(side="left", padx=(8, 0))

        p2 = tk.Frame(wrapper, bg="#f4f6f8")
        p2.pack(fill="x", pady=(0, 8))
        tk.Label(p2, text="출력 폴더", bg="#f4f6f8", font=("Malgun Gothic", 10, "bold")).pack(side="left", padx=(0, 8))
        tk.Entry(p2, textvariable=self.output_dir, font=("Consolas", 10)).pack(side="left", fill="x", expand=True)
        tk.Button(p2, text="찾아보기", command=self.select_output).pack(side="left", padx=(8, 0))

        self.pb = ttk.Progressbar(wrapper, mode="determinate", maximum=100)
        self.pb.pack(fill="x", pady=(8, 8))

        self.status = tk.StringVar(value="대기 중")
        tk.Label(wrapper, textvariable=self.status, bg="#f4f6f8", fg="#34495e", font=("Malgun Gothic", 10)).pack(anchor="w")

        self.log = tk.Text(wrapper, height=22, font=("Consolas", 9), bg="#ffffff")
        self.log.pack(fill="both", expand=True, pady=(10, 10))

        self.btn = tk.Button(
            wrapper,
            text="변환 시작",
            command=self.start,
            font=("Malgun Gothic", 13, "bold"),
            bg="#1e8449",
            fg="white",
            height=2,
        )
        self.btn.pack(fill="x")

    def select_input(self) -> None:
        d = filedialog.askdirectory()
        if d:
            self.input_dir.set(d)

    def select_output(self) -> None:
        d = filedialog.askdirectory()
        if d:
            self.output_dir.set(d)

    def append_log(self, text: str) -> None:
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def set_progress(self, done: int, total: int) -> None:
        percent = int((done / total) * 100) if total else 0
        self.pb.configure(value=percent)

    def start(self) -> None:
        if self.running:
            return
        if not self.input_dir.get() or not self.output_dir.get():
            messagebox.showwarning("경고", "입력/출력 폴더를 먼저 지정하세요.")
            return
        self.running = True
        self.btn.configure(state="disabled", text="변환 진행 중...")
        threading.Thread(target=self.run_convert, daemon=True).start()

    def run_convert(self) -> None:
        try:
            inp = self.input_dir.get()
            out = self.output_dir.get()
            os.makedirs(out, exist_ok=True)

            pdfs = [f for f in os.listdir(inp) if f.lower().endswith('.pdf')]
            total = len(pdfs)
            if total == 0:
                self.status.set("PDF 파일이 없습니다.")
                self.append_log("[INFO] 입력 폴더에 PDF가 없습니다.")
                return

            conv = DocumentConverter()
            ok = 0
            fail = 0

            for i, name in enumerate(pdfs, start=1):
                src = os.path.join(inp, name)
                stem = os.path.splitext(name)[0]
                self.status.set(f"변환 중: {name} ({i}/{total})")
                self.append_log(f"[START] {name}")
                try:
                    result = conv.convert(src)
                    doc = result.document
                    md_path = os.path.join(out, stem + ".md")
                    txt_path = os.path.join(out, stem + ".txt")

                    md_text = ""
                    if hasattr(doc, "export_to_markdown"):
                        md_text = doc.export_to_markdown()
                    elif hasattr(doc, "export_to_text"):
                        md_text = doc.export_to_text()
                    else:
                        md_text = str(doc)

                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(md_text)
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(md_text)

                    ok += 1
                    self.append_log(f"[OK] {name} -> {os.path.basename(md_path)}")
                except Exception as e:
                    fail += 1
                    self.append_log(f"[FAIL] {name} : {e}")
                    self.append_log(traceback.format_exc())

                self.set_progress(i, total)

            self.status.set(f"완료: 성공 {ok} / 실패 {fail}")
            messagebox.showinfo("변환 완료", f"성공 {ok}개, 실패 {fail}개")
        finally:
            self.running = False
            self.btn.configure(state="normal", text="변환 시작")


if __name__ == "__main__":
    root = tk.Tk()
    RunnerApp(root)
    root.mainloop()
'''


class InstallerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("760x420")
        self.root.configure(bg="#f7f9fb")

        desktop = Path.home() / "Desktop"
        self.install_dir = tk.StringVar(value=str(desktop / DEFAULT_DIRNAME))
        self.status_text = tk.StringVar(value="대기 중")

        self.total_steps = 5
        self.current_step = 0

        self._build_ui()

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, bg="#f7f9fb", padx=18, pady=18)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Docling 설치 관리자 (실행 가능한 파일)",
            font=("Malgun Gothic", 16, "bold"),
            bg="#f7f9fb",
            fg="#1f3a56",
        ).pack(anchor="w", pady=(0, 14))

        row = tk.Frame(frame, bg="#f7f9fb")
        row.pack(fill="x")

        tk.Label(row, text="설치 경로", bg="#f7f9fb", font=("Malgun Gothic", 10, "bold")).pack(
            side="left", padx=(0, 10)
        )
        tk.Entry(row, textvariable=self.install_dir, font=("Consolas", 10)).pack(
            side="left", fill="x", expand=True
        )
        tk.Button(row, text="찾아보기", command=self.change_dir).pack(side="left", padx=(8, 0))

        tk.Label(frame, text="설치 단계 진행률", bg="#f7f9fb", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(20, 6))
        self.pb_total = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.pb_total.pack(fill="x")

        tk.Label(frame, text="현재 단계 진행률", bg="#f7f9fb", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(16, 6))
        self.pb_current = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.pb_current.pack(fill="x")

        tk.Label(frame, textvariable=self.status_text, bg="#f7f9fb", fg="#34495e").pack(anchor="w", pady=(16, 10))

        self.btn_install = tk.Button(
            frame,
            text="설치 시작",
            command=self.start_install,
            font=("Malgun Gothic", 14, "bold"),
            bg="#1e8449",
            fg="white",
            height=2,
        )
        self.btn_install.pack(fill="x", pady=(6, 0))

    def change_dir(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.install_dir.set(str(Path(selected) / DEFAULT_DIRNAME))

    def _set_status(self, text: str, step_progress: int | None = None) -> None:
        self.status_text.set(text)
        total = int((self.current_step / self.total_steps) * 100)
        self.pb_total.configure(value=total)
        if step_progress is not None:
            self.pb_current.configure(value=max(0, min(100, step_progress)))
        self.root.update_idletasks()

    def _run_cmd(self, cmd: list[str], cwd: str | None = None) -> None:
        subprocess.run(cmd, cwd=cwd, check=True, shell=False)

    def start_install(self) -> None:
        self.btn_install.configure(state="disabled", text="설치 진행 중...")
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self) -> None:
        try:
            if os.name != "nt":
                raise RuntimeError("이 설치 프로그램은 Windows 대상입니다.")

            target = Path(self.install_dir.get())
            venv_dir = target / "venv"

            self.current_step = 0
            self._set_status("1/5 설치 경로 생성 중...", 20)
            target.mkdir(parents=True, exist_ok=True)
            self.current_step = 1
            self._set_status("1/5 설치 경로 생성 완료", 100)

            self._set_status("2/5 가상환경 생성 중...", 15)
            self._run_cmd([sys.executable, "-m", "venv", str(venv_dir)])
            self.current_step = 2
            self._set_status("2/5 가상환경 생성 완료", 100)

            venv_python = venv_dir / "Scripts" / "python.exe"
            venv_pythonw = venv_dir / "Scripts" / "pythonw.exe"
            self._set_status("3/5 pip 업그레이드 중...", 25)
            self._run_cmd([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
            self.current_step = 3
            self._set_status("3/5 pip 업그레이드 완료", 100)

            self._set_status("4/5 필수 라이브러리 설치 중...", 30)
            self._run_cmd([str(venv_python), "-m", "pip", "install", "psutil", "pillow", "docling"])
            self.current_step = 4
            self._set_status("4/5 필수 라이브러리 설치 완료", 100)

            self._set_status("5/5 실행 파일 생성 중...", 20)
            runner_path = target / "runner_app.pyw"
            runner_path.write_text(RUNNER_SOURCE, encoding="utf-8")
            self._set_status("5/5 실행 파일 생성 완료", 55)

            launch = target / "RUN_DOCLING.bat"
            launch.write_text(
                f'@echo off\n'
                f'cd /d "{target}"\n'
                f'"{venv_pythonw}" "{runner_path}"\n'
                f'if %errorlevel% neq 0 (\n'
                f'  echo 실행 오류가 발생했습니다.\n'
                f'  pause\n'
                f')\n',
                encoding="utf-8",
            )

            vbs_path = target / "실행하기(무중단).vbs"
            vbs_path.write_text(
                'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run chr(34) & "{launch}" & chr(34), 0\n'
                'Set WshShell = Nothing\n',
                encoding="cp949",
            )

            self.current_step = 5
            self._set_status("5/5 설치 완료", 100)

            messagebox.showinfo(
                "설치 완료",
                "설치가 완료되었습니다.\n"
                f"경로: {target}\n\n"
                "실행 파일: RUN_DOCLING.bat 또는 실행하기(무중단).vbs",
            )
            self.btn_install.configure(state="normal", text="설치 다시 실행")

        except Exception as exc:
            log_path = Path.cwd() / "installer_boot.log"
            log_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
            self.status_text.set(f"설치 실패: {exc}")
            messagebox.showerror("설치 실패", f"오류: {exc}\n로그: {log_path}")
            self.btn_install.configure(state="normal", text="설치 재시도")


if __name__ == "__main__":
    tk_root = tk.Tk()
    InstallerApp(tk_root)
    tk_root.mainloop()
