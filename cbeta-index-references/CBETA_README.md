# CBETA检索与重建

当前版本2.4.0：135条经录、21项研究依据、18条重点映射复核及4,651条历史短词派生候选。v2.3命名路径保留兼容，所有生成文件的内部版本统一为2.4.0。

查询关键词时，evidence_review显示语境限制、论文ID和原典字串定位；weight_basis显示历史分值及派生候选。它们不自动重算引擎得分。查询经号时，selection_uses、chronology_status、chronology_note显示选本用途与年代争议。

唯一经录源：assets/cbeta-catalog.json。完整来源索引：assets/cbeta-keyword-index-v2.3.json。旧路径的Markdown索引也由统一数据重新生成，不再保留错误T号表作为运行时回退。

运行 `python3 scripts/rebuild_cbeta_index.py` 可重建全部索引；`--check` 检查生成文件是否与源数据一致。该操作不修改 scripts/data/term_index.json 的关键词、卷号或权重。

查询示例：

- `python3 scripts/cbeta_query.py --t-number 366`
- `python3 scripts/sutra_lookup.py --name 阿弥陀经`
- `python3 scripts/cbeta_index_search.py --search 佛性 --exact`
- `python3 scripts/sutra_lookup.py --volume 卷十一`
- `python3 scripts/cbeta_query.py --t-number T0893A --check-online --timeout 8`

查询脚本仅使用Python标准库。默认离线查目录，只有--check-online触发网络；支持--proxy http://127.0.0.1:端口。代理端口由用户环境确定，代码不硬编码本机端口。TLS证书正常校验；网络错误不会伪装成检索成功。CBETA入口失败时尝试CBETA官方XML仓库，返回实际使用的来源。HTML返回200仅表示页面可达，不能声称已读取经文。

来源状态：missing_source为原始出处缺失，unresolved_source为出处未解析，title_catalog_match为书名匹配经录，explicit_id_catalog_match为显式编号匹配，ambiguous_edition为多版本候选；corrected_by_passage_review表示依据原典核对更正了经录指向，旧值仍保留在source_raw和original_reference_ids。quotation_verified仍为false，避免把字串出现提升为原始使用史或宗派独占证明；具体字串核验见evidence_review.verified_occurrences。

同一个词不同卷的映射逐条保存。修复检索不会改动既有分类得分，但若人工采用新增文献重新标注或赋权，则形成新的实验版本。

inferred_reference_correction用于6条短词：在唯一历史母词候选且来源字段一致的前提下，继承母词的出处更正。它仍是逆向推断，不计入18条个别复核，不能称为短词独立完成了原句或语义验证。
