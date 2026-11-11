"""Generate offline documentation from the exported PostgreSQL metadata."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / 'schema.json').read_text(encoding='utf-8'))
INK, MUTED, PURPLE, TEAL, BLUE = '#241e3b', '#665e77', '#7351c5', '#237e74', '#426ba6'
PURPOSE = {
    'divisions': 'Master divisi Konsumer dan Komersil.',
    'users': 'Akun PIC dan Head Funding. Password berupa hash pada kolom password.',
    'products': 'Master produk dana (IDR) dan layanan (UNIT).',
    'division_products': 'Pasangan produk yang tersedia untuk setiap divisi; PK komposit.',
    'opportunities': 'Peluang dana, status ketertarikan, tindak lanjut, hasil closing, dan realisasi.',
    'opportunity_assignments': 'Riwayat penugasan/pergantian PIC pada peluang.',
    'target_scopes': 'Lingkup komersil, konsumer, atau shared. Shared tidak terikat satu divisi.',
    'annual_targets': 'Satu target per lingkup, produk, dan tahun.',
    'monthly_targets': 'Rincian target bulanan dari target tahunan.',
    'unit_realizations': 'Realisasi layanan dalam unit per bulan; bukan realisasi dana Won.',
    'branch_targets': 'Target cabang kompatibilitas versi lama; bukan penyebut target dana utama.',
    'audit_events': 'Pelaku, waktu, aksi, dan snapshot sebelum/sesudah perubahan.',
    'request_receipts': 'Hasil sukses permintaan tulis untuk percobaan ulang yang aman.',
    'personal_access_tokens': 'Token Laravel Sanctum yang disimpan sebagai hash.',
    'password_reset_tokens': 'Struktur bawaan Laravel untuk token reset password; tidak berarti ada fitur reset di UI.',
    'sessions': 'Penyimpanan sesi bawaan Laravel; autentikasi SPA ini menggunakan bearer token Sanctum.',
    'cache': 'Penyimpanan cache Laravel.', 'cache_locks': 'Kunci cache Laravel.',
    'jobs': 'Antrean pekerjaan Laravel; bukan jalur wajib simpan peluang/target saat ini.',
    'job_batches': 'Metadata kelompok pekerjaan Laravel.',
    'failed_jobs': 'Catatan pekerjaan antrean yang gagal.',
    'migrations': 'Riwayat migration yang sudah dijalankan.',
}
DOMAIN = ['divisions', 'users', 'products', 'division_products', 'opportunities',
          'opportunity_assignments', 'target_scopes', 'annual_targets', 'monthly_targets',
          'unit_realizations', 'branch_targets', 'audit_events', 'request_receipts']
ORDER = DOMAIN + ['personal_access_tokens', 'password_reset_tokens', 'sessions', 'cache',
                  'cache_locks', 'jobs', 'job_batches', 'failed_jobs', 'migrations']
assert set(ORDER) == {t['table_name'] for t in SCHEMA['tables']}
columns = {t: [c for c in SCHEMA['columns'] if c['table_name'] == t] for t in ORDER}
constraints = {t: [c for c in SCHEMA['constraints'] if c['table_name'] == t] for t in ORDER}

def sqltype(c):
    name = c['data_type']
    if name == 'character varying':
        return f"varchar({c['character_maximum_length']})"
    return name

def write_dictionary():
    lines = ['# Desain database — Pipeline Funding Management', '',
        'Versi implementasi: **19 Oktober 2026**. Disusun dari metadata PostgreSQL lokal dan migration Laravel, bukan rancangan MySQL lama.', '',
        f"Database memuat **{len(ORDER)} tabel dan {len(SCHEMA['columns'])} kolom**: 13 tabel domain, 1 tabel autentikasi Sanctum, dan 8 tabel infrastruktur Laravel. Tidak ada isi record atau kredensial yang diekspor.", '',
        '## Diagram', '',
        '- [ERD gabungan seluruh 22 tabel dalam satu gambar](ERD-LENGKAP.png)',
        '- [PDF ERD gabungan satu halaman](ERD-LENGKAP.pdf)',
        '- [ERD master dan pipeline](erd-pipeline.png)',
        '- [ERD target dan realisasi](erd-target.png)',
        '- [ERD autentikasi dan audit](erd-keamanan.png)',
        '- [Sumber Mermaid lengkap, 22 tabel](erd-lengkap.mmd)', '',
        'Gambar menampilkan atribut dan relasi utama supaya terbaca. Kamus berikut mencakup setiap kolom, FK, UNIQUE, dan indeks. Garis putus-putus berarti hubungan logis yang tidak ditegakkan sebagai FK SQL.', '',
        '## Relasi dan ketentuan utama', '',
        '1. Divisi memiliki banyak akun dan peluang. `users.division_id` boleh NULL; akun Head pada konfigurasi saat ini tidak mempunyai satu divisi tetap.',
        '2. Produk dan divisi berelasi banyak-ke-banyak melalui `division_products`. Kesesuaian PIC/produk/divisi diperiksa controller; FK individual saja tidak menjamin pasangan tersebut.',
        '3. Peluang dana merujuk satu divisi, produk IDR, dan PIC. Perpindahan PIC dicatat pada `opportunity_assignments`.',
        '4. Won/Lost tetap berada di `opportunities`. Halaman Riwayat, Dashboard, dan Tim tidak mempunyai tabel salinan.',
        '5. `annual_targets` unik pada `(scope_code, product_id, year)`. `monthly_targets` dan `unit_realizations` masing-masing unik pada `(annual_target_id, month)`.',
        '6. Rentang bulan 1–12 dan tahun 2000–2100 ditegakkan validasi API. Tidak ada CHECK SQL rentang tersebut pada skema yang diperiksa.',
        '7. CMS menggunakan scope `shared`, dihitung satu kali. Bale Syariah dan QRIS milik Konsumer. Dana dan unit tidak dijumlahkan.',
        '8. `target_scopes.division_id` tidak mempunyai UNIQUE SQL: satu divisi secara struktur dapat dirujuk beberapa scope, walaupun seeder saat ini membuat satu scope per divisi.',
        '9. `version` menjaga konflik pembaruan. Simpan satu formulir target serta closing berlangsung dalam transaksi; konflik membatalkan perubahan formulir.',
        '10. `request_receipts` unik pada `(user_id, request_key)`. Hasil sukses dan perubahan bisnis disimpan di transaksi yang sama; key yang sama dengan payload berbeda ditolak.',
        '11. `audit_events.resource_type/resource_id` adalah referensi logis, bukan FK. `actor_id` adalah FK yang boleh NULL.',
        '12. `personal_access_tokens.tokenable_type/tokenable_id` merupakan relasi polimorfik Sanctum tanpa FK SQL ke `users`. `sessions.user_id` juga hanya berindeks, bukan FK.', '',
        '## Tipe data fisik dan validasi', '',
        'Nilai dana/target disimpan sebagai **bigint**, bukan DECIMAL atau float. PostgreSQL tidak memiliki BIGINT UNSIGNED: aturan nonnegatif diterapkan pada validasi API. Status dan role disimpan sebagai varchar, bukan tipe ENUM PostgreSQL. Snapshot audit memakai `json`. Kolom waktu menggunakan `timestamp without time zone`; DATE dipakai untuk tanggal bisnis. Tipe dan panjang persis per kolom tercantum di bawah.', '',
        'Target nol berarti belum ditetapkan. Realisasi dana berasal dari Won menurut tahun tanggal closing. Realisasi unit berasal dari jumlah `unit_realizations.units` dalam satu tahun. Total target bulanan tidak diwajibkan sama dengan target tahunan pada aturan saat ini.', '',
        '## Ringkasan tabel', '', '| Tabel | Kelompok | Fungsi |', '| --- | --- | --- |']
    for t in ORDER:
        group = 'Domain' if t in DOMAIN else 'Autentikasi' if t == 'personal_access_tokens' else 'Infrastruktur'
        lines.append(f'| `{t}` | {group} | {PURPOSE[t]} |')
    lines += ['', '## Kamus kolom, constraint, dan indeks', '']
    for t in ORDER:
        lines += [f'### {t}', '', PURPOSE[t], '', '| Kolom | Tipe PostgreSQL | NULL | Default |', '| --- | --- | --- | --- |']
        for c in columns[t]:
            default = c['column_default'] if c['column_default'] is not None else '—'
            lines.append(f"| `{c['column_name']}` | `{sqltype(c)}` | {'Ya' if c['is_nullable'] == 'YES' else 'Tidak'} | `{default}` |")
        if constraints[t]:
            lines += ['', 'Constraint SQL:', '']
            lines += [f"- `{c['definition']}`" for c in constraints[t]]
        indexes = [i for i in SCHEMA['indexes'] if i['table_name'] == t]
        if indexes:
            lines += ['', 'Indeks fisik:', '', '```sql'] + [i['definition']+';' for i in indexes] + ['```']
        lines.append('')
    lines += ['## Sumber implementasi', '',
        '- `src/backend/database/migrations/0001_01_01_000000_create_users_table.php`',
        '- `src/backend/database/migrations/0001_01_01_000001_create_cache_table.php`',
        '- `src/backend/database/migrations/0001_01_01_000002_create_jobs_table.php`',
        '- `src/backend/database/migrations/2026_09_14_073227_create_personal_access_tokens_table.php`',
        '- `src/backend/database/migrations/2026_09_14_080000_create_pipeline_tables.php`',
        '- `src/backend/database/migrations/2026_10_19_000001_create_request_receipts_table.php`',
        '- `src/backend/database/seeders/DatabaseSeeder.php`',
        '- Metadata aktual: `schema.json`; dapat diperbarui memakai `scripts/export-schema.php`.', '']
    (ROOT/'DESAIN-DATABASE.md').write_text('\n'.join(lines), encoding='utf-8')

def write_mermaid():
    lines = ['erDiagram', '    %% FK dan tipe fisik berasal dari PostgreSQL. Garis putus-putus: relasi logis.']
    for t in ORDER:
        for k in constraints[t]:
            if k['type'] != 'f': continue
            m = re.match(r'FOREIGN KEY \(([^)]+)\) REFERENCES (\w+)\(([^)]+)\)', k['definition'])
            assert m, k
            child, parent, _ = m.groups()
            column = next(c for c in columns[t] if c['column_name'] == child)
            cardinal = 'o|' if column['is_nullable'] == 'YES' else '||'
            lines.append(f'    {parent} {cardinal}--o{{ {t} : {child}')
    lines += ['    users ||..o{ personal_access_tokens : "tokenable (logis)"',
              '    users o|..o{ sessions : "user_id (logis)"']
    for t in ORDER:
        lines.append(f'    {t} {{')
        for c in columns[t]:
            name = c['column_name']
            tags = []
            for k in constraints[t]:
                m = re.search(r'\(([^)]+)\)', k['definition'])
                if m and name in [x.strip() for x in m[1].split(',')]:
                    tag = {'p':'PK', 'f':'FK', 'u':'UK'}.get(k['type'])
                    if tag and (tag != 'UK' or ',' not in m[1]): tags.append(tag)
            typ = c['udt_name'].replace('int8','bigint').replace('int4','integer').replace('int2','smallint')
            note = 'nullable' if c['is_nullable'] == 'YES' else 'required'
            lines.append(f'        {typ} {name}' + (' '+', '.join(sorted(set(tags))) if tags else '') + f' "{note}"')
        lines.append('    }')
    (ROOT/'erd-lengkap.mmd').write_text('\n'.join(lines)+'\n', encoding='utf-8')

def text(x, y, content, size=18, color=INK, weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(content))}</text>'

def panel(x,y,w,h,title,lines,color=PURPLE, size=18):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#fff" stroke="#ded8ea" stroke-width="1.5"/>'
    out += f'<path d="M{x+16} {y}H{x+w-16}Q{x+w} {y} {x+w} {y+16}V{y+52}H{x}V{y+16}Q{x} {y} {x+16} {y}" fill="{color}"/>'
    out += text(x+20,y+34,title,20,'#fff',700)
    for i, line in enumerate(lines): out += text(x+20,y+84+i*29,line,size)
    return out

def link(path,label='',x=0,y=0,dashed=False):
    out = f'<path d="{path}" fill="none" stroke="{TEAL if dashed else "#89819a"}" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#arrow)"'+(' stroke-dasharray="8 6"' if dashed else '')+'/>'
    if label:
        width = len(label)*8.3+18
        out += f'<rect x="{x-7}" y="{y-19}" width="{width}" height="27" rx="5" fill="#f7f5fb"/>' + text(x,y,label,15,MUTED,600)
    return out

def note(x,y,w,title,lines,color='#efebf8'):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{64+len(lines)*28}" rx="14" fill="{color}"/>' + text(x+20,y+32,title,19,PURPLE,700)
    return out + ''.join(text(x+20,y+65+i*28,s,17,MUTED) for i,s in enumerate(lines))

def svg(name,title,subtitle,body,height=1120):
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title><desc>{escape(subtitle)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="none" stroke="#89819a" stroke-width="1.4"/></marker></defs>
<style>text{{font-family:'Segoe UI',Arial,sans-serif}}</style><rect width="1600" height="{height}" fill="#faf9fd"/>
{text(50,42,'PIPELINE FUNDING MANAGEMENT  /  DESAIN SISTEM  /  19 OKTOBER 2026',15,PURPLE,700)}
{text(50,88,title,34,INK,700)}{text(50,118,subtitle,18,MUTED)}{body}
<path d="M50 {height-62}H1550" stroke="#ded8ea"/>{text(50,height-32,'PK = primary key  ·  FK = foreign key  ·  UK = unique  ·  ? = nullable  ·  1:N = satu ke banyak  ·  putus-putus = relasi logis',16,MUTED)}
{text(1550,height-32,'PostgreSQL · Laravel · Vue.js',16,MUTED,400,'end')}</svg>'''
    (ROOT/f'{name}.svg').write_text(content,encoding='utf-8')

def build_pipeline():
    body = ''.join([
        link('M390 225H630','0..1 divisi / N akun',420,210),
        link('M220 342V480','1:N',236,420),
        link('M1380 365V425H220V480','produk 1:N pasangan divisi',900,417),
        link('M390 290H470V460H710V490','divisi 1:N peluang',480,450),
        link('M800 385V490','PIC 1:N',815,451),
        link('M1210 300H1110V680H1000','produk 1:N',1030,703),
        link('M1000 590H1200','1:N',1072,575),
        link('M970 250H1125V465H1370V500','PIC 1:N',1245,455),
        link('M630 335H440V755H240V790','actor 1:N',450,744),
        link('M430 910H520V800H600','resource_type / id',455,900,True),
        panel(50,160,340,182,'divisions',['PK id · bigint','UK code · varchar(30)','name · varchar(80)']),
        panel(630,160,340,225,'users',['PK id · bigint','FK division_id? → divisions','UK username · varchar(50)','name · password (hash)','role · is_active']),
        panel(1210,160,340,205,'products',['PK id · bigint','UK code · varchar(40)','name · varchar(80)','measure: IDR / UNIT']),
        panel(50,480,340,145,'division_products',['PK, FK division_id','PK, FK product_id']),
        panel(600,490,400,370,'opportunities',[
            'PK id · UK legacy_id?','FK division_id · pic_id · product_id',
            'customer_name · segment','nominal · realization : bigint',
            'interest_status · outcome','recorded_date · follow_up_date?',
            'follow_up_completed · closed_date?', 'notes? · lost_reason?',
            'FK created_by? · updated_by?', 'version · timestamps'],size=17),
        panel(1200,500,350,254,'opportunity_assignments',[
            'PK id · FK opportunity_id','FK pic_id → users','assigned_at? · unassigned_at?',
            'FK changed_by? → users','source · timestamps'],size=17),
        panel(50,790,380,225,'audit_events',[
            'PK id · FK actor_id? → users','resource_type · resource_id',
            'action · before_data? · after_data?', 'occurred_at · source'],color=TEAL,size=17),
        note(600,910,950,'Status ketertarikan berbeda dengan hasil closing',[
            'Cold / Warm / Hot = ketertarikan. Active / Won / Lost = hasil peluang.',
            'Riwayat membaca opportunities yang sama; tidak membuat tabel salinan.',
            'Kolom pembuat/editor/changed_by merujuk users; FK lengkap ada di kamus data.']),
    ])
    svg('erd-pipeline','ERD 01 — Master dan pipeline','Atribut utama; kardinalitas dan FK lengkap tersedia pada DESAIN-DATABASE.md dan erd-lengkap.mmd.',body)

def build_target():
    body = ''.join([
        link('M380 240H570','0..1 divisi / N scope',402,225),
        link('M770 375V500','1:N',790,449),
        link('M380 560H570','produk 1:N',407,546),
        link('M970 565H1080V255H1190','1:N',1096,240),
        link('M970 665H1190','1:N',1053,650),
        link('M50 290H25V920H50','1:N',30,798),
        panel(50,160,330,211,'divisions',['PK id · bigint','UK code','Konsumer / Komersil']),
        panel(50,450,330,211,'products',['PK id · UK code','measure: IDR / UNIT','Dana dan unit dipisahkan']),
        panel(570,160,400,215,'target_scopes',[
            'PK code · varchar(30)','FK division_id? → divisions','label · timestamps',
            'komersil / konsumer / shared']),
        panel(570,500,400,285,'annual_targets',[
            'PK id · FK scope_code','FK product_id → products','year · target_value : bigint',
            'FK updated_by? → users','version · timestamps','UK(scope_code, product_id, year)']),
        panel(1190,160,360,215,'monthly_targets',[
            'PK id · FK annual_target_id','month · target_value : bigint','timestamps','UK(annual_target_id, month)'],size=17),
        panel(1190,500,360,270,'unit_realizations',[
            'PK id · FK annual_target_id','month · units : bigint','FK updated_by? → users',
            'version · timestamps','UK(annual_target_id, month)'],color=TEAL,size=17),
        panel(50,820,420,215,'branch_targets',[
            'PK id · FK division_id','branch_code · year · target_value',
            'FK updated_by? · version','UK(division_id, branch_code, year)'],color=BLUE,size=17),
        note(570,840,980,'Lingkup target dan sumber realisasi',[
            'CMS: scope shared, satu target untuk kedua divisi. Bale Syariah / QRIS: Konsumer.',
            'Realisasi dana: opportunities berstatus Won, menurut tahun closed_date.',
            'Realisasi layanan: jumlah units bulanan. Target cabang lama tetap disimpan.',
            'Bulan 1–12 dan tahun 2000–2100 diperiksa API; bukan CHECK SQL.']),
    ])
    svg('erd-target','ERD 02 — Target dan realisasi','Target tahunan, rincian bulanan, realisasi layanan, dan data target cabang kompatibilitas.',body)

def build_security():
    body = ''.join([
        link('M400 250H610','1:N · polimorfik',420,235,True),
        link('M400 335H500V475H1350V440','1:N permintaan tersimpan',680,463),
        link('M400 370H485V710H610','actor 0..1 / N audit',500,560),
        link('M1010 730H1160','referensi logis',1025,715,True),
        panel(50,160,350,250,'users',[
            'PK id · FK division_id?','UK username · email?','password: hash, bukan plaintext',
            'role: pic / head','is_active · timestamps'],size=17),
        panel(610,160,400,250,'personal_access_tokens',[
            'PK id · UK token (hash)','tokenable_type · tokenable_id',
            'name · abilities?', 'last_used_at? · expires_at?', 'timestamps'],color=BLUE,size=17),
        panel(1160,160,390,280,'request_receipts',[
            'PK id · FK user_id → users','request_key : uuid','request_hash : varchar(64)',
            'status_code · response_body','created_at','UK(user_id, request_key)'],color=TEAL,size=17),
        panel(610,600,400,270,'audit_events',[
            'PK id · FK actor_id? → users','resource_type · resource_id','action',
            'before_data? · after_data? : json','occurred_at · source'],size=17),
        note(50,600,400,'8 tabel infrastruktur Laravel',[
            'password_reset_tokens · sessions', 'cache · cache_locks', 'jobs · job_batches · failed_jobs',
            'migrations', 'sessions.user_id: indeks, bukan FK.',
            'Tabel tersedia tidak berarti semua', 'fiturnya diaktifkan pada halaman.']),
        note(1160,600,390,'Referensi resource audit',[
            'opportunity', 'annual_target', 'unit_realization', 'branch_target',
            'resource_id disimpan sebagai teks.', 'Tidak ada FK SQL ke empat tabel.']),
        note(610,930,940,'Simpan dan retry berada dalam transaksi yang sama',[
            'Key + payload sama: hasil sukses sebelumnya dikembalikan tanpa duplikasi.',
            'Payload berbeda pada key yang sama atau versi lama: konflik HTTP 409.']),
    ])
    svg('erd-keamanan','ERD 03 — Autentikasi, audit, dan retry','Relasi token polimorfik dan referensi audit dibedakan dari foreign key fisik PostgreSQL.',body)

def build_architecture():
    body = ''.join([
        text(50,165,'01  PENGGUNA',17,PURPLE,700),
        panel(50,200,290,210,'PIC / Head Funding',[
            'Konsumer · Komersil','Browser desktop / ponsel', 'Akses mengikuti divisi dan role'],size=17),
        link('M340 300H410','UI',358,285),
        text(410,165,'02  FRONTEND · VUE.JS',17,PURPLE,700),
        panel(410,200,480,210,'Vue Router + halaman',[
            'Dashboard · Pipeline · Target', 'Riwayat · Tim · Login',
            'Chart.js: grafik laporan', 'Komponen kartu, formulir, dan dialog'],size=18),
        panel(410,465,480,210,'State dan layanan API',[
            'useSession · usePipeline', 'services/api.js: fetch + bearer token',
            'Idempotency-Key untuk penyimpanan', 'Guard isian, sesi, tahun, dan divisi'],color=BLUE,size=18),
        link('M650 410V465','state / aksi',665,448),
        link('M890 565H950V300H1020','HTTP / JSON',903,447),
        text(1020,165,'03  BACKEND · LARAVEL REST API',17,PURPLE,700),
        panel(1020,200,530,210,'Middleware dan autentikasi',[
            'Login: pembatasan percobaan', 'Sanctum: validasi bearer token',
            'IdempotentWrite: transaksi dan replay', 'Controller: izin divisi dan validasi input'],size=18),
        panel(1020,465,530,240,'Controller + logika bisnis',[
            'AuthController · LookupController', 'OpportunityController · TargetController',
            'ReportController → DashboardReport', 'WritesAudit: catatan perubahan',
            'Eloquent Models: baca / tulis data'],size=18),
        link('M1285 410V465','request terautentikasi',1300,447),
        link('M1285 705V800','query / transaksi',1300,760),
        panel(1020,800,530,190,'PostgreSQL',[
            '13 tabel domain + Sanctum + infrastruktur', 'FK · UNIQUE · row lock · version',
            'Data peluang, target, audit, request_receipts'],color=TEAL,size=18),
        note(50,760,840,'Alur data dan batas sistem',[
            'Browser mengirim aksi; Laravel memvalidasi, menyimpan, lalu mengembalikan JSON.',
            'DashboardReport menghitung laporan di backend; Chart.js menggambar di browser.',
            'Token ada di browser. Data operasional tetap berada di PostgreSQL.',
            'Lokal: frontend 5173 → proxy /api → Laravel 8000 → PostgreSQL 5432.',
            'Aplikasi ini mencatat pipeline; tidak menjalankan transaksi sistem inti bank.']),
    ])
    svg('arsitektur-sistem','Arsitektur aplikasi yang diterapkan','Pola client–server berlapis: antarmuka Vue.js, Laravel REST API, dan penyimpanan relasional PostgreSQL.',body)

def build_html():
    sheets = [
        ('arsitektur-sistem', 'Arsitektur sistem', 'Browser → Vue.js → Laravel REST API → PostgreSQL. Perhitungan laporan berada di backend; grafik dirender di frontend.'),
        ('erd-pipeline', 'Database: master dan pipeline', 'Relasi divisi, akun, produk, peluang, riwayat PIC, dan audit. Atribut utama ditampilkan; kamus data mencakup seluruh kolom.'),
        ('erd-target', 'Database: target dan realisasi', 'Target dana dan unit memiliki lingkup yang jelas. CMS dipakai bersama; realisasi dana berasal dari closing Won.'),
        ('erd-keamanan', 'Database: autentikasi dan audit', 'FK SQL, relasi polimorfik, dan referensi logis dibedakan. Hasil retry disimpan atomik bersama perubahan bisnis.'),
    ]
    parts = []
    for index,(name,title,description) in enumerate(sheets):
        parts.append(f'''<section id="{name}" class="sheet"><div class="section-head"><span>0{index+1} / 04</span><h2>{title}</h2><p>{description}</p></div>
<div class="tools"><label>Perbesaran <input type="range" min="100" max="200" value="100" aria-label="Perbesaran {title}"></label><a href="{name}.png">PNG</a><a href="{name}.svg">SVG</a></div>
<div class="diagram-scroll"><div class="diagram-canvas">{(ROOT/f'{name}.svg').read_text(encoding='utf-8')}</div></div></section>''')
    css = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f6f4fa;color:#241e3b;font:16px/1.6 'Segoe UI',Arial,sans-serif}header{background:#251b3b;color:white;padding:42px max(24px,calc((100vw - 1320px)/2))}header small{letter-spacing:2px;color:#cab8f4}h1{font-size:36px;line-height:1.2;margin:14px 0}header p{max-width:900px;color:#ded4ed}a{color:#6640b1}header a{color:white}nav{display:flex;gap:22px;flex-wrap:wrap;padding:16px 24px;background:white;border-bottom:1px solid #e5dfed}nav a{text-decoration:none;font-size:14px;font-weight:600}main{max-width:1416px;margin:auto;padding:24px}.sheet,.files{background:white;border:1px solid #e3ddec;border-radius:16px;margin:0 0 28px;padding:24px;scroll-margin-top:20px}.section-head span{font-size:12px;color:#7351c5;letter-spacing:1px;font-weight:700}h2{margin:6px 0;font-size:26px}.section-head p{color:#665e77;margin:6px 0 20px}.tools{display:flex;gap:16px;align-items:center;justify-content:flex-end;background:#efebf8;border-radius:10px 10px 0 0;padding:12px 16px;font-size:14px}.tools label{margin-right:auto;display:flex;align-items:center;gap:12px}.diagram-scroll{overflow:auto;border:1px solid #e5dfed}.diagram-canvas{min-width:920px;width:100%}.diagram-canvas svg{display:block;width:100%;height:auto}.files ul{padding-left:22px}.files li{margin:10px 0}.badge{display:inline-block;border-radius:20px;background:#e8f5f0;color:#237e74;padding:5px 12px;font-size:13px}footer{padding:18px 0;color:#665e77;font-size:13px}button{border:0;border-radius:8px;background:#7351c5;padding:11px 18px;color:white;font:inherit;cursor:pointer}.actions{display:flex;gap:20px;align-items:center;flex-wrap:wrap}@media(max-width:700px){h1{font-size:28px}main{padding:14px}.sheet,.files{padding:16px}.tools{flex-wrap:wrap}.tools label{width:100%}h2{font-size:22px}}@page{size:A3 landscape;margin:12mm}@media print{html{scroll-behavior:auto}body{background:white}header,nav,.files,.tools,footer,.section-head{display:none}main{max-width:none;padding:0}.sheet{padding:0;margin:0;border:0;border-radius:0;break-after:page;break-inside:avoid;height:266mm;display:flex;align-items:center;justify-content:center}.sheet:last-of-type{break-after:auto}.diagram-scroll{border:0;overflow:visible;width:100%}.diagram-canvas{min-width:0;width:100%!important}.diagram-canvas svg{width:100%;max-height:266mm}a{color:inherit}}'''
    nav = ''.join(f'<a href="#{name}">{title}</a>' for name,title,_ in sheets)
    html = f'''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Desain database dan arsitektur — Pipeline Funding</title><style>{css}</style></head><body>
<header><small>DOKUMENTASI IMPLEMENTASI · 19 OKTOBER 2026</small><h1>Desain database dan arsitektur</h1><p>Pipeline Funding Management System. Disusun dari kode aplikasi dan metadata PostgreSQL: 22 tabel, 162 kolom, serta relasi yang benar-benar diterapkan.</p><div class="actions"><a href="desain-database-dan-arsitektur.pdf">Unduh PDF</a><button id="print">Cetak diagram</button></div></header><nav>{nav}<a href="#files">Dokumen lengkap</a></nav><main>{''.join(parts)}
<section id="files" class="files"><span class="badge">Dokumentasi terbaru · PostgreSQL</span><h2>Dokumen dan sumber editable</h2><ul><li><a href="desain-database-dan-arsitektur.pdf">PDF: empat halaman diagram siap dibagikan</a></li><li><a href="DESAIN-DATABASE.md">Kamus database: seluruh 22 tabel, 162 kolom, constraint, dan indeks</a></li><li><a href="ARSITEKTUR.md">Penjelasan arsitektur, alur permintaan, dan aturan akses</a></li><li><a href="erd-lengkap.mmd">Mermaid: ERD lengkap seluruh tabel</a></li><li><a href="arsitektur-sistem.mmd">Mermaid: arsitektur sistem</a></li><li><a href="alur-penyimpanan.mmd">Mermaid: sequence penyimpanan dan percobaan ulang</a></li><li><a href="schema.json">Metadata PostgreSQL tanpa data operasional</a></li><li><a href="README.md">Panduan berkas dan cara memperbarui dokumen</a></li></ul><p>Kolom yang ditampilkan pada gambar dipilih agar terbaca. Kamus database dan ERD Mermaid lengkap mencatat semua atribut dan FK. Dokumen evaluasi September pada folder sebelah merupakan arsip versi lama.</p></section><footer>Sumber: migration, controller, model, layanan API Vue, dan metadata database lokal. Berkas ini dapat dibuka tanpa internet.</footer></main><script>document.querySelector('#print').addEventListener('click',()=>window.print());document.querySelectorAll('input[type=range]').forEach(input=>input.addEventListener('input',()=>input.closest('.sheet').querySelector('.diagram-canvas').style.width=input.value+'%'));</script></body></html>'''
    html = html.replace('<div class="actions">', '<div class="actions"><a href="ERD-LENGKAP.html">Buka ERD lengkap — 22 tabel dalam satu diagram</a>', 1)
    html = html.replace('<div class="actions">', '<div class="actions"><a href="DFD.html">DFD: konteks dan Level 1–3</a>', 1)
    html = html.replace('<div class="actions">', '<div class="actions"><a href="../materi-ujian/MATERI-BELAJAR-UJIAN-MAGANG.pdf">Buku belajar ujian magang — 88 halaman</a>', 1)
    (ROOT/'index.html').write_text(html,encoding='utf-8')

if __name__ == '__main__':
    write_dictionary()
    write_mermaid()
    build_pipeline()
    build_target()
    build_security()
    build_architecture()
    build_html()
    print(f'Dokumen dihasilkan: {ROOT}')
