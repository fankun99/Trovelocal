import os
import sqlite3
import requests
import feedparser
from datetime import datetime, timezone
requests.packages.urllib3.disable_warnings()


DB_NAME = 'rss.db'
TABLE_NAME = 'rss_feed'
RSS_FILE = 'rss.txt'
SRV_URL = 'https://127.0.0.1:443/url/add/api'
TOKEN = 'cQTXL8hS9ig5Gc1WFEst4ERUXX3Oi_'
# 如果需要的话，可以设置代理
proxies = {
    # 'http': 'http://your_proxy:port',
    # 'https': 'http://your_proxy:port',
}

def craw_url(serv_url, token, data):
    post_data = data
    bearer_token = token
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    req = requests.post(serv_url, files=post_data, verify=False, timeout=30, headers=headers, proxies={})
    # print(req.status_code, req.text)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            rss TEXT PRIMARY KEY,
            last_pubdate TEXT
        )
    ''')
    conn.commit()
    return conn

def get_rss_list(filename):
    if not os.path.exists(filename):
        print(f"{filename} 不存在")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def get_last_pubdate(cur, rss_url):
    cur.execute(f'SELECT last_pubdate FROM {TABLE_NAME} WHERE rss = ?', (rss_url,))
    row = cur.fetchone()
    return row[0] if row else None

def update_pubdate(cur, rss_url, pubdate):
    cur.execute(f'''
        INSERT INTO {TABLE_NAME} (rss, last_pubdate)
        VALUES (?, ?)
        ON CONFLICT(rss) DO UPDATE SET last_pubdate = excluded.last_pubdate
    ''', (rss_url, pubdate))

def parse_rss(rss_url, last_pub_str):
    try:
        req = requests.get(rss_url, proxies=proxies, timeout=15, verify=False)
    except:
        return None, None
    feed = feedparser.parse(req.content)
    if feed.bozo:
        print(f"解析失败: {rss_url}")
        return None, None

    new_last_pub = last_pub_str
    new_entries = []

    last_pub = datetime.min.replace(tzinfo=timezone.utc)
    if last_pub_str:
        try:
            last_pub = datetime.fromisoformat(last_pub_str)
        except Exception:
            pass

    for entry in feed.entries:
        pub = entry.get('published_parsed') or entry.get('updated_parsed')
        if not pub:
            continue

        pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)

        if pub_dt > last_pub:
            new_entries.append({
                'title': entry.get('title', '无标题'),
                'link': entry.get('link', ''),
                'description': entry.get('summary', ''),
                'content': entry.get('content', [{'value': ''}])[0].get('value', '') if 'content' in entry else '',
                'category': entry.get('tags', [{}])[0].get('term', '') if 'tags' in entry else '',
                'pubdate': pub_dt.isoformat(),
            })
            if not new_last_pub or pub_dt > datetime.fromisoformat(new_last_pub):
                new_last_pub = pub_dt.isoformat()

    return new_entries, new_last_pub

def main():
    conn = init_db()
    cur = conn.cursor()
    rss_list = get_rss_list(RSS_FILE)

    for rss_url in rss_list:
        last_pub_str = get_last_pubdate(cur, rss_url)
        print(f"\n检查 RSS: {rss_url} （上次时间：{last_pub_str}）")
        new_entries, new_last_pub = parse_rss(rss_url, last_pub_str)

        if new_entries:
            print(f"发现 {len(new_entries)} 条新内容：")
            for entry in new_entries:
                print(f"- 标题: {entry['title']}")
                print(f"  链接: {entry['link']}")
                print(f"  发布时间: {entry['pubdate']}")
                print(f"  分类: {entry['category']}")
                print(f"  描述: {entry['description']}")
                print()
                
                post_data = {
                    # 'custom_tags': (None, entry['category']),
                    'custom_tags': (None, 'rss'),
                    'title': (None, entry['title']),
                    'remark': (None, rss_url),
                    'summary': (None, entry['description']),
                    'user': (None, 'admin'),
                    'url': (None, entry['link']),
                }
                craw_url(SRV_URL, TOKEN, post_data)

            update_pubdate(cur, rss_url, new_last_pub)
        else:
            print("无新内容")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()

