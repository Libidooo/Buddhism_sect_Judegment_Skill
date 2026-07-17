#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sect_engine.py - 佛教宗派判定计算引擎
四川地区佛教石窟铭文宗派判定系统的核心计算脚本

功能:
  1. 异体字归一化（variant_normalizer）
  2. 词条匹配（term_matcher）: 最长匹配 + 全量扫描
  3. S 得分计算（score_calculator）
  4. 互斥冲突消解（mutex_resolver）
  5. 判定报告格式化（report_formatter）

用法:
  python sect_engine.py --input "铭文内容"
  python sect_engine.py --input "题记" --subject "造像题材" --date "时间" --location "地点"
  python sect_engine.py --input "弟子某甲为亡父造药师如来像一躯愿亡父往生净土"
  python sect_engine.py --test  # 运行内置测试用例（含结构化数据）
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── 配置 ─────────────────────────────────────────────────────────────
# 数据文件路径
DATA_DIR = Path(__file__).parent / "data"
TERM_INDEX_FILE = DATA_DIR / "term_index.json"
MUTEX_MATRIX_FILE = DATA_DIR / "mutex_matrix.json"
EXTENDED_MUTEX_FILE = DATA_DIR / "extended_mutex.json"
WEIGHT_DEFS_FILE = DATA_DIR / "weight_definitions.json"
S_SCORE_THRESHOLDS_FILE = DATA_DIR / "s_score_thresholds.json"

# 主体优先级（数值越小优先级越高）
SUBJECT_PRIORITY = {
    "4": 1,   # 药师
    "10": 2,  # 弥勒
    "9": 3,   # 地藏
    "2": 4,   # 观音
    "3": 5,   # 阿弥陀
    "5": 10,  # 密教（绝对优先）
    "6": 20,  # 华严
    "7": 30,  # 禅宗
    "11": 40, # 三论
    "12": 50, # 唯识
    "1": 60,  # 通用大乘
}

# S 得分阈值
S_THRESHOLDS = {
    "established": 160,   # 确立
    "high": 120,          # 高可信
    "weak": 80,           # 弱可信
    "indeterminate": 0,   # 不可判定
}

# 密教强因阈值
ESOTERIC_THRESHOLD = 60

# 道教强信号词条（在原始文本中出现即标识为道教/非佛教）
DAOIST_STRONG_TERMS = [
    "天尊",      # 道教独有尊号（区别于佛教"世尊"）
    "老君",      # 太上老君
    "道民",      # 道教信徒自称
    "三洞弟子",  # 灵宝经派弟子称号
    "道士",      # 道教修行者
    "灵宝",      # 灵宝经
    "三清",      # 三清尊神
    "仙男",      # 道教仙人
    "仙女",      # 道教仙女
    "元始天尊",  # 元始天尊
    "道教",      # 道教自称（题材/文献中出现）
    "圣母",      # 道教尊神（四川石窟圣母造像属道教体系）
]

# 强佛教信号词条（存在时覆盖道教预过滤，按佛道混合处理）
BUDDHIST_OVERRIDE_TERMS = [
    "阿弥陀", "释迦", "观世音", "药师琉璃光", "药师如来",
    "地藏菩萨", "弥勒", "毗卢", "罗汉", "曼荼罗",
    "陀罗尼", "灌顶", "菩提", "千手观音", "孔雀明王",
    "炽盛光", "大日如来", "卢舍那", "柳本尊",
    "菩萨",      # 泛化强佛教信号
    "三世佛",    # 佛教三世佛题材
]


# ── 结构化铭文数据 ──────────────────────────────────────────────────
@dataclass
class InscriptionData:
    """结构化铭文数据，支持多字段输入

    字段:
        inscription_text: 题记文字（铭文正文）
        sculpture_subject: 造像题材（造像主题，如"善财童子参礼善知识像"）
        date: 造像时间（如"南宋绍兴二十五年"）
        location: 地点（如"重庆市大足区"）
    """
    inscription_text: str = ""
    sculpture_subject: str = ""
    date: str = ""
    location: str = ""

    # 组合后的统一匹配文本（由引擎自动构建）
    _combined_text: str = ""
    # 各字段在组合文本中的字符偏移 [start, end)
    _field_ranges: Dict[str, Tuple[int, int]] = field(default_factory=dict)

    def build_combined_text(self) -> str:
        """将所有文本字段拼接为统一的匹配文本，记录各字段偏移"""
        parts = []
        ranges = {}

        # 题记文字（主文本）
        start = 0
        end = start + len(self.inscription_text)
        parts.append(self.inscription_text)
        ranges["inscription"] = (start, end)

        # 造像题材
        if self.sculpture_subject:
            start = end
            # 用空格分隔
            if parts[-1]:
                parts.append(" ")
                start += 1
                end = start
            end = start + len(self.sculpture_subject)
            parts.append(self.sculpture_subject)
            ranges["subject"] = (start, end)

        self._combined_text = "".join(parts)
        self._field_ranges = ranges
        return self._combined_text

    def get_field_for_position(self, pos: int) -> str:
        """根据字符位置判断属于哪个字段"""
        for field, (start, end) in self._field_ranges.items():
            if start <= pos < end:
                return field
        return "unknown"

    def get_field_name(self, field: str) -> str:
        """获取字段的中文显示名"""
        names = {
            "inscription": "题记文字",
            "subject": "造像题材",
            "date": "造像时间",
            "location": "地点",
        }
        return names.get(field, field)


