#!/usr/bin/env python3
"""
CBETA索引搜索脚本

功能：
- 支持在所有索引文件中进行全文搜索
- 支持按T号、经名、卷别、关键词多维度搜索
- 支持模糊匹配和精确匹配
- 返回JSON格式结果，包含所有匹配项和来源信息

使用示例：
python scripts/cbeta_index_search.py --search "观世音"
python scripts/cbeta_index_search.py --search T0262 --exact
python scripts/cbeta_index_search.py --search "金刚经" --volume 卷一
python scripts/cbeta_index_search.py --search "净土" --type keyword
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Set

# 资源路径
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
INDEX_DIR = PROJECT_DIR / "cbeta-index-references"

class CBETAIndexSearcher:
    """CBETA索引搜索类"""

    def __init__(self):
        self.t_index = self._load_t_index()
        self.keyword_index = self._load_keyword_index()
        self.volume_mapping = self._load_volume_mapping()

    def _load_t_index(self) -> List[Dict[str, Any]]:
        """加载T号索引"""
        try:
            t_index_file = ASSETS_DIR / "cbeta-t-number-index.md"
            with open(t_index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_t_index(content)
        except Exception as e:
            return {"error": f"加载T号索引失败: {str(e)}"}

    def _load_keyword_index(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载关键词索引"""
        try:
            keyword_file = ASSETS_DIR / "cbeta-keyword-index.md"
            with open(keyword_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_keyword_index(content)
        except Exception as e:
            return {"error": f"加载关键词索引失败: {str(e)}"}

    def _load_volume_mapping(self) -> Dict[str, Any]:
        """加载卷别映射"""
        try:
            mapping_file = ASSETS_DIR / "cbeta-volume-query-path.md"
            with open(mapping_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return {"error": f"加载卷别映射失败: {str(e)}"}

    def _parse_t_index(self, content: str) -> List[Dict[str, Any]]:
        """解析T号索引"""
        results = []
        table_pattern = r'^\| ([T]\d{4}) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \|'
        matches = re.findall(table_pattern, content, re.MULTILINE)

        for match in matches:
            t_number, name, volume, category, importance, link = match
            results.append({
                "source": "T号索引",
                "file": "cbeta-t-number-index.md",
                "t_number": t_number.strip(),
                "name": name.strip(),
                "volume": volume.strip(),
                "category": category.strip(),
                "importance": importance.strip(),
                "cbeta_url": f"https://cbetaonline.dila.edu.tw/{t_number.strip()}"
            })

        return results

    def _parse_keyword_index(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """解析关键词索引"""
        results = {}
        letter_pattern = r'### ([A-Z])\s*\n\s*\| 关键词 \| 经典 \| T号 \| 卷别 \|'
        sections = re.split(letter_pattern, content)[1:]

        for i in range(0, len(sections), 2):
            if i + 1 < len(sections):
                letter = sections[i]
                table_content = sections[i + 1]

                row_pattern = r'\| ([^|]+) \| ([^|]+) \| ([T]\d{4}) \| ([^|]+) \| ([^|]+) \|'
                rows = re.findall(row_pattern, table_content)

                for row in rows:
                    keyword, sutra, t_number, volume, location = row
                    keyword = keyword.strip()
                    if keyword not in results:
                        results[keyword] = []
                    results[keyword].append({
                        "source": "关键词索引",
                        "file": "cbeta-keyword-index.md",
                        "keyword": keyword,
                        "sutra": sutra.strip(),
                        "t_number": t_number.strip(),
                        "volume": volume.strip(),
                        "location": location.strip(),
                        "cbeta_url": f"https://cbetaonline.dila.edu.tw/{t_number.strip()}"
                    })

        return results

    def search(self, query: str, exact: bool = False, search_type: str = "all") -> Dict[str, Any]:
        """
        在索引中搜索

        Args:
            query: 搜索查询字符串
            exact: 是否精确匹配
            search_type: 搜索类型 ('all', 't-number', 'name', 'keyword')

        Returns:
            搜索结果字典
        """
        results = {
            "status": "success",
            "query": query,
            "exact": exact,
            "search_type": search_type,
            "matches": {
                "t_index": [],
                "keyword_index": []
            },
            "total_count": 0
        }

        query = query.strip()

        # 检查索引加载状态
        if isinstance(self.t_index, dict) and "error" in self.t_index:
            return {
                "status": "error",
                "message": self.t_index["error"]
            }

        if isinstance(self.keyword_index, dict) and "error" in self.keyword_index:
            return {
                "status": "error",
                "message": self.keyword_index["error"]
            }

        # 搜索T号索引
        if search_type in ["all", "t-number", "name"]:
            for item in self.t_index:
                match = False
                match_type = []

                # 搜索T号
                if search_type in ["all", "t-number"]:
                    if exact:
                        if item["t_number"].lower() == query.lower():
                            match = True
                            match_type.append("T号")
                    else:
                        if query.lower() in item["t_number"].lower():
                            match = True
                            match_type.append("T号")

                # 搜索经名
                if search_type in ["all", "name"]:
                    if exact:
                        if item["name"].lower() == query.lower():
                            match = True
                            match_type.append("经名")
                    else:
                        if query.lower() in item["name"].lower():
                            match = True
                            match_type.append("经名")

                if match:
                    result_item = item.copy()
                    result_item["match_type"] = match_type
                    results["matches"]["t_index"].append(result_item)

        # 搜索关键词索引
        if search_type in ["all", "keyword"]:
            for keyword, sutras in self.keyword_index.items():
                match = False

                if exact:
                    if keyword.lower() == query.lower():
                        match = True
                else:
                    if query.lower() in keyword.lower():
                        match = True

                if match:
                    for sutra in sutras:
                        result_item = sutra.copy()
                        result_item["match_type"] = ["关键词"]
                        results["matches"]["keyword_index"].append(result_item)

        # 按卷别过滤
        # （如果有--volume参数，会在main函数中处理）

        # 统计总数
        results["total_count"] = (
            len(results["matches"]["t_index"]) +
            len(results["matches"]["keyword_index"])
        )

        return results

    def search_by_volume(self, query: str, volume: str, exact: bool = False) -> Dict[str, Any]:
        """
        按卷别搜索

        Args:
            query: 搜索查询字符串
            volume: 卷别（如"卷二"）
            exact: 是否精确匹配

        Returns:
            搜索结果字典
        """
        # 先进行普通搜索
        search_result = self.search(query, exact=exact)

        if search_result["status"] != "success":
            return search_result

        # 规范化卷名
        volume = volume.strip()
        if not volume.startswith("卷"):
            volume = f"卷{volume}"

        # 按卷别过滤结果
        filtered_t_index = [
            item for item in search_result["matches"]["t_index"]
            if volume in item.get("volume", "")
        ]

        filtered_keyword_index = [
            item for item in search_result["matches"]["keyword_index"]
            if volume in item.get("volume", "")
        ]

        search_result["matches"]["t_index"] = filtered_t_index
        search_result["matches"]["keyword_index"] = filtered_keyword_index
        search_result["volume_filter"] = volume
        search_result["total_count"] = len(filtered_t_index) + len(filtered_keyword_index)

        return search_result

    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        if isinstance(self.t_index, dict) and "error" in self.t_index:
            return {
                "status": "error",
                "message": self.t_index["error"]
            }

        stats = {
            "status": "success",
            "t_index_count": len(self.t_index),
            "keyword_index_count": len(self.keyword_index),
            "volumes": {},
            "categories": {},
            "importance": {}
        }

        # 统计卷别
        for item in self.t_index:
            volume = item.get("volume", "")
            if volume:
                if volume not in stats["volumes"]:
                    stats["volumes"][volume] = 0
                stats["volumes"][volume] += 1

        # 统计类别
        for item in self.t_index:
            category = item.get("category", "")
            if category:
                if category not in stats["categories"]:
                    stats["categories"][category] = 0
                stats["categories"][category] += 1

        # 统计重要度
        for item in self.t_index:
            importance = item.get("importance", "")
            if importance:
                if importance not in stats["importance"]:
                    stats["importance"][importance] = 0
                stats["importance"][importance] += 1

        return stats

def main():
    parser = argparse.ArgumentParser(
        description='CBETA索引搜索工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 全文搜索
  python scripts/cbeta_index_search.py --search "观世音"

  # 精确匹配
  python scripts/cbeta_index_search.py --search "T0262" --exact

  # 按卷别搜索
  python scripts/cbeta_index_search.py --search "净土" --volume 卷三

  # 按类型搜索
  python scripts/cbeta_index_search.py --search "金刚经" --type name

  # 获取统计信息
  python scripts/cbeta_index_search.py --stats
        """
    )

    parser.add_argument('--search', type=str, help='搜索查询字符串')
    parser.add_argument('--exact', action='store_true', help='使用精确匹配')
    parser.add_argument('--volume', type=str, help='按卷别过滤（如"卷二"或"2"）')
    parser.add_argument('--type', type=str, default='all',
                       choices=['all', 't-number', 'name', 'keyword'],
                       help='搜索类型')
    parser.add_argument('--stats', action='store_true', help='显示索引统计信息')
    parser.add_argument('--format', type=str, default='json', choices=['json', 'text'],
                       help='输出格式')

    args = parser.parse_args()

    # 验证参数
    if not args.stats and not args.search:
        parser.error("必须提供 --search 或 --stats 参数")

    searcher = CBETAIndexSearcher()
    result = None

    # 执行搜索
    if args.stats:
        result = searcher.get_index_stats()
    else:
        if args.volume:
            result = searcher.search_by_volume(args.search, args.volume, args.exact)
        else:
            result = searcher.search(args.search, args.exact, args.type)

    # 输出结果
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        if result.get("status") == "success":
            print(f"✓ 查询成功\n")
            print(f"查询: {result.get('query', 'N/A')}")
            if "exact" in result:
                print(f"模式: {'精确' if result['exact'] else '模糊'}")
            if "search_type" in result and result['search_type'] != 'all':
                print(f"类型: {result['search_type']}")
            if "volume_filter" in result:
                print(f"卷别: {result['volume_filter']}")
            print(f"总计: {result.get('total_count', 0)} 条匹配\n")

            # 输出T号索引结果
            t_matches = result.get("matches", {}).get("t_index", [])
            if t_matches:
                print(f"【T号索引】({len(t_matches)} 条)")
                for i, item in enumerate(t_matches[:10], 1):  # 限制显示数量
                    match_type = ", ".join(item.get("match_type", []))
                    print(f"  [{i}] {item.get('name', 'N/A')} ({match_type})")
                    print(f"      T号: {item.get('t_number', 'N/A')}")
                    print(f"      卷别: {item.get('volume', 'N/A')}")
                    print(f"      链接: {item.get('cbeta_url', 'N/A')}")
                if len(t_matches) > 10:
                    print(f"      ...（还有 {len(t_matches) - 10} 条）")
                print()

            # 输出关键词索引结果
            k_matches = result.get("matches", {}).get("keyword_index", [])
            if k_matches:
                print(f"【关键词索引】({len(k_matches)} 条)")
                for i, item in enumerate(k_matches[:10], 1):  # 限制显示数量
                    print(f"  [{i}] {item.get('sutra', 'N/A')} - {item.get('keyword', 'N/A')}")
                    print(f"      T号: {item.get('t_number', 'N/A')}")
                    print(f"      卷别: {item.get('volume', 'N/A')}")
                    print(f"      位置: {item.get('location', 'N/A')}")
                if len(k_matches) > 10:
                    print(f"      ...（还有 {len(k_matches) - 10} 条）")
                print()

        elif result.get("status") == "stats":
            print("索引统计信息:\n")
            print(f"T号索引: {result.get('t_index_count', 0)} 部经典")
            print(f"关键词索引: {result.get('keyword_index_count', 0)} 个关键词\n")

            if result.get("volumes"):
                print("按卷别分布:")
                for vol, count in sorted(result['volumes'].items()):
                    print(f"  {vol}: {count} 部")
                print()

            if result.get("categories"):
                print("按类别分布:")
                for cat, count in sorted(result['categories'].items()):
                    print(f"  {cat}: {count} 部")
                print()

            if result.get("importance"):
                print("按重要度分布:")
                for imp, count in sorted(result['importance'].items()):
                    print(f"  {imp}: {count} 部")
                print()

        else:
            print(f"✗ 查询失败: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    main()
