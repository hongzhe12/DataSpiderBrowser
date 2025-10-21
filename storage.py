import os
import sqlite3

def get_cookies_dict():
    """从 SQLite 数据库读取 cookies"""
    cookies_db_path = os.path.join(os.getcwd(),"profile","Cookies")
    cookies = []
    conn = None  # 确保初始化为 None

    try:
        # 检查数据库文件是否存在
        if not os.path.exists(cookies_db_path):
            print(f"Cookies 数据库文件不存在: {cookies_db_path}")
            return cookies
        print("路径：", cookies_db_path)
        conn = sqlite3.connect(cookies_db_path)
        cursor = conn.cursor()

        # 检查 cookies 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cookies'")
        if not cursor.fetchone():
            print("cookies 表不存在")
            return cookies

        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly 
            FROM cookies
        """)

        for row in cursor.fetchall():
            cookies.append({
                'domain': row[0],
                'name': row[1],
                'value': row[2],
                'path': row[3],
                'expires': row[4],
                'secure': bool(row[5]),
                'httponly': bool(row[6])
            })

        print(f"成功读取 {len(cookies)} 个 cookies")

    except sqlite3.Error as e:
        print(f"读取 cookies 数据库错误: {e}")
    except Exception as e:
        print(f"读取 cookies 失败: {e}")
    finally:
        # 只有在连接成功建立时才关闭
        if conn is not None:
            conn.close()
            conn = None

    return {c['name']: c['value'] for c in cookies}



cookie = get_cookies_dict()