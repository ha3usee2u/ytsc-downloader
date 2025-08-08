# ytsc-downloader

# **For education only.**

音樂下載器，具有圖形化介面、智慧搜尋、音訊格式選擇、長度篩選等功能，並且支援免安裝單檔執行。基於 yt-dlp 與 ffmpeg 打造，快速又穩定。

## 功能特點

- 音樂下載
- 智慧關鍵字搜尋，自動嘗試多筆搜尋結果
- 篩選音訊長度、格式與品質
- GUI 介面簡潔易用，下載進度即時更新
- 免安裝版本，打包成單一 `.exe` 執行檔

## 執行方式

> 💡 不需安裝 Python、yt-dlp 或 ffmpeg，僅需下載執行檔即可使用！

1. 下載 `YTSC_Downloader.exe`（在 release 資料夾）
2. 雙擊執行，輸入關鍵字或網址
3. 選擇下載格式、品質與長度範圍
4. 點擊「開始下載」，就完成啦 🎧

## 技術架構

- 開發語言：Python 3.13 + tkinter GUI
- 下載核心：yt-dlp.exe（嵌入式）
- 音訊轉檔：ffmpeg.exe（嵌入式）
- 打包工具：PyInstaller（onefile windowed）

## 打包方式（開發者用）

請參考 `build.bat` 腳本，支援：

- 自動嵌入 yt-dlp.exe 與 ffmpeg.exe
- 檢查是否有 icon.ico，選擇是否加入圖示
- 隱藏執行時的命令列黑窗（CREATE_NO_WINDOW）
