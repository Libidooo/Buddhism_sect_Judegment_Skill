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
    research=json.loads((ROOT/'assets/research-evidence.json').read_text())
    valid_papers={r['id'] for r in research['papers']}
    reconstruction=json.loads((ROOT/'assets/weight-reconstruction.json').read_text())
    profiles={(r['term'],r['vid']):r for r in reconstruction['profiles']}
    review_data=json.loads((ROOT/'assets/weight-context-reviews.json').read_text())
    reviews={(r['term'],r['vid']):r for r in review_data['rules']}
    for review in reviews.values():
        assert set(review['paper_ids'])<=valid_papers, 'unknown research citation'
        assert all(code.casefold() in bycode for code in review['corrected_reference_ids']), 'unknown corrected T-number'
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
            profile=profiles.get((term,vid))
            row['weight_basis']=dict(kind='legacy_numeric_configuration',derivation=profile,
                historical_weight_changed=bool(profile and item.get('w')!=profile['historical_weight']),
                note='分值保留；短词生成是逆向候选，文献论文不证明此分值')
            review=reviews.get((term,vid))
            row['evidence_review']=review
            row['review_status']='reviewed_with_conditions' if review else 'not_individually_reviewed'
            row['quotation_verified']=False
            if review and review['corrected_reference_ids']:
                row['original_reference_ids']=[r['t_number'] for r in row['references']]
                row['references']=[bycode[code.casefold()] for code in review['corrected_reference_ids']]
                row['source_status']='corrected_by_passage_review'
                row['unresolved_codes']=[]
            elif not review and profile and profile['candidate_count']==1:
                parent=profile['candidate_parents'][0]['term']
                parent_review=reviews.get((parent,vid))
                parent_sources={str(r.get('source','')).strip() for r in terms.get(parent,[]) if str(r['vid'])==vid}
                if parent_review and parent_review['corrected_reference_ids'] and source and parent_sources=={source}:
                    row['original_reference_ids']=[r['t_number'] for r in row['references']]
                    row['references']=[bycode[code.casefold()] for code in parent_review['corrected_reference_ids']]
                    row['source_status']='inferred_reference_correction'
                    row['unresolved_codes']=[]
                    row['source_derivation_review']=dict(parent=parent,paper_ids=parent_review['paper_ids'],
                        reason='依唯一历史母词候选和相同来源字段继承出处更正；仍为逆向推断，不是该短词独立的语义／原句核验')
            unique=row['references'][0] if len(row['references'])==1 and not row.get('unresolved_codes') else None
            row['t_number']=unique['t_number'] if unique else None
            row['cbeta_url']=unique['cbeta_url'] if unique else None
            row['sutra']=unique['name'] if unique else source or '来源待核验'
            rows.append(row)
    counts=Counter(r['source_status'] for r in rows)
    report=dict(version='2.4.0',term_count=len(terms),mapping_count=sum(map(len,terms.values())),indexed_mapping_count=len(rows),catalog_count=len(refs),
        paper_count=len(valid_papers),reviewed_mapping_count=sum(r['evidence_review'] is not None for r in rows),
        derivation_profile_count=sum(r['weight_basis']['derivation'] is not None for r in rows),
        inherited_reference_correction_count=sum(r['source_status']=='inferred_reference_correction' for r in rows),
        status_counts=dict(sorted(counts.items())),term_index_sha256=hashlib.sha256(termfile.read_bytes()).hexdigest(),
        catalog_sha256=hashlib.sha256((ROOT/'assets/cbeta-catalog.json').read_bytes()).hexdigest(),
        limitation='全量收录映射不等于全部文献已校勘；缺失来源不生成链接；同词异卷权重逐条保留')
    assert len(rows)==report['mapping_count']
    out={}
    out['assets/cbeta-keyword-index-v2.3.json']=json.dumps({'version':'2.4.0','records':rows},ensure_ascii=False,indent=2)+'\n'
    out['assets/cbeta-index-build-report.json']=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    header='# CBETA经录索引\n\n由 scripts/rebuild_cbeta_index.py 生成，唯一经录源为 assets/cbeta-catalog.json。经名与编号核验不代表词条逐句校勘。\n\n'
    table='| T号 | 标准经名 | 卷别 | 作译题署 | 选本定位 | 论文依据 | 年代与使用边界 |\n|---|---|---|---|---|---|---|\n'
    for r in refs:
        uses=r.get('selection_uses',[])
        ids=sorted({p for u in uses for p in u.get('group_paper_ids',[])})
        assert set(ids)<=valid_papers
        table+='| '+' | '.join(map(cell,[r['t_number'],r['name'],r['volume'],r['byline'],'；'.join(dict.fromkeys(u['role'] for u in uses)),','.join(ids),r.get('chronology_status','')+'；'+r.get('chronology_note',r['temporal_note'])]))+' |\n'
    for p in ['assets/cbeta-t-number-canonical-v2.3.md','assets/cbeta-t-number-index.md','cbeta-index-references/cbeta-classics-index.md']:out[p]=header+table
    kh='# 关键词来源全量索引\n\n全部映射均保留；无来源或版本不明者标明状态。书名匹配仅用于经录导航，未验证关键词原句。机器查询读取同名JSON。\n\n'
    kt='| 关键词 | 卷别 | 历史权重 | 原始来源 | 当前经录指向 | 来源状态 | 语境复核 |\n|---|---|---|---|---|---|---|\n'
    kt+='\n'.join('| '+' | '.join(map(cell,[r['keyword'],r['volume'],r['weight'],r['source_raw'],','.join(x['t_number'] for x in r['references']),r['source_status'],r['evidence_review']['reason'] if r['evidence_review'] else '未逐条复核']))+' |' for r in rows)+'\n'
    for p in ['assets/cbeta-keyword-index-v2.3.md','assets/cbeta-keyword-index.md']:out[p]=kh+kt
    vh='# 卷别经录导航\n\n由统一经录生成；卷别是项目组织关系，不代表经典专属某宗派。\n'
    for i in range(17):
        selected=[r for r in refs if str(i) in r['vids']]
        vh+='\n## 卷'+CN[i]+'\n\n'+ ('\n'.join('- ['+r['name']+']('+r['cbeta_url']+') '+r['t_number'] for r in selected) or '本卷没有指定T号；参见覆盖核验文件。')+'\n'
    out['assets/cbeta-volume-query-path.md']=vh
    literature='# 文献研究与选经依据\n\n用于解释传统、选本与年代边界；不证明具体权重。核验范围逐项列明。\n'
    for p in research['papers']:
        literature+='\n## '+p['id']+' '+p['title']+'\n\n'+p['author']+'，'+p['journal']+'，'+p['year']+'，'+p['volume']+'：'+(p['pages'] or '页码待核')+'。类型：'+p['type']+'。\n\n[来源]('+p['url']+')。'+p['checked']+'。\n\n'+p['support']+'\n'
    out['sect-judgment-hub/references/research-support.md']=literature
    review_text='# 重点词条语境及出处更正\n\n仅涵盖'+str(len(reviews))+'条映射；其余不自动认定已经验证。原权重保留，以下条件用于AI／专家复核。\n'
    for r in reviews.values():
        review_text+='\n## '+r['term']+' 卷'+r['vid']+'\n\n'+r['reason']+'\n\n论文依据：'+', '.join(r['paper_ids'])+'；不是分值证明。\n'
        for occ in r['verified_occurrences']:
            review_text+='\n- '+occ['t_number']+'，'+str(occ['line'])+'，核查字串“'+occ['matched_form']+'”；[原典]('+occ['url']+')。\n'
    out['sect-judgment-hub/references/term-evidence-review.md']=review_text
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
