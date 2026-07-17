# 四川地区佛教石窟铭文宗派判定系统 - 总提示词

## 系统概述

本系统由两个核心Skill组成，用于系统化分析四川地区佛教石窟铭文内容并判定主体与宗派：

1. **sect-preliminary-filter**（前置过滤Skill）
2. **sect-judgment-hub**（宗派判定主控Skill）

**适用范围**：四川地区佛教石窟铭文（石刻题记、造像记、碑刻等）

---

## 执行流程（必须严格遵守）

### 步骤一：前置过滤（sect-preliminary-filter）

**何时使用**：在执行宗派判定之前，必须先使用 `sect-preliminary-filter` Skill。

**Skill功能**：
- 过滤无效题记（无关内容、现代添加、伪造铭文等）
- 识别非佛教内容
- 检测残损过度的题记
- 标记允许进入分析的条目

**输出结果**：
- 条目状态：允许进入分析 / 拒绝进入分析 / 需人工复核
- 拒绝原因说明（如：现代内容、无关主题、残损严重等）

**关键规则**：
- 任何条目必须通过前置过滤，才能进入宗派判定流程
- 未通过过滤的条目，不得进行宗派判定
- 前置过滤的输出状态具有绝对优先权

---

### 步骤二：宗派判定（sect-judgment-hub）

**何时使用**：仅当前置过滤结果为"允许进入分析"时使用。

**Skill功能**：
- 卷零总则应用：理解全局框架、互斥矩阵、权重体系
- 卷一至卷十五完整判定：经文词干、观音体系、净土体系、药师体系、密教体系、华严体系、禅宗体系、区域体系、地藏体系、弥勒体系、三论宗、唯识宗、天台宗、成实宗、律宗
- 证据权重计算：A层决定因、B层强因缘、C层中因缘、D层弱因缘
- 卷间交叉逻辑处理：互斥矩阵、主体优先级、冲突消解
- 输出标准化结果：宗派判定、信任得分、证据链、备注

**核心规则文件**：
- 卷零总则：`references/volume-zero-general-rules.md`
- 卷一经文词干：`references/volume-one-sutra-stems.md`
- 卷二观音体系：`references/volume-two-guanyin-system.md`（核心规则）+ `detail/volume-two-guanyin-system-full.md`（完整版）
- 卷三净土体系：`references/volume-three-pure-land.md` + `detail/volume-three-pure-land-full.md`
- 卷四药师体系：`references/volume-four-medicine-buddha.md` + `detail/volume-four-medicine-buddha-full.md`
- 卷五密教体系：`references/volume-five-esoteric.md` + `detail/volume-five-esoteric-full.md`
- 卷六华严体系：`references/volume-six-huayan.md` + `detail/volume-six-huayan-full.md`
- 卷七禅宗体系：`references/volume-seven-zen.md` + `detail/volume-seven-zen-full.md`
- 卷八区域体系：`references/volume-eight-regional.md` + `detail/volume-eight-regional-full.md`
- 卷九地藏体系：`references/volume-nine-kshitigarbha.md` + `detail/volume-nine-kshitigarbha-full.md`
- 卷十弥勒体系：`references/volume-ten-maitreya.md` + `detail/volume-ten-maitreya-full.md`
- 卷十一三论宗：`references/volume-eleven-sanlun.md` + `detail/volume-eleven-sanlun-full.md`
- 卷十二唯识宗：`references/volume-twelve-yogacara.md` + `detail/volume-twelve-yogacara-full.md`
- 卷十三天台宗：`references/volume-thirteen-tiantai.md` + `detail/volume-thirteen-tiantai-full.md`
- 卷十四成实宗：`references/volume-fourteen-satyasiddhi.md` + `detail/volume-fourteen-satyasiddhi-full.md`
- 卷十五律宗：`references/volume-fifteen-vinaya.md` + `detail/volume-fifteen-vinaya-full.md`

