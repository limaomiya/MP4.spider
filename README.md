# M3U8 Video Downloader

一个简单高效的 Python 脚本，用于下载 M3U8 流媒体视频并将其合并为 MP4 文件。无需安装 FFmpeg，纯 Python 实现合并，适合快速保存网页中的 TS 分段视频。
A lightweight Python script to download M3U8 streaming videos and merge TS segments into a single MP4 file without FFmpeg. Features multi-threading, auto-retry, and SSL bypass.
## 功能特点

- **多线程下载**：可自定义并发数，大幅提升下载速度。
- **失败重试**：单个片段下载失败时自动重试，提高成功率。
- **自动拼接**：无需 FFmpeg，使用原生 Python 合并 TS 片段。
- **SSL 兼容**：自动忽略无效证书，解决部分网站的证书验证问题。
- **灵活保存**：支持自定义输出路径和文件名。
- **自动清理**：合并完成后自动删除临时片段，节省磁盘空间。

 注意事项
链接时效性：M3U8 地址通常包含签名参数，有效时间较短，请获取后立即运行脚本。
视频加密：本脚本仅支持未加密的 TS 流。若 M3U8 中包含 #EXT-X-KEY，需先解密片段。
仅供学习：请遵守目标网站的 robots.txt 及相关法律法规，仅将下载内容用于个人学习与研究。
ps:因为抓猫的下载器确实是有点慢的，所以特意编写一个脚本提高爬取效率，本质是一个半自动化的爬虫脚本。
##环境要求
- Python 3.6 或更高版本
- 第三方库：`requests`、`urllib3`

安装依赖：
```bash
pip install requests
