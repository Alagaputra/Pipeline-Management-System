"""Print-oriented Gane–Sarson layouts. Logical specifications live in build-dfd.py."""
from html import escape
from textwrap import wrap
import json

W, H = 3360, 2380
INK = '#172b3a'
MUTED = '#4f626e'
LINE = '#627680'
RULE = '#cbd5dc'
STORE = '#486d68'
FONT = 'Arial, Helvetica, sans-serif'
PAGES = [
    ('dfd-konteks', 'Diagram konteks', 'Batas Sistem Manajemen Pipeline Funding', 'DFD-00'),
    ('dfd-level-1', 'DFD Level 1', 'Dekomposisi proses 0 · Fungsi utama sistem', 'DFD-01'),
    ('dfd-level-2-pipeline', 'DFD Level 2 — Pipeline', 'Dekomposisi proses 3.0 · Pengelolaan peluang funding', 'DFD-02'),
    ('dfd-level-3-closing', 'DFD Level 3 — Closing', 'Dekomposisi proses 3.5 · Penyelesaian peluang Won/Lost', 'DFD-03'),
]


def txt(x, y, value, size=26, fill=INK, weight=400, anchor='middle', spacing=None):
    lines = [value] if isinstance(value, str) else value
    step = spacing or size*1.5
    return ''.join(f'<text x="{x}" y="{y+i*step}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(line))}</text>' for i, line in enumerate(lines))


def external(x, y, code, repeat=True, width=400, height=110):
    title, subtitle = ('PIC Funding', 'Konsumer / Komersil') if code == 'E1' else ('Head Funding', 'Pemantauan lintas divisi')
    duplicate = f'<path d="M{x+width-32} {y+12}l-10 16m22-16l-10 16" stroke="{LINE}" stroke-width="2"/>' if repeat else ''
    return f'''<g class="entity" data-entity="{code}"><rect x="{x}" y="{y}" width="{width}" height="{height}" fill="white" stroke="{INK}" stroke-width="2.4"/>{duplicate}
{txt(x+18,y+27,code,18,MUTED,600,'start')}{txt(x+width/2,y+53,title,27,weight=600)}{txt(x+width/2,y+88,subtitle,21,MUTED)}</g>'''


def proc(x, y, number, name, width=460, height=250):
    lines = wrap(name, 27)
    first = y+52+(height-52)/2+10-(len(lines)-1)*22
    return f'''<g class="process" data-process="{number}"><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" fill="#f8fafc" stroke="{INK}" stroke-width="2.5"/>
<path d="M{x} {y+52}H{x+width}" stroke="{INK}" stroke-width="1.5"/>{txt(x+24,y+36,number,26,weight=700,anchor='start')}{txt(x+width/2,first,lines,29,weight=600,spacing=44)}</g>'''


def storage(x, y, code, stores, repeat=True, width=460):
    duplicate = f'<path d="M{x+width-20} {y+10}l-10 15m22-15l-10 15" stroke="{STORE}" stroke-width="1.8"/>' if repeat else ''
    return f'''<g class="store" data-store="{code}"><path d="M{x+width} {y}H{x}V{y+78}H{x+width}M{x+70} {y}V{y+78}" fill="#f6faf9" stroke="{STORE}" stroke-width="2.2"/>{duplicate}
{txt(x+35,y+49,code,25,STORE,700)}{txt(x+88,y+48,stores[code][0],25,INK,500,'start')}</g>'''


def edge(path, x, y, label, width=52, anchor='middle', size=25):
    lines = wrap(label, width) if isinstance(label, str) else label
    return f'<g class="flow"><path d="{path}" fill="none" stroke="{LINE}" stroke-width="2.3" stroke-linejoin="round" marker-end="url(#arrow)"/>{txt(x,y,lines,size,MUTED,anchor=anchor)}</g>'


