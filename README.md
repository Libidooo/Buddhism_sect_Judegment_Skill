# 四川地区佛教石窟铭文宗派判定系统

> 基于确定性规则引擎 + AI 协作的佛教造像铭文宗派自动分类系统，覆盖四川地区6-13世纪 8 大宗派体系，集成 CBETA 大藏经经典索引查询。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v4.1-orange.svg)]()
[![F1](https://img.shields.io/badge/Micro--F1-0.679-blueviolet.svg)]()

---

## 目录

- [系统简介](#系统简介)
- [性能指标](#性能指标)
- [核心架构](#核心架构)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [项目结构](#项目结构)
- [判定体系](#判定体系)
- [CBETA 经典索引](#cbeta-经典索引)
- [引擎与 AI 协作](#引擎与-ai-协作)
- [数据集与评测](#数据集与评测)
- [安装与依赖](#安装与依赖)
- [文档](#文档)
- [许可证](#许可证)

---

## 系统简介

本系统用于系统化分析四川地区佛教石窟铭文（石刻题记、造像记、碑刻等），自动判定其所属宗派体系。系统采用**确定性计算引擎 + AI 解读**的混合架构：引擎负责词条匹配、权重计算和冲突消解，AI 负责结果解读和上下文补充，杜绝 LLM 心算导致的权重幻觉。

### 核心能力

| 能力 | 说明 |
|------|------|
| 宗派判定 | 将铭文分类到 8 个宗派体系（药师/净土/密教/观音/华严/禅宗/地藏/弥勒）+ 律宗等扩展卷 |
| 多字段输入 | 支持铭文文本 + 造像题材 + 年代 + 地点四字段联合判定 |
| 异体字归一 | 自动将繁体/异体字转换为标准字形（藥→药、瑠→璃、來→来等） |
| 复合词保护 | 自动合并相邻短词条，防止跨卷拆分冲突（"孔雀"+"明王"→"孔雀明王"） |
| 互斥消解 | 6×6 基础互斥矩阵 + 10×10 扩展矩阵，自动处理跨宗派冲突 |
| 观音子分类 | 自动检测观音体系内部子分类（天台系/心经系/密教系/民间大乘） |
| CBETA 查询 | 集成 54 部大藏经经典的 T 号/经名/关键词/卷别四级索引查询 |

---

## 性能指标

### 基线对比

| 基线 | Micro-F1 | 说明 |
|------|----------|------|
| 朴素基线（纯字符串匹配） | 0.390 | 下限 |
| **本系统（完整信息）** | **0.679** | 题记+题材+地点 |
| **本系统（仅题材+地点）** | **0.708** | 无题记原文 |
| 专家规则基线（手工关键词表） | 0.730 | 上限 |
| 本系统+AI（LLM 逐条分析） | 0.800 | 48 条小样本 |

### 412 条标注数据集各宗派表现（完整信息条件）

| 宗派 | Precision | Recall | F1 |
|------|-----------|--------|----|
| 地藏 | 0.892 | 0.717 | 0.795 |
| 观音 | 0.789 | 0.716 | 0.751 |
| 华严 | 0.900 | 0.628 | 0.740 |
| 密教 | 0.708 | 0.656 | 0.681 |
| 弥勒 | 0.530 | 0.921 | 0.673 |
| 药师 | 0.500 | 0.867 | 0.634 |
| 净土 | 0.527 | 0.773 | 0.627 |
| 禅宗 | 0.737 | 0.378 | 0.500 |

> 详见 [数据集与评测](#数据集与评测) 章节。

---

## 核心架构

```
┌─────────────────────────────────────────────────┐
│                   用户输入                       │
│   (铭文文本 / 造像题材 / 年代 / 地点)             │
└──────────────────────┬──────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │   前置过滤 (Filter)      │
          │   非佛教内容检测          │
          │   残损度判断              │
          │   伪造铭文识别            │
          └────────────┬────────────┘
                       │ 通过
          ┌────────────▼────────────┐
          │   确定性计算引擎          │
          │                         │
          │  1. 异体字归一化          │
          │  2. 词条最长匹配          │
          │     (7175 条术语库)       │
          │  3. 复合词保护合并        │
          │  4. S 得分计算            │
          │  5. 互斥冲突消解          │
          │  6. 观音子分类检测        │
          │  7. 字段贡献分析          │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   AI 解读与补充           │
          │   验证结果合理性          │
          │   补充引擎未覆盖信息      │
          │   生成标准化报告          │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   CBETA 经典索引         │
          │   T号 / 经名 / 关键词    │
          │   按卷别检索              │
          └─────────────────────────┘
```

---

## 快速开始

### 环境要求

- Python 3.8+
- 依赖包见 [requirements.txt](requirements.txt)

### 安装

```bash
git clone https://github.com/your-username/buddhist-judgment.git
cd buddhist-judgment
pip install -r requirements.txt
```

### 30 秒上手

```bash
# 单条铭文判定
python scripts/sect_engine.py --input "弟子某甲为亡父造药师如来像一躯愿亡父往生净土"

# 多字段输入（铭文 + 造像题材 + 年代 + 地点）
python scripts/sect_engine.py \
  --input "敬造药师琉璃光如来一躯" \
  --subject "药师佛" \
  --date "乾德三年" \
  --location "安岳"

# 运行内置测试
python scripts/sect_engine.py --test

# JSON 格式输出
python scripts/sect_engine.py --input "敬造药师琉璃光如来一躯" --json
```

### CLI 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--input` | string | `""` | 铭文文本，宗派判定的主要依据 |
| `--subject` | string | `""` | 造像题材，与铭文拼接后统一匹配 |
| `--date` | string | `""` | 造像年代，仅展示，不参与匹配 |
| `--location` | string | `""` | 造像地点，仅展示，不参与匹配 |
| `--json` | flag | — | 以 JSON 格式输出结果 |
| `--test` | flag | — | 运行内置测试用例 |

---

## 使用示例

### 示例 1：药师体系判定

```bash
python scripts/sect_engine.py --input "敬造药师琉璃光如来一躯" --subject "药师佛" --date "乾德三年" --location "安岳"
```

**输出**：

```
============================================================
宗派判定报告
============================================================

【题记文字】
敬造药师琉璃光如来一躯

【造像题材】
药师佛

【造像年代】
乾德三年

【造像地点】
安岳

【判定宗派】
药师体系（卷4）

【S 得分】
主卷 S = 160.0

【判定等级】
确立（Established）

【证据链】
- 药师如来（W=80, 决定因, 题记文字）
- 药师琉璃光（W=80, 决定因, 题记文字）
- 药师佛（W=80, 决定因, 造像题材）

【字段贡献】
  题记文字 S 贡献: 80.0
  造像题材 S 贡献: 80.0
============================================================
```

### 示例 2：复合词保护

"孔雀明王"由"孔雀"（卷3净土, W=45）和"明王"（卷5密教, W=54）两个短词组成。引擎自动检测相邻短词并合并为复合词条"孔雀明王"（卷5密教, W=80），防止错误拆分。

```bash
python scripts/sect_engine.py --input "敬造孔雀明王像一躯"
# → 判定为密教体系（卷5），S=80
```

### 示例 3：观音子分类

```bash
python scripts/sect_engine.py --input "观世音菩萨普门品愿往生西方极乐世界"
# → 判定为观音体系（天台系），自动检测"普门品"子分类
```

### 示例 4：异体字归一化

```bash
python scripts/sect_engine.py --input "敬造藥師琉瑠光如來一軀"
# → 繁体字自动归一：藥→药, 瑠→璃, 來→来
# → 判定为药师体系（卷4），S=80
```

### 示例 5：非佛教内容过滤

```bash
python scripts/sect_engine.py --input "今日天气晴朗去公园散步"
# → 不可判定（无匹配词条）
```

### 示例 6：CBETA 经典查询

```bash
# 按T号查询
python scripts/cbeta_query.py --t-number T0450
# → 药师琉璃光如来本愿功德经，卷四，核心经典

# 按经名查询
python scripts/cbeta_query.py --sutra-name "妙法莲华经"
# → T0262，卷一/卷二，核心经典

# 按关键词查询
python scripts/cbeta_query.py --keyword "观世音"
# → 返回所有包含"观世音"的经典及其位置

# 按卷别查找
python scripts/sutra_lookup.py --volume "卷六"
# → 返回卷六（华严体系）所有经典

# 索引统计
python scripts/cbeta_index_search.py --stats
```

---

## 项目结构

```
buddhist-judgment/
├── SKILL.md                                      # 总控 Skill（系统入口）
├── sichuan-buddhist-inscription-judgment-system.md  # 总提示词
├── requirements.txt                              # Python 依赖
├── .coze / .gitignore
│
├── scripts/                                      # 计算引擎与查询脚本
│   ├── sect_engine.py                           # 宗派判定计算引擎（核心）
│   ├── cbeta_query.py                           # CBETA 经典查询
│   ├── sutra_lookup.py                          # 经典检索（按卷别/T号/经名/关键词）
│   ├── cbeta_index_search.py                    # 索引全文搜索与统计
│   ├── test_cbeta_scripts.py                    # 自动测试套件（13项）
│   └── data/                                    # 引擎数据文件
│       ├── term_index.json                     # 词条索引（7175 条）
│       ├── mutex_matrix.json                   # 6×6 基础互斥矩阵
│       ├── extended_mutex.json                 # 10×10 扩展互斥矩阵
│       ├── weight_definitions.json             # 权重定义
│       ├── s_score_thresholds.json             # S 得分阈值
│       ├── exclusion_terms.json                # 排除词表
│       ├── volume_catalog.json                 # 卷目目录
│       └── terms_vol_0.json ~ terms_vol_15.json  # 16卷分卷词条索引
│
├── assets/                                       # CBETA 索引数据
│   ├── cbeta-t-number-index.md                 # T 号索引（54 部经典）
│   ├── cbeta-keyword-index.md                   # 关键词索引（118 条映射）
│   └── cbeta-volume-query-path.md              # 卷别查询路径
│
├── cbeta-index-references/                       # CBETA 经典总索引
│   ├── cbeta-classics-index.md                  # 完整经典索引
│   └── CBETA_README.md                          # 索引使用说明
│
├── sect-judgment-hub/                            # 宗派判定 Skill
│   ├── SKILL.md                                 # 判定规则与执行流程
│   └── references/                              # 十六卷规则文件
│       ├── volume-zero-general-rules.md        # 卷零：总则（互斥矩阵/权重体系）
│       ├── volume-one-sutra-stems.md           # 卷一：经文词干
│       ├── volume-two-guanyin-system.md        # 卷二：观音体系
│       ├── volume-three-pure-land.md           # 卷三：净土体系
│       ├── volume-four-medicine-buddha.md      # 卷四：药师体系
│       ├── volume-five-esoteric.md             # 卷五：密教体系
│       ├── volume-six-huayan.md                # 卷六：华严体系
│       ├── volume-seven-zen.md                 # 卷七：禅宗
│       ├── volume-eight-regional.md            # 卷八：区域体系
│       ├── volume-nine-kshitigarbha.md         # 卷九：地藏体系
│       ├── volume-ten-maitreya.md              # 卷十：弥勒体系
│       ├── volume-eleven-sanlun.md             # 卷十一：三论宗
│       ├── volume-twelve-yogacara.md           # 卷十二：唯识宗
│       ├── volume-thirteen-tiantai.md          # 卷十三：天台宗
│       ├── volume-fourteen-satyasiddhi.md      # 卷十四：成实宗
│       ├── volume-fifteen-vinaya.md            # 卷十五：律宗
│       ├── cross-reference-matrix.md           # 交叉引用矩阵
│       ├── output-format.md                    # 输出格式规范
│       ├── variant-characters.md               # 异体字表
│       └── detail/                             # 14 卷完整版规则（卷2-15）
│
├── sect-preliminary-filter/                      # 前置过滤 Skill
│   ├── SKILL.md
│   └── references/
│       ├── detailed-rules.md                   # 过滤详细规则
│       └── output-format.md                    # 输出格式
│
└── docs/                                         # 文档
    ├── README.md                                # 文档索引
    ├── AI_USAGE_GUIDE.md                       # AI 使用指南
    ├── PROJECT_STRUCTURE.md                     # 项目结构说明
    ├── SKILL_COMPLETENESS_CHECK.md             # 完整性检查报告
    ├── SKILL_CORRECTION_REPORT.md               # 修正报告
    └── 2024-08-15_original-system.md           # 原始系统设计文档
```

---

## 判定体系

### 十六卷宗派体系

| 卷 | 名称 | 核心经典 | T号 | 判定关键词 |
|----|------|----------|-----|------------|
| 0 | 总则 | — | — | 互斥矩阵、权重体系 |
| 1 | 经文词干 | 金刚经 | T0235 | 经文原句/词干匹配 |
| 2 | 观音体系 | 妙法莲华经 | T0262 | 观世音、普门品、千手千眼 |
| 3 | 净土体系 | 佛说无量寿经 | T0360 | 阿弥陀佛、往生、极乐世界 |
| 4 | 药师体系 | 药师琉璃光如来本愿功德经 | T0450 | 药师如来、十二大愿、琉璃光 |
| 5 | 密教体系 | 大日经 | T0848 | 大日如来、曼荼罗、种子字、明王 |
| 6 | 华严体系 | 大方广佛华严经 | T0279 | 善财童子、普贤、华严三圣 |
| 7 | 禅宗 | 六祖壇經 | T0334 | 顿悟、无念、本来面目 |
| 8 | 区域体系 | — | — | 四川地域信息、安岳工匠 |
| 9 | 地藏体系 | 地藏菩萨本愿经 | T0412 | 地藏菩萨、地狱、六道轮回 |
| 10 | 弥勒体系 | 弥勒上生经 | T0453 | 弥勒、兜率天、龙华三会 |
| 11 | 三论宗 | 中论 | — | 八不中道、二谛 |
| 12 | 唯识宗 | 成唯识论 | — | 三性、三无性、阿赖耶识 |
| 13 | 天台宗 | 法华玄义 | — | 一心三观、三谛圆融 |
| 14 | 成实宗 | 成实论 | — | 四谛、二空 |
| 15 | 律宗 | 四分律 | T1428 | 比丘戒、羯磨、布萨 |

### S 得分计算公式

```
S = Σ(W≥60的权重) + Σ(0.5 × W<60的权重)
```

**权重等级**：

| 等级 | 权重范围 | 说明 |
|------|----------|------|
| A层 决定因 | W=80-85 | 主体明确，决定性证据 |
| B层 强因缘 | W=60-79 | 强力证据，显著支持判定 |
| C层 中因缘 | W=40-59 | 中等证据，辅助性支持 |
| D层 弱因缘 | W=20-39 | 弱证据，仅作参考 |

**判定阈值**：

| S 得分 | 判定等级 | 说明 |
|--------|----------|------|
| S ≥ 160 | 确立（Established） | 判定明确，无需进一步检查 |
| 120 ≤ S < 160 | 可信（Confident） | 判定可靠，需检查冲突卷 |
| 80 ≤ S < 120 | 弱可信（Weak） | 判定较弱，需补强 |
| S < 80 | 不可判定 | 需人工复核 |

### 优先级规则

1. **密教绝对优先**：出现 W≥60 的密教词（种子字/手印/曼荼罗/大日如来/明王）→ 必入卷五
2. **主体判定优先**：五大主体（药师/弥勒/地藏/观音/阿弥陀）一旦判定，不跨卷
3. **互斥矩阵消解**：跨卷冲突由互斥矩阵自动消解
4. **复合词保护**：相邻短词合并为复合词，防止跨卷拆分

---

## CBETA 经典索引

系统集成 CBETA 大藏经经典索引，支持四维查询：

| 查询维度 | 脚本 | 命令示例 |
|----------|------|----------|
| T号查询 | `cbeta_query.py` | `python scripts/cbeta_query.py --t-number T0450` |
| 经名查询 | `cbeta_query.py` | `python scripts/cbeta_query.py --sutra-name "药师经"` |
| 关键词查询 | `cbeta_query.py` | `python scripts/cbeta_query.py --keyword "观世音"` |
| 卷别查找 | `sutra_lookup.py` | `python scripts/sutra_lookup.py --volume "卷四"` |
| 全文搜索 | `cbeta_index_search.py` | `python scripts/cbeta_index_search.py --search "药师"` |
| 索引统计 | `cbeta_index_search.py` | `python scripts/cbeta_index_search.py --stats` |

**索引规模**：54 部经典、118 条关键词映射、16 卷别映射。

所有查询结果附带 CBETA Online 链接（`https://cbetaonline.dila.edu.tw/{T号}`），可直接访问原文。

---

## 引擎与 AI 协作

本系统的核心设计原则：**权重计算必须由确定性引擎完成，AI 不得心算**。

### 分工边界

| 任务 | 执行者 | 原因 |
|------|--------|------|
| 异体字归一化 | 引擎 | 确定性映射，无需判断 |
| 词条匹配 | 引擎 | 最长匹配算法，避免遗漏 |
| S 得分计算 | 引擎 | 数学公式，禁止心算 |
| 互斥冲突消解 | 引擎 | 规则化优先级，无歧义 |
| 结果解读 | AI | 需要语义理解和上下文 |
| 补充分析 | AI | 引擎未覆盖的新术语/残损铭文 |
| 最终报告 | AI | 需要自然语言生成 |

### 协作流程

```
用户输入 → 引擎计算 → AI解读 → 补充分析 → 标准化输出
                         ↑
                    引擎输出数值结果
                    AI 负责解读证据链
                    补充引擎未覆盖信息
                    标注"引擎未覆盖"
```

---

## 数据集与评测

系统在三个数据集上进行了分层验证：

### 数据集概览

| 数据集 | 样本数 | 用途 | 特点 |
|--------|--------|------|------|
| 专家标注基准集 | 48 | 深度评测 | 专家逐条标注，引擎 vs 引擎+AI 对比 |
| 有标注大规模集 | 412 | 核心指标 | 从 992 条 CSV 排除"无法判定" |
| 全量数据集 | 989 | 规模验证 | 含标注基准对比，验证可扩展性 |

### 数据集 1：48 条专家标注基准

| 指标 | 引擎-only | 引擎+AI |
|------|-----------|---------|
| 可判定率 | 62.5% (30/48) | 70.8% (34/48) |
| 完全正确率（总） | 31.2% (15/48) | 50.0% (24/48) |
| 完全正确率（可判定内） | 50.0% (15/30) | 70.6% (24/34) |
| 完全不匹配率 | 12.5% (6/48) | 4.2% (2/48) |
| 简化 F1 | 0.588 | 0.800 |

### 数据集 2：412 条有标注数据（最可靠指标）

**完整信息条件（造像题材 + 地点 + 题记原文）**：

| 指标 | 数值 |
|------|------|
| 准确率 | 50.97% |
| Micro-Precision | 0.653 |
| Micro-Recall | 0.707 |
| **Micro-F1** | **0.679** |
| 不可判定数 | 108 (26.2%) |

**仅题材+地点条件**：

| 指标 | 数值 |
|------|------|
| 准确率 | 36.17% |
| **Micro-F1** | **0.708** |
| 不可判定数 | 219 (53.2%) |

### 数据集 3：989 条全量数据

| 指标 | 引擎-only | 引擎+规则模拟 |
|------|-----------|---------------|
| 可判定率 | 20.2% (200) | 34.7% (343) |
| 完全正确 | 71.9% (711) | 75.9% (751) |
| 完全不匹配 | 24.3% (240) | 17.8% (176) |

> **注意**：数据集 3 的正确率包含大量"引擎输出不可判定 + 专家也标注无法判定"的真阴性匹配（580 条），因此正确率虚高。数据集 2 的 Micro-F1=0.679 是最可靠的引擎性能指标。

---

## 安装与依赖

### 系统要求

- Python 3.8+
- 操作系统：Windows / macOS / Linux

### 依赖安装

```bash
pip install -r requirements.txt
```

主要依赖：

| 包 | 用途 |
|----|------|
| `requests` | CBETA Online API 请求 |
| `beautifulsoup4` | CBETA 页面解析 |
| `lxml` | XML/HTML 解析 |

### 验证安装

```bash
# 运行引擎内置测试
python scripts/sect_engine.py --test

# 运行 CBETA 测试套件（13 项）
python scripts/test_cbeta_scripts.py
```

两个测试全部通过即表示安装成功。

---

## 文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 总控 Skill，系统主入口 |
| [sichuan-buddhist-inscription-judgment-system.md](sichuan-buddhist-inscription-judgment-system.md) | 总提示词，完整系统说明 |
| [docs/AI_USAGE_GUIDE.md](docs/AI_USAGE_GUIDE.md) | AI 使用指南 |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | 项目结构详细说明 |
| [docs/SKILL_COMPLETENESS_CHECK.md](docs/SKILL_COMPLETENESS_CHECK.md) | 完整性检查报告 |
| [docs/2024-08-15_original-system.md](docs/2024-08-15_original-system.md) | 原始系统设计文档 |

---

## 技术统计

| 指标 | 数值 |
|------|------|
| 词条索引总量 | 7,175 条 |
| 十六卷规则文件 | 16 核心 + 14 完整版 |
| CBETA 经典索引 | 54 部经典 + 118 条关键词映射 |
| Python 脚本 | 5 个，2,522 行 |
| 互斥矩阵 | 6×6 基础 + 10×10 扩展 |
| 异体字映射 | 45+ 组繁简/异体对应 |
| 项目总文件 | 87 个 |
| Micro-F1（核心指标） | 0.679 |

---

## 许可证

MIT License

---

**版本**：v4.1
**最后更新**：2026-06-25
**维护者**：Cicsoncy