# ── 异体字归一化器 ──────────────────────────────────────────────────
class VariantNormalizer:
    """异体字归一化：将铭文中的异体字转换为标准字形"""

    def __init__(self):
        self.variant_map = self._load_variant_map()

    def _load_variant_map(self) -> Dict[str, str]:
        """加载异体字映射表"""
        variant_file = DATA_DIR / "variant_characters.json"
        if variant_file.exists():
            with open(variant_file, "r", encoding="utf-8") as f:
                return json.load(f)
        # 默认映射（常见异体字/繁简体字）
        return {
            "薬": "药",
            "藥": "药",
            "師": "师",
            "彿": "佛",
            "薩": "萨",
            "彌": "弥",
            "觀": "观",
            "勢": "势",
            "願": "愿",
            "淨": "净",
            "華": "华",
            "嚴": "严",
            "禪": "禅",
            "蔵": "藏",
            "禮": "礼",
            "義": "义",
            "經": "经",
            "論": "论",
            "釋": "释",
            "迦": "迦",
            "毘": "毗",
            "盧": "卢",
            "遮": "遮",
            "那": "那",
            "來": "来",
            "軀": "躯",
            "琉": "琉",
            "瑠": "璃",
            "壇": "坛",
            "寶": "宝",
            "網": "网",
            "曼": "曼",
            "荼": "荼",
            "羅": "罗",
            "稱": "称",
            "讚": "赞",
            "懺": "忏",
            "誦": "诵",
            "養": "养",
            "幢": "幢",
            "剎": "刹",
            "極": "极",
            "樂": "乐",
            "尊": "尊",
            "勝": "胜",
            "頂": "顶",
            "種": "种",
        }

    def normalize(self, text: str) -> str:
        """将文本中的异体字转换为标准字形"""
        result = []
        for char in text:
            normalized = self.variant_map.get(char, char)
            result.append(normalized)
        return "".join(result)


# ── 词条匹配器 ──────────────────────────────────────────────────────
class TermMatcher:
    """词条匹配器：在铭文中查找词条，仅支持精确最长匹配"""

    def __init__(self, term_index: Dict[str, List[dict]]):
        """
        初始化词条匹配器

        Args:
            term_index: 词条索引，格式为 {term: [{vid, w, source, category}]}
        """
        self.term_index = term_index
        # 按长度排序的词条列表（用于最长匹配）
        self.sorted_terms = sorted(term_index.keys(), key=len, reverse=True)

    def match(self, text: str, inscription_data: InscriptionData = None) -> List[dict]:
        """
        在文本中匹配词条（精确匹配 + 最长优先）

        返回匹配结果列表，每个结果包含:
        - term: 匹配的词条
        - vid: 所属卷号
        - w: 权重
        - source: 文献来源
        - category: 类别
        - start: 起始位置
        - end: 结束位置
        - field: 来源字段（题记文字/造像题材，仅在有 InscriptionData 时提供）

        Args:
            text: 要匹配的文本
            inscription_data: 可选的结构化铭文数据，用于标记匹配来源字段

        匹配策略:
        1. 逐位置扫描，每位置尝试最长精确匹配
        2. 找到最长精确匹配后立即前进到匹配结束位置
        3. 无匹配时前进1字符
        4. 不做前缀/子串匹配，避免误吞字符
        """
        matches = []
        text_len = len(text)
        i = 0

        while i < text_len:
            best_match = None

            # 按长度降序尝试精确匹配
            for term in self.sorted_terms:
                term_len = len(term)
                if i + term_len > text_len:
                    continue
                if text[i : i + term_len] == term:
                    best_match = term
                    break  # 已是最长匹配

            if best_match:
                term_len = len(best_match)
                term_info = self.term_index[best_match]
                for info in term_info:
                    match_result = {
                        "term": best_match,
                        "vid": info["vid"],
                        "w": info["w"],
                        "source": info["source"],
                        "category": info["category"],
                        "start": i,
                        "end": i + term_len,
                    }
                    # 追溯来源字段
                    if inscription_data is not None:
                        match_result["field"] = inscription_data.get_field_for_position(i)
                    # 传播卷2子分类
                    if "sub_type" in info:
                        match_result["sub_type"] = info["sub_type"]
                    matches.append(match_result)
                i += term_len
            else:
                i += 1

        # 后处理：合并相邻短匹配为已知复合词条
        matches = self._merge_adjacent_compounds(matches)

        return matches

    def _merge_adjacent_compounds(
        self, matches: List[dict]
    ) -> List[dict]:
        """
        合并相邻短匹配为已知复合词条（系统性子串归属保护）

        当两个短词条匹配（各≤3字）在原文中紧邻，且它们的拼接结果
        存在于词条索引中时，丢弃子匹配，改用复合词条的归属信息。

        例如:
          "孔雀"(卷3,W=45) + "明王"(卷5,W=54) 紧邻
          → 若"孔雀明王"存在于索引中，合并为: "孔雀明王"(卷5,W=80)

        此机制确保任一复合词条加入索引后，其组成部分即使恰好在
        其他卷也有注册，也不会产生跨卷冲突。
        """
        if len(matches) < 2:
            return matches

        # 按起始位置排序
        sorted_m = sorted(matches, key=lambda m: (m["start"], -m["end"]))
        result = []
        skip_until = -1

        for i in range(len(sorted_m)):
            if i < skip_until:
                continue

            m = sorted_m[i]
            m_term = m["term"]
            m_end = m["end"]
            merged = False

            # 只对短词条（≤3字）尝试合并
            if len(m_term) <= 3:
                # 向后检查最多3个相邻匹配
                for j in range(i + 1, min(i + 4, len(sorted_m))):
                    n = sorted_m[j]
                    if n["start"] != m_end:
                        break  # 不紧邻，放弃
                    n_term = n["term"]
                    if len(n_term) > 3:
                        continue  # 跳过过长词条
                    compound = m_term + n_term
                    if compound in self.term_index:
                        # 用复合词条的归属信息替换
                        compound_info = self.term_index[compound]
                        for info in compound_info:
                            entry = {
                                "term": compound,
                                "vid": info["vid"],
                                "w": info["w"],
                                "source": info.get("source", ""),
                                "category": info.get("category", ""),
                                "start": m["start"],
                                "end": n["end"],
                                "field": m.get("field", ""),
                            }
                            if "sub_type" in info:
                                entry["sub_type"] = info["sub_type"]
                            result.append(entry)
                        skip_until = j + 1
                        merged = True
                        break

            if not merged:
                result.append(m)

        return result


