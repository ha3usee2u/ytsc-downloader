import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from downloader import download_music
from utils import preprocess_queries, is_url, smart_query_mode
from config import DEFAULT_FORMAT, DEFAULT_QUALITY, DEFAULT_SLEEP, DEFAULT_MIN_DURATION_MINUTES, \
DEFAULT_MAX_DURATION_MINUTES, DEFAULT_PLATFORM, DEFAULT_OUTPUT_DIR, DEFAULT_REMOVE_NUMBER, DEFAULT_MAX_RESULTS
import os
import threading

def start_gui():
    def browse_directory():
        path = filedialog.askdirectory()
        if path:
            path_entry.delete(0, tk.END)
            path_entry.insert(0, path)

    def refresh_preview():
        raw_text = query_entry.get("1.0", tk.END).strip()
        search_queries = preprocess_queries(raw_text, remove_number_var.get())
        preview_listbox.delete(0, tk.END)
        for item in search_queries:
            label = "[URL] " + item if is_url(item) else item
            preview_listbox.insert(tk.END, label)

    def update_progress(current, total, title):
        percent = (current / total) * 100
        progress["value"] = percent
        progress_label.config(text=f"進度：{current}/{total} | 現在下載：{title}")
        root.update_idletasks()

    def start_download():
        download_button.config(text="下載中...", state="disabled") # 禁用按鈕

        raw_text = query_entry.get("1.0", tk.END).strip()
        queries = preprocess_queries(raw_text, remove_number_var.get())
        output_path = path_entry.get().strip()

        if not output_path or not os.path.isdir(output_path):
            messagebox.showerror("錯誤", "請輸入有效的下載資料夾路徑")
            download_button.config(text="開始下載", state="normal")
            return
        if not queries:
            messagebox.showwarning("錯誤", "請輸入至少一個搜尋關鍵字")
            download_button.config(text="開始下載", state="normal")
            return

        try:
            min_duration = int(float(min_duration_entry.get()) * 60)
            max_duration = int(float(max_duration_entry.get()) * 60)
            sleep_interval = int(sleep_entry.get())
        except ValueError:
            messagebox.showerror("錯誤", "請輸入正確的數值")
            download_button.config(text="開始下載", state="normal")
            return

        try:
            max_results = int(max_results_entry.get())
        except ValueError:
            messagebox.showerror("錯誤", "請輸入正確的 max_results 整數")
            download_button.config(text="開始下載", state="normal")
            return

        options = {
            "format": audio_format.get(),
            "quality": audio_quality.get(),
            "output_path": output_path,
            "platform": source_platform.get(),
            "min_duration": min_duration,
            "max_duration": max_duration,
            "sleep": sleep_interval,
            "max_results": max_results,
            "download_type": download_type.get()
        }

        def finish_download_ui(success, skipped):
            msg = f"✅ 成功下載：{len(success)} 首\n⏭ 跳過項目：{len(skipped)} 筆"

            if success:
                msg += "\n\n成功：\n" + "\n".join(success)
            if skipped:
                msg += "\n\n跳過：\n" + "\n".join(skipped)

            messagebox.showinfo("下載完成", msg)

            progress["value"] = 0
            progress_label.config(text="準備下載...")
            download_button.config(text="開始下載", state="normal")

        def threaded_download():
            success, skipped = download_music(queries, options, update_progress)
            root.after(0, lambda: finish_download_ui(success, skipped))

        threading.Thread(target=threaded_download).start()

    # GUI 介面建立
    global root
    root = tk.Tk()
    root.title("音樂下載器（YT & SoundCloud）")

    # 主框架分成左右兩欄
    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10, fill="both")

    setting_frame = tk.Frame(main_frame)
    setting_frame.pack(side="left", padx=(0, 10), anchor="n")

    query_frame = tk.Frame(main_frame)
    query_frame.pack(side="right", anchor="n")

    # 右側：搜尋與預覽區域
    tk.Label(query_frame, text="搜尋關鍵字或網址（每行一個）:").pack(anchor="w")
    query_entry = tk.Text(query_frame, height=12, width=50)
    query_entry.pack()
    query_entry.bind("<KeyRelease>", lambda e: refresh_preview())

    remove_number_var = tk.BooleanVar(value=True)
    remove_number_check = tk.Checkbutton(query_frame, text="自動去除數字標號", variable=remove_number_var)
    remove_number_check.pack(anchor="w", pady=(5, 0))

    tk.Label(query_frame, text="歌曲預覽（已判別是否為 URL）:").pack(anchor="w")
    preview_listbox = tk.Listbox(query_frame, height=8, width=50)
    preview_listbox.pack()

    # 左側：下載設定欄
    tk.Label(setting_frame, text="下載資料夾路徑:").pack(anchor="w")
    path_subframe = tk.Frame(setting_frame)
    path_subframe.pack(fill="x")
    path_entry = tk.Entry(path_subframe, width=30)
    path_entry.pack(side="left", fill="x", expand=True)
    browse_btn = tk.Button(path_subframe, text="瀏覽", command=browse_directory)
    browse_btn.pack(side="left", padx=5)

    # 📌 下載類型下拉選單
    tk.Label(setting_frame, text="下載類型:").pack(anchor="w", pady=(10, 0))
    download_type = tk.StringVar(value="音樂")
    download_type_box = ttk.Combobox(setting_frame, textvariable=download_type, values=["音樂", "影片"], state="readonly", width=10)
    download_type_box.pack()

    # 建立音訊設定區塊
    audio_settings_frame = tk.Frame(setting_frame)

    # 音訊格式
    label_audio_format = tk.Label(audio_settings_frame, text="音訊格式:")
    label_audio_format.pack(anchor="w", pady=(10, 0))
    audio_format = tk.StringVar(value="mp3")
    combo_audio_format = ttk.Combobox(audio_settings_frame, textvariable=audio_format,
                                    values=["mp3", "m4a", "wav"], state="readonly", width=10)
    combo_audio_format.pack()

    # 音訊品質
    label_audio_quality = tk.Label(audio_settings_frame, text="音訊品質 (kbps):")
    label_audio_quality.pack(anchor="w", pady=(10, 0))
    audio_quality = tk.StringVar(value="320")
    combo_audio_quality = ttk.Combobox(audio_settings_frame, textvariable=audio_quality,
                                        values=["128", "192", "320"], state="readonly", width=10)
    combo_audio_quality.pack()

    # 用 pack() 固定位置（初始顯示）
    audio_settings_frame.pack(anchor="w", fill="x")

    # 切換類型時顯示/遮蔽內容但保留位置
    def toggle_audio_settings(event=None):
        if download_type.get() == "音樂":
            label_audio_format.pack(anchor="w", pady=(10, 0))
            combo_audio_format.pack()
            label_audio_quality.pack(anchor="w", pady=(10, 0))
            combo_audio_quality.pack()
        else:
            label_audio_format.pack_forget()
            combo_audio_format.pack_forget()
            label_audio_quality.pack_forget()
            combo_audio_quality.pack_forget()

    # 綁定事件
    download_type_box.bind("<<ComboboxSelected>>", toggle_audio_settings)


    # 建立新的一列 Frame
    duration_frame = tk.Frame(setting_frame)
    duration_frame.pack(anchor="w", pady=(10, 0))

    # 最短長度（左側）
    tk.Label(duration_frame, text="最短長度（分鐘）:").pack(side="left")
    min_duration_entry = tk.Entry(duration_frame, width=5)
    min_duration_entry.insert(0, "0")
    min_duration_entry.pack(side="left", padx=(5, 15))  # 增加左右間距

    # 最長長度（右側）
    tk.Label(duration_frame, text="最長長度（分鐘）:").pack(side="left")
    max_duration_entry = tk.Entry(duration_frame, width=5)
    max_duration_entry.insert(0, "10")
    max_duration_entry.pack(side="left", padx=5)

    tk.Label(setting_frame, text="間隔秒數 sleep_interval:").pack(anchor="w", pady=(10, 0))
    sleep_entry = tk.Entry(setting_frame, width=10)
    sleep_entry.insert(0, "10")
    sleep_entry.pack()

    tk.Label(setting_frame, text="最大搜尋結果數（max_results）:").pack(anchor="w", pady=(10, 0))
    max_results_entry = tk.Entry(setting_frame, width=10)
    max_results_entry.insert(0, "3")  # 預設值，例如只抓前三筆
    max_results_entry.pack()

    tk.Label(setting_frame, text="來源平台:").pack(anchor="w", pady=(10, 0))
    source_platform = tk.StringVar(value="YouTube")
    ttk.Combobox(setting_frame, textvariable=source_platform, values=["YouTube", "SoundCloud"], state="readonly", width=15).pack()

    download_button = tk.Button(setting_frame, text="開始下載", command=start_download)
    download_button.pack(pady=(15, 5))

    progress = ttk.Progressbar(setting_frame, length=250, mode="determinate")
    progress.pack()
    progress_label = tk.Label(
        setting_frame,
        text="準備下載...",
        width=40,              # 固定寬度（可微調）
        anchor="w",            # 左對齊
        justify="left",        # 左段落對齊
        wraplength=300         # 限定換行寬度
    )
    progress_label.pack()

    root.mainloop()

