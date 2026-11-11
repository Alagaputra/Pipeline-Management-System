"""Create a single, complete ERD from the verified PostgreSQL catalog snapshot."""
from pathlib import Path
from html import escape
from collections import defaultdict
import heapq
import json
import re

ROOT = Path(__file__).resolve().parent.parent
schema = json.loads((ROOT/'schema.json').read_text(encoding='utf-8'))
W, H = 3440, 2600
positions = {
    'divisions': (80,200), 'users': (760,200), 'opportunities': (1440,200),
    'opportunity_assignments': (2120,200), 'personal_access_tokens': (2800,200),
    'division_products': (80,570), 'products': (80,850), 'target_scopes': (760,880),
    'annual_targets': (1440,1100), 'monthly_targets': (2120,900),
    'unit_realizations': (2120,1340), 'audit_events': (760,1330),
    'request_receipts': (1440,1570), 'branch_targets': (80,1330), 'sessions': (2800,880),
}
infra = ['password_reset_tokens','cache','cache_locks','jobs','job_batches','failed_jobs','migrations']
positions.update({t: (60+i*480,2040) for i,t in enumerate(infra)})
assert set(positions) == {t['table_name'] for t in schema['tables']}
cols = {t: [c for c in schema['columns'] if c['table_name'] == t] for t in positions}
cons = {t: [c for c in schema['constraints'] if c['table_name'] == t] for t in positions}
composites = defaultdict(list)
keys = defaultdict(lambda: defaultdict(list))
relations = []
for t in positions:
    for con in cons[t]:
        group = re.search(r'\(([^)]+)\)', con['definition'])
        fields = group[1].split(', ') if group else []
        if con['type'] in ('p','f') or (con['type']=='u' and len(fields)==1):
            for field in fields: keys[t][field].append({'p':'PK','f':'FK','u':'UK'}[con['type']])
        if con['type'] in ('p','u') and len(fields)>1:
            composites[t].append(('PK' if con['type']=='p' else 'UK')+' ('+', '.join(fields)+')')
        if con['type']=='f':
            match = re.match(r'FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)',con['definition'])
            assert match, con
            child_field,parent,parent_field=match.groups()
            nullable = next(c for c in cols[t] if c['column_name']==child_field)['is_nullable']=='YES'
            relations.append(dict(parent=parent,parent_field=parent_field,child=t,child_field=child_field,nullable=nullable,logical=False))
relations += [
    dict(parent='users',parent_field='id',child='personal_access_tokens',child_field='tokenable_id',nullable=False,logical=True),
    dict(parent='users',parent_field='id',child='sessions',child_field='user_id',nullable=True,logical=True),
]

def height(t): return 55+30*len(cols[t])+25+30*len(composites[t])
width = lambda t: 440 if t in infra else 520
for i,a in enumerate(positions):
    ax,ay=positions[a]
    for b in list(positions)[i+1:]:
        bx,by=positions[b]
        assert not (ax<bx+width(b) and ax+width(a)>bx and ay<by+height(b) and ay+height(a)>by), (a,b)