**辅助规则文件**：
- 跨卷校对矩阵：`references/cross-reference-matrix.md`（包含延寿/宝珠/施食跨卷校对、卷11-15冲突消解规则）
- 异体字集录：`references/variant-characters.md`（佛菩萨名号、宗派术语、地域性异体字、OCR易错字）
- 交叉引用矩阵：`references/cross-reference-matrix.md`
- 输出格式规范：`references/output-format.md`

**分层读取策略**：
- 默认读取 `references/` 下的核心规则文件（覆盖90%场景）
- 复杂场景按需读取 `references/detail/` 下的完整版文件（100%覆盖）

---

## 判定流程（完整版）

### 第一阶段：前置过滤

1. 加载 `sect-preliminary-filter` Skill
2. 按过滤规则检查题记：
   - 是否为非宗教内容
   - 是否为现代添加或伪造
   - 是否残损度过高
   - 是否符合最低可识别标准
3. 输出过滤结果：
   - ✓ 允许进入分析 → 进入第二阶段
   - ✗ 拒绝进入分析 → 终止流程，返回拒绝原因
   - ? 需人工复核 → 标记并等待人工确认

### 第二阶段：宗派判定

1. 加载 `sect-judgment-hub` Skill
2. 读取卷零总则，理解全局框架
3. 识别主体（按优先序）：
   - 药师佛（卷四） > 弥勒菩萨（卷十） > 地藏菩萨（卷九） > 观音菩萨（卷二） > 阿弥陀佛（卷三）
4. 逐卷执行判定（卷一→卷十五）：
   - 计算各卷证据权重（W）
   - 计算综合得分（S）
   - 应用Gate进入门槛检查
5. 处理卷间交叉逻辑：
   - 应用互斥矩阵检查冲突
   - 依据跨卷校对矩阵消解歧义（延寿/宝珠/施食）
   - 应用主体优先级规则
6. 异体字识别与归一化：
   - 使用 `variant-characters.md` 识别异体字
   - OCR易错字校读
   - 词形归一化（不影响宗派权重）
7. 经典原典查阅（必要时）：
   - **识别经典线索**：从题记中识别经典名称、T号、关键词
   - **查询索引系统**：
     - 使用 `cbeta-classics-index.md` 查找经典T号和在线链接
     - 使用 `cbeta-t-number-index.md` 进行T号快速查找
     - 使用 `cbeta-keyword-index.md` 进行关键词检索
     - 使用 `cbeta-volume-query-path.md` 按卷别查找经典
   - **调用脚本工具**：
     - `scripts/cbeta_query.py --t-number T0262`：按T号查询
     - `scripts/sutra_lookup.py --volume 卷二`：按卷别查找
     - `scripts/cbeta_index_search.py --search "药师"`：关键词搜索
     - `scripts/cbeta_index_search.py --stats`：获取统计信息
   - **访问CBETA在线数据库**：获取原典内容进行验证
   - **验证词条出处的准确性**：确认题记内容与原典一致
   - **辅助宗派判定**：结合经典内容进行更准确的宗派判定
8. 生成标准化输出：
   - 判定宗派（主宗派.权重分；副宗派.权重分）
   - 判定权重分对应可信度（W≥90极高 / 80≤W<90很高 / 70≤W<80较高 / 60≤W<70中等 / 50≤W<60偏低 / W<50很低）
   - 线索（主要证据；次要证据）
   - 备注（混合情况、规则跳转、经文原文摘录）
   - RG标记（需人工复核时标注）

---

## CBETA经典索引使用说明

### 索引位置
- **主索引**：`projects/cbeta-index-references/cbeta-classics-index.md`
- **T号索引**：`projects/assets/cbeta-t-number-index.md`
- **关键词索引**：`projects/assets/cbeta-keyword-index.md`
- **卷别映射**：`projects/assets/cbeta-volume-query-path.md`

### 脚本工具
- **CBETA查询**：`projects/scripts/cbeta_query.py`
- **经典查找**：`projects/scripts/sutra_lookup.py`
- **索引搜索**：`projects/scripts/cbeta_index_search.py`
- **综合测试**：`projects/scripts/test_cbeta_scripts.py`

