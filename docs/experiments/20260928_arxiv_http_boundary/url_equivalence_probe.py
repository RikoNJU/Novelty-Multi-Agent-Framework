"""Adaptive follow-up after a successful canonical API response; eight equivalent/public requests."""
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base_probe',P/'probe.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.OUT=P/'url_equivalence';mod.OUT.mkdir(exist_ok=True)
mod.CASES=[
 ('raw_colon','https://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1',{}),
 ('encoded_colon','https://export.arxiv.org/api/query?search_query=all%3Aelectron&start=0&max_results=1',{}),
 ('reordered_parameters','https://export.arxiv.org/api/query?start=0&max_results=1&search_query=all:electron',{}),
 ('explicit_empty_id','https://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1&id_list=',{}),
 ('raw_colon_graph','https://export.arxiv.org/api/query?search_query=all:%22graph%20neural%20network%22&start=0&max_results=1',{}),
 ('minimal_known_id','https://export.arxiv.org/api/query?id_list=1706.03762',{}),
 ('graph_project_ua','https://export.arxiv.org/api/query?search_query=all%3A%22graph%20neural%20network%22&start=0&max_results=1',{'user-agent':'NoveltyFramework-Audit/1.0 (+https://github.com/RikoNJU/Novelty-Multi-Agent-Framework)'}),
 ('raw_colon_repeat','https://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1',{}),
]
mod.main()