def legend():
    return f'''<path d="M100 2080H3260" stroke="{RULE}" stroke-width="1.5"/>
{txt(100,2123,'NOTASI GANE–SARSON',18,MUTED,700,'start')}
<rect x="100" y="2150" width="90" height="48" fill="white" stroke="{INK}" stroke-width="2"/>{txt(210,2182,'Entitas eksternal',25,anchor='start')}
<rect x="900" y="2150" width="90" height="48" rx="7" fill="#f8fafc" stroke="{INK}" stroke-width="2"/><path d="M900 2167H990" stroke="{INK}"/>{txt(1010,2182,'Proses bernomor',25,anchor='start')}
<path d="M1770 2150H1680V2198H1770M1702 2150V2198" fill="#f6faf9" stroke="{STORE}" stroke-width="2"/>{txt(1790,2182,'Penyimpanan data',25,anchor='start')}
<path d="M2560 2174H2650" stroke="{LINE}" stroke-width="2.3" marker-end="url(#arrow)"/>{txt(2670,2182,'Aliran data',25,anchor='start')}
{txt(100,2250,'Tanda garis miring pada simbol = pengulangan entitas / penyimpanan dengan ID yang sama. Rincian paket data: DFD.md.',22,MUTED,anchor='start')}'''


def sheet(root, index, body, note):
    name, title, subtitle, code = PAGES[index]
    header = txt(100,70,'BSN KC BEKASI  /  FUNDING',22,MUTED,700,'start')
    header += txt(100,137,title,52,weight=700,anchor='start')
    header += txt(100,183,subtitle,28,MUTED,anchor='start')
    header += txt(3260,70,f'{code}  /  REV. 02',22,MUTED,700,'end')
    header += txt(3260,111,'Dokumentasi perancangan sistem',21,MUTED,anchor='end')
    header += txt(3260,149,'20 Oktober 2026',21,MUTED,anchor='end')
    header += f'<path d="M100 211H3260" stroke="{INK}" stroke-width="2"/>'
    footer = legend()+txt(100,2300,note,22,MUTED,anchor='start')
    footer += txt(100,2349,'PIPELINE FUNDING MANAGEMENT SYSTEM',18,MUTED,600,'start')
    footer += txt(3260,2349,f'{index+1:02} / 04',20,MUTED,600,'end')
    markup = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1L9 5L0 9Z" fill="{LINE}"/></marker></defs>
