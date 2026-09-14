# CBETA检索与重建

唯一经录源：assets/cbeta-catalog.json。完整来源索引：assets/cbeta-keyword-index-v2.3.json。旧路径的Markdown索引也由统一数据重新生成，不再保留错误T号表作为运行时回退。

运行 `python3 scripts/rebuild_cbeta_index.py` 可重建全部索引；`--check` 检查生成文件是否与源数据一致。该操作不修改 scripts/data/term_index.json 的关键词、卷号或权重。

查询示例：

- `python3 scripts/cbeta_query.py --t-number 366`
- `python3 scripts/sutra_lookup.py --name 阿弥陀经`
- `python3 scripts/cbeta_index_search.py --search 佛性 --exact`
- `python3 scripts/sutra_lookup.py --volume 卷十一`
- `python3 scripts/cbeta_query.py --t-number T0893A --check-online --timeout 8`

查询脚本仅使用Python标准库。默认离线查目录，只有--check-online触发网络；支持--proxy http://127.0.0.1:端口。代理端口由用户环境确定，代码不硬编码本机端口。TLS证书正常校验；网络错误不会伪装成检索成功。CBETA入口失败时尝试CBETA官方XML仓库，返回实际使用的来源。HTML返回200仅表示页面可达，不能声称已读取经文。

来源状态：missing_source为无出处，unresolved_source为出处未解析，title_catalog_match为书名匹配经录，explicit_id_catalog_match为显式编号匹配，ambiguous_edition为多版本候选。以上匹配均不代表原句已验证，不能由词语所属卷自动补造经典出处。

同一个词不同卷的映射逐条保存。修复检索不会改动既有分类得分，但若人工采用新增文献重新标注或赋权，则形成新的实验版本。
