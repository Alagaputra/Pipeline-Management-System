"""Build a detailed private study book from reviewed project evidence."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import importlib.util
import json
import re
import runpy
import shutil
import sys
from book_common import *
from content_business import pages as business_pages
from content_technical import pages as technical_pages

ROOT=Path(__file__).resolve().parent.parent
PROJECT=ROOT.parents[2]
DESIGN=ROOT.parent/'desain-sistem'


def schema_pages():
    schema=json.loads((DESIGN/'schema.json').read_text(encoding='utf-8'))
    definitions=runpy.run_path(str(DESIGN/'scripts/build.py'))
    order=definitions['ORDER']
    purpose=definitions['PURPOSE']
    groups=[]
    current=[]
    weight=0
    for name in order:
        cols=[c for c in schema['columns'] if c['table_name']==name]
        cost=len(cols)+5
        if current and weight+cost>31:
            groups.append(current)
            current=[]
            weight=0
        current.append((name,cols))
        weight+=cost
    if current:
        groups.append(current)
    result=[]
    for i,group in enumerate(groups):
        body=''
        for name,cols in group:
            cons=[c for c in schema['constraints'] if c['table_name']==name]
            rows=[]
            for col in cols:
                flags=[]
                for c in cons:
                    match=re.search(r'\(([^)]+)\)',c['definition'])
                    fields=[v.strip().strip('"') for v in match.group(1).split(',')] if match else []
                    if col['column_name'] in fields:
                        if c['type']=='p': flags.append('PK')
                        elif c['type']=='u': flags.append('U*' if len(fields)>1 else 'U')
                        elif c['type']=='f':
                            ref=re.search(r'REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)',c['definition'])
                            flags.append('FK → '+ref.group(1)+'.'+ref.group(2) if ref else 'FK')
                typ=col['data_type']
                if typ=='character varying':typ='varchar('+str(col['character_maximum_length'])+')'
                if typ=='timestamp without time zone':typ='timestamp tanpa zona'
                rows.append((f'<code>{col["column_name"]}</code>',typ,'Ya' if col['is_nullable']=='YES' else 'Tidak','; '.join(flags) or '—'))
            body+=h(name)+p(purpose[name])+table(['Kolom','Tipe fisik','NULL','Kunci / relasi'],rows,'schema')
        body+=p('<small>PK = primary key; FK = foreign key; U = unik tunggal; U* = bagian kombinasi unik. Kolom tanpa tanda kunci tetap dapat mempunyai indeks biasa. Metadata cocok dengan database aktif pada 20 Oktober 2026.</small>')
        result.append(page('LAMPIRAN · KAMUS DATA',f'Kamus kolom · {i+1}/{len(groups)}','Seluruh 162 kolom dari 22 tabel, dikelompokkan agar dapat dipelajari per fungsi.',body,'dictionary'))
    return result


def reference_pages():
    pairs=list(SOURCES.items())
    result=[]
    for start in range(0,len(pairs),10):
        body=p('Sumber konsep berikut diperiksa pada penyusunan materi 20 Oktober 2026. Versi paket tetap mengikuti lockfile proyek. Dokumentasi Laravel 12 dan Vite 7 dipilih agar tidak mencampur perilaku mayor versi lain.')
        for key,(title,url) in pairs[start:start+10]:
            body+=f'<div class="ref"><strong>{key} · {escape(title)}</strong><br><a href="{url}">{escape(url)}</a></div>'
        result.append(page('SUMBER DAN BUKTI','Rujukan resmi teknologi',f'Daftar {start+1}–{min(start+10,len(pairs))} dari {len(pairs)} rujukan. Tautan dapat diklik dari PDF.',body,'references'))
    return result


def diagram_pages():
    names=[('arsitektur-sistem','Arsitektur sistem'),('erd-pipeline','ERD master dan pipeline'),('erd-target','ERD target dan realisasi'),('erd-keamanan','ERD autentikasi, audit, dan retry'),('dfd-konteks','DFD konteks'),('dfd-level-1','DFD Level 1'),('dfd-level-2-pipeline','DFD Level 2 pipeline'),('dfd-level-3-closing','DFD Level 3 closing')]
    result=[]
    for name,title in names:
        svg=(DESIGN/f'{name}.svg').read_text(encoding='utf-8')
        result.append(page('LAMPIRAN · DIAGRAM A3',title,'',f'<div class="diagram">{svg}</div>','wide'))
    return result


def screenshots():
    source=PROJECT/'src/frontend/test-results'
    assets=ROOT/'assets'
    assets.mkdir(exist_ok=True)
    result=[]
    for route,title,explanation in [
        ('pipeline','Pipeline aktif','Amati pencarian, filter, penanggung jawab, produk, nominal, dan tindakan detail. Kartu/daftar berubah mengikuti ukuran layar.'),
        ('target','Target tahunan','Bandingkan target, realisasi Won, sisa, dan satuan. Target layanan tetap terpisah dari target dana.'),
        ('tim','Tim dan PIC','Bedakan penanggung jawab saat ini dengan peluang yang pernah ditangani. Tahun digunakan untuk hasil closing.')]:
        name=f'layout-head-{route}-1440.png'
        if (source/name).exists():
            shutil.copy2(source/name,assets/name)
            body=f'<figure class="screen"><img src="assets/{name}" alt="Tampilan {title} pada akun Head Funding di database pengujian"><figcaption>{escape(explanation)}</figcaption></figure>'
            body+=note('Baca sebagai ilustrasi','Screenshot berasal dari suite pengujian lokal 20 Oktober 2026, bukan data kinerja operasional cabang. Angka fixture tidak sama dengan contoh hitung A–E pada bab belajar.')
            result.append(page('LAMPIRAN · TAMPILAN UI',title,'Contoh tampilan nyata dari hasil pengujian terbaru.',body,'ui'))
    return result


def build():
    ROOT.mkdir(exist_ok=True)
    body_pages=business_pages()+technical_pages()
    learning=Path(__file__).with_name('content_learning.py')
    if learning.exists():
        spec=importlib.util.spec_from_file_location('content_learning',learning)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        body_pages+=module.pages()
    body_pages+=schema_pages()+reference_pages()+screenshots()+diagram_pages()
    cover=page('BUKU BELAJAR PRIBADI','Pipeline Funding Management','Memahami website untuk menjelaskan proyek pada ujian magang.',
        '<div class="cover-rule"></div><p class="cover-summary">Bisnis dan fitur<br>Arsitektur dan aliran data<br>Frontend, API, dan database<br>Integritas, keamanan, dan pengujian<br>Latihan penjelasan dan tanya jawab</p>'+note('Dasar penyusunan','Kode proyek, katalog PostgreSQL aktif, hasil tes 20 Oktober 2026, dan dokumentasi resmi teknologi. Materi dibuat untuk belajar pribadi tanpa identitas peserta.')+p('<strong>Vue 3 · Laravel 12 · PostgreSQL 18 · Chart.js 4</strong>'),'cover')
    # Two contents pages are reserved so printed page numbers stay stable.
    sections=[]
    for i,pg in enumerate(body_pages,4):
        if not sections or sections[-1][0]!=pg['section']:
            sections.append((pg['section'],i))
    chunks=[sections[:len(sections)//2],sections[len(sections)//2:]]
    contents=[]
    for idx,chunk in enumerate(chunks):
        rows=[(f'<a href="#page-{n}">{escape(title)}</a>',str(n)) for title,n in chunk]
        contents.append(page('PETA MATERI',f'Daftar isi · {idx+1}/2','Nomor mengikuti halaman PDF, termasuk lampiran A3.',table(['Bagian','Halaman'],rows,'toc')+note('Mulai dari alur, lalu teknologinya','Jika waktu belajar terbatas, dahulukan alur peluang, contoh perhitungan, arsitektur, transaksi/version/idempotensi, lalu pertanyaan latihan. Lampiran kamus data membantu saat perlu menelusuri kolom tertentu.')))
    pages=[cover]+contents+body_pages
    markup=[]
    for n,pg in enumerate(pages,1):
        wide=pg['kind']=='wide'
        header='' if wide else f'<header><div class="eyebrow">{escape(pg["section"])}</div><h1>{escape(pg["title"])}</h1><p class="lead">{pg["lead"]}</p></header>'
        markup.append(f'<section class="paper {pg["kind"]}" id="page-{n}" data-title="{escape(pg["title"],quote=True)}">{header}<main class="content">{pg["body"]}</main><footer><span>PIPELINE FUNDING · BUKU BELAJAR · 20 OKT 2026</span><b>{n:02} / {len(pages):02}</b></footer></section>')
    css='''
*{box-sizing:border-box}html{background:#e7edf0;scroll-behavior:smooth}body{margin:0;color:#192f3d;font:10.5pt/1.5 Arial,Helvetica,sans-serif}.toolbar{max-width:210mm;margin:20px auto;background:#fff;border-top:4px solid #214c60;padding:18px 24px;font-size:14px}.toolbar a{margin-right:20px}.paper{width:210mm;height:297mm;margin:24px auto;padding:17mm 18mm 22mm;background:#fff;position:relative;display:flex;flex-direction:column;box-shadow:0 4px 22px #162b3b18;break-after:page;break-inside:avoid}.paper:last-child{break-after:auto}header{border-top:3px solid #244d60;padding-top:12px;padding-bottom:12px;margin-bottom:8px;border-bottom:1px solid #d8e2e8}h1{font-size:24pt;line-height:1.13;letter-spacing:-.6px;margin:9px 0 10px;max-width:100%;overflow-wrap:anywhere}.eyebrow{color:#487180;font-size:8pt;font-weight:700;letter-spacing:1.3px}.lead{font-size:11pt;line-height:1.5;color:#516874;margin:0}h3{font-size:11.5pt;line-height:1.35;margin:14px 0 7px;color:#1b4c60}p{margin:8px 0 11px}ul{padding-left:19px;margin:8px 0 12px}li{margin:6px 0}.content{flex:1;min-height:0}table{width:100%;border-collapse:collapse;font-size:9.3pt;line-height:1.4;margin:10px 0 14px;table-layout:auto}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #d5dfe5;padding:7px 8px;overflow-wrap:anywhere}th{background:#edf3f5;color:#214b60;font-weight:700}tbody tr:nth-child(even){background:#fafcfd}code{font:9.2pt/1.4 Consolas,'Courier New',monospace;overflow-wrap:anywhere;color:#274b60}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:13px 15px;border-left:3px solid #557f90;background:#f1f5f7;line-height:1.45;margin:12px 0 15px}pre code{color:#193d50}aside{padding:12px 14px;border-left:3px solid #779f91;background:#f0f7f4;margin:14px 0}aside>strong{font-size:10pt;color:#285b4b}aside p{margin:6px 0 0;font-size:10pt;line-height:1.5}.sources{font-size:8pt;line-height:1.5;color:#617782;margin:7px 0 12px}a{color:#245e78;text-decoration:none;overflow-wrap:anywhere}a:hover{text-decoration:underline}footer{position:absolute;left:18mm;right:18mm;bottom:10mm;border-top:1px solid #d0dde4;display:flex;justify-content:space-between;padding-top:8px;color:#5d7581;font-size:7.5pt;letter-spacing:.2px}footer b{font-size:8pt;white-space:nowrap}.cover{border-top:8mm solid #193d50;padding-top:31mm}.cover header{border-top:0;border-bottom:0;padding:0}.cover h1{font-size:42pt;line-height:1.02;max-width:150mm;margin:26px 0}.cover .lead{font-size:15pt;max-width:150mm}.cover-rule{height:5px;width:34mm;background:#659589;margin:24px 0}.cover-summary{font-size:16pt;line-height:1.65;margin-bottom:34px}.toc{font-size:10pt}.toc td{padding:11px 8px}.toc td:last-child{width:18mm;text-align:right}.dictionary{font-size:9.5pt}.dictionary h3{font-size:12pt;margin-top:11px}.dictionary table{font-size:8.6pt;line-height:1.3;margin-bottom:10px}.dictionary td,.dictionary th{padding:5px 6px}.dictionary code{font-size:8.5pt}.dictionary .schema td:first-child{width:31%}.dictionary .schema td:nth-child(2){width:24%}.dictionary .schema td:nth-child(3){width:8%}.dictionary small{font-size:8pt}.ref{margin:12px 0 16px;line-height:1.55}.ref a{font-size:8.7pt}.qa{border-bottom:1px solid #e2e9ed;padding-bottom:4px}.qa h3{font-size:11pt}.qa p{margin-bottom:10px}.screen{margin:10px 0}.screen img{max-width:100%;max-height:177mm;display:block;margin:auto;border:1px solid #d8e2e8;object-fit:contain}.screen figcaption{font-size:9pt;color:#536c7a;padding:10px 0}.wide{page:wide;width:420mm;height:297mm;padding:5mm 7mm 14mm}.wide .content{display:flex;align-items:center;justify-content:center}.diagram{width:100%;height:100%;display:flex;align-items:center;justify-content:center}.diagram svg{display:block;width:auto;height:auto;max-width:100%;max-height:100%}.wide footer{left:7mm;right:7mm;bottom:4mm;font-size:6.5pt}.compact{font-size:9.8pt;line-height:1.43}.compact table{font-size:8.7pt}.compact p{margin:6px 0 9px}.compact li{margin:4px 0}.compact aside p{font-size:9.5pt}.compact h3{margin-top:11px}.compact pre{padding:10px 12px}.compact header{padding-bottom:9px;margin-bottom:6px}.compact h1{font-size:22pt}.compact .lead{font-size:10.5pt}
@page{size:A4;margin:0}@page wide{size:A3 landscape;margin:0}@media print{html,body{background:white}.toolbar{display:none}.paper{margin:0;box-shadow:none}a{color:#245e78}}
'''
    html='<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Buku Belajar Pipeline Funding Management</title><style>'+css+'</style></head><body><div class="toolbar"><strong>Buku belajar pribadi · Pipeline Funding</strong><p><a href="MATERI-BELAJAR-UJIAN-MAGANG.pdf">Unduh PDF</a><a href="AUDIT-PROFESIONAL.md">Hasil peninjauan</a><a href="#page-2">Daftar isi</a></p></div>'+''.join(markup)+'</body></html>'
    (ROOT/'MATERI-BELAJAR-UJIAN-MAGANG.html').write_text(html,encoding='utf-8')
    metadata={'date':'2026-10-20','pages':len(pages),'widePages':sum(pg['kind']=='wide' for pg in pages),'sources':len(SOURCES),'tableCount':22,'columnCount':162,'pageIndex':[{'page':i,'title':p['title'],'section':p['section'],'kind':p['kind']} for i,p in enumerate(pages,1)]}
    (ROOT/'materi.metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    class Plain(HTMLParser):
        def __init__(self):super().__init__();self.parts=[]
        def handle_data(self,data):self.parts.append(data)
        def handle_starttag(self,tag,attrs):
            if tag in ['p','h3','li','tr','pre','div','aside']:self.parts.append('\n')
            if tag in ['td','th']:self.parts.append(' | ')
    readable=['# Buku belajar Pipeline Funding Management','Disusun 20 Oktober 2026; versi tata letak lengkap berada di PDF/HTML.','']
    for pg in pages:
        if pg['kind']=='wide':continue
        parser=Plain();parser.feed(pg['body'])
        readable += ['## '+pg['title'],pg['lead'],'',''.join(parser.parts),'']
    (ROOT/'MATERI-BELAJAR.md').write_text('\n'.join(readable),encoding='utf-8')
    print(f'Generated {len(pages)} pages ({metadata["widePages"]} A3 diagrams); {len(SOURCES)} official references.')


if __name__=='__main__':build()