<style>text{{font-family:{FONT}}}</style><rect width="{W}" height="{H}" fill="white"/>{header}{body}{footer}</svg>'''
    (root/f'{name}.svg').write_text(markup, encoding='utf-8')


def context(root, stores):
    body = external(100,825,'E1',False,width=420)
    body += proc(1380,760,'0','Sistem Manajemen Pipeline Funding',width=600,height=310)
    body += external(2840,825,'E2',False,width=420)
    for actor_right, process_left, incoming_path, outgoing_path, label_x in [
        (520,1380,'M520 860H1380','M1380 910H520',950),
        (1980,2840,'M2840 860H1980','M1980 910H2840',2410),
    ]:
        body += edge(incoming_path,label_x,756,['Data akses, referensi, pipeline,','target dan permintaan laporan'],size=27)
        body += edge(outgoing_path,label_x,1000,['Hasil akses, referensi, pipeline,','target dan laporan'],size=27)
    body += f'<path d="M100 1380H3260" stroke="{RULE}" stroke-width="1.5"/>'
    blocks = [
        (100,'E1  /  PIC FUNDING',['Mengelola peluang dan target divisinya.','Membaca ringkasan dan riwayat divisi.','CMS dikelola pada lingkup bersama.']),
        (1190,'E2  /  HEAD FUNDING',['Mengakses Konsumer dan Komersil.','Mengelola data sesuai divisi / lingkup.','Memantau laporan divisi atau gabungan.']),
        (2280,'BATAS SISTEM',['Nasabah dicatat sebagai data peluang.','Interaksi aplikasi melalui PIC dan Head.','Tidak ada integrasi sistem inti bank.']),
    ]
    for x, title, lines in blocks:
        body += txt(x,1450,title,24,INK,700,'start')
        body += txt(x,1510,lines,27,MUTED,anchor='start',spacing=48)
    body += txt(100,1805,'Paket masukan dan keluaran diuraikan pada Level 1; penyimpanan internal mulai ditampilkan pada Level 1.',26,MUTED,anchor='start')
    sheet(root,0,body,'Hierarki: konteks 0 → Level 1 (1.0–5.0) → Level 2 proses 3.0 → Level 3 proses 3.5.')


def logical_rows(root, index, rows, stores):
    body = txt(100,267,'ENTITAS EKSTERNAL',20,MUTED,700,'start')
    body += txt(1400,267,'PROSES',20,MUTED,700,'start')
    body += txt(2800,267,'PENYIMPANAN DATA',20,MUTED,700,'start')
    for i, (number, name, incoming, outgoing, accesses) in enumerate(rows):
        top = 300+i*340
        if i:
            body += f'<path d="M100 {top-5}H3260" stroke="#e2e7eb" stroke-width="1.3"/>'
        body += external(100,top+75,'E1')+external(100,top+205,'E2')
        body += proc(1400,top+45,number,name)
        for yin, yout, labelin, labelout in [(110,150,82,185),(240,280,222,325)]:
            body += edge(f'M500 {top+yin}H1400',950,top+labelin,incoming,width=64)
            body += edge(f'M1400 {top+yout}H500',950,top+labelout,outgoing,width=64)
        gap = 330/len(accesses)
        for j, (code, read, write) in enumerate(accesses):
            sy = top+j*gap+(gap-78)/2
            body += storage(2800,sy,code,stores)
            if read:
                target = sy+24
                port = top+100+(target-top)*0.52
                body += edge(f'M2800 {target}H2160L1930 {port}H1860',2480,sy+12,read,width=48)
            if write:
                target = sy+67
                port = top+100+(target-top)*0.52
                body += edge(f'M1860 {port}H1930L2160 {target}H2800',2480,sy+55,write,width=48)
    note = 'Akses PIC mengikuti divisinya; Head Funding mencakup kedua divisi. Simbol yang berulang mempertahankan ID yang sama.'
    if index == 2:
        note = 'Proses induk 3.0: masukan dan keluaran pipeline; penyimpanan D1, D2, D3, D5. Closing tidak menghapus peluang.'
    sheet(root,index,body,note)


def closing(root, level2, level3, edges, stores):
    body = ''
    positions = [(1450,400),(1450,840),(1450,1280),(2450,1280),(1450,1780)]
    for (_, number, name), (x,y) in zip(level3,positions):
        body += proc(x,y,number,name,height=190)
    for x, code in [(100,'E1'),(2860,'E2')]:
        body += external(x,430,code)+external(x,880,code)+external(x,1820,code)
    # Boundary input is the parent's closing packet; errors and success are its output packet.
    for path, x in [('M500 470H1450',975),('M2860 470H1910',2385)]:
        body += edge(path,x,376,['Hasil closing, tanggal,','nilai / alasan dan versi'],size=26)
    for path, x in [('M1450 520H500',975),('M1910 520H2860',2385)]:
        body += edge(path,x,582,'Hasil validasi / konflik',size=26)
    for path, x in [('M1450 935H500',975),('M1910 935H2860',2385)]:
        body += edge(path,x,1000,'Hasil validasi Won / Lost',size=26)
    for path, x in [('M1450 1875H500',975),('M1910 1875H2860',2385)]:
        body += edge(path,x,1945,'Hasil closing dan versi baru',size=26)
    body += storage(1450,250,'D3',stores)
    body += edge('M1680 328V400',1740,363,'Peluang aktif dan versi',anchor='start',size=25)
    body += edge('M1680 590V840',1740,709,['Data closing terverifikasi','dan peluang awal'],anchor='start',size=26)
    body += edge('M1680 1030V1280',1740,1149,['Data closing valid','dan snapshot awal'],anchor='start',size=26)
    body += storage(100,1336,'D3',stores)
    body += edge('M1450 1375H560',1005,1300,['Won/Lost, realisasi,','tanggal dan catatan'],size=26)
    body += edge('M1910 1375H2450',2180,1280,['Snapshot sebelum/sesudah','dan identitas pelaku'],size=25)
    body += storage(2450,1600,'D5',stores)
    body += edge('M2680 1470V1600',2740,1545,'Audit closing Won / Lost',anchor='start',size=25)
    body += edge('M2450 1435H2200V1690H1680V1780',1950,1585,['Data hasil closing','yang tersimpan'],size=26)
    body += storage(800,1660,'D1',stores)
    body += edge('M1260 1699H1370V1840H1450',1300,1790,'Identitas PIC',anchor='end',size=25)
    body += storage(2350,1760,'D2',stores)
    body += edge('M2350 1799H2100V1850H1910',2190,1735,'Nama produk dan divisi',size=25)
    sheet(root,3,body,'Proses induk 3.5 · Batas: E1, E2, D1, D2, D3, D5. Perubahan peluang dan audit disimpan dalam satu transaksi.')


def mermaid(root, level1, level2, level3, edges, stores):
    for name, rows in [('dfd-level-1',level1),('dfd-level-2-pipeline',level2)]:
        lines = ['flowchart LR','  %% Gane–Sarson pada SVG/PDF; bentuk penyimpanan bawaan pada Mermaid.',
                 '  E1["E1 · PIC Funding"]','  E2["E2 · Head Funding"]']
        for number, title, incoming, outgoing, accesses in rows:
            pid = 'process'+number.replace('.','')
            lines += [f'  {pid}("{number} · {title}")']
            for ent in ['E1','E2']:
                lines += [f'  {ent} -->|"{incoming}"| {pid}',f'  {pid} -->|"{outgoing}"| {ent}']
            for code, read, write in accesses:
                sid = 'store'+code+pid
                lines += [f'  {sid}[("{code} · {stores[code][0]}")]']
                if read:
                    lines += [f'  {sid} -->|"{read}"| {pid}']
                if write:
                    lines += [f'  {pid} -->|"{write}"| {sid}']
        (root/f'{name}.mmd').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    lines = ['flowchart LR','  E1["E1 · PIC Funding"]','  E2["E2 · Head Funding"]','  P0("0 · Sistem Manajemen Pipeline Funding")']
    for ent in ['E1','E2']:
        lines += [f'  {ent} -->|"Data akses, referensi, pipeline, target dan permintaan laporan"| P0',f'  P0 -->|"Hasil akses, referensi, pipeline, target dan laporan"| {ent}']
    (root/'dfd-konteks.mmd').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    lines = ['flowchart TB','  E1["E1 · PIC Funding"]','  E2["E2 · Head Funding"]']
    lines += [f'  {pid}("{number} · {title}")' for pid,number,title in level3]
    lines += [f'  {code}[("{code} · {stores[code][0]}")]' for code in ['D1','D2','D3','D5']]
    lines += [f'  {src} -->|"{label}"| {dst}' for src,dst,label in edges]
    (root/'dfd-level-3-closing.mmd').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def viewer(root):
    sheets = ''.join(f'''<section class="sheet" id="{name}"><div class="tools"><div><small>{code}</small><h2>{title}</h2></div><label>Perbesaran <input aria-label="Perbesaran {title}" type="range" min="100" max="220" value="100"></label><a href="{name}.png">PNG</a><a href="{name}.svg">SVG</a><a href="{name}.mmd">Mermaid</a></div><div class="scroll"><div class="canvas">{(root/f'{name}.svg').read_text(encoding='utf-8')}</div></div></section>''' for name,title,subtitle,code in PAGES)
    nav = ''.join(f'<a href="#{name}">{title}</a>' for name,title,_,_ in PAGES)
    html = f'''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Data Flow Diagram · BSN KC Bekasi</title><style>
