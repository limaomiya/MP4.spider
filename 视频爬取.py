import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

# ================== 配置区 ==================
M3U8_URL = "https://ppvod011.blbtgg.com/splitOut/20260106/1228337/V20260106012739759441228337/index.m3u8?auth_key=1775725507-495184819d8841388fea08e9c74fab29-0-4adb761208f9fadc0687dacff8430a10"

OUTPUT_MP4 = "video.mp4"                # 最终视频文件名
MAX_WORKERS = 36                        # 下载线程数（i5-13500H 适合 24~32）
TEMP_DIR = "ts_temp"                    # 存放 TS 片段的临时文件夹
# =============================================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    # 如果下载 TS 片段时遇到 403，请取消下面 Referer 的注释，并填写视频播放页的网址
    # "Referer": "https://播放页面的域名/",
}

def download_ts(ts_url, ts_path, retries=3):
    """下载单个 TS 片段，支持失败重试"""
    for i in range(retries):
        try:
            r = requests.get(ts_url, headers=headers, timeout=10)
            if r.status_code == 200:
                with open(ts_path, 'wb') as f:
                    f.write(r.content)
                return True
        except Exception:
            pass
        time.sleep(1)   # 重试前等待 1 秒
    return False

def merge_ts_files(ts_dir, output_file):
    """使用纯 Python 按顺序合并所有 TS 片段（无需 ffmpeg）"""
    # 获取所有 .ts 文件并按文件名排序
    ts_files = sorted([f for f in os.listdir(ts_dir) if f.endswith('.ts')])
    if not ts_files:
        print("没有找到任何 TS 文件，无法合并。")
        return

    print(f"正在合并 {len(ts_files)} 个片段...")
    with open(output_file, 'wb') as outfile:
        for ts_file in ts_files:
            ts_path = os.path.join(ts_dir, ts_file)
            with open(ts_path, 'rb') as infile:
                # 使用 copyfileobj 可以避免一次性读入大文件导致内存溢出
                outfile.write(infile.read())
            # 可选：打印进度（如果片段很多）
            # print(f"\r已合并: {ts_file}", end='', flush=True)
    print(f"\n合并完成！视频已保存至: {os.path.abspath(output_file)}")

def main():
    # 1. 获取 M3U8 文件
    print("正在获取 M3U8 文件...")
    resp = requests.get(M3U8_URL, headers=headers)
    if resp.status_code != 200:
        print(f"M3U8 请求失败，状态码: {resp.status_code}")
        return

    # 2. 提取 TS 文件名（非 # 开头的行）
    lines = resp.text.split('\n')
    ts_names = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    print(f"共发现 {len(ts_names)} 个 TS 片段")

    if not ts_names:
        print("M3U8 文件中未找到 TS 片段列表，请检查内容。")
        return

    # 3. 拼接完整 TS 下载地址
    base_url = M3U8_URL.rsplit('/', 1)[0] + '/'
    ts_urls = [urljoin(base_url, name) for name in ts_names]

    # 4. 创建临时目录
    os.makedirs(TEMP_DIR, exist_ok=True)

    # 5. 多线程下载 TS 片段
    print("开始下载 TS 片段...")
    ts_files = []
    failed_count = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for i, url in enumerate(ts_urls):
            # 用零补齐文件名，确保排序正确（例如 00001.ts, 00002.ts）
            ts_path = os.path.join(TEMP_DIR, f"{i:05d}.ts")
            ts_files.append(ts_path)
            futures[executor.submit(download_ts, url, ts_path)] = i

        completed = 0
        for future in as_completed(futures):
            idx = futures[future]
            if future.result():
                completed += 1
                print(f"\r下载进度: {completed}/{len(ts_urls)}", end='', flush=True)
            else:
                failed_count += 1
                print(f"\n片段 {idx} 下载失败，URL: {ts_urls[idx]}")

    print(f"\n下载完成！成功: {completed}, 失败: {failed_count}")

    # 6. 如果有片段下载失败，询问是否继续合并
    if failed_count > 0:
        print("警告: 部分片段下载失败，合并后的视频可能不完整或无法播放。")
        choice = input("是否继续合并？(y/n): ").strip().lower()
        if choice != 'y':
            print("已取消合并，临时文件保留在:", os.path.abspath(TEMP_DIR))
            return

    # 7. 合并 TS 片段为 MP4
    merge_ts_files(TEMP_DIR, OUTPUT_MP4)

    # 8. 询问是否删除临时文件夹
    choice = input("是否删除临时文件夹 ts_temp？(y/n): ").strip().lower()
    if choice == 'y':
        import shutil
        shutil.rmtree(TEMP_DIR)
        print("临时文件夹已删除")
    else:
        print(f"临时文件夹保留在: {os.path.abspath(TEMP_DIR)}")

if __name__ == '__main__':
    main()