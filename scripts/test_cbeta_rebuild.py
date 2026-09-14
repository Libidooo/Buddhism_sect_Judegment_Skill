"""Offline invariants and HTTP failure/success tests, without external requests."""
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError,URLError
import cbeta_common as c
from rebuild_cbeta_index import build

class Response:
    status=200
    def __init__(self,body=b'<html>CBETA</html>'):self.body=body
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.body[:n]
    def geturl(self):return 'https://cbetaonline.dila.edu.tw/T0366'

class Checks(unittest.TestCase):
    def test_all_mappings_preserved(self):
        source=json.loads((c.ROOT/'scripts/data/term_index.json').read_text())
        indexed=c.keywords()
        self.assertEqual(len(indexed),sum(len(v) for v in source.values()))
        for r in indexed:
            old=source[r['keyword']][r['mapping_index']]
            self.assertEqual(str(old['vid']),r['vid']);self.assertEqual(old['w'],r['weight'])
    def test_missing_kept_without_links(self):
        hits=c.by_keyword('佛性',True)['results'];self.assertTrue(hits)
        for r in c.keywords():
            if r['source_status']=='missing_source':self.assertFalse(r['cbeta_url'])
    def test_context_weights_preserved(self):
        rows=c.by_keyword('佛性',True)['results']
        self.assertGreater(len(rows),1)
        self.assertGreater(len({r['weight'] for r in rows}),1)
    def test_sources_resolve(self):
        rows=c.by_keyword('阿弥陀佛',True)['results']
        self.assertTrue(any(r['t_number']=='T0366' for r in rows))
    def test_codes(self):
        for arg,expected in [('366','T0366'),('t0893A','T0893a'),('1998a','T1998A')]:
            self.assertEqual(c.by_id(arg)['t_number'],expected)
        self.assertEqual(c.by_id('https://example.com')['status'],'error')
        self.assertEqual(c.by_id('9999')['status'],'not_found')
    def test_correct_titles(self):
        expected={'T0452':'佛說觀彌勒菩薩上生兜率天經','T0453':'佛說彌勒下生經','T1980':'往生禮讚偈','T2182':'律宗章疏','T1579':'瑜伽師地論'}
        for tid,title in expected.items():self.assertEqual(c.by_id(tid)['results'][0]['name'],title)
    def test_volume_exact(self):
        for q in ['1','卷一']:
            self.assertTrue(all('1' in r['vids'] for r in c.by_volume(q)['results']))
        self.assertNotEqual(c.by_volume('1')['results'],c.by_volume('11')['results'])
    def test_reproducible(self):
        a,ra=build();b,rb=build();self.assertEqual(a,b)
        for p,t in a.items():self.assertEqual((c.ROOT/p).read_text(),t)
    @patch('cbeta_common.build_opener')
    def test_html_not_text_proof(self,op):
        op.return_value.open.return_value=Response()
        r=c.online('366');self.assertTrue(r['online_available']);self.assertFalse(r['text_identity_verified'])
    @patch('cbeta_common.build_opener')
    def test_xml_fallback(self,op):
        op.return_value.open.side_effect=[HTTPError('https://example.com',403,'forbidden',{},None),Response('<title>佛說阿彌陀經</title>'.encode())]
        r=c.online('366');self.assertEqual(r['source'],'cbeta_xml');self.assertTrue(r['text_identity_verified'])
    @patch('cbeta_common.build_opener')
    def test_bounded_network_failure(self,op):
        op.return_value.open.side_effect=URLError('offline')
        r=c.online('366');self.assertEqual(r['status'],'error');self.assertEqual(op.return_value.open.call_count,4)
        self.assertEqual(c.by_id('366')['status'],'success')

if __name__=='__main__':unittest.main()
