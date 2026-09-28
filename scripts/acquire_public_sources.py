"""Acquire only listed public documents. Never treat an HTML error as a PDF/XML.
Run: python scripts/acquire_public_sources.py
Requires requests. Files are for source review; no personal account access.
"""
from pathlib import Path
import concurrent.futures, datetime, hashlib, json
import xml.etree.ElementTree as ET
import requests
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'source_acquisition'
OUT.mkdir(exist_ok=True)
TARGETS = json.loads((ROOT/'sources/acquisition_targets.json').read_text())
def acquire(t):
    r = {**t, 'retrieved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status':'not_retrieved'}
    try:
        response = requests.get(t['url'], timeout=(12,45), headers={'User-Agent':'Mozilla/5.0 (compatible; PublicRecordsSourceReview/1.0)'})
        r.update(http_status=response.status_code, final_url=response.url, content_type=response.headers.get('Content-Type'))
        response.raise_for_status()
        b=response.content
        if len(b)>40_000_000: raise ValueError('Over 40 MB review limit')
        if t['format']=='pdf' and b'%PDF-' not in b[:1024]: raise ValueError('Response is not a PDF')
        if t['format']=='xml':
            node=ET.fromstring(b)
            if node.tag.split('}')[-1] != 'Return': raise ValueError('Not an IRS Return XML root')
            if b'237116216' not in b: raise ValueError('Expected EIN not found')
        (OUT/t['file']).write_bytes(b)
        r.update(status='retrieved_pending_review',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e: r['error']=str(e)
    return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    results=list(ex.map(acquire,TARGETS))
(OUT/'retrieval_log.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'requested':len(results),'retrieved':sum(r['status']=='retrieved_pending_review' for r in results),'failed':sum(r['status']=='not_retrieved' for r in results)},indent=2))
