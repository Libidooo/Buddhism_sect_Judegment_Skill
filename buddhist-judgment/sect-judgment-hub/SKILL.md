---
name: sect-judgment-hub
description: 宗派判定十五卷主控中心；当用户需要执行完整的宗派判定流程、进行主体与宗派的综合分析、或需要基于卷零至卷十五规则系统化判断题记时使用
dependency:
  python:
    - python-docx==0.8.11
---

# 宗派判定主控中心 - 资源索引

## 计算引擎

引擎位于 `scripts/sect_engine.py`。

**每次宗派判定时必须调用引擎**，禁止 AI 心算：
```bash
python scripts/sect_engine.py --input 铭文内容
```

## 十五卷规则索引

| 卷号 | 名称 | 核心规则 | 完整细节 |
|------|------|----------|----------|
| 零 | 总则 | volume-zero-general-rules.md | — |
| 一 | 经文词干库 | volume-one-sutra-stems.md | — |
| 二 | 观音体系 | volume-two-guanyin-system.md | detail |
| 三 | 净土体系 | volume-three-pure-land.md | detail |
| 四 | 药师体系 | volume-four-medicine-buddha.md | detail |
| 五 | 密教体系 | volume-five-esoteric.md | detail |
| 六 | 华严体系 | volume-six-huayan.md | detail |
| 七 | 禅宗体系 | volume-seven-zen.md | detail |
| 八 | 区域体系 | volume-eight-regional.md | detail |
| 九 | 地藏体系 | volume-nine-kshitigarbha.md | detail |
| 十 | 弥勒体系 | volume-ten-maitreya.md | detail |
| 十一 | 三论宗 | volume-eleven-sanlun.md | detail |
| 十二 | 唯识宗 | volume-twelve-yogacara.md | detail |
| 十三 | 天台宗 | volume-thirteen-tiantai.md | detail |
| 十四 | 成实宗 | volume-fourteen-satyasiddhi.md | detail |
| 十五 | 律宗 | volume-fifteen-vinaya.md | detail |

### 通用参考

- cross-reference-matrix.md — 跨卷冲突处理
- output-format.md — 输出格式规范
- variant-characters.md — 异体字识别

分层读取策略：默认读取 references/ 核心规则，复杂场景按需读取 references/detail/ 完整版。
卷零总则是所有判定规则的母规则，必须优先理解。

## 当前集成状态

- 卷零至卷十五全部规则（完整集成）
- 计算引擎 sect_engine.py（v4.0，100+ 词条库）
