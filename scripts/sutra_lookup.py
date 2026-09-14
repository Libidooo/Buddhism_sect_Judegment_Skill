#!/usr/bin/env python3
"""All queries share the verified catalog and full provenance index."""
from cbeta_common import by_id,by_name,by_keyword,by_volume,records,keywords,cli

class SutraLookup:
    def __init__(self):
        self.t_index=records()
        self.keyword_index=keywords()
    lookup_by_t_number=staticmethod(by_id)
    lookup_by_name=staticmethod(by_name)
    lookup_by_keyword=staticmethod(by_keyword)
    lookup_by_volume=staticmethod(by_volume)
    def get_volume_summary(self):
        return {'status':'success','summary':{str(i):by_volume(str(i))['count'] for i in range(17)}}

if __name__ == '__main__':
    raise SystemExit(cli('lookup'))
