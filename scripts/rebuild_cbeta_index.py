#!/usr/bin/env python3
"""Rebuild every index from ALL term mappings. Classifier data remain unchanged."""
import argparse
import hashlib
import json
import re
from collections import Counter
from cbeta_common import ROOT,CN,catalog,norm

def cell(value):
    return str(value if value is not None and value != '' else '—').replace('|','&#124;').replace('\n',' ')

def build():
    cat=catalog();refs=cat['records'];bycode={r['t_number'].casefold():r for r in refs}
    termfile=ROOT/'scripts/data/term_index.json'
    terms=json.loads(termfile.read_text(encoding='utf-8'))
    rows=[]
    for term,mappings in terms.items():
        for offset,item in enumerate(mappings):
            source=str(item.get('source','')).strip();vid=str(item.get('vid',''))
            row=dict(keyword=term,mapping_index=offset,vid=vid,vids=[vid],volume='卷'+CN[int(vid)] if vid.isdigit() and int(vid)<len(CN) else vid,
                weight=item.get('w'),source_raw=source,category=item.get('category',''),references=[],source_status='missing_source' if not source else 'unresolved_source')
            tids=re.findall(r'(?<![A-Za-z0-9])T\d{4}[A-Za-z]?',source)
            if tids:
                row['unresolved_codes']=[t for t in tids if t.casefold() not in bycode]
                row['references']=[bycode[t.casefold()] for t in dict.fromkeys(tids) if t.casefold() in bycode]
                if row['references']:row['source_status']='explicit_id_catalog_match'
            elif source:
                matches=[]
                for r in refs:
                    for alias in [r['name']]+r['aliases']:
                        s=norm(source);n=norm(alias)
                        if len(n)>=2 and (s==n or s.startswith(n+'卷') or s.startswith('《'+n+'》')):
                            matches.append((len(n),r));break
                if matches:
                    longest=max(n for n,r in matches)
                    selected={r['t_number']:r for n,r in matches if n==longest}
                    row['references']=list(selected.values())
                    row['source_status']='title_catalog_match' if len(selected)==1 else 'ambiguous_edition'
            row['quotation_verified']=False
            unique=row['references'][0] if len(row['references'])==1 and not row.get('unresolved_codes') else None
            row['t_number']=unique['t_number'] if unique else None
            row['cbeta_url']=unique['cbeta_url'] if unique else None
            row['sutra']=unique['name'] if unique else source or '来源待核验'
            rows.append(row)
    counts=Counter(r['source_status'] for r in rows)
    report=dict(version='2.3.1',term_count=len(terms),mapping_count=sum(map(len,terms.values())),indexed_mapping_count=len(rows),catalog_count=len(refs),
        status_counts=dict(sorted(counts.items())),term_index_sha256=hashlib.sha256(termfile.read_bytes()).hexdigest(),
        catalog_sha256=hashlib.sha256((ROOT/'assets/cbeta-catalog.json').read_bytes()).hexdigest(),
        limitation='全量收录映射不等于全部文献已校勘；缺失来源不生成链接；同词异卷权重逐条保留')
    assert len(rows)==report['mapping_count']
    out={}
    out['assets/cbeta-keyword-index-v2.3.json']=json.dumps({'version':'2.3.1','records':rows},ensure_ascii=False,indent=2)+'\n'
    out['assets/cbeta-index-build-report.json']=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    header='# CBETA经录索引\n\n由 scripts/rebuild_cbeta_index.py 生成，唯一经录源为 assets/cbeta-catalog.json。经名与编号核验不代表词条逐句校勘。\n\n'
    table='| T号 | 标准经名 | 卷别 | 作译者 | 时间说明 |\n|---|---|---|---|---|\n'
    table+='\n'.join('| '+' | '.join(map(cell,[r['t_number'],r['name'],r['volume'],r['byline'],r['temporal_note']]))+' |' for r in refs)+'\n'
    for p in ['assets/cbeta-t-number-canonical-v2.3.md','assets/cbeta-t-number-index.md','cbeta-index-references/cbeta-classics-index.md']:out[p]=header+table
    kh='# 关键词来源全量索引\n\n全部映射均保留；无来源或版本不明者标明状态。书名匹配仅用于经录导航，未验证关键词原句。机器查询读取同名JSON。\n\n'
    kt='| 关键词 | 卷别 | 权重 | 原始来源 | 候选经号 | 核验状态 |\n|---|---|---|---|---|---|\n'
    kt+='\n'.join('| '+' | '.join(map(cell,[r['keyword'],r['volume'],r['weight'],r['source_raw'],','.join(x['t_number'] for x in r['references']),r['source_status']]))+' |' for r in rows)+'\n'
    for p in ['assets/cbeta-keyword-index-v2.3.md','assets/cbeta-keyword-index.md']:out[p]=kh+kt
    vh='# 卷别经录导航\n\n由统一经录生成；卷别是项目组织关系，不代表经典专属某宗派。\n'
    for i in range(17):
        selected=[r for r in refs if str(i) in r['vids']]
        vh+='\n## 卷'+CN[i]+'\n\n'+ ('\n'.join('- ['+r['name']+']('+r['cbeta_url']+') '+r['t_number'] for r in selected) or '本卷没有指定T号；参见覆盖核验文件。')+'\n'
    out['assets/cbeta-volume-query-path.md']=vh
    return out,report

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    out,report=build()
    if a.check:
        changed=[p for p,t in out.items() if not (ROOT/p).exists() or (ROOT/p).read_text()!=t]
        if changed:raise SystemExit('索引需要重建: '+', '.join(changed))
    else:
        for p,t in out.items():(ROOT/p).write_text(t,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