### 使用场景
1. **词条出处验证**：当需要验证题记中术语的经典出处时
2. **原文查阅**：当需要获取经典完整原文时
3. **经文对比**：当需要对比不同版本的经文时
4. **卷别定位**：当需要快速定位某卷的经典时
5. **关键词检索**：当需要查找包含特定术语的所有经典时

### 查询方式

#### 方式一：手动查询
1. 打开 `cbeta-classics-index.md`
2. 在"按卷分类索引"中找到对应卷
3. 查找经典名和T号
4. 点击CBETA在线链接访问原文

#### 方式二：T号查询
```bash
# 按T号查询经典信息
python scripts/cbeta_query.py --t-number T0450

# 查询并检查在线资源
python scripts/cbeta_query.py --t-number T0450 --check-online

# 按卷别过滤
python scripts/cbeta_query.py --t-number T0262 --volume 卷二
```

#### 方式三：经名查询
```bash
# 按经名检索
python scripts/cbeta_query.py --sutra-name "药师琉璃光如来本愿功德经"

# 模糊匹配
python scripts/sutra_lookup.py --name "药师经"
```

#### 方式四：关键词检索
```bash
# 按关键词检索
python scripts/cbeta_query.py --keyword "延寿无量愿"

# 全文搜索
python scripts/cbeta_index_search.py --search "药师"

# 按卷别搜索
python scripts/cbeta_index_search.py --search "净土" --volume 卷三

# 精确匹配
python scripts/cbeta_index_search.py --search "T0262" --exact
```

#### 方式五：卷别查询
```bash
# 查找某卷的所有经典
python scripts/sutra_lookup.py --volume 卷二

# 获取卷别摘要统计
python scripts/sutra_lookup.py --summary

# 查看系统统计信息
python scripts/cbeta_index_search.py --stats
```

### 索引内容
- **T号快速索引**：60部经典的T号、经名、所属卷、类型、核心度、在线链接
- **关键词索引**：118个关键词，按拼音首字母组织（A-Z）
- **卷别映射**：按卷零至卷十五组织的经典列表和路径映射
- **在线链接**：直接访问CBETA数据库

### 数据统计
- **经典数量**：60部
- **关键词数量**：118个
- **覆盖卷别**：卷一至卷十五
- **核心经典**：38部
- **论典**：7部
- **律典**：9部

### 输出格式
- **JSON格式**：便于程序化处理（默认）
- **文本格式**：便于人类阅读（使用 --format text 参数）

### 注意事项
- CBETA在线链接可能需要网络访问
- 请遵守CBETA的版权和使用规定
- 索引仅包含系统明确引用的经典
- 所有脚本已通过测试，通过率100%
- 使用 `test_cbeta_scripts.py` 可进行系统测试

---

## 关键规则摘要

### sect-preliminary-filter 核心规则

**过滤条件**（满足任一即拒绝进入分析）：
- 现代添加内容（如近现代题刻、人为添加的说明文字）
- 非宗教内容（如世俗生活记录、商业广告等）
- 伪造铭文（风格不符、字迹矛盾、内容混乱）
- 残损度过高（关键信息缺失50%以上）
- 无法识别的符号或文字（OCR识别率低于30%）

**通过条件**：
- 包含明确的佛教元素（佛菩萨名号、经文片段、造像题材）
- 具备可识别的文字内容（至少30%可读）
- 符合石刻题记的基本格式特征

---

### sect-judgment-hub 核心规则

**卷零总则**（母规则）：
- 互斥矩阵：⛔绝对互斥、⚠允许并存但需主体判定、—自身
- 权重体系：A层决定因(W=80-85)、B层强因缘(W=60-79)、C层中因缘(W=40-59)、D层弱因缘(W=20-39)
- 主体优先级：药师 > 弥勒 > 地藏 > 观音 > 阿弥陀
- 密教绝对优先：W≥60的密教词→必入卷五

