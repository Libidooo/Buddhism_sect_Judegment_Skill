"""Shared catalog, complete provenance index and bounded network access (stdlib only)."""
import argparse
import json
import os
import re
import ssl
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, HTTPSHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
CN = ['零','一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五','十六']

def catalog():
    return json.loads((ASSETS/'cbeta-catalog.json').read_text(encoding='utf-8'))

def records():
    return catalog()['records']

def normalize_id(value):
    value = unicodedata.normalize('NFKC', value.strip())
    if not re.fullmatch(r'[Tt]?\d{1,4}[a-zA-Z]?', value):
        raise ValueError('经号格式应为T0366、366或T0893a，不能是任意网址')
    value = re.sub('^[Tt]', '', value)
    match = re.fullmatch(r'(\d+)([a-zA-Z]?)', value)
    candidate = 'T'+match[1].zfill(4)+match[2]
    for row in records():
        if row['t_number'].casefold() == candidate.casefold(): return row['t_number']
    return candidate

def volume_id(value):
    value = value.strip()
    if value.startswith('卷'): value=value[1:]
    if value in CN: return str(CN.index(value))
    if value.isdigit() and 0 <= int(value) <= 16: return str(int(value))
    raise ValueError('卷别须为0至16或卷一、卷十一等')

def in_volume(row, value):
    return volume_id(value) in row.get('vids', [row.get('vid')])

def norm(value):
    return unicodedata.normalize('NFKC', value).casefold().strip()

def by_id(value):
    try: tid = normalize_id(value)
    except ValueError as e: return {'status':'error','message':str(e),'results':[]}
    hits = [r for r in records() if r['t_number']==tid]
    return {'status':'success' if hits else 'not_found','t_number':tid,'results':hits,'count':len(hits)}

def by_name(value):
    query = norm(value)
    hits = [r for r in records() if query and any(query in norm(n) for n in [r['name']]+r['aliases'])]
    return {'status':'success' if hits else 'not_found','sutra_name':value,'results':hits,'count':len(hits)}

def keywords():
    path=ASSETS/'cbeta-keyword-index-v2.3.json'
    if not path.exists(): raise ValueError('请先运行 scripts/rebuild_cbeta_index.py')
    return json.loads(path.read_text(encoding='utf-8'))['records']

def by_keyword(value, exact=False):
    query=norm(value)
    hits=[r for r in keywords() if query and (norm(r['keyword'])==query if exact else query in norm(r['keyword']))]
    return {'status':'success' if hits else 'not_found','keyword':value,'results':hits,'count':len(hits)}

def by_volume(value):
    vid=volume_id(value);hits=[r for r in records() if vid in r['vids']]
    return {'status':'success' if hits else 'not_found','volume':'卷'+CN[int(vid)],'results':hits,'count':len(hits)}

def online(value, timeout=12, proxy=None):
    result=by_id(value)
    if result['status']!='success': return dict(result, online_available=False)
    row=result['results'][0]
    context=ssl.create_default_context()
    # Python.org macOS installs can have no CA bundle until certificates are installed.
    # Use the OS bundle only if Python loaded no CAs and the user has not chosen one.
    if not context.get_ca_certs() and not os.environ.get('SSL_CERT_FILE') and not os.environ.get('SSL_CERT_DIR'):
        for candidate in ['/etc/ssl/cert.pem','/etc/ssl/certs/ca-certificates.crt']:
            if Path(candidate).is_file():
                context.load_verify_locations(cafile=candidate)
                break
    handlers=[HTTPSHandler(context=context)]
    if proxy is not None:
        if proxy and not re.match(r'^https?://[^\s]+$',proxy):
            return {'status':'error','message':'proxy须为http/https代理URL','online_available':False}
        handlers.append(ProxyHandler({'https':proxy,'http':proxy} if proxy else {}))
    opener=build_opener(*handlers);attempts=[]
    for kind,url in [('cbeta_online',row['cbeta_url']),('cbeta_xml',row['xml_url'])]:
        for attempt in range(2):
            try:
                req=Request(url,headers={'User-Agent':'buddhist-inscription-judgment/2.3.1','Accept':'text/html,application/xml;q=0.9,*/*;q=0.5'})
                with opener.open(req,timeout=timeout) as response:
                    body=response.read(131072).decode('utf-8',errors='replace');status=response.status;final_url=response.geturl()
                if status!=200: raise ValueError('HTTP '+str(status))
                verified=kind=='cbeta_xml' and row['name'] in body
                if kind=='cbeta_xml' and not verified:
                    attempts.append({'source':kind,'error':'返回内容未匹配经名'});break
                return {'status':'success','online_available':True,'t_number':row['t_number'],'url':final_url,
                    'source':kind,'http_status':status,'text_identity_verified':verified,'attempts':attempts,
                    'message':'XML经名已核对，未逐句校勘' if verified else 'CBETA页面可访问；HTML入口可达不代表经文已取回或校勘'}
            except (HTTPError,URLError,TimeoutError,ValueError,OSError) as e:
                reason=getattr(e,'reason',e)
                detail='证书验证失败，请检查系统CA或SSL_CERT_FILE' if isinstance(reason,ssl.SSLCertVerificationError) else '请求失败；检查代理、网络或服务状态'
                attempts.append({'source':kind,'attempt':attempt+1,'error_type':type(reason).__name__,'http_status':getattr(e,'code',None),'message':detail})
                if isinstance(e,HTTPError) and e.code not in (429,500,502,503,504): break
    return {'status':'error','online_available':False,'t_number':row['t_number'],'attempts':attempts,
        'message':'在线请求失败，本地查询仍可用；支持--proxy；未关闭TLS证书校验'}