blocked=set()
for t,(x,y) in positions.items():
    for gx in range((x-20)//10,(x+width(t)+20)//10+1):
        for gy in range((y-20)//10,(y+height(t)+20)//10+1): blocked.add((gx,gy))
usage=defaultdict(int)

def route(start,end):
    sx,sy=start[0]//10,start[1]//10
    ex,ey=end[0]//10,end[1]//10
    initial=(sx,sy,2)
    queue=[((abs(sx-ex)+abs(sy-ey))*10,0,initial)]
    costs={initial:0}; previous={}
    while queue:
        _,cost,state=heapq.heappop(queue)
        if cost!=costs[state]: continue
        x,y,direction=state
        if (x,y)==(ex,ey):
            path=[]
            while state in previous:
                path.append((state[0]*10,state[1]*10)); state=previous[state]
            path.append(start); path.reverse()
            return path
        for dx,dy,nd in [(1,0,0),(-1,0,0),(0,1,1),(0,-1,1)]:
            nx,ny=x+dx,y+dy
            if not(2<=nx<=W//10-2 and 15<=ny<=198) or (nx,ny) in blocked: continue
            nc=cost+10+(16 if direction!=2 and direction!=nd else 0)+usage[(nx,ny)]*13
            ns=(nx,ny,nd)
            if nc>=costs.get(ns,float('inf')): continue
            costs[ns]=nc; previous[ns]=state
            heuristic=(abs(nx-ex)+abs(ny-ey))*10
            heapq.heappush(queue,(nc+heuristic,nc,ns))
    raise RuntimeError(f'Tidak ditemukan jalur relasi: {start} -> {end}')

def port(t,field,side):
    x,y=positions[t]
    row=next(i for i,c in enumerate(cols[t]) if c['column_name']==field)
    y+=70+row*30
    x+=width(t) if side==1 else 0
    return (x,y),(x+30*side,y)

palette={'divisions':'#4478ad','users':'#8054b9','products':'#26816b','opportunities':'#b47a3e','target_scopes':'#8c6843','annual_targets':'#278e98'}

def txt(x,y,value,size=18,fill='#25334a',weight=400,anchor='start',cls=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" class="{cls}">{escape(str(value))}</text>'

paths=[]
# Shorter edges first; later edges are routed around existing lines where practical.
relations.sort(key=lambda r: abs(positions[r['parent']][0]-positions[r['child']][0])+abs(positions[r['parent']][1]-positions[r['child']][1]))
for index,r in enumerate(relations):
    options=[]
    for a in [-1,1]:
        for b in [-1,1]:
            actual_a,ext_a=port(r['parent'],r['parent_field'],a)
            actual_b,ext_b=port(r['child'],r['child_field'],b)
            score=abs(ext_a[0]-ext_b[0])+abs(ext_a[1]-ext_b[1])
            options.append((score,actual_a,ext_a,actual_b,ext_b))
    _,actual_a,ext_a,actual_b,ext_b=min(options)
    points=route(ext_a,ext_b)
    for p in points: usage[(p[0]//10,p[1]//10)]+=1
    full=[actual_a]+points+[actual_b]
    reduced=[full[0]]
    for j in range(1,len(full)-1):
        p,q,s=full[j-1],full[j],full[j+1]
        if not((p[0]==q[0]==s[0]) or (p[1]==q[1]==s[1])): reduced.append(q)
    reduced.append(full[-1])
    color='#17858c' if r['logical'] else palette.get(r['parent'],'#687c96')
    d='M'+' L'.join(f'{x},{y}' for x,y in reduced)
    title=f"{r['child']}.{r['child_field']} → {r['parent']}.{r['parent_field']}"+(' (relasi logis, bukan FK SQL)' if r['logical'] else '')
    dash=' stroke-dasharray="12 9"' if r['logical'] else ''
    paths.append(f'<path class="relation" data-from="{r["parent"]}" data-to="{r["child"]}" d="{d}" fill="none" stroke="{color}" stroke-width="3" marker-start="url(#{"optional" if r["nullable"] else "one"})" marker-end="url(#many)"{dash}><title>{escape(title)}</title></path>')

cards=[]
for t,(x,y) in positions.items():
    w,h=width(t),height(t)
    color='#64758b' if t in infra else palette.get(t,'#44638f')
    if t in ('personal_access_tokens','request_receipts','audit_events','sessions'): color='#347e89'
    part=f'<g class="entity" data-table="{t}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="white" stroke="#c9d5e4" stroke-width="2"/>'
    part+=f'<path d="M{x+10} {y}H{x+w-10}Q{x+w} {y} {x+w} {y+10}V{y+55}H{x}V{y+10}Q{x} {y} {x+10} {y}" fill="{color}"/>'
    part+=txt(x+18,y+36,t,24,'white',700)
    for i,c in enumerate(cols[t]):
        top=y+55+i*30
        if i%2==0: part+=f'<rect x="{x+1}" y="{top}" width="{w-2}" height="30" fill="#f2f6fa"/>'
        tags='/'.join(sorted(set(keys[t][c['column_name']]),reverse=True))
        part+=txt(x+12,top+21,tags,14,'#42618d',700)
        part+=txt(x+79,top+21,c['column_name']+(' ?' if c['is_nullable']=='YES' else ''),18,cls='column-name')
        typ=c['udt_name']
        typ={'int8':'bigint','int4':'integer','int2':'smallint','bool':'boolean'}.get(typ,typ)
        if typ=='varchar': typ+=f"({c['character_maximum_length']})"
        part+=txt(x+w-15,top+21,typ,16,'#62728a',anchor='end')
    for i,label in enumerate(composites[t]): part+=txt(x+14,y+55+len(cols[t])*30+24+i*30,label,15,'#476079',600)
    part+='</g>'
    cards.append(part)

fk_count=sum(not r['logical'] for r in relations)
head=txt(70,64,'ENTITY RELATIONSHIP DIAGRAM',27,'#536f95',700)+txt(70,119,'Pipeline Funding Management System',46,'#22334a',700)
head+=txt(W-70,77,f'{len(positions)} tabel  ·  {len(schema["columns"])} kolom  ·  {fk_count} FK SQL',23,'#526881',600,'end')
head+=txt(W-70,118,'PostgreSQL · Implementasi 19 Oktober 2026',20,'#526881',400,'end')
legend=txt(2820,1360,'Cara membaca ERD',26,'#2e6679',700)
for i,line in enumerate([
    'PK = primary key; FK = foreign key.', 'UK = unique key; ? = boleh NULL.',
    'Garis penuh: FK fisik PostgreSQL.', 'Garis putus-putus: relasi logis.',
    'Ujung || = tepat satu; o| = opsional.', 'Ujung kaki gagak = nol atau banyak.',
    'Warna garis mengikuti tabel induk.', 'Hubungan tepat ke baris kolom FK.',
    'Audit resource_type / resource_id', 'bukan FK SQL ke tabel transaksi.',
    'CMS memakai scope shared satu kali.',
]): legend+=txt(2820,1400+i*31,line,21,'#526881')
legend+=txt(2820,1780,'Tidak ada tabel terpisah untuk',21,'#526881')+txt(2820,1811,'Dashboard, Tim, dan Riwayat.',21,'#526881')
band=f'<rect x="45" y="1950" width="{W-90}" height="545" rx="18" fill="#eef2f7"/>'
band+=txt(65,1992,'INFRASTRUKTUR LARAVEL — TABEL TANPA FK SQL KE DOMAIN',23,'#5c6d85',700)
footer=txt(65,2545,'Sumber: metadata skema PostgreSQL dan migration Laravel. Seluruh atribut ditampilkan; garis tidak menunjukkan aliran permintaan API.',19,'#62728a')
markers='''<defs>
<marker id="one" viewBox="-14 -9 24 18" refX="0" refY="0" markerWidth="18" markerHeight="15" orient="auto-start-reverse"><path d="M-4 -7V7 M3 -7V7" fill="none" stroke="context-stroke" stroke-width="2"/></marker>
<marker id="optional" viewBox="-16 -9 26 18" refX="0" refY="0" markerWidth="20" markerHeight="15" orient="auto-start-reverse"><circle cx="-7" cy="0" r="4" fill="white" stroke="context-stroke" stroke-width="1.6"/><path d="M3 -7V7" stroke="context-stroke" stroke-width="2"/></marker>
<marker id="many" viewBox="-22 -10 25 20" refX="0" refY="0" markerWidth="23" markerHeight="18" orient="auto"><path d="M-12 -8L0 0L-12 8" fill="none" stroke="context-stroke" stroke-width="1.8"/><circle cx="-18" cy="0" r="3" fill="white" stroke="context-stroke" stroke-width="1.5"/></marker>
</defs>'''
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ERD lengkap 22 tabel Pipeline Funding Management">
<title>ERD lengkap database Pipeline Funding Management</title><style>text{{font-family:'Segoe UI',Arial,sans-serif}}.relation{{opacity:.82}}</style>{markers}<rect width="{W}" height="{H}" fill="#fcfdff"/>{head}{band}{''.join(paths)}{''.join(cards)}{legend}{footer}</svg>'''
(ROOT/'ERD-LENGKAP.svg').write_text(svg,encoding='utf-8')
html=f'''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ERD lengkap — Pipeline Funding</title><style>
*{{box-sizing:border-box}}body{{margin:0;font:16px 'Segoe UI',sans-serif;background:#edf1f7;color:#24354d}}header{{padding:20px 28px;background:white;border-bottom:1px solid #d3deeb}}h1{{font-size:24px;margin:0 0 12px}}.actions{{display:flex;align-items:center;gap:20px;flex-wrap:wrap}}a{{color:#5e3ca3}}label{{display:flex;gap:10px;align-items:center}}main{{margin:20px;overflow:auto;border:1px solid #d3deeb;background:white}}#canvas{{width:100%;min-width:1000px}}svg{{display:block;width:100%;height:auto}}.entity{{cursor:pointer}}svg.active .relation{{opacity:.10}}svg.active .relation.selected{{opacity:1;stroke-width:5}}svg.active .entity{{opacity:.45}}svg.active .entity.selected{{opacity:1}}@page{{size:A1 landscape;margin:12mm}}@media print{{body{{background:white}}header{{display:none}}main{{margin:0;border:0;overflow:visible}}#canvas{{width:100%!important;min-width:0}}svg{{width:100%;max-height:564mm}}}}
</style></head><body><header><h1>ERD lengkap — 22 tabel dalam satu diagram</h1><div class="actions"><a href="ERD-LENGKAP.png">Gambar PNG</a><a href="ERD-LENGKAP.pdf">PDF satu halaman</a><a href="ERD-LENGKAP.svg">SVG</a><a href="erd-lengkap.mmd">Sumber Mermaid</a><label>Perbesar <input id="zoom" type="range" min="100" max="300" value="100"></label><span>Klik tabel untuk menyorot relasinya; klik kembali untuk melihat semua.</span></div></header><main><div id="canvas">{svg}</div></main><script>
document.querySelector('#zoom').addEventListener('input',event=>document.querySelector('#canvas').style.width=event.target.value+'%');let active='';document.querySelectorAll('.entity').forEach(node=>node.addEventListener('click',()=>{{active=active===node.dataset.table?'':node.dataset.table;document.querySelector('svg').classList.toggle('active',Boolean(active));const linked=new Set([active]);document.querySelectorAll('.relation').forEach(path=>{{const yes=path.dataset.from===active||path.dataset.to===active;path.classList.toggle('selected',yes);if(yes){{linked.add(path.dataset.from);linked.add(path.dataset.to)}}}});document.querySelectorAll('.entity').forEach(entity=>entity.classList.toggle('selected',linked.has(entity.dataset.table)))}}));
</script></body></html>'''
(ROOT/'ERD-LENGKAP.html').write_text(html,encoding='utf-8')
(ROOT/'ERD-LENGKAP.metadata.json').write_text(json.dumps(dict(tables=len(positions),columns=len(schema['columns']),sql_foreign_keys=fk_count,logical_relations=2,width=W,height=H),indent=2)+'\n',encoding='utf-8')
print(f'ERD gabungan: {len(positions)} tabel, {len(schema["columns"])} kolom, {fk_count} FK SQL dan 2 relasi logis.')
