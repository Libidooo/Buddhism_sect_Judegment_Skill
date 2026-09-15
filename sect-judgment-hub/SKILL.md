---
name: sect-judgment-hub
description: 宗派判定十六卷主控中心；当用户需要执行完整的宗派判定流程、进行主体与宗派的综合分析、或需要基于卷零至卷十六规则系统化判断题记时使用
metadata:
  version: "2.4.0"
---

# 宗派判定主控中心 - 资源索引

## 计算引擎

引擎位于项目根目录 `scripts/sect_engine.py`（相对于本Skill为 `../scripts/sect_engine.py`）。下列命令从项目根目录执行。

**每次宗派判定时必须调用引擎**，禁止 AI 心算：
```bash
python scripts/sect_engine.py --input 铭文内容
```

## 十六卷规则索引

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
| 十六 | 三阶教 | volume-sixteen-sanjie.md | 写本版本待核验 |

### 通用参考

- cross-reference-matrix.md — 跨卷冲突处理
- output-format.md — 输出格式规范
- variant-characters.md — 异体字识别

先读取 references/weighting-rules-v2.3.md（内部版本2.4）和 references/term-evidence-review.md，再按卷读取历史规则。历史卷零及各卷中与新证据规范冲突的强制锁宗、概率化措辞，不再作为最终判定依据。复杂场景可读detail，但不得将旧表直接冒充新语境门槛。

## 2.4 文献与权重规则

- `references/weighting-rules-v2.3.md`：同一关键词按宗派语境分别赋权、跨卷重合度分级、过滤词和证据记录规则
- `references/classics-coverage-v2.3.md`：各卷经典覆盖核验、缺项和非T号文献边界
- `../assets/cbeta-catalog.json`：统一经录源；全部旧索引已从此源重建。未落实的题名见unresolved，不强配T号。
- `references/research-support.md`：21项研究文献、核验范围和选经依据。
- `references/term-evidence-review.md`：18条重点词条映射的出处／语境复核。
- `../assets/weight-reconstruction.json`：基础条目与短词派生、去重机制的逆向线索，不能当成已恢复的原始算法日志。

## 当前集成状态

- 卷零至卷十六规则（卷十六三阶教为补充体系）
- 计算引擎及数值词库保留历史配置；7,189个词条、7,512条映射。2.4新增文献复核和说明不等于全套语境条件已实现于计分器。
