"""Compare tokenization with frozen observed usage; never request generation."""
from pathlib import Path
import copy
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parent
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
records = []
for path in sorted((ROOT/'reader_local_pair_restarted').glob('state_*/MF*/runtime/*/llm_calls/*.json')):
    old = json.loads(path.read_text())
    original = old['request_payload']
    payload = {key: copy.deepcopy(value) for key, value in original.items() if key in {
        'model','messages','chat_template','chat_template_kwargs','add_generation_prompt','continue_final_message','add_special_tokens'}}
    if original.get('tools'):
        payload.setdefault('chat_template_kwargs', {}).setdefault('tools', original['tools'])
    request = urllib.request.Request('http://127.0.0.1:8000/tokenize',
        data=json.dumps(payload,ensure_ascii=False).encode(), headers={'Content-Type':'application/json'}, method='POST')
    with opener.open(request,timeout=8) as response:
        measured=json.load(response)
    usage=(old.get('provider_usage') or {}).get('prompt_tokens')
    records.append({'call':str(path.relative_to(ROOT)),'expected_provider_input_tokens':usage,
        'tokenizer_count':measured['count'],'server_context_window':measured['max_model_len'],
        'matches':usage==measured['count'],'tools_count':len(original.get('tools',[])),
        'tool_choice':original.get('tool_choice'),
        'payload_sha256':hashlib.sha256(json.dumps(original,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
        'tokenize_payload_sha256':hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()})
    print(path.name, usage, measured['count'], usage==measured['count'], flush=True)
(ROOT/'vllm_tokenization_comparison.json').write_text(json.dumps({
    'generation_calls':0,'tokenize_calls':len(records),'server_version':'0.8.5.post1',
    'method':'Legacy tools forwarded as chat_template_kwargs.tools; no new inference.',
    'all_match':bool(records) and all(row['matches'] for row in records),'records':records},ensure_ascii=False,indent=2)+'\n')
