"""Trace retained Web candidate cards back to original persisted Reader text."""
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT), str(ROOT / 'backend/src')]
from novelty_agent_framework.tools.evidence_card_builder import _quote_matches

BASE = Path(__file__).resolve().parent
root = BASE / 'runtime/full'
manifest = json.loads((root / 'MF2033k6lC/references/list.json').read_text())
records = {r['source_record_id']: r for r in manifest['source_records']}
artifacts = {a['artifact_id']: a for a in manifest['artifacts']}
retained = {c['card_id'] for c in json.loads((root / 'result.json').read_text())['evidence_cards']}
proof = []
for path in root.glob('MF*/runtime/*/stages/*run_research_task/output.json'):
    for result in json.loads(path.read_text()).get('task_research_results', []):
        evidence = {e['evidence_id']: e for e in result['evidence']}
        reads = {r['read_id']: r for r in result['read_results']}
        for card in result['evidence_cards']:
            external = [evidence[eid] for eid in card['evidence_ids']
                if evidence[eid]['provenance']['artifact_namespace'] == 'research_reference']
            if not external:
                continue
            bindings = []
            for item in external:
                provenance = item['provenance']
                record = records[provenance['source_record_id']]
                read = reads[provenance['read_id']]
                assert item['artifact_id'] in artifacts
                assert record['raw_metadata']['channel'] == 'arxiv-web-search'
                assert _quote_matches(item['quote'], read['text'])
                bindings.append({'evidence_id': item['evidence_id'],
                    'artifact_id': item['artifact_id'], 'source_record_id': record['source_record_id'],
                    'source_id': record['source_id'], 'source_url': record['landing_url'],
                    'channel': record['raw_metadata']['channel'], 'read_id': read['read_id'],
                    'read_sha256': read['sha256'], 'quote_exact_substring': item['quote'] in read['text'],
                    'quote_matches_builder_rules': True})
            proof.append({'stage_output': str(path.relative_to(BASE)), 'card_id': card['card_id'],
                'title': card['document_title'], 'novelty_point_id': card['novelty_point_id'],
                'retained_in_final_report': card['card_id'] in retained, 'bindings': bindings})
(BASE / 'metrics/web-card-provenance.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(f'{len(proof)} Web candidate cards traced to their original Reader results.')
