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
    def test_new_catalog_and_papers(self):
        self.assertEqual(len(c.records()),135)
        for tid,title in [('T1331','佛說灌頂經'),('T1982','集諸經禮懺儀'),('T1161','佛說觀藥王藥上二菩薩經')]:
            row=c.by_id(tid)['results'][0]
            self.assertEqual(row['name'],title)
            self.assertIn('本次新增',row['historical_use_status'])
        research=json.loads((c.ASSETS/'research-evidence.json').read_text())
        self.assertEqual(len(research['papers']),21)
        valid={p['id'] for p in research['papers']}
        for row in c.records():
            for use in row['selection_uses']:self.assertTrue(set(use['group_paper_ids'])<=valid)
    def test_corrected_source_keeps_original(self):
        row=c.by_keyword('无对光佛',True)['results'][0]
        self.assertEqual(row['source_raw'],'阿弥陀经')
        self.assertEqual(row['t_number'],'T0360')
        self.assertIn('T0366',row['original_reference_ids'])
        self.assertEqual(row['source_status'],'corrected_by_passage_review')
        self.assertEqual(row['weight'],70)
        self.assertFalse(row['quotation_verified'])
        self.assertTrue(row['evidence_review']['verified_occurrences'])
    def test_context_does_not_become_automatic_gate(self):
        row=c.by_keyword('海潮音',True)['results'][0]
        self.assertIn('不足以单独',row['evidence_review']['reason'])
        self.assertIn('非新增计分器',row['evidence_review']['enforcement'])
    def test_short_source_correction_stays_an_inference(self):
        row=next(r for r in c.by_keyword('无对光',True)['results'] if r['vid']=='3')
        self.assertEqual(row['source_status'],'inferred_reference_correction')
        self.assertEqual(row['t_number'],'T0360')
        self.assertEqual(row['source_raw'],'阿弥陀经')
        self.assertEqual(row['weight'],42)
        self.assertIsNone(row['evidence_review'])
        self.assertFalse(row['quotation_verified'])
    def test_derivation_is_explicitly_inferred(self):
        row=next(r for r in c.by_keyword('阿弥陀',True)['results'] if r['vid']=='3')
        p=row['weight_basis']['derivation']
        self.assertEqual(row['weight'],48)
        self.assertEqual(p['status'],'inferred_prefix_suffix_derivation')
        self.assertIn('阿弥陀佛',[r['term'] for r in p['candidate_parents']])
    def test_chronology_is_separate_from_titles(self):
        self.assertEqual(c.by_id('T0412')['results'][0]['chronology_status'],'disputed_authorship_and_date')
        for tid in ['T0927','T1938','T1939','T2024']:
            self.assertEqual(c.by_id(tid)['results'][0]['chronology_status'],'post_13th_century')
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
