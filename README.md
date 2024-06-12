# WReader
**[English](https://github.com/ThinkerWen/wreader/blob/main/README_EN.md)**

在线体验：[wreader.onrender.com](https://wreader.onrender.com/)
## 介绍
自定义书源，自己设置规则<br>
自动抓取网页数据，规则简单易懂

## 使用
### 一、下载源代码
```bash
git clone https://github.com/ThinkerWen/wreader.git
cd wreader
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
浏览器打开 `http://127.0.0.1:8000`即可搜索阅读小说
<br>
### 二、Docker（未启用）
```bash
docker run -d --name wreader -p 8001:8001 ThinkerWen/wreader
```
浏览器打开 `http://127.0.0.1:8000`即可搜索阅读小说

## 其他
不擅前端，感谢大家多多贡献PR