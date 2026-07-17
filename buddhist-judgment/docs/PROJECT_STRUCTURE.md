# 四川地区佛教石窟铭文宗派判定系统 - 项目结构说明

## 项目根目录

```
./
├── SKILL.md                                    # 总控Skill（入口）
├── sichuan-buddhist-inscription-judgment-system.md  # 总提示词（必读）
├── AI_USAGE_GUIDE.md                           # AI使用指南
├── sect-preliminary-filter/                    # 前置过滤Skill
│   ├── SKILL.md
│   └── references/
├── sect-judgment-hub/                         # 宗派判定Skill
│   ├── SKILL.md
│   └── references/
├── cbeta-index-references/                     # CBETA经典索引
│   └── cbeta-classics-index.md
├── assets/                                    # 索引文件
│   ├── cbeta-t-number-index.md
│   ├── cbeta-keyword-index.md
│   └── cbeta-volume-query-path.md
├── scripts/                                   # Python脚本
│   ├── cbeta_query.py
│   ├── sutra_lookup.py
│   ├── cbeta_index_search.py
│   └── test_cbeta_scripts.py
└── *.skill                                    # 打包的Skill文件
```

## 文件说明

### 1. SKILL.md（总控入口）
- **位置**：项目根目录
- **作用**：总控Skill，系统入口
- **功能**：协调两个核心Skill的执行顺序
- **指示AI**：首先阅读 `sichuan-buddhist-inscription-judgment-system.md`

### 2. sichuan-buddhist-inscription-judgment-system.md（总提示词）
- **位置**：项目根目录
- **作用**：系统总说明文档
- **内容**：
  - 系统概述和适用范围
  - 完整执行流程（前置过滤→宗派判定）
  - 各卷判定规则和核心文件
  - CBETA经典索引使用说明
  - 使用示例和注意事项
  - 文件清单和快速参考卡

### 3. sect-preliminary-filter/（前置过滤Skill）
- **位置**：项目根目录下的独立目录
- **作用**：过滤无效题记，确认是否允许进入分析
- **关键文件**：
  - `SKILL.md`：前置过滤规则和流程
  - `references/`：详细规则和输出格式

### 4. sect-judgment-hub/（宗派判定Skill）
- **位置**：项目根目录下的独立目录
- **作用**：执行宗派判定，计算权重，输出结果
- **关键文件**：
  - `SKILL.md`：宗派判定规则和流程
  - `references/`：卷零总则和各卷规则

### 5. CBETA索引系统
- **cbeta-index-references/**：CBETA经典总索引
- **assets/**：T号索引、关键词索引、卷别映射
- **scripts/**：Python查询脚本

## 执行流程

### AI执行标准流程

```
1. 加载总控Skill
   load_skill: "buddhist-inscription-judgment-system"

2. 阅读总提示词（在当前目录）
   read_file: "sichuan-buddhist-inscription-judgment-system.md"

3. 第一步：前置过滤
   load_skill: "sect-preliminary-filter"

4. 判断结果
   - 拒绝 → 终止
   - 复核 → 等待
   - 允许 → 继续

5. 第二步：宗派判定
   load_skill: "sect-judgment-hub"

6. 经典查阅（必要时）
   使用CBETA索引系统

7. 输出结果
   标准化输出
```

## 关键路径

### 总控Skill路径
- **相对路径**：`SKILL.md`（从项目根目录）
- **绝对路径**：`./SKILL.md`

### 总提示词路径
- **相对路径**：`sichuan-buddhist-inscription-judgment-system.md`
- **绝对路径**：`./sichuan-buddhist-inscription-judgment-system.md`

### 核心Skill路径
- **前置过滤**：`sect-preliminary-filter/SKILL.md`
- **宗派判定**：`sect-judgment-hub/SKILL.md`

## 注意事项

### 文件查找
1. 所有路径都是相对于项目根目录 `./`
2. 总控Skill `SKILL.md` 在根目录
3. 总提示词 `sichuan-buddhist-inscription-judgment-system.md` 在根目录
4. 两个核心Skill都是独立的子目录

### 执行顺序
1. 必须先加载总控Skill
2. 必须先阅读总提示词
3. 必须先执行前置过滤
4. 前置过滤通过后才能执行宗派判定

### 路径引用
- 在Skill文件中使用相对路径
- 在Python脚本中使用绝对路径
- 在总提示词中使用相对路径

## 版本信息
- **系统版本**：v2.1
- **最后更新**：2025-04-17
- **维护者**：Cicsoncy
