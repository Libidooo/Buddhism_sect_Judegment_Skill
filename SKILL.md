---
name: buddhist-inscription-judgment-system
description: 分析四川佛教题记的造像主体、信仰和宗派关联，结合历史规则引擎与可核文献；支持T号、经名、关键词和证据来源查询。
metadata:
  version: "2.4.0"
  query-dependencies: "Python 3.8+ standard library"
---
# 四川佛教题记文献证据与关联标注

## 任务和输出边界

分析题记原文、已有造像题材描述、年代和地点，分别标注造像主体、信仰／教学传统关联及不确定性。卷2、4、9、10为主体或信仰体系，不视为四个独立宗派。引用某经典、使用某词与历史人物的宗派组织身份是不同判断。

本版依据现存原典、研究论文和逆向结果更新解释规则与索引；没有重算数值词库。经典代表性、作者使用史、字串命中、语境支持与数值评分必须分别报告。论文能支持选本和解释范围，不能直接证明某词应设80分。

## 必要参考

- 判定前读取 [权重与语境规则](sect-judgment-hub/references/weighting-rules-v2.3.md)。
- 使用某卷时读取 [宗派主控](sect-judgment-hub/SKILL.md)及对应卷的历史规则，但有冲突时以2.4的证据规则和核验记录为准。
- 查选经与时代边界时读取 [经典覆盖说明](sect-judgment-hub/references/classics-coverage-v2.3.md)及 [研究论文依据](sect-judgment-hub/references/research-support.md)。
- 涉及普门、佛性、七宝池、地藏愿语、光佛名号等，读取 [重点词条复核](sect-judgment-hub/references/term-evidence-review.md)。

## 操作流程

1. 保存原输入字段，区分原刻文字、现代拟题和图像描述。前置过滤用于说明适用范围和残损情况，不从证据不足推出“历史上不属于某宗派”。
2. 调用既有计算引擎获得历史配置的匹配和得分，不由AI心算替代：
   `python3 scripts/sect_engine.py --input "题记原文" --subject "已有造像题材" --date "年代" --location "地点" --json`
3. 对关键命中查询 `python3 scripts/cbeta_query.py --keyword "词条" --exact`。查看source_raw、source_status、weight_basis、evidence_review和候选经号，不把缺失来源补造成已知来源。
4. 核对经典版本及题记年代。共享术语须有独立的引经、教观、仪轨或师承语境；不能让该术语自身循环证明语境。
5. 分开呈现“引擎原始得分”与“文献复核后的解释”。低信号、年代冲突或来源争议保留未决，不能仅因W≥80或某经题名出现就认定历史宗派身份。
6. 输出主体、信仰／学派关联、依据与反证、文献和论文、未决原因。文献条件的复核发生在AI／专家层，不能声称旧引擎已自动执行全部语境门槛。

## 经录和索引

统一经录为 `assets/cbeta-catalog.json`；全量查询数据为 `assets/cbeta-keyword-index-v2.3.json`。保留v2.3文件名以兼容既有入口，内部版本为2.4.0。

- 135条经录含正式经名、传统题署、选本用途、论文ID、历史使用状态与年代限制。
- 7,189个词条、7,512条映射及其原权重全部保留。18条重点映射有个别复核，其余不自动视为已审查。
- 4,651条当前映射附历史短词派生候选；候选不是恢复的原始生成日志。
- `assets/research-evidence.json`保存21项论文／研究资料及其实际阅读核验范围。
- `assets/weight-context-reviews.json`保存逐条语境复核；`assets/weight-reconstruction.json`保存逆向证据。
- 经名出处已更正但原source保留在source_raw。原句另有定位也不证明该经典专属某宗派。
- 三阶教核心写本、泛称及佚疏仍保留待核。新增目录项不等于已经全文提词或用于旧实验。

## 查询与维护

```bash
python3 scripts/cbeta_query.py --t-number 366
python3 scripts/sutra_lookup.py --name 摄大乘论
python3 scripts/sutra_lookup.py --volume 卷十一
python3 scripts/cbeta_index_search.py --search 佛性 --exact
python3 scripts/cbeta_query.py --t-number T0893A --check-online --timeout 8
python3 scripts/rebuild_cbeta_index.py
python3 scripts/rebuild_cbeta_index.py --check
python3 scripts/test_cbeta_scripts.py
```

在线检查仅在--check-online时发起，支持--proxy。入口失败时尝试CBETA官方XML，保留TLS校验并报告实际来源；HTML 200仅证明页面可达。详见 [检索说明](cbeta-index-references/CBETA_README.md)。

## 历史实验与新版本

数值词库和引擎保留原版本，0.8744等为旧实验报告值，不是本次文献规则更新后的评估结果。新增或改动数值、语境门槛或最终解释流程后须另做评价。不能把0.6短词派生假设或“三维评分相乘”写成已经完整恢复并验证的建库算法。