*{{box-sizing:border-box}}body{{margin:0;color:{INK};background:#edf1f4;font:15px/1.6 Arial,sans-serif}}header{{background:white;border-top:5px solid {INK};padding:36px max(24px,calc((100vw - 1500px)/2));border-bottom:1px solid {RULE}}}header small,.tools small{{font-size:11px;letter-spacing:1.5px;color:{MUTED};font-weight:700}}h1{{font-size:34px;line-height:1.2;margin:12px 0}}header p{{color:{MUTED};max-width:850px}}a{{color:#255d72;text-underline-offset:3px}}nav,.downloads{{display:flex;gap:22px;flex-wrap:wrap}}nav{{margin-top:22px;padding-top:18px;border-top:1px solid {RULE}}}main{{max-width:1580px;margin:auto;padding:28px 20px}}.sheet{{background:white;border:1px solid {RULE};margin-bottom:28px;scroll-margin-top:16px}}.tools{{display:flex;gap:20px;flex-wrap:wrap;align-items:center;padding:16px 22px;border-bottom:1px solid {RULE}}}.tools>div{{margin-right:auto}}h2{{font-size:20px;line-height:1.3;margin:4px 0}}label{{display:flex;align-items:center;gap:10px;font-size:13px;color:{MUTED}}}input{{accent-color:#255d72}}.scroll{{overflow:auto}}.canvas{{width:100%;min-width:1100px}}svg{{display:block;width:100%;height:auto}}footer{{max-width:1580px;margin:auto;padding:0 20px 28px;color:{MUTED};font-size:13px}}@media(max-width:600px){{h1{{font-size:27px}}main{{padding:12px}}.tools{{padding:14px;gap:14px}}.tools>div{{width:100%}}}}@page{{size:A3 landscape;margin:8mm}}@media print{{body{{background:white}}header,.tools,footer{{display:none}}main{{padding:0;max-width:none}}.sheet{{margin:0;padding:0;border:0;height:279mm;display:flex;align-items:center;justify-content:center;break-after:page;break-inside:avoid}}.sheet:last-child{{break-after:auto}}.scroll{{overflow:visible;width:100%}}.canvas{{min-width:0;width:100%!important}}svg{{height:278mm;width:auto;max-width:100%;margin:auto}}}}
</style></head><body><header><small>BSN KC BEKASI / DOKUMENTASI SISTEM / REVISI 02</small><h1>Data Flow Diagram</h1><p>Diagram konteks dan Level 1–3 Sistem Manajemen Pipeline Funding. Notasi Gane–Sarson, penomoran hierarkis, dan pemetaan ke implementasi aplikasi.</p><div class="downloads"><a href="DFD.pdf">PDF lengkap · 4 halaman A3</a><a href="DFD.md">Kamus aliran dan penjelasan</a><a href="index.html">Dokumentasi sistem</a></div><nav>{nav}</nav></header><main>{sheets}</main><footer>Setiap entitas eksternal digambar terpisah. Simbol bertanda garis miring adalah pengulangan dengan ID yang sama. Berkas dapat dibuka tanpa internet.</footer><script>document.querySelectorAll('input').forEach(input=>input.addEventListener('input',()=>input.closest('.sheet').querySelector('.canvas').style.width=input.value+'%'));</script></body></html>'''
    (root/'DFD.html').write_text(html,encoding='utf-8')


def build(root, level1, level2, level3, edges, stores):
    context(root,stores)
    logical_rows(root,1,level1,stores)
    logical_rows(root,2,level2,stores)
    closing(root,level2,level3,edges,stores)
    mermaid(root,level1,level2,level3,edges,stores)
    viewer(root)
    metadata = {'width':W,'height':H,'revision':'02','notation':'Gane–Sarson',
                'level1Processes':len(level1),'level2Processes':len(level2),'level3Processes':len(level3),
                'level3Parent':'3.5','level3Stores':['D1','D2','D3','D5'],'logicalStores':stores}
    (root/'DFD.metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('DFD revision 02: four A3 diagrams, SVG, Mermaid, and offline viewer generated.')
