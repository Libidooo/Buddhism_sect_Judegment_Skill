# CBETA经典索引系统使用说明

## 系统概述

CBETA经典索引系统是为四川地区佛教石窟铭文宗派判定系统设计的经典查询工具，支持通过T号、经名、卷别、关键词等多种方式快速查找CBETA在线数据库中的佛教经典。

## 目录结构

```
./
├── assets/                              # 索引文件目录
│   ├── cbeta-t-number-index.md          # T号快速索引表
│   ├── cbeta-keyword-index.md           # 关键词索引表
│   └── cbeta-volume-query-path.md       # 卷别查询路径映射
├── scripts/                             # Python脚本目录
│   ├── cbeta_query.py                   # CBETA API查询脚本
│   ├── sutra_lookup.py                  # 经典查找脚本
│   ├── cbeta_index_search.py            # 索引搜索脚本
│   └── test_cbeta_scripts.py            # 综合测试脚本
└── cbeta-index-references/              # 完整索引目录
    └── cbeta-classics-index.md          # CBETA经典索引总表
```

## 脚本功能说明

### 1. cbeta_query.py - CBETA API查询脚本

**功能**：
- 支持通过T号查询经典信息
- 支持通过经名查询经典信息
- 支持通过关键词查询经典信息
- 支持按卷别过滤结果
- 支持检查CBETA在线资源是否可访问

**使用示例**：
```bash
# 按T号查询
python scripts/cbeta_query.py --t-number T0262

# 按经名查询
python scripts/cbeta_query.py --sutra-name 金刚经

# 按关键词查询
python scripts/cbeta_query.py --keyword 观世音

# 按卷别过滤
python scripts/cbeta_query.py --keyword 佛 --volume 卷三

# 检查在线资源
python scripts/cbeta_query.py --t-number T0262 --check-online

# 文本格式输出
python scripts/cbeta_query.py --t-number T0262 --format text
```

### 2. sutra_lookup.py - 经典查找脚本

**功能**：
- 支持按卷别查找经典
- 支持按T号快速查找
- 支持按经名查找
- 支持按关键词查找
- 支持获取卷别摘要统计

**使用示例**：
```bash
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

# 文本格式输出
python scripts/sutra_lookup.py --volume 卷二 --format text
```

### 3. cbeta_index_search.py - 索引搜索脚本

**功能**：
- 支持在所有索引文件中进行全文搜索
- 支持按T号、经名、卷别、关键词多维度搜索
- 支持模糊匹配和精确匹配
- 支持获取索引统计信息

**使用示例**：
```bash
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

# 文本格式输出
python scripts/cbeta_index_search.py --search "药师" --format text
```

### 4. test_cbeta_scripts.py - 综合测试脚本

**功能**：
- 自动测试所有CBETA相关脚本
- 验证索引文件是否正确加载
- 测试各种查询功能
- 生成测试报告

**使用示例**：
```bash
# 运行综合测试
python scripts/test_cbeta_scripts.py
```

## 索引文件说明

### 1. cbeta-t-number-index.md

**内容**：
- T号快速索引对照表
- 包含T号、经名、卷别、类型、核心度、快速链接
- 按T号、卷别、经名三个维度组织

**使用场景**：
- 已知T号，快速获取经典信息
- 已知卷别，查看该卷的所有经典
- 已知经名，查找对应的T号和链接

### 2. cbeta-keyword-index.md

**内容**：
- 关键词索引表
- 按拼音首字母组织（A-Z）
- 包含关键词、经典、T号、卷别、位置

**使用场景**：
- 已知关键词，查找相关经典
- 了解特定概念在哪些经典中出现
- 快速定位术语的具体位置

### 3. cbeta-volume-query-path.md

**内容**：
- 按卷别查询路径映射
- 每卷的经典清单
- 卷别到索引文件的路径映射
- 查询示例

**使用场景**：
- 按卷别系统化查询
- 了解每个卷的经典分布
- 快速定位卷别相关的资源

## 在宗派判定流程中的使用

### 步骤7：经典原典查阅

在四川地区佛教石窟铭文宗派判定系统中，CBETA经典索引系统用于第7步"经典原典查阅"：

1. **识别经典线索**：从题记中识别出经典名称、T号或关键词
2. **查询索引系统**：使用相应的脚本查询CBETA索引
3. **获取在线链接**：获取CBETA在线数据库的直接链接
4. **查阅原典内容**：访问CBETA在线数据库查阅完整经典
5. **辅助宗派判定**：结合经典内容进行宗派判定

### 使用流程示例

**场景**：题记中出现"观世音菩萨"字样

```bash
# 步骤1：查询观世音相关经典
python scripts/cbeta_query.py --keyword 观世音

# 输出示例：
# {
#   "status": "success",
#   "keyword": "观世音",
#   "results": [
#     {
#       "sutra": "妙法莲华经",
#       "t_number": "T0262",
#       "volume": "卷一、卷二",
#       "location": "普门品",
#       "cbeta_url": "https://cbetaonline.dila.edu.tw/T0262"
#     }
#   ]
# }

# 步骤2：根据T号访问CBETA在线数据库
# 访问：https://cbetaonline.dila.edu.tw/T0262

# 步骤3：查阅普门品内容，辅助判定是否为天台宗
```

## 数据统计

- **经典数量**：60部
- **关键词数量**：118个
- **覆盖卷别**：卷一至卷十五（卷八为融合体系）
- **核心经典**：38部
- **论典**：7部
- **律典**：9部

## 常见问题

### Q1: 如何查找某卷的所有经典？
```bash
python scripts/sutra_lookup.py --volume 卷二
```

### Q2: 如何根据经名查找T号？
```bash
python scripts/cbeta_query.py --sutra-name "经名"
```

### Q3: 如何查找包含特定关键词的所有经典？
```bash
python scripts/cbeta_index_search.py --search "关键词"
```

### Q4: 如何获取系统统计信息？
```bash
python scripts/cbeta_index_search.py --stats
```

### Q5: T号格式是什么？
T号格式为"T"后跟4位数字，例如：T0262、T0235、T0360

## 技术特性

- **纯Python实现**：无需额外依赖，开箱即用
- **JSON格式输出**：便于程序化处理
- **文本格式支持**：便于人类阅读
- **模糊匹配**：支持部分匹配和模糊搜索
- **多维度查询**：支持T号、经名、卷别、关键词等多种查询方式
- **在线链接**：直接提供CBETA在线数据库访问链接
- **错误处理**：完善的错误处理和状态返回

## 维护说明

**更新日期**：2025-04-17
**数据来源**：CBETA在线数据库
**维护者**：四川地区佛教石窟铭文宗派判定系统

**索引更新**：
- 当需要添加新经典时，更新 `cbeta-t-number-index.md`
- 当需要添加新关键词时，更新 `cbeta-keyword-index.md`
- 当卷别规则变更时，更新 `cbeta-volume-query-path.md`

## 测试状态

所有脚本已通过综合测试，通过率100%：
- ✓ T号查询
- ✓ 经名查询
- ✓ 关键词查询
- ✓ 按卷别查找
- ✓ 按T号查找
- ✓ 按经名查找
- ✓ 按关键词查找
- ✓ 全文搜索
- ✓ 按卷别搜索
- ✓ 精确匹配
- ✓ 统计信息
- ✓ 索引文件存在性
- ✓ 脚本文件存在性

## 联系与支持

如有问题或建议，请联系四川地区佛教石窟铭文宗派判定系统维护团队。
