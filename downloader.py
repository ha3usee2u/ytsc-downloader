import subprocess
import sys
import os
import tempfile
import shutil
import time
import json
from utils import smart_query_mode
from urllib.parse import urlparse
import datetime

def extract_binary(name):
    # 從 PyInstaller 打包的 _MEIPASS 資料夾取出執行檔
    if hasattr(sys, "_MEIPASS"):
        source_path = os.path.join(sys._MEIPASS, name)
    else:
        source_path = os.path.join(os.getcwd(), name)

    target_path = os.path.join(tempfile.gettempdir(), name)

    if not os.path.exists(target_path):
        shutil.copy(source_path, target_path)

    return target_path

def call_yt_dlp(url, output_path, format_selected, quality_selected):
    yt_dlp_path = extract_binary("yt-dlp.exe")
    if not os.path.exists(yt_dlp_path):
        print("❌ 錯誤：找不到 yt-dlp.exe，請將執行檔放在程式目錄中")
        return

    command = [
        yt_dlp_path, url,
        "--extract-audio",
        "--audio-format", format_selected,
        "--audio-quality", quality_selected,
        "--no-playlist",
        "-o", f"{output_path}/%(title)s.%(ext)s"
    ]

    try:
        subprocess.run(
            command,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW  # 隱藏 CMD 視窗
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ 下載失敗：{url}\n{e}")

def call_yt_dlp_video(url, output_path):
    yt_dlp_path = extract_binary("yt-dlp.exe")
    if not os.path.exists(yt_dlp_path):
        print("❌ 錯誤：找不到 yt-dlp.exe")
        return

    # 🔥 強制選擇最高畫質和最高音質
    format_code = "bestvideo+bestaudio/best"

    # 先取得影片標題以判斷是否重複
    get_title_cmd = [
        yt_dlp_path, url,
        "--get-title"
    ]
    try:
        title = subprocess.check_output(get_title_cmd, creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ 無法取得影片標題：{url}\n{e}")
        return

    # 檢查是否已有同名檔案
    base_filename = f"{title}.mp4"
    full_path = os.path.join(output_path, base_filename)
    if os.path.exists(full_path):
        # 加上時間戳記避免覆蓋
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{title}_{timestamp}.mp4"
        full_path = os.path.join(output_path, base_filename)

    command = [
        yt_dlp_path, url,
        "-f", format_code,
        "--no-playlist",
        "-o", full_path
    ]

    try:
        subprocess.run(
            command,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ 影片下載失敗：{url}\n{e}")
    
def get_search_results(query, platform, max_results):
    search_prefix = "ytsearch" if platform == "YouTube" else "scsearch"
    search_query = f"{search_prefix}{max_results}:{query}"

    command = [
        "yt-dlp.exe", search_query,
        "--dump-json",
        "--skip-download",
        "--no-playlist"
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW  # 隱藏搜尋階段的 CMD 視窗
        )
        return [json.loads(line) for line in result.stdout.strip().split("\n") if line]
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []

def get_title(url):
    yt_dlp_path = extract_binary("yt-dlp.exe")
    try:
        result = subprocess.run(
            [yt_dlp_path, url, "--dump-single-json", "--skip-download"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        data = json.loads(result.stdout.strip())
        return data.get("title", url)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return url

def download_music(search_queries, options, progress_callback):
    format_selected = options["format"]
    quality_selected = options["quality"]
    output_path      = options["output_path"]
    platform         = options["platform"]
    min_duration     = options["min_duration"]
    max_duration     = options["max_duration"]
    sleep_time       = options["sleep"]
    max_results      = options["max_results"]
    download_type    = options["download_type"]

    total = len(search_queries)
    success_list = []
    skipped_list = []

    def is_url(text):
        return urlparse(text).scheme in ("http", "https")

    for current, query in enumerate(search_queries, start=1):
        if is_url(query):
            # 直接下載網址
            progress_callback(current, total, query)
            ffmpeg_path = extract_binary("ffmpeg.exe")
            os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ";" + os.environ["PATH"]

            if download_type == "video":
                call_yt_dlp_video(query, output_path)
            else:
                call_yt_dlp(query, output_path, format_selected, quality_selected)

            success_list.append(query)
            continue
        results = get_search_results(query, platform, max_results)
        for entry in results:
            duration = entry.get("duration", 0)
            url = entry.get("webpage_url")

            if url and min_duration <= duration <= max_duration:
                title = get_title(url)
                progress_callback(current, total, title)
                ffmpeg_path = extract_binary("ffmpeg.exe")
                os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ";" + os.environ["PATH"]

                if download_type == "video":
                    call_yt_dlp_video(url, output_path, audio_format=format_selected, audio_quality=quality_selected)
                else:
                    call_yt_dlp(query, output_path, format_selected, quality_selected)

                success_list.append(title)
                break
        else:
            skipped_list.append(query)
            print(f"❌ 沒有任何符合條件的搜尋結果：{query}")

        time.sleep(sleep_time)

    return success_list, skipped_list