**各卷定位**：
- 卷一：通用经文词干（不单独判宗派）
- 卷二：观音体系（主体卷，细分天台/净土/密）
- 卷三：净土体系（宗派卷，阿弥陀主体）
- 卷四：药师体系（宗派卷，药师主体）
- 卷五：密教体系（宗派卷，绝对优先权）
- 卷六：华严体系（宗派卷，普贤/毘卢主体）
- 卷七：禅宗体系（思想卷，语录类判定）
- 卷八：区域体系（辅助卷，四川史料）
- 卷九：地藏体系（主体卷，非宗派）
- 卷十：弥勒体系（主体卷，非宗派）
- 卷十一：三论宗（思想卷，否定结构判定）
- 卷十二：唯识宗（思想卷，八识体系判定）
- 卷十三：天台宗（思想卷，法华经专用）
- 卷十四：成实宗（思想卷，论典硬锚点）
- 卷十五：律宗（制度卷，律典/羯磨/戒本）

**跨卷校对关键点**：
- 延寿：卷四药师（延寿+药师大愿） vs 卷九地藏（亡灵拔苦→回向现世）
- 宝珠：卷二观音（如意宝珠） vs 卷三净土（大势至宝光珠） vs 卷四药师（药珠） vs 卷九地藏（明珠+锡杖）
- 施食：卷九地藏（普施饿鬼） vs 卷三净土（超度往生） vs 卷五密教（施食法+梵字）

**卷11-15冲突消解**：
- 卷12唯识优先：出现八识/阿赖耶→卷11/13/14退为背景
- 卷11三论消解：仅出现"空/有/假名"→不入判定，需硬锚点
- 卷13天台消解：卷二天台系观音已成立→卷十三仅做背景引证
- 卷14成实消解：未出现成实论硬锚点→不得成立
- 卷15律宗消解：未出现律典/羯磨/戒本硬锚点→不得成立

**异体字规则**：
- 工具性质，只用于题记识别，不得影响宗派权重
- 必须溯源，不能臆造
- OCR易错字：毘、薩、觀、藥、釋、識、顗

---

## 四川地区特色说明

### 地域特征
本系统专门针对四川地区佛教石窟铭文设计，具有以下地域特色：

1. **地名异体字**：资州、安嶽、遂州、綿州、劍州等地名常见异体写法
2. **匠人体系**：四川石刻匠人群落（安岳、大足、简州等）具有特定风格
3. **异体字密集**：四川石刻中异体字出现频率极高，需重点识别
4. **时代特征**：四川石窟从隋唐至宋金均有分布，需结合年号体系判断

### 区域体系（卷八）重要性
- 卷八专门收录四川地区地名、匠人、年号、异体字体系
- 为宗派判定提供重要的地域背景信息
- 例如："资州 + 大悲观音" → 仍判为卷二观音，但资州提供地域佐证

---

## 使用示例

### 示例1：标准流程（含CBETA经典查阅）

**输入**：
"弟子某甲，为亡父造药师如来像一躯，愿亡父往生净土"

**执行流程**：
1. 加载 `sect-preliminary-filter` → 检查通过 → "允许进入分析"
2. 加载 `sect-judgment-hub`
3. 识别主体：药师如来（卷四）
4. 逐卷判定：
   - 卷四药师：药师如来(W=85) + 药师像(W=75) → S=160
   - 卷三净土：往生净土(W=60) → S=60
5. 跨卷校对：延寿未出现，净土为辅助愿望
6. 经典原典查阅：
   - 查询药师经典：`python scripts/cbeta_query.py --t-number T0450`
   - 访问CBETA：https://cbetaonline.dila.edu.tw/T0450
   - 验证"药师如来"和"往生"的经典依据
7. 输出结果：
   - 判定宗派：主：药师体系·160；副：净土体系·60
   - 判定概论得分：160 → 很高（约0.90）
   - 线索：主要证据：卷四·A层决定因：药师如来；次要证据：造像题材
   - 备注：与净土并存：药师为主，净土为辅愿

