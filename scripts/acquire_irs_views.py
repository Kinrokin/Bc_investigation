"""Retrieve the public IRS-derived viewer and only its same-host iframe targets.
No login, account access or respondent records. Do not publish signed redirect URLs.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from html.parser import HTMLParser
import requests,json,hashlib,datetime
OUT=Path('source_acquisition');OUT.mkdir(exist_ok=True)
class Frames(HTMLParser):
    def __init__(self): super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=='iframe':
            a=dict(attrs)
            if a.get('src'):self.urls.append(a['src'])
logs=[]
s=requests.Session();s.headers['User-Agent']='Mozilla/5.0 (compatible; PublicRecordsSourceReview/1.0)'
for fy,oid in [(2025,'202610519349300211'),(2024,'202510529349300816')]:
    url=f'https://projects.propublica.org/nonprofits/organizations/237116216/{oid}/full'
    item={'fiscal_year':fy,'object_id':oid,'viewer_url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[]}
    try:
        r=s.get(url,timeout=(10,40));r.raise_for_status()
        p=Frames();p.feed(r.text)
        for index,src in enumerate(p.urls[:12]):
            endpoint=urljoin(url,src)
            if urlsplit(endpoint).hostname!='projects.propublica.org':continue
            row={'url':endpoint,'status':'not_retrieved'}
            try:
                q=s.get(endpoint,timeout=(10,40));q.raise_for_status();b=q.content
                if b'<html' not in b.lower() or len(b)<5000:raise ValueError('Not a substantive rendered return page')
                stem=urlsplit(endpoint).path.rstrip('/').split('/')[-1]
                name=f'Bartlett_FY{fy}_{stem}_IRS_Derived_Viewer.html'
                (OUT/name).write_bytes(b)
                row.update(status='retrieved_pending_review',file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
            except Exception as e:row['error_type']=type(e).__name__;row['http_status']=getattr(locals().get('q'),'status_code',None)
            item['files'].append(row)
    except Exception as e:item['error_type']=type(e).__name__
    logs.append(item)
(OUT/'irs_viewer_retrieval_log.json').write_text(json.dumps(logs,indent=2)+'\n')
print(json.dumps(logs,indent=2))
