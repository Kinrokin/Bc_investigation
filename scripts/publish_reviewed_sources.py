"""Publish reviewed public-source artifact copies, not private records or signed redirect URLs.
The workflow supplies a previously downloaded artifact. Files must match the review allowlist.
"""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json,re,shutil,zipfile,html
import fitz
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];IN=ROOT/'_review_download';OUT=ROOT/'sources';(OUT/'originals').mkdir(parents=True,exist_ok=True);(OUT/'irs_views').mkdir(exist_ok=True);(OUT/'extracts').mkdir(exist_ok=True)
EXPECTED={
'City_September28_2026_Agenda.pdf':'5c8f1af35b875255168d93361f1b2829a7f5166225992d3d96910d97c6da71b2',
'United_Way_2025_Annual_Report.pdf':'0b163cb97f69d2738e62aac6ae70154adcf7351214dffb851cbfd97d4c828e15',
'City_September28_2026_Statement.pdf':'e954c757034cb5725c0b0234b7521423e5f5589796a27540e60d3ad4a1558ac1',
'City_September21_2026_Statement.pdf':'650ba4d14498c0e31a5c8502a7d38e6f06a2cdbbbf3ce5a6a1930c055dbbd381',
'City_June22_2026_Packet.pdf':'c4a88af9cc3737a0ca14f77985ff9f5d83a257851be02279bb2b3785d6cc2bc7',
'United_Way_2024_Annual_Report.pdf':'87dab5f7149be5ac69518049c26166b85bfb00de761cc4534027a62c5527f6e0',
'Bartlett_September25_2026_Resolution.pdf':'a27a546b607607b47b1180bd2bca67665ff6394544029c551064d98e3d4a6614',
'City_Procurement_Policy.pdf':'f80bd0640141d2255536376f95d82027e3d6ee894eb87ef4a0ca43dd7c86c7a7',
'Missouri_House_September10_2024_Testimony.pdf':'0b123515316b9a8f142c5c6600d24b16953fb5b8f9b32bd300b1a6ff710bb2e8',
'HUD_October16_2025_Lapse_Plan.pdf':'1d27c0c788fe6130d112f5271521f1336b2f8b16c97293236e06b77de5bc4c6d'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
log=[];retrieval=json.loads((IN/'retrieval_log.json').read_text());urls={r['file']:r['url'] for r in retrieval}
for name,want in EXPECTED.items():
    p=IN/name
    if digest(p)!=want:raise ValueError('Review hash mismatch: '+name)
    row=dict(source_file=name,source_url=urls[name],acquired_sha256=want)
    if name.startswith('Missouri_House_'):
        doc=fitz.open(p);n=0
        patterns=[r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}',r'(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}(?!\d)']
        for page in doc:
            text=page.get_text()
            for pattern in patterns:
                for value in set(re.findall(pattern,text,re.I)):
                    for rect in page.search_for(value):page.add_redact_annot(rect,fill=(1,1,1));n+=1
            page.apply_redactions()
            page.insert_text((30,page.rect.height-14),'CONTACT-REDACTED DERIVATIVE | source retained privately',fontsize=6)
        doc.set_metadata({});target=OUT/'originals'/name.replace('.pdf','_CONTACT_REDACTED.pdf');doc.save(target,garbage=4,deflate=True);doc.close();row.update(status='contact-redacted derivative',redactions=n)
    else:target=OUT/'originals'/name;shutil.copy2(p,target);row['status']='reviewed downloaded original'
    row.update(published_file=str(target.relative_to(ROOT)),published_sha256=digest(target));log.append(row)
irslog=json.loads((IN/'irs_viewer_retrieval_log.json').read_text())
for year in irslog:
    for item in year['files']:
        if item.get('status')!='retrieved_pending_review':continue
        p=IN/item['file']
        if digest(p)!=item['sha256']:raise ValueError('IRS acquisition hash mismatch')
        if urlsplit(item['url']).hostname!='projects.propublica.org':raise ValueError('Unexpected source host')
        soup=BeautifulSoup(p.read_text(),'html.parser')
        for el in soup.find_all(['script','iframe','object','embed','link','base']):el.decompose()
        for el in soup.find_all(True):
            for key in list(el.attrs):
                val=el.attrs[key]
                if key.lower().startswith('on') or (key in ['src','href','action'] and isinstance(val,str) and val.lower().startswith(('javascript:','data:text/html'))):del el.attrs[key]
            if el.name=='input':el['disabled']='disabled'
        for form in soup.find_all('form'):form.unwrap()
        target=OUT/'irs_views'/p.name;target.write_text(str(soup),encoding='utf-8');target.with_suffix('.txt').write_text(soup.get_text('\n',strip=True),encoding='utf-8')
        log.append(dict(source_url=item['url'],acquired_sha256=item['sha256'],published_file=str(target.relative_to(ROOT)),published_sha256=digest(target),status='passive IRS-derived rendering; not original XML'))
(OUT/'publication_log.json').write_text(json.dumps(log,indent=2)+'\n')
packet=fitz.open(OUT/'originals/City_June22_2026_Packet.pdf')
for name,first,last in [('Independent_Audit_FY2025',41,67),('Ordinance_and_Lease',8,18),('CDBG_Chronology',6,6),('Internal_Financials',31,40)]:
    doc=fitz.open();doc.insert_pdf(packet,from_page=first-1,to_page=last-1);doc.save(OUT/'extracts'/f'{name}_source_pp{first}-{last}.pdf');doc.close()
packet.close()
files=[p for folder in ['docs','portfolio','data','scripts','sources'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files += [ROOT/'README.md']
manifest=[dict(file=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(files)]
(OUT/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
links='\n'.join('<li><a href="'+html.escape(str(p.relative_to(ROOT)))+'">'+html.escape(str(p.relative_to(ROOT)))+'</a></li>' for p in sorted(files))
(ROOT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bartlett evidence portfolio</title><style>body{max-width:960px;margin:3rem auto;font:17px/1.6 system-ui;padding:0 1rem}h1{color:#153448}a{color:#135e76}li{margin:.3rem 0}</style><h1>Bartlett / Horace Mann</h1><p>Robert King — source-linked research and reproducible financial review. This is a portfolio/source edition, not the larger160-file collected-report archive and not a legal finding. Read README and the current findings first.</p><ul>'+links+'</ul></html>',encoding='utf-8')
(ROOT/'downloads').mkdir(exist_ok=True)
with zipfile.ZipFile(ROOT/'downloads/Bartlett_Git_Portfolio_and_Sources.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files+[ROOT/'index.html',OUT/'FILE_MANIFEST.json']:z.write(p,str(p.relative_to(ROOT)))
print(json.dumps({'reviewed_pdf_sources':len(EXPECTED),'irs_render_components':sum(1 for r in log if 'IRS-derived' in r['status']),'manifest_files':len(manifest),'source_files':len(log)},indent=2))