# ── S 得分计算器 ────────────────────────────────────────────────────
class ScoreCalculator:
    """S 得分计算器：计算每个卷的 S 得分"""

    def __init__(self, s_thresholds: Dict[str, int]):
        """
        初始化 S 得分计算器

        Args:
            s_thresholds: S 得分阈值，格式为 {level: threshold}
        """
        self.s_thresholds = s_thresholds

    def calculate(self, matches: List[dict]) -> Dict[str, float]:
        """
        计算每个卷的 S 得分

        Args:
            matches: 词条匹配结果列表

        Returns:
            每个卷的 S 得分，格式为 {vid: score}
        """
        scores = {}

        # 按卷分组
        by_vid = {}
        for match in matches:
            vid = match["vid"]
            if vid not in by_vid:
                by_vid[vid] = []
            by_vid[vid].append(match)

        # 计算每卷的 S 得分
        for vid, vid_matches in by_vid.items():
            # 主要证据：W >= 60（原数计入）
            primary_w = sum(
                m["w"] for m in vid_matches if m["w"] is not None and m["w"] >= 60
            )
            # 次要证据：W < 60（减半计入）
            secondary_w = sum(
                0.5 * m["w"]
                for m in vid_matches
                if m["w"] is not None and m["w"] < 60
            )
            # S 得分 = 主要证据权重 + 次要证据权重
            s_score = primary_w + secondary_w
            scores[vid] = s_score

        return scores