def cli(mode):
    p=argparse.ArgumentParser(description='CBETA统一经录与全量来源查询')
    p.add_argument('--t-number');p.add_argument('--sutra-name','--name',dest='name');p.add_argument('--keyword')
    p.add_argument('--volume');p.add_argument('--search');p.add_argument('--exact',action='store_true')
    p.add_argument('--type',default='all',choices=['all','t-number','name','keyword'])
    p.add_argument('--stats','--summary',dest='stats',action='store_true');p.add_argument('--check-online',action='store_true')
    p.add_argument('--timeout',type=float,default=12);p.add_argument('--proxy',default=None,help='显式HTTP代理；空字符串直连；默认遵循环境代理')
    p.add_argument('--format',choices=['json','text'],default='json');a=p.parse_args()
    if not 0<a.timeout<=60:p.error('timeout须在0至60秒之间')
    if a.check_online and not a.t_number:p.error('--check-online需要--t-number')
    try:
        if a.stats:result=dict(status='stats',**json.loads((ASSETS/'cbeta-index-build-report.json').read_text()))
        elif a.t_number:result=by_id(a.t_number)
        elif a.name:result=by_name(a.name)
        elif a.keyword:result=by_keyword(a.keyword,a.exact)
        elif a.search:
            q=a.search;hits=[]
            if a.type in ('all','t-number') and re.fullmatch(r'[Tt]?\d{1,4}[a-zA-Z]?',q):hits.extend(by_id(q)['results'])
            if a.type in ('all','name'):
                nh=by_name(q)['results']
                if a.exact:nh=[r for r in nh if norm(q) in [norm(x) for x in [r['name']]+r['aliases']]]
                hits.extend(r for r in nh if r not in hits)
            if a.type in ('all','keyword'):hits.extend(by_keyword(q,a.exact)['results'])
            result={'status':'success' if hits else 'not_found','query':q,'results':hits,'count':len(hits)}
        elif a.volume:result=by_volume(a.volume)
        else:p.error('请提供经号、经名、关键词、卷别或--stats')
        if a.volume and 'results' in result:
            result['results']=[r for r in result['results'] if in_volume(r,a.volume)]
            result['count']=len(result['results']);result['status']='success' if result['count'] else 'not_found'
        if a.check_online and result['status']=='success':result['online_check']=online(a.t_number,a.timeout,a.proxy)
    except (ValueError,OSError,json.JSONDecodeError) as e:result={'status':'error','message':str(e)}
    if a.format=='json':print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print(result.get('message',result['status']))
        for r in result.get('results',[]):
            print(r.get('keyword',''),r.get('name',r.get('sutra','')),r.get('t_number') or '待核验',r.get('volume',''))
            if 'weight' in r:print('  历史权重:',r['weight'],'；来源状态:',r.get('source_status'))
            if r.get('evidence_review'):
                review=r['evidence_review'];print('  复核:',review['reason']);print('  研究依据:',','.join(review['paper_ids']))
            elif 'review_status' in r:print('  尚未逐条文献复核')
            if r.get('source_derivation_review'):print('  来源继承推断:',r['source_derivation_review']['reason'])
            if r.get('chronology_note'):print('  版本与年代:',r['chronology_note'])
    return 1 if result['status']=='error' or result.get('online_check',{}).get('status')=='error' else 0
