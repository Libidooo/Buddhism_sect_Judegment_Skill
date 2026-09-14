#!/usr/bin/env python3
"""Offline catalog queries and optional bounded online check (stdlib only)."""
from cbeta_common import records as load_t_number_index, keywords as load_keyword_index
from cbeta_common import by_id as query_by_t_number, by_name as query_by_sutra_name
from cbeta_common import by_keyword as query_by_keyword, online as query_cbeta_online, cli

if __name__ == '__main__':
    raise SystemExit(cli('query'))