# ── 互斥冲突消解器 ──────────────────────────────────────────────────
class MutexResolver:
    """互斥冲突消解器：处理卷间的互斥冲突"""

    def __init__(self, mutex_matrix: Dict[str, Dict[str, str]]):
        """
        初始化互斥冲突消解器

        Args:
            mutex_matrix: 互斥矩阵，格式为 {vid1: {vid2: relation}}
                          relation 为 "⛔"（互斥）或 "⚠"（协同）
        """
        self.mutex_matrix = mutex_matrix

    def resolve(
        self, scores: Dict[str, float], matches_by_vid: Dict[str, List[dict]]
    ) -> Tuple[str, List[str], List[dict]]:
        """
        消解互斥冲突，返回最终判定的卷、协同卷列表和证据列表

        消解规则:
        1. 密教强因（W≥60）绝对优先
        2. 主体卷优先级：药师(4) > 弥勒(10) > 地藏(9) > 观音(2) > 阿弥陀(3)
        3. ⛔ 互斥：保留 S 得分较高的卷
        4. ⚠ 协同：两卷并列标注为混合判定

        Args:
            scores: 每个卷的 S 得分
            matches_by_vid: 每个卷的匹配结果

        Returns:
            (final_vid, cooperative_vids, final_matches):
              最终判定的卷号、协同卷列表、合并证据列表
        """
        # 找出 S 得分最高的卷
        if not scores:
            return None, [], []

        sorted_vids = sorted(scores.keys(), key=lambda v: scores[v], reverse=True)
        top_vid = sorted_vids[0]

        # 检查是否有互斥冲突
        conflicts = []
        for vid in sorted_vids[1:]:
            if top_vid in self.mutex_matrix and vid in self.mutex_matrix[top_vid]:
                relation = self.mutex_matrix[top_vid][vid]
                if relation == "⛔":
                    conflicts.append(vid)

        if conflicts:
            for conflict_vid in conflicts:
                top_score = scores.get(top_vid, 0)
                conflict_score = scores.get(conflict_vid, 0)
                # S得分差距显著时，由证据强度决定，不使用主体优先级
                # 显著 = top_vid得分是conflict_vid的2倍以上，或绝对差≥30
                if top_score > 0 and (
                    top_score >= 2 * conflict_score
                    or (top_score - conflict_score) >= 30
                ):
                    continue
                # S得分接近时，使用主体优先级（数值越小优先级越高）
                if SUBJECT_PRIORITY.get(conflict_vid, 999) < SUBJECT_PRIORITY.get(
                    top_vid, 999
                ):
                    top_vid = conflict_vid

        # 收集最终卷的所有证据
        final_matches = list(matches_by_vid.get(top_vid, []))

        # 检查是否有协同卷（⚠ 关系 + S 得分有意义，即 ≥ 40）
        cooperative_vids = []
        for vid in sorted_vids:
            if vid == top_vid:
                continue
            if scores.get(vid, 0) < 40:  # S < 40 忽略（噪声/弱交叉注册）
                continue
            if top_vid in self.mutex_matrix and vid in self.mutex_matrix[top_vid]:
                if self.mutex_matrix[top_vid][vid] == "⚠":
                    cooperative_vids.append(vid)

        # 将协同卷的证据标记后合并
        if cooperative_vids:
            for vid in cooperative_vids:
                for m in matches_by_vid.get(vid, []):
                    tagged = dict(m)
                    tagged["_cooperative_vid"] = vid
                    final_matches.append(tagged)

        return top_vid, cooperative_vids, final_matches


