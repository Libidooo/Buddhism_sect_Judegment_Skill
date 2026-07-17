# AI执行指南 - 四川地区佛教石窟铭文宗派判定系统

## 快速开始（AI必读）

### 第一步：确认当前目录
确保你在项目根目录：`./`

### 第二步：加载总控Skill
```bash
load_skill: "buddhist-inscription-judgment-system"
```

### 第三步：阅读总提示词
```bash
read_file: "sichuan-buddhist-inscription-judgment-system.md"
```

### 第四步：执行两步流程
1. **前置过滤**：加载 `sect-preliminary-filter`
2. **宗派判定**：如果过滤通过，加载 `sect-judgment-hub`

## 项目结构

### 根目录文件
```
./
├── SKILL.md                                    # 总控Skill（入口）
├── sichuan-buddhist-inscription-judgment-system.md  # 总提示词（必读）
├── AI_USAGE_GUIDE.md                           # 本文件
├── PROJECT_STRUCTURE.md                        # 项目结构说明
├── sect-preliminary-filter/                    # 前置过滤Skill（目录）
├── sect-judgment-hub/                         # 宗派判定Skill（目录）
├── cbeta-index-references/                     # CBETA索引（目录）
├── assets/                                    # 索引文件（目录）
└── scripts/                                   # Python脚本（目录）
```

## AI执行检查清单

在开始任何判定任务前，检查以下项目：

- [ ] 我是否在正确的目录（`./`）？
- [ ] 我是否已加载总控Skill（`SKILL.md`）？
- [ ] 我是否已阅读总提示词（`sichuan-buddhist-inscription-judgment-system.md`）？
- [ ] 我是否理解必须按"前置过滤→宗派判定"顺序执行？
- [ ] 我是否知道CBETA索引系统在步骤7使用？

## 关键路径（使用相对路径）

### 总控相关
- **总控Skill**：`SKILL.md`（根目录）
- **总提示词**：`sichuan-buddhist-inscription-judgment-system.md`（根目录）

### 核心Skill
- **前置过滤**：`sect-preliminary-filter/SKILL.md`
- **宗派判定**：`sect-judgment-hub/SKILL.md`

### CBETA索引
- **主索引**：`cbeta-index-references/cbeta-classics-index.md`
- **T号索引**：`assets/cbeta-t-number-index.md`
- **关键词索引**：`assets/cbeta-keyword-index.md`
- **卷别映射**：`assets/cbeta-volume-query-path.md`

## 执行流程图

```
收到用户请求
    ↓
【步骤1】加载总控Skill
  文件：SKILL.md
  命令：load_skill "buddhist-inscription-judgment-system"
    ↓
【步骤2】阅读总提示词
  文件：sichuan-buddhist-inscription-judgment-system.md
  命令：read_file "sichuan-buddhist-inscription-judgment-system.md"
    ↓
【步骤3】前置过滤
  加载：sect-preliminary-filter
  文件：sect-preliminary-filter/SKILL.md
  命令：load_skill "sect-preliminary-filter"
    ↓
    判断结果
    ├─ 拒绝 → 终止，返回拒绝原因
    ├─ 复核 → 标记，等待人工确认
    └─ 允许 → 继续下一步
          ↓
【步骤4】宗派判定
  加载：sect-judgment-hub
  文件：sect-judgment-hub/SKILL.md
  命令：load_skill "sect-judgment-hub"
    ↓
【步骤5】经典查阅（必要时）
  使用CBETA索引系统
  命令：python scripts/cbeta_query.py --t-number T0262
    ↓
【步骤6】输出结果
  标准化输出
```

## 常见命令参考

### 文件操作
```bash
# 读取总提示词
read_file: "sichuan-buddhist-inscription-judgment-system.md"

# 读取项目结构
read_file: "PROJECT_STRUCTURE.md"

# 读取前置过滤Skill
read_file: "sect-preliminary-filter/SKILL.md"

# 读取宗派判定Skill
read_file: "sect-judgment-hub/SKILL.md"
```

### CBETA查询
```bash
# 查询经典
python scripts/cbeta_query.py --t-number T0262

# 按卷别查找
python scripts/sutra_lookup.py --volume 卷二

# 关键词搜索
python scripts/cbeta_index_search.py --search "药师"

# 查看统计
python scripts/cbeta_index_search.py --stats

# 运行测试
python scripts/test_cbeta_scripts.py
```

## 常见问题与解决

### 问题1：找不到文件
**症状**：AI报告找不到某个文件
**解决方法**：
1. 确认当前目录：`pwd`（应该是 `./`）
2. 使用相对路径而非绝对路径
3. 检查文件名拼写是否正确
4. 参考本指南的"关键路径"部分

### 问题2：跳过前置过滤
**症状**：AI直接执行宗派判定
**解决方法**：
1. 明确指示AI必须先执行前置过滤
2. 检查总控Skill的SKILL.md是否正确
3. 确认AI已阅读总提示词

### 问题3：CBETA索引使用错误
**症状**：在错误的步骤使用CBETA索引
**解决方法**：
1. 明确CBETA索引仅在步骤7使用
2. 不要在前置过滤或卷零总则中使用
3. 仅在"经典原典查阅"必要时使用

## 测试验证

### 验证AI是否正确执行
```
测试命令：
load_skill: "buddhist-inscription-judgment-system"

AI应该能够回答：
1. 系统的核心流程是什么？
2. 为什么必须先进行前置过滤？
3. CBETA索引系统在什么步骤使用？
4. 总提示词文件的相对路径是什么？
5. 核心Skill的相对路径是什么？
```

### 验证文件路径
```bash
# 检查总控Skill
ls -la SKILL.md

# 检查总提示词
ls -la sichuan-buddhist-inscription-judgment-system.md

# 检查核心Skill
ls -la sect-preliminary-filter/SKILL.md
ls -la sect-judgment-hub/SKILL.md

# 检查CBETA索引
ls -la cbeta-index-references/cbeta-classics-index.md
```

## 系统版本信息
- **系统版本**：v2.1
- **最后更新**：2025-04-17
- **维护者**：Cicsoncy
- **项目结构**：见 PROJECT_STRUCTURE.md
