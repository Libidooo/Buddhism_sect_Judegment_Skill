#!/usr/bin/env python3
"""
CBETA经典查找脚本

功能：
- 支持按卷别查找经典
- 支持按T号快速查找
- 支持按经名查找
- 支持按关键词查找
- 返回JSON格式结果，包含T号、经名、卷别、在线链接

使用示例：
python scripts/sutra_lookup.py --volume 卷二
python scripts/sutra_lookup.py --t-number T0262
python scripts/sutra_lookup.py --name 妙法莲华经
python scripts/sutra_lookup.py --keyword 观世音
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any

# 资源路径
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
INDEX_DIR = PROJECT_DIR / "cbeta-index-references"

class SutraLookup:
    """经典查找类"""

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

    def _load_volume_mapping(self) -> Dict[str, Dict[str, Any]]:
        """加载卷别映射"""
        try:
            mapping_file = ASSETS_DIR / "cbeta-volume-query-path.md"
            with open(mapping_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_volume_mapping(content)
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
                        "sutra": sutra.strip(),
                        "t_number": t_number.strip(),
                        "volume": volume.strip(),
                        "location": location.strip(),
                        "cbeta_url": f"https://cbetaonline.dila.edu.tw/{t_number.strip()}"
                    })

        return results

    def _parse_volume_mapping(self, content: str) -> Dict[str, Dict[str, Any]]:
        """解析卷别映射"""
        mapping = {}

        # 查找每个卷别的T号列表
        volume_pattern = r'## (卷[一二三四五六七八九十]+[：:][^\n]+)'
        volumes = re.finditer(volume_pattern, content)

        for vol_match in volumes:
            volume_header = vol_match.group(1)
            volume_name = re.match(r'(卷[一二三四五六七八九十]+)', volume_header)
            if volume_name:
                vol = volume_name.group(1)

                # 提取该卷的T号
                section_start = vol_match.end()
                next_section = re.search(r'\n## ', content[section_start:])
                if next_section:
                    section_end = section_start + next_section.start()
                else:
                    section_end = len(content)

                section = content[section_start:section_end]

                # 查找T号
                t_numbers = re.findall(r'([T]\d{4})', section)

                if t_numbers:
                    mapping[vol] = {
                        "t_numbers": list(set(t_numbers)),  # 去重
                        "description": volume_header
                    }

        return mapping

    def lookup_by_volume(self, volume: str) -> Dict[str, Any]:
        """按卷别查找"""
        # 规范化卷名
        volume = volume.strip()
        if not volume.startswith("卷"):
            volume = f"卷{volume}"

        if isinstance(self.t_index, dict) and "error" in self.t_index:
            return self.t_index

        # 过滤出该卷的经典
        results = [
            item for item in self.t_index
            if volume in item.get("volume", "")
        ]

        if results:
            return {
                "status": "success",
                "volume": volume,
                "count": len(results),
                "results": results
            }
        else:
            return {
                "status": "not_found",
                "volume": volume,
                "message": f"未找到 {volume} 的经典"
            }

    def lookup_by_t_number(self, t_number: str) -> Dict[str, Any]:
        """按T号查找"""
        t_number = t_number.upper().strip()
        if not t_number.startswith('T'):
            t_number = 'T' + t_number

        if isinstance(self.t_index, dict) and "error" in self.t_index:
            return self.t_index

        matches = [item for item in self.t_index if item['t_number'] == t_number]

        if matches:
            return {
                "status": "success",
                "t_number": t_number,
                "results": matches
            }
        else:
            return {
                "status": "not_found",
                "t_number": t_number,
                "message": f"未找到T号为 {t_number} 的经典"
            }

    def lookup_by_name(self, name: str) -> Dict[str, Any]:
        """按经名查找"""
        if isinstance(self.t_index, dict) and "error" in self.t_index:
            return self.t_index

        matches = [
            item for item in self.t_index
            if name.lower() in item['name'].lower()
        ]

        if matches:
            return {
                "status": "success",
                "name": name,
                "count": len(matches),
                "results": matches
            }
        else:
            return {
                "status": "not_found",
                "name": name,
                "message": f"未找到名称包含 '{name}' 的经典"
            }

    def lookup_by_keyword(self, keyword: str) -> Dict[str, Any]:
        """按关键词查找"""
        if isinstance(self.keyword_index, dict) and "error" in self.keyword_index:
            return self.keyword_index

        matches = []
        for kw, sutras in self.keyword_index.items():
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
                "count": len(unique_matches),
                "results": list(unique_matches.values())
            }
        else:
            return {
                "status": "not_found",
                "keyword": keyword,
                "message": f"未找到包含关键词 '{keyword}' 的经典"
            }

    def get_volume_summary(self) -> Dict[str, Any]:
        """获取卷别摘要"""
        if isinstance(self.t_index, dict) and "error" in self.t_index:
            return self.t_index

        summary = {}
        for item in self.t_index:
            volume = item.get("volume", "")
            if volume:
                if volume not in summary:
                    summary[volume] = {
                        "count": 0,
                        "core": 0,
                        "sutra_names": []
                    }
                summary[volume]["count"] += 1
                if item.get("importance") == "核心":
                    summary[volume]["core"] += 1
                if item.get("name") not in summary[volume]["sutra_names"]:
                    summary[volume]["sutra_names"].append(item.get("name"))

        return {
            "status": "success",
            "summary": summary
        }

def main():
    parser = argparse.ArgumentParser(
        description='CBETA经典查找工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 按卷别查找
  python scripts/sutra_lookup.py --volume 卷二
  python scripts/sutra_lookup.py --volume 2

  # 按T号查找
  python scripts/sutra_lookup.py --t-number T0262
  python scripts/sutra_lookup.py --t-number 0262

  # 按经名查找
  python scripts/sutra_lookup.py --name 妙法莲华经

  # 按关键词查找
  python scripts/sutra_lookup.py --keyword 观世音

  # 获取卷别摘要
  python scripts/sutra_lookup.py --summary
        """
    )

    parser.add_argument('--volume', type=str, help='按卷别查找（如"卷二"或"2"）')
    parser.add_argument('--t-number', type=str, help='按T号查找（如T0262或0262）')
    parser.add_argument('--name', type=str, help='按经名查找（如妙法莲华经）')
    parser.add_argument('--keyword', type=str, help='按关键词查找（如观世音）')
    parser.add_argument('--summary', action='store_true', help='获取卷别摘要')
    parser.add_argument('--format', type=str, default='json', choices=['json', 'text'], help='输出格式')

    args = parser.parse_args()

    # 验证参数
    if not any([args.volume, args.t_number, args.name, args.keyword, args.summary]):
        parser.error("必须提供至少一个查询参数")

    lookup = SutraLookup()
    result = None

    # 执行查询
    if args.summary:
        result = lookup.get_volume_summary()
    elif args.volume:
        result = lookup.lookup_by_volume(args.volume)
    elif args.t_number:
        result = lookup.lookup_by_t_number(args.t_number)
    elif args.name:
        result = lookup.lookup_by_name(args.name)
    elif args.keyword:
        result = lookup.lookup_by_keyword(args.keyword)

    # 输出结果
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        if result.get("status") == "success":
            print(f"✓ 查询成功\n")

            if "volume" in result:
                print(f"卷别: {result['volume']}")
                print(f"数量: {result['count']} 部经典\n")

            if "t_number" in result:
                print(f"T号: {result['t_number']}\n")

            if "name" in result:
                print(f"经名: {result['name']}")
                print(f"数量: {result['count']} 部匹配经典\n")

            if "keyword" in result:
                print(f"关键词: {result['keyword']}")
                print(f"数量: {result['count']} 部匹配经典\n")

            if "summary" in result:
                print("卷别摘要:\n")
                for vol, info in result['summary'].items():
                    print(f"  {vol}:")
                    print(f"    总计: {info['count']} 部")
                    print(f"    核心: {info['core']} 部")
                    print(f"    经典: {', '.join(info['sutra_names'][:5])}")
                    if len(info['sutra_names']) > 5:
                        print(f"          等...（共 {len(info['sutra_names'])} 部）")
                    print()
            elif "results" in result:
                print("查询结果:\n")
                for i, item in enumerate(result['results'], 1):
                    print(f"  [{i}] {item.get('name', item.get('sutra', 'N/A'))}")
                    if 't_number' in item:
                        print(f"      T号: {item['t_number']}")
                    if 'volume' in item:
                        print(f"      卷别: {item['volume']}")
                    if 'category' in item:
                        print(f"      类型: {item['category']}")
                    if 'importance' in item:
                        print(f"      重要度: {item['importance']}")
                    if 'location' in item:
                        print(f"      位置: {item['location']}")
                    if 'cbeta_url' in item:
                        print(f"      链接: {item['cbeta_url']}")
                    print()
        else:
            print(f"✗ 查询失败: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    main()