### 示例2：过滤拒绝

**输入**：
"今日天气晴朗，去公园散步"

**执行流程**：
1. 加载 `sect-preliminary-filter` → 检查不通过 → "拒绝进入分析"
2. 拒绝原因：非宗教内容（无佛教元素）

**输出**：
- 条目状态：拒绝进入分析
- 拒绝原因：非宗教内容，无佛教元素

### 示例3：四川地域特征（含CBETA经典查阅）

**输入**：
"安嶽工匠文氏造，药师琉璃光如来，愿延寿无量"

**执行流程**：
1. 加载 `sect-preliminary-filter` → 检查通过 → "允许进入分析"
2. 加载 `sect-judgment-hub`
3. 异体字识别：安嶽→安岳（四川地名异体）
4. 识别主体：药师琉璃光如来（卷四）
5. 逐卷判定：
   - 卷四药师：药师琉璃光如来(W=85) + 延寿无量(W=80) → S=165
   - 卷八区域：安嶽(W=0) + 工匠文氏(W=0) → 仅提供地域佐证
6. 经典原典查阅：
   - 查询药师经典：`python scripts/sutra_lookup.py --name "药师琉璃光如来本愿功德经"`
   - 查询关键词：`python scripts/cbeta_query.py --keyword "延寿"`
   - 验证"延寿无量"在药师经中的依据
   - 访问CBETA：https://cbetaonline.dila.edu.tw/T0450
7. 输出结果：
   - 判定宗派：主：药师体系·165
   - 判定概论得分：165 → 很高（约0.90）
   - 线索：主要证据：卷四·A层决定因：药师琉璃光如来；次要证据：安嶽工匠文氏
   - 备注：四川地域特征明显，安嶽工匠文氏提供地域佐证；经典依据：药师琉璃光如来本愿功德经（T0450）第12大愿

### 示例4：CBETA经典索引使用

**场景**：题记中出现"观世音菩萨普门示现救苦救难"

**执行流程**：
1. 加载 `sect-judgment-hub`
2. 识别关键词：观世音菩萨、普门示现、救苦救难
3. 使用CBETA索引系统：
   - 按关键词查询：`python scripts/cbeta_query.py --keyword 观世音`
   - 按T号查询：`python scripts/cbeta_query.py --t-number T0262`
   - 按卷别查找：`python scripts/sutra_lookup.py --volume 卷二`
4. 查询结果：
   - 妙法莲华经（T0262）- 普门品
   - 在线链接：https://cbetaonline.dila.edu.tw/T0262
5. 访问CBETA查阅普门品内容
6. 结合经典内容判定为卷二观音体系（天台系）

---

## 注意事项

1. **前置过滤绝对优先**：任何条目必须先通过前置过滤，未通过者不得进入宗派判定。

2. **主体判定优先**：五大主体（药师/弥勒/地藏/观音/阿弥陀）一旦判定，不得跨卷判断宗派。

3. **密教绝对优先**：出现W≥60的密教词（种子字/手印/曼荼罗/大日如来/明王）→必入卷五，其他卷全部靠后。

4. **异体字工具化**：异体字仅用于题记识别和OCR校读，不得影响宗派权重。

5. **分层读取策略**：默认使用核心规则（references/），复杂场景再读取完整版（references/detail/）。

6. **输出透明性**：必须输出全部W条目、主要/次要分类、S结果与等级，保证可复查性。

7. **人工复核标记**：题记缺损严重、关键信息缺失、超出规则体系时，必须标注RG（需人工复核）。

8. **四川地域特色**：重视卷八区域体系的地域信息，正确识别四川地名异体字。

---

## 文件清单

### sect-preliminary-filter
- SKILL.md：前置过滤规则与流程
- references/preliminary-rules.md：过滤规则详情
- references/filter-criteria.md：过滤标准

