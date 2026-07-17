#!/usr/bin/env python3
"""
CBETA API查询脚本

功能：
- 支持通过T号查询经典信息
- 支持通过经名查询经典信息
- 支持通过关键词查询经典信息
- 返回JSON格式结果

使用示例：
python scripts/cbeta_query.py --t-number T0262
python scripts/cbeta_query.py --sutra-name 妙法莲华经
python scripts/cbeta_query.py --keyword 观世音
"""

import argparse
import json
import sys
import re
from pathlib import Path

# 尝试导入coze_workload_identity，如果失败则回退到标准requests
try:
    from coze_workload_identity import requests
except ImportError:
    import requests

# 索引文件路径
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
INDEX_DIR = PROJECT_DIR / "cbeta-index-references"
ASSETS_DIR = PROJECT_DIR / "assets"

def load_t_number_index():
    """加载T号索引文件"""
    try:
        t_index_file = ASSETS_DIR / "cbeta-t-number-index.md"
        with open(t_index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_t_index(content)
    except Exception as e:
        return {"error": f"加载T号索引失败: {str(e)}"}

def load_keyword_index():
    """加载关键词索引文件"""
    try:
        keyword_file = ASSETS_DIR / "cbeta-keyword-index.md"
        with open(keyword_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_keyword_index(content)
    except Exception as e:
        return {"error": f"加载关键词索引失败: {str(e)}"}

def parse_t_index(content):
    """解析T号索引内容"""
    results = []
    # 查找表格部分
    table_pattern = r'^\| ([T]\d{4}) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \|'
    matches = re.findall(table_pattern, content, re.MULTILINE)

    for match in matches:
        t_number, name, volume, category, importance, link = match
        results.append({
            "t_number": t_number.strip(),
            "name": name.strip(),
            "volume": volume.strip(),
            "category": category.strip(),
            "importance": importance.strip(),
            "cbeta_url": f"https://cbetaonline.dila.edu.tw/{t_number.strip()}"
        })

    return results

def parse_keyword_index(content):
    """解析关键词索引内容"""
    results = {}
    # 按字母分组解析
    letter_pattern = r'### ([A-Z])\s*\n\s*\| 关键词 \| 经典 \| T号 \| 卷别 \|'
    sections = re.split(letter_pattern, content)[1:]  # 跳过第一个空元素

    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            letter = sections[i]
            table_content = sections[i + 1]

            # 解析表格行
            row_pattern = r'\| ([^|]+) \| ([^|]+) \| ([T]\d{4}) \| ([^|]+) \| ([^|]+) \|'
            rows = re.findall(row_pattern, table_content)

            for row in rows:
                keyword, sutra, t_number, volume, location = row
                keyword = keyword.strip()
                if keyword not in results:
                    results[keyword] = []
                results[keyword].append({
                    "sutra": sutra.strip(),
                    "t_number": t_number.strip(),
                    "volume": volume.strip(),
                    "location": location.strip(),
                    "cbeta_url": f"https://cbetaonline.dila.edu.tw/{t_number.strip()}"
                })

    return results

def query_by_t_number(t_number):
    """通过T号查询经典信息"""
    # 规范化T号格式
    t_number = t_number.upper().strip()
    if not t_number.startswith('T'):
        t_number = 'T' + t_number

    index_data = load_t_number_index()

    if "error" in index_data:
        return index_data

    # 查找匹配的T号
    matches = [item for item in index_data if item['t_number'] == t_number]

    if matches:
        return {
            "status": "success",
            "t_number": t_number,
            "results": matches,
            "cbeta_url": f"https://cbetaonline.dila.edu.tw/{t_number}"
        }
    else:
        return {
            "status": "not_found",
            "t_number": t_number,
            "message": f"未找到T号为 {t_number} 的经典"
        }

def query_by_sutra_name(sutra_name):
    """通过经名查询经典信息"""
    index_data = load_t_number_index()

    if "error" in index_data:
        return index_data

    # 模糊匹配经名
    matches = [
        item for item in index_data
        if sutra_name.lower() in item['name'].lower()
    ]

    if matches:
        return {
            "status": "success",
            "sutra_name": sutra_name,
            "results": matches
        }
    else:
        return {
            "status": "not_found",
            "sutra_name": sutra_name,
            "message": f"未找到名称包含 '{sutra_name}' 的经典"
        }

def query_by_keyword(keyword):
    """通过关键词查询经典信息"""
    index_data = load_keyword_index()

    if "error" in index_data:
        return index_data

    # 模糊匹配关键词
    matches = []
    for kw, sutras in index_data.items():
        if keyword.lower() in kw.lower():
            matches.extend(sutras)

    if matches:
        # 去重
        unique_matches = {}
        for item in matches:
            key = f"{item['t_number']}_{item['sutra']}"
            if key not in unique_matches:
                unique_matches[key] = item

        return {
            "status": "success",
            "keyword": keyword,
            "results": list(unique_matches.values())
        }
    else:
        return {
            "status": "not_found",
            "keyword": keyword,
            "message": f"未找到包含关键词 '{keyword}' 的经典"
        }

def query_cbeta_online(t_number):
    """查询CBETA在线数据库（可选功能）"""
    try:
        url = f"https://cbetaonline.dila.edu.tw/{t_number}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return {
                "status": "success",
                "online_available": True,
                "url": url,
                "message": "CBETA在线资源可访问"
            }
        else:
            return {
                "status": "error",
                "online_available": False,
                "message": f"CBETA在线资源暂时不可用 (HTTP {response.status_code})"
            }
    except Exception as e:
        return {
            "status": "error",
            "online_available": False,
            "message": f"无法访问CBETA在线资源: {str(e)}"
        }

def main():
    parser = argparse.ArgumentParser(
        description='CBETA经典查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/cbeta_query.py --t-number T0262
  python scripts/cbeta_query.py --sutra-name 妙法莲华经
  python scripts/cbeta_query.py --keyword 观世音
  python scripts/cbeta_query.py --t-number T0262 --check-online
        """
    )

    parser.add_argument('--t-number', type=str, help='按T号查询（如T0262）')
    parser.add_argument('--sutra-name', type=str, help='按经名查询（如妙法莲华经）')
    parser.add_argument('--keyword', type=str, help='按关键词查询（如观世音）')
    parser.add_argument('--check-online', action='store_true', help='检查CBETA在线资源是否可访问')
    parser.add_argument('--volume', type=str, help='按卷别过滤（如卷一、卷二）')
    parser.add_argument('--format', type=str, default='json', choices=['json', 'text'], help='输出格式')

    args = parser.parse_args()

    # 验证至少提供一个查询参数
    if not any([args.t_number, args.sutra_name, args.keyword]):
        parser.error("必须提供至少一个查询参数：--t-number、--sutra-name 或 --keyword")

    result = None

    # 执行查询
    if args.t_number:
        result = query_by_t_number(args.t_number)
        if args.check_online and result.get("status") == "success":
            online_check = query_cbeta_online(args.t_number)
            result["online_check"] = online_check
    elif args.sutra_name:
        result = query_by_sutra_name(args.sutra_name)
    elif args.keyword:
        result = query_by_keyword(args.keyword)

    # 按卷别过滤
    if args.volume and result.get("status") == "success" and "results" in result:
        filtered_results = [
            item for item in result["results"]
            if args.volume in item.get("volume", "")
        ]
        result["results"] = filtered_results
        result["filtered_by"] = args.volume

    # 输出结果
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        if result.get("status") == "success":
            print(f"✓ 查询成功")
            if "t_number" in result:
                print(f"  T号: {result['t_number']}")
            if "sutra_name" in result:
                print(f"  经名: {result['sutra_name']}")
            if "keyword" in result:
                print(f"  关键词: {result['keyword']}")
            print(f"  找到 {len(result['results'])} 条结果:\n")
            for i, item in enumerate(result['results'], 1):
                print(f"  [{i}] {item.get('name', item.get('sutra', 'N/A'))}")
                if 't_number' in item:
                    print(f"      T号: {item['t_number']}")
                if 'volume' in item:
                    print(f"      卷别: {item['volume']}")
                if 'cbeta_url' in item:
                    print(f"      链接: {item['cbeta_url']}")
                print()
            if "online_check" in result:
                print(f"  在线状态: {result['online_check']['message']}")
        else:
            print(f"✗ 查询失败: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    main()