# ── 判定报告格式化器 ────────────────────────────────────────────────
class ReportFormatter:
    """判定报告格式化器：生成标准化的判定报告"""

    def __init__(self):
        self.volume_names = {
            "1": "通用大乘",
            "2": "观音体系",
            "3": "净土体系",
            "4": "药师体系",
            "5": "密教体系",
            "6": "华严体系",
            "7": "禅宗体系",
            "8": "区域体系",
            "9": "地藏体系",
            "10": "弥勒体系",
            "11": "三论宗",
            "12": "唯识宗",
            "13": "天台宗",
            "14": "成实宗",
            "15": "律宗",
        }

    def format_non_buddhist_report(
        self,
        inscription: str,
        reason: str,
        matched_terms: List[str],
        inscription_data: InscriptionData = None,
    ) -> str:
        """
        生成非佛教（如道教）的判定报告

        Args:
            inscription: 铭文内容
            reason: 非佛教原因（如"道教"）
            matched_terms: 匹配到的非佛教信号词条
            inscription_data: 结构化铭文数据
        """
        lines = []
        lines.append("=" * 60)
        lines.append("宗派判定报告")
        lines.append("=" * 60)
        lines.append("")

        if inscription_data is not None:
            if inscription_data.inscription_text:
                lines.append("【题记文字】")
                text = inscription_data.inscription_text
                if len(text) > 200:
                    text = text[:100] + "\n  ...（中间省略）...\n" + text[-100:]
                lines.append(text)
                lines.append("")
            if inscription_data.sculpture_subject:
                lines.append("【造像题材】")
                lines.append(inscription_data.sculpture_subject)
                lines.append("")
        else:
            lines.append("【铭文】")
            lines.append(inscription)
            lines.append("")

        lines.append("【判定结果】")
        lines.append(f"非佛教 — {reason}")
        lines.append("")

        lines.append("【判定等级】")
        lines.append("拒绝判定（非佛教文本）")
        lines.append("")

        if matched_terms:
            lines.append("【信号词条】")
            for term in matched_terms:
                lines.append(f"- {term}（{reason}信号）")
            lines.append("")

        lines.append("=" * 60)
        lines.append("报告生成完毕")
        lines.append("=" * 60)

        return "\n".join(lines)

    def format_report(
        self,
        inscription: str,
        final_vid: str,
        cooperative_vids: List[str],
        final_matches: List[dict],
        scores: Dict[str, float],
        conflicts: List[str] = None,
        vol2_sub_type: str = None,
        inscription_data: InscriptionData = None,
    ) -> str:
        """
        生成标准化的判定报告

        Args:
            inscription: 铭文内容（纯文本，用于显示）
            final_vid: 最终判定的卷号
            cooperative_vids: 协同卷列表（⚠ 关系）
            final_matches: 最终证据列表
            scores: 所有卷的 S 得分
            conflicts: 冲突卷列表
            vol2_sub_type: 卷2子分类（天台系/心经系/密教系/民间大乘）
            inscription_data: 结构化铭文数据（用于显示元数据和字段溯源）

        Returns:
            格式化的报告文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("宗派判定报告")
        lines.append("=" * 60)
        lines.append("")

        # 输入元数据（结构化数据模式）
        if inscription_data is not None:
            if inscription_data.inscription_text:
                lines.append("【题记文字】")
                # 长文本截断显示
                text = inscription_data.inscription_text
                if len(text) > 200:
                    text = text[:100] + "\n  ...（中间省略）...\n" + text[-100:]
                lines.append(text)
                lines.append("")
            if inscription_data.sculpture_subject:
                lines.append("【造像题材】")
                lines.append(inscription_data.sculpture_subject)
                lines.append("")
            if inscription_data.date:
                lines.append("【造像时间】")
                lines.append(inscription_data.date)
                lines.append("")
            if inscription_data.location:
                lines.append("【地点】")
                lines.append(inscription_data.location)
                lines.append("")
        else:
            # 纯文本模式
            lines.append("【铭文】")
            lines.append(inscription)
            lines.append("")

        # 判定结果（含协同卷 + 子分类）
        lines.append("【判定宗派】")
        if final_vid is None:
            lines.append("不可判定（无匹配词条）")
            lines.append("")
            lines.append("=" * 60)
            lines.append("报告生成完毕")
            lines.append("=" * 60)
            return "\n".join(lines)

        vol_name = self.volume_names.get(final_vid, f"卷{final_vid}")
        # 卷2为主卷时附加子分类
        if final_vid == "2" and vol2_sub_type:
            vol_name = f"{vol_name}（{vol2_sub_type}）"
        elif final_vid == "2" and not vol2_sub_type:
            vol_name = f"{vol_name}（未定系）"
        if cooperative_vids:
            coop_names = [
                f"{self.volume_names.get(v, f'卷{v}')}（卷{v}）"
                for v in cooperative_vids
            ]
            lines.append(
                f"{vol_name}（卷{final_vid}）+ {' + '.join(coop_names)} 混合"
            )
        else:
            lines.append(f"{vol_name}（卷{final_vid}）")
        lines.append("")

        # S 得分（主卷 + 协同卷）
        lines.append("【S 得分】")
        s_score = scores.get(final_vid, 0)
        lines.append(f"主卷 S = {s_score:.1f}")
        if cooperative_vids:
            for v in cooperative_vids:
                cs = scores.get(v, 0)
                cn = self.volume_names.get(v, f"卷{v}")
                # 协同卷是卷2（观音）时附加子分类
                if v == "2" and vol2_sub_type:
                    cn = f"{cn}（{vol2_sub_type}）"
                lines.append(f"协同 {cn}(卷{v}) S = {cs:.1f}")
        lines.append("")

        # 判定等级
        lines.append("【判定等级】")
        if s_score >= S_THRESHOLDS["established"]:
            level = "确立（Established）"
        elif s_score >= S_THRESHOLDS["high"]:
            level = "高可信（High）"
        elif s_score >= S_THRESHOLDS["weak"]:
            level = "弱可信（Weak）"
        else:
            level = "不可判定（Indeterminate）"
        lines.append(level)
        lines.append("")

        # 证据链（含字段溯源）
        lines.append("【证据链】")
        for match in final_matches:
            term = match["term"]
            w = match["w"]
            source = match.get("source", "")
            category = match.get("category", "")
            field = match.get("field", "")
            field_tag = ""
            if field and inscription_data is not None:
                if field == "subject":
                    field_tag = " [题材]"
            lines.append(f"- {term}（W={w}, {category}）{field_tag}")
            if source:
                lines.append(f"  来源: {source}")
        lines.append("")

        # 各字段贡献摘要（仅结构化模式）
        if inscription_data is not None and inscription_data.sculpture_subject:
            subj_matches = [m for m in final_matches if m.get("field") == "subject"]
            ins_matches = [m for m in final_matches if m.get("field") != "subject"]
            subj_s = 0
            ins_s = 0
            for m in subj_matches:
                w = m.get("w", 0) or 0
                subj_s += w if w >= 60 else 0.5 * w
            for m in ins_matches:
                w = m.get("w", 0) or 0
                ins_s += w if w >= 60 else 0.5 * w
            lines.append("【字段贡献】")
            lines.append(f"  题记文字 S 贡献: {ins_s:.1f}")
            lines.append(f"  造像题材 S 贡献: {subj_s:.1f}")
            lines.append("")

        # 冲突说明
        if conflicts:
            lines.append("【冲突说明】")
            for conflict_vid in conflicts:
                conflict_name = self.volume_names.get(conflict_vid, f"卷{conflict_vid}")
                lines.append(f"- 与 {conflict_name}（卷{conflict_vid}）存在互斥冲突")
            lines.append("")

        # 各卷得分汇总
        lines.append("【各卷得分汇总】")
        for vid in sorted(scores.keys(), key=lambda x: int(x)):
            vol_name = self.volume_names.get(vid, f"卷{vid}")
            score = scores[vid]
            lines.append(f"{vol_name}（卷{vid}）: S = {score:.1f}")
        lines.append("")

        lines.append("=" * 60)
        lines.append("报告生成完毕")
        lines.append("=" * 60)

        return "\n".join(lines)


# ── 主引擎类 ────────────────────────────────────────────────────────
class SectJudgmentEngine:
    """宗派判定引擎：整合所有组件的主控类"""

    def __init__(self):
        """初始化引擎，加载所有数据文件"""
        self.normalizer = VariantNormalizer()
        self.term_index = self._load_term_index()
        self.matcher = TermMatcher(self.term_index)
        self.score_calculator = ScoreCalculator(S_THRESHOLDS)
        self.mutex_resolver = MutexResolver(self._load_mutex_matrix())
        self.formatter = ReportFormatter()

    def _load_term_index(self) -> Dict[str, List[dict]]:
        """加载词条索引"""
        if TERM_INDEX_FILE.exists():
            with open(TERM_INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_mutex_matrix(self) -> Dict[str, Dict[str, str]]:
        """加载互斥矩阵"""
        if MUTEX_MATRIX_FILE.exists():
            with open(MUTEX_MATRIX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 从 "卷2 观音" 或 "卷2" 中提取纯数字卷号
                def extract_vid(label: str) -> str:
                    m = re.search(r'(\d+)', label)
                    return m.group(1) if m else label
                # 转换为嵌套字典 {vid_num: {vid_num: relation}}
                matrix = {}
                for row in data.get("rows", []):
                    vid = extract_vid(row[0])
                    matrix[vid] = {}
                    for i, col in enumerate(data.get("header", [])[1:], 1):
                        if i < len(row):
                            col_vid = extract_vid(col)
                            matrix[vid][col_vid] = row[i]
                return matrix
        return {}

    def _check_non_buddhist(self, text: str) -> dict:
        """
        道教预过滤：检测文本是否以道教为主（非佛教）

        在佛教词条匹配之前运行。当检测到强道教信号且无
        强佛教覆盖信号时，标记为非佛教文本，跳过后续佛教
        宗派判定流程。

        Returns:
            {"is_non_buddhist": bool, "reason": str, "matched_terms": list}
        """
        matched = []
        for term in DAOIST_STRONG_TERMS:
            if term in text:
                matched.append(term)

        if not matched:
            return {"is_non_buddhist": False, "reason": "", "matched_terms": []}

        # 检查是否有强佛教信号覆盖（佛道混合场景）
        has_buddhist = any(bt in text for bt in BUDDHIST_OVERRIDE_TERMS)

        if has_buddhist:
            return {
                "is_non_buddhist": False,
                "reason": "佛道混合，仍进行佛教判定",
                "matched_terms": matched,
            }

        return {
            "is_non_buddhist": True,
            "reason": "道教文本，非佛教",
            "matched_terms": matched,
        }

    def _process_internal(self, inscription: str = "", inscription_data: InscriptionData = None) -> dict:
        """
        内部处理逻辑，返回结构化判定数据

        Returns:
            dict 包含 report, final_vid, cooperative_vids, final_matches,
                 scores, conflicts, vol2_sub_type, inscription_data, field_contributions
        """
        # 构建统一匹配文本
        if inscription_data is not None:
            data = inscription_data
        else:
            data = InscriptionData(inscription_text=inscription)

        combined = data.build_combined_text()
        if not combined:
            result = self.formatter.format_report(
                inscription=inscription,
                final_vid=None, cooperative_vids=[], final_matches=[],
                scores={}, conflicts=[], vol2_sub_type=None,
                inscription_data=data,
            )
            return {
                "report": result,
                "final_vid": None,
                "cooperative_vids": [],
                "final_matches": [],
                "scores": {},
                "conflicts": [],
                "vol2_sub_type": None,
                "inscription_data": data,
                "field_contributions": {"inscription": 0.0, "subject": 0.0},
            }

        # 1. 异体字归一化
        normalized = self.normalizer.normalize(combined)

        # 1a. 道教预过滤（在佛教词条匹配前运行）
        daoist_check = self._check_non_buddhist(normalized)
        if daoist_check["is_non_buddhist"]:
            result = self.formatter.format_non_buddhist_report(
                inscription=inscription or combined,
                reason="道教",
                matched_terms=daoist_check["matched_terms"],
                inscription_data=data,
            )
            return {
                "report": result,
                "final_vid": None,
                "cooperative_vids": [],
                "final_matches": [],
                "scores": {},
                "conflicts": [],
                "vol2_sub_type": None,
                "inscription_data": data,
                "field_contributions": {"inscription": 0.0, "subject": 0.0},
                "non_buddhist": True,
                "non_buddhist_reason": "道教",
                "non_buddhist_matched_terms": daoist_check["matched_terms"],
            }

        # 2. 词条匹配（带字段溯源）
        matches = self.matcher.match(normalized, inscription_data=data)

        # 3. 按卷分组
        matches_by_vid = {}
        for match in matches:
            vid = match["vid"]
            if vid not in matches_by_vid:
                matches_by_vid[vid] = []
            matches_by_vid[vid].append(match)

        # 4. 计算 S 得分
        scores = self.score_calculator.calculate(matches)

        # 5. 互斥冲突消解
        final_vid, cooperative_vids, final_matches = self.mutex_resolver.resolve(
            scores, matches_by_vid
        )

        # 5a. 检测卷2（观音）的子分类
        vol2_sub_type = None
        if "2" in matches_by_vid:
            sub_type_scores = {}
            for m in matches_by_vid["2"]:
                st = m.get("sub_type")
                if st:
                    sw = sub_type_scores.get(st, 0)
                    sub_type_scores[st] = max(sw, m.get("w", 0))
            if sub_type_scores:
                vol2_sub_type = max(sub_type_scores, key=sub_type_scores.get)

        # 6. 找出冲突卷
        conflicts = []
        if final_vid:
            for vid in scores:
                if vid != final_vid and scores[vid] >= S_THRESHOLDS["weak"]:
                    if vid not in cooperative_vids:
                        conflicts.append(vid)

        # 7. 计算字段贡献
        field_contributions = {"inscription": 0.0, "subject": 0.0}
        for m in final_matches:
            w = m.get("w", 0) or 0
            contrib = w if w >= 60 else 0.5 * w
            f = m.get("field", "")
            if f == "subject":
                field_contributions["subject"] += contrib
            else:
                field_contributions["inscription"] += contrib

        # 8. 生成报告
        report = self.formatter.format_report(
            inscription=inscription or combined,
            final_vid=final_vid,
            cooperative_vids=cooperative_vids,
            final_matches=final_matches,
            scores=scores,
            conflicts=conflicts,
            vol2_sub_type=vol2_sub_type,
            inscription_data=data,
        )

        return {
            "report": report,
            "final_vid": final_vid,
            "cooperative_vids": cooperative_vids,
            "final_matches": final_matches,
            "scores": scores,
            "conflicts": conflicts,
            "vol2_sub_type": vol2_sub_type,
            "inscription_data": data,
            "field_contributions": field_contributions,
        }

    def process(self, inscription: str = "", inscription_data: InscriptionData = None) -> str:
        """
        处理铭文，返回判定报告

        支持两种调用方式:
          1. process("铭文内容")  — 纯文本（向后兼容）
          2. process(inscription_data=InscriptionData(...))  — 结构化数据

        Args:
            inscription: 铭文内容（纯文本模式）
            inscription_data: 结构化铭文数据（多字段模式）

        Returns:
            格式化的判定报告
        """
        result = self._process_internal(inscription, inscription_data)
        return result["report"]

    def process_to_dict(self, inscription: str = "", inscription_data: InscriptionData = None) -> dict:
        """
        处理铭文，返回结构化JSON字典（供 --json 调用）

        返回字段:
          - report: 格式化的判定报告文本
          - final_vid: 最终判定的卷号
          - final_vid_name: 判定宗派名称
          - cooperative_vids: 协同卷列表
          - s_score: 主卷 S 得分
          - level: 判定等级
          - matches: 证据列表 [{term, vid, w, source, category, field}]
          - scores: 所有卷 S 得分 {vid: score}
          - field_contributions: 字段贡献 {inscription: 分数, subject: 分数}
          - vol2_sub_type: 卷2子分类（如有）
          - conflicts: 冲突卷列表
        """
        result = self._process_internal(inscription, inscription_data)
        d = result["inscription_data"]
        final_vid = result["final_vid"]
        s_score = result["scores"].get(final_vid, 0) if final_vid else 0

        # 非佛教标记
        is_non_buddhist = result.get("non_buddhist", False)
        non_buddhist_reason = result.get("non_buddhist_reason", "")
        non_buddhist_matched_terms = result.get("non_buddhist_matched_terms", [])

        # 判定等级
        level = "不可判定（Indeterminate）"
        if is_non_buddhist:
            level = f"拒绝判定 — {non_buddhist_reason}"
        elif final_vid:
            if s_score >= S_THRESHOLDS["established"]:
                level = "确立（Established）"
            elif s_score >= S_THRESHOLDS["high"]:
                level = "高可信（High）"
            elif s_score >= S_THRESHOLDS["weak"]:
                level = "弱可信（Weak）"

        # 宗派名称
        final_vid_name = ""
        if final_vid:
            vol_name = ReportFormatter().volume_names.get(final_vid, f"卷{final_vid}")
            if final_vid == "2" and result["vol2_sub_type"]:
                vol_name = f"{vol_name}（{result['vol2_sub_type']}）"
            final_vid_name = vol_name

        # 精简证据列表
        matches_clean = []
        for m in result["final_matches"]:
            matches_clean.append({
                "term": m["term"],
                "vid": m["vid"],
                "w": m["w"],
                "source": m.get("source", ""),
                "category": m.get("category", ""),
                "field": m.get("field", "inscription"),
            })

        return {
            "inscription": d.inscription_text,
            "subject": d.sculpture_subject,
            "date": d.date,
            "location": d.location,
            "report": result["report"],
            "final_vid": final_vid,
            "final_vid_name": final_vid_name,
            "cooperative_vids": result["cooperative_vids"],
            "s_score": round(s_score, 1),
            "level": level,
            "matches": matches_clean,
            "scores": {k: round(v, 1) for k, v in result["scores"].items()},
            "field_contributions": {k: round(v, 1) for k, v in result["field_contributions"].items()},
            "vol2_sub_type": result["vol2_sub_type"],
            "conflicts": result["conflicts"],
            "non_buddhist": is_non_buddhist,
            "non_buddhist_reason": non_buddhist_reason,
            "non_buddhist_matched_terms": non_buddhist_matched_terms,
        }


# ── CLI 入口 ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="佛教宗派判定计算引擎")
    parser.add_argument("--input", type=str, help="题记文字（铭文正文）")
    parser.add_argument("--subject", type=str, default="", help='造像题材（如「善财童子参礼善知识像」）')
    parser.add_argument("--date", type=str, default="", help='造像时间（如「南宋绍兴二十五年」）')
    parser.add_argument("--location", type=str, default="", help='地点（如「重庆市大足区」）')
    parser.add_argument("--test", action="store_true", help="运行内置测试用例")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    args = parser.parse_args()

    engine = SectJudgmentEngine()

    if args.test:
        # 运行测试用例
        test_cases = [
            ("纯文本: 药师", "弟子某甲为亡父造药师如来像一躯愿亡父往生净土"),
            ("纯文本: 观音普门品", "观世音菩萨普门品愿往生西方极乐世界"),
            ("纯文本: 密教绝对优先", "造毗卢遮那佛曼荼罗真言灌顶"),
            ("纯文本: 孔雀明王复合词保护", "敬造孔雀明王像一躯"),
            ("纯文本: 毗沙门天王", "敬造毗沙门天王一躯"),
            ("纯文本: 无匹配", "今日天气晴朗"),
        ]
        for label, tc in test_cases:
            print(f"\n{'=' * 60}")
            print(f"测试: {label}")
            print(f"{'=' * 60}")
            report = engine.process(tc)
            print(report)

        # 结构化数据测试
        print("\n" + "=" * 60)
        print("结构化数据测试: 铭文 + 造像题材（含字段贡献）")
        print("=" * 60)
        data = InscriptionData(
            inscription_text="大宋昌州永川县使汉卿本师庞上明与祖母胡氏三娘为永世□发心认砌第十一级",
            sculpture_subject="善财童子参礼善知识像",
            date="南宋绍兴二十五年（1155年）",
            location="重庆市大足区北山多宝塔",
        )
        report = engine.process(inscription_data=data)
        print(report)

        # JSON 输出测试
        print("\n" + "=" * 60)
        print("JSON 输出测试")
        print("=" * 60)
        json_result = engine.process_to_dict("敬造药师琉璃光如来一躯")
        print(json.dumps(json_result, ensure_ascii=False, indent=2))

        # JSON 结构化数据测试
        print("\n" + "=" * 60)
        print("JSON 结构化数据测试（铭文 + 题材）")
        print("=" * 60)
        data2 = InscriptionData(
            inscription_text="敬造药师琉璃光如来一躯",
            sculpture_subject="药师佛",
        )
        json_result2 = engine.process_to_dict(inscription_data=data2)
        print(json.dumps(json_result2, ensure_ascii=False, indent=2))
    elif args.input or args.subject:
        if args.json:
            # JSON 输出路径（使用 process_to_dict 避免二次处理）
            if args.subject or args.date or args.location:
                data = InscriptionData(
                    inscription_text=args.input or "",
                    sculpture_subject=args.subject or "",
                    date=args.date or "",
                    location=args.location or "",
                )
                result = engine.process_to_dict(inscription_data=data)
            else:
                result = engine.process_to_dict(args.input or "")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 文本输出路径
            if args.subject or args.date or args.location:
                data = InscriptionData(
                    inscription_text=args.input or "",
                    sculpture_subject=args.subject or "",
                    date=args.date or "",
                    location=args.location or "",
                )
                print(engine.process(inscription_data=data))
            else:
                print(engine.process(args.input or ""))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