### sect-judgment-hub
- SKILL.md：宗派判定主控中心
- references/volume-zero-general-rules.md：卷零总则
- references/volume-one-sutra-stems.md：卷一经文词干
- references/volume-two-guanyin-system.md：卷二观音体系（核心）
- references/detail/volume-two-guanyin-system-full.md：卷二观音体系（完整）
- references/volume-three-pure-land.md：卷三净土体系（核心）
- references/detail/volume-three-pure-land-full.md：卷三净土体系（完整）
- references/volume-four-medicine-buddha.md：卷四药师体系（核心）
- references/detail/volume-four-medicine-buddha-full.md：卷四药师体系（完整）
- references/volume-five-esoteric.md：卷五密教体系（核心）
- references/detail/volume-five-esoteric-full.md：卷五密教体系（完整）
- references/volume-six-huayan.md：卷六华严体系（核心）
- references/detail/volume-six-huayan-full.md：卷六华严体系（完整）
- references/volume-seven-zen.md：卷七禅宗体系（核心）
- references/detail/volume-seven-zen-full.md：卷七禅宗体系（完整）
- references/volume-eight-regional.md：卷八区域体系（核心）
- references/detail/volume-eight-regional-full.md：卷八区域体系（完整）
- references/volume-nine-kshitigarbha.md：卷九地藏体系（核心）
- references/detail/volume-nine-kshitigarbha-full.md：卷九地藏体系（完整）
- references/volume-ten-maitreya.md：卷十弥勒体系（核心）
- references/detail/volume-ten-maitreya-full.md：卷十弥勒体系（完整）
- references/volume-eleven-sanlun.md：卷十一三论宗（核心）
- references/detail/volume-eleven-sanlun-full.md：卷十一三论宗（完整）
- references/volume-twelve-yogacara.md：卷十二唯识宗（核心）
- references/detail/volume-twelve-yogacara-full.md：卷十二唯识宗（完整）
- references/volume-thirteen-tiantai.md：卷十三天台宗（核心）
- references/detail/volume-thirteen-tiantai-full.md：卷十三天台宗（完整）
- references/volume-fourteen-satyasiddhi.md：卷十四成实宗（核心）
- references/detail/volume-fourteen-satyasiddhi-full.md：卷十四成实宗（完整）
- references/volume-fifteen-vinaya.md：卷十五律宗（核心）
- references/detail/volume-fifteen-vinaya-full.md：卷十五律宗（完整）
- references/cross-reference-matrix.md：跨卷校对矩阵
- references/variant-characters.md：异体字集录
- references/output-format.md：输出格式规范

**CBETA经典索引**（projects/cbeta-index-references/）：
- cbeta-classics-index.md：CBETA经典总索引（T号快速索引、按卷分类索引）
- 包含60部经典的CBETA编号、分类和在线阅读链接

**索引文件**（projects/assets/）：
- cbeta-t-number-index.md：T号快速索引对照表（9.2KB，60部经典）
- cbeta-keyword-index.md：关键词索引表（15KB，118个关键词）
- cbeta-volume-query-path.md：卷别查询路径映射（15KB，15卷完整映射）

**脚本工具**（projects/scripts/）：
- cbeta_query.py：CBETA查询脚本（9.7KB，按T号/经名/关键词查询）
- sutra_lookup.py：经文检索脚本（14KB，按卷别/T号/经名/关键词查找）
- cbeta_index_search.py：索引搜索脚本（16KB，全文搜索/统计信息）
- test_cbeta_scripts.py：综合测试脚本（自动测试所有功能，13项测试，100%通过）

**文档文件**（projects/）：
- CBETA_README.md：CBETA经典索引系统使用说明（7.7KB）
- cbeta_implementation_report.md：CBETA系统实施报告

---

## 快速参考卡

### 过滤检查清单
- [ ] 是否包含佛教元素？
- [ ] 是否为现代添加内容？
- [ ] 是否残损度过高？
- [ ] 是否为伪造铭文？
- [ ] OCR识别率是否≥30%？

### 宗派判定检查清单
- [ ] 前置过滤是否通过？
- [ ] 主体是否已识别（药师/弥勒/地藏/观音/阿弥陀）？
- [ ] 是否出现密教强因（W≥60）？
- [ ] 各卷Gate是否满足？
- [ ] 跨卷冲突是否已消解？
- [ ] 异体字是否已归一化？
- [ ] 四川地域信息是否已识别？
- [ ] 经典出处是否已验证（必要时）？
- [ ] CBETA索引查询是否正确（必要时）？
- [ ] 输出是否符合格式规范？

### 跨卷校对快速查询
| 关键词 | 主要归属 | 次要归属 | 判定规则 |
|--------|----------|----------|----------|
| 延寿 | 卷四药师 | 卷九地藏 | 药师+延寿→卷四；地藏+亡灵+荐拔+延寿→卷九 |
| 宝珠 | 卷二观音 | 卷三/四/九 | 宝珠+观音→卷二；宝珠+锡杖→卷九 |
| 施食 | 卷九地藏 | 卷三净土 | 地藏+施食→卷九；净土+施食→卷三 |

### 四川地名异体字速查
| 标准字 | 异体字 | 备注 |
|--------|--------|------|
| 安岳 | 安嶽 | 四川高频 |
| 资州 | 資洲 | 治所今资中 |
| 遂州 | 遂州 | 今遂宁 |
| 绵州 | 綿州 | 今绵阳 |
| 剑州 | 劍州 | 今剑阁 |

### CBETA经典索引速查

**按卷别查找经典**：
```bash
python scripts/sutra_lookup.py --volume 卷二
```

**按T号查询经典**：
```bash
python scripts/cbeta_query.py --t-number T0262
```

**按关键词检索**：
```bash
python scripts/cbeta_index_search.py --search "药师"
```

**查看系统统计**：
```bash
python scripts/cbeta_index_search.py --stats
```

**核心经典速查**：
| 卷别 | 核心经典 | T号 | 查询命令 |
|------|----------|-----|----------|
| 卷一 | 金刚经 | T0235 | `python scripts/cbeta_query.py --t-number T0235` |
| 卷二 | 妙法莲华经 | T0262 | `python scripts/cbeta_query.py --t-number T0262` |
| 卷三 | 佛说无量寿经 | T0360 | `python scripts/cbeta_query.py --t-number T0360` |
| 卷四 | 药师琉璃光如来本愿功德经 | T0450 | `python scripts/cbeta_query.py --t-number T0450` |
| 卷五 | 大日经 | T0848 | `python scripts/cbeta_query.py --t-number T0848` |
| 卷六 | 大方广佛华严经 | T0279 | `python scripts/cbeta_query.py --t-number T0279` |
| 卷七 | 六祖壇經 | T0334 | `python scripts/cbeta_query.py --t-number T0334` |
| 卷九 | 地藏菩萨本愿经 | T0412 | `python scripts/cbeta_query.py --t-number T0412` |
| 卷十 | 弥勒上生经 | T0453 | `python scripts/cbeta_query.py --t-number T0453` |
| 卷十五 | 四分律 | T1428 | `python scripts/cbeta_query.py --t-number T1428` |

**CBETA在线访问**：
- 基础链接：https://cbetaonline.dila.edu.tw/
- 经典链接：https://cbetaonline.dila.edu.tw/[T号]
- 示例：https://cbetaonline.dila.edu.tw/T0262（妙法莲华经）

---

**系统名称**：四川地区佛教石窟铭文宗派判定Skill
**版本**：v2.1
**最后更新**：2025-04-17
**维护者**：Cicsoncy
**更新内容**：
- 新增CBETA经典索引系统
- 新增4个索引文件（52.2KB）
- 新增4个Python脚本（~40KB）
- 新增CBETA使用说明文档
- 完善15卷经典索引（60部经典，118个关键词）
- 所有测试通过（13项测试，100%通过率）
