from book_common import *


def pages():
    out=[]
    out.append(page('10 · TECH STACK','Teknologi yang benar-benar dipakai','Versi berasal dari lockfile proyek dan runtime lokal; bukan klaim memakai versi terbaru di internet.',
        table(['Teknologi','Versi terverifikasi','Peran'],[
            ('Vue','3.5.42','Framework antarmuka berbasis komponen.'),('Vue Router','4.6.4','Navigasi SPA dan hash history.'),
            ('Vite','7.3.6','Dev server dan build frontend.'),('Chart.js','4.5.1','Grafik batang, doughnut, dan garis.'),
            ('PHP','8.2.12 lokal; requirement ^8.2','Bahasa backend untuk Laravel.'),('Laravel','12.69.2','Routing, middleware, ORM, validasi, transaksi, API.'),
            ('Laravel Sanctum','4.3.3','Penerbitan dan pemeriksaan token API.'),('PostgreSQL','18.4 lokal','Database relasional operasional.'),
            ('Node.js','24.15.0 lokal','Menjalankan tooling frontend dan tes JavaScript.'),('Playwright Test','1.63.0','Tes browser end-to-end.'),
            ('PHPUnit','11.5.56','Tes backend PHP.'),('Prettier','3.9.6','Pemformatan kode frontend.')])+
        h('Framework, library, runtime, dan database berbeda')+
        p('Vue dan Laravel menyediakan kerangka pengembangan pada lapisan masing-masing. Chart.js merupakan library untuk kebutuhan grafik. PHP dan Node.js menjalankan kode pada konteks yang berbeda. PostgreSQL menyimpan serta mengelola data. Vite membantu pengembangan/build; Vite tidak mengambil alih tugas backend Laravel.')+
        note('Membaca versi dengan benar','<code>package.json</code> atau <code>composer.json</code> dapat memakai rentang seperti ^3.5.0 atau ^12.0. Lockfile mencatat resolusi versi tertentu. Karena itu angka minimum deklarasi tidak selalu sama dengan versi paket yang dipasang.')+
        p('<strong>Acuan lokal:</strong> <code>src/frontend/package-lock.json</code>, <code>src/backend/composer.lock</code>, serta inspeksi runtime/database. Font dan ikon berasal dari paket lokal; penyajian aplikasi tidak bergantung pada CDN font untuk berjalan.')))

    out.append(page('10 · TECH STACK','Alasan pemilihan dan konsekuensinya','Alasan yang baik menghubungkan teknologi dengan kebutuhan proyek, bukan hanya popularitas.',
        table(['Pilihan','Kesesuaian kebutuhan','Konsekuensi / batas'],[
            ('Vue + komponen','Formulir dan kartu target dapat dipakai ulang; state UI reaktif.','Membutuhkan pengaturan state, lifecycle, dan penanganan request.'),
            ('Laravel API','Aturan akses, validasi, ORM, dan transaksi tersedia dalam satu backend.','Logika perlu tetap terstruktur; framework tidak otomatis menyelesaikan semua aturan bisnis.'),
            ('PostgreSQL','Data saling berelasi serta membutuhkan transaksi dan constraint.','Desain indeks, backup, dan operasional server tetap perlu dikelola.'),
            ('Chart.js','Jenis grafik yang dipakai proyek tersedia dan terintegrasi pada canvas.','Aksesibilitas dan interpretasi angka tetap tanggung jawab aplikasi.'),
            ('SPA','Navigasi internal dan panel detail dapat berlangsung tanpa memuat seluruh dokumen baru.','Perlu strategi sesi, pemuatan data, serta penanganan error yang baik.'),
            ('Satu backend','Cakupan proyek masih dapat dikelola tanpa pemisahan layanan.','Perlu pengukuran sebelum memutuskan skala arsitektur berikutnya.')])+
        p('Pilihan tersebut adalah pertimbangan kecocokan untuk implementasi ini. Jangan mengatakan PostgreSQL selalu lebih cepat daripada semua database atau Vue selalu lebih baik daripada React. Tidak ada benchmark perbandingan alternatif yang dikerjakan pada audit ini.')+
        h('Cara menjawab alternatif')+
        p('Jika ditanya “mengapa tidak pakai teknologi lain?”, jelaskan kebutuhan inti: UI dinamis, data relasional, aturan bisnis, dan integritas penyimpanan. Lalu tunjukkan fitur teknologi yang mendukungnya. Akhiri dengan konsekuensi yang kamu pahami, misalnya kebutuhan mengelola state SPA atau menerapkan validasi server.')+
        note('Jawaban singkat','“Stack ini sesuai untuk aplikasi internal dengan formulir, ringkasan, dan data relasional. Saya menggunakan fasilitas framework, lalu menambahkan pembatasan divisi, perhitungan, audit, dan pengaman penyimpanan sesuai kebutuhan proyek.”')))

    out.append(page('11 · FRONTEND','Vue: komponen dan reaktivitas','Reaktivitas membuat tampilan mengikuti perubahan state tanpa menulis manipulasi DOM untuk setiap angka.',
        p('Vue membangun antarmuka secara deklaratif dan berbasis komponen. Pengembang menyatakan hubungan data dengan tampilan; Vue melacak perubahan state dan memperbarui bagian antarmuka yang membutuhkannya. Pada proyek ini halaman, panel detail, kartu target, dan grafik dipisah menjadi komponen.')+cite('V1','V2')+
        h('Konsep yang terlihat pada kode')+
        table(['API / konsep','Penerapan proyek'],[
            ('ref','Nilai reaktif seperti pengguna, tahun, array peluang, status loading, dan panel terpilih.'),
            ('computed','Nilai turunan: produk yang diizinkan, daftar aktif/closing, ringkasan tampilan, dataset grafik.'),
            ('watch','Menanggapi perubahan tertentu; komponen grafik menggambar ulang saat data berubah.'),
            ('props / event','Data masuk ke komponen dan pemberitahuan tindakan kembali ke induknya.'),
            ('lifecycle','Grafik dibuat setelah canvas tersedia dan dibersihkan sebelum komponen dilepas.')])+
        code("const selectedYear = ref(2026)\nconst activeRows = computed(() =>\n  rows.value.filter(row => !isClosed(row))\n)")+
        p('Contoh ringkas tersebut mengikuti pola pada <code>usePipeline.js</code>. Ketika daftar peluang diperbarui setelah simpan, <code>activeRows</code> dapat dihitung kembali. Penyaringan ini menyajikan data yang sudah dibatasi akses oleh backend; bukan pengganti pemeriksaan izin.')+
        note('Fakta kecil Vue','Vue diucapkan seperti kata Inggris “view”. Satu berkas .vue dapat menyatukan template, logika, dan style komponen. Istilah reactive berarti tampilan mengikuti dependensi data, bukan berarti database otomatis tersimpan saat suatu variabel berubah.')+
        p('<strong>Jebakan ujian:</strong> mengubah nilai <code>ref</code> hanya mengubah state proses browser. Data baru permanen setelah operasi API berhasil dan transaksi database selesai.')))

    out.append(page('11 · FRONTEND','Computed, composable, dan state bersama','Proyek menggunakan Composition API dan composable; tidak menunjukkan pemakaian Pinia sebagai store utama.',
        p('Computed menyimpan hasil turunan berdasarkan dependensi reaktif dan mengevaluasi ulang ketika dependensinya berubah. Composable adalah fungsi yang mengemas logika reaktif agar dapat dipakai kembali oleh komponen. Keduanya membantu memisahkan logika dari template.')+cite('V3','V4')+
        table(['Berkas','Tanggung jawab yang dapat ditelusuri'],[
            ('useSession.js','Identitas pengguna, inisialisasi /me, login, logout, dan respons ketika token tidak sah.'),
            ('usePipeline.js','Master, peluang, target, ringkasan, tahun, pilihan divisi Head, dan operasi data.'),
            ('useUnsavedChanges.js','Pengaman ketika formulir berubah lalu pengguna meninggalkan konteks.'),
            ('services/api.js','Fetch, bearer header, timeout, error status, dan penyimpanan request retry yang belum pasti.'),
            ('utils/pipeline.js','Validasi awal, format rupiah, kategori status, tanggal, dan utilitas perhitungan.')])+
        h('Mengapa sebagian ref berada di luar fungsi?')+
        p('State tingkat modul dapat dipakai bersama oleh komponen yang mengimpor composable tersebut dalam aplikasi browser yang sama. Ini menjelaskan mengapa pilihan tahun atau data yang dimuat dapat konsisten pada beberapa tampilan. Desain ini berbeda dari membuat state baru setiap kali suatu fungsi dipanggil.')+
        h('Mencegah respons lama menimpa pilihan baru')+
        p('Loader merekam konteks pengguna, divisi, dan tahun, serta nomor urut request. Sebelum menerapkan respons, kode memastikan konteksnya masih berlaku. Jika Head beralih dari Komersil ke Konsumer ketika respons Komersil terlambat tiba, respons lama diabaikan.')+
        note('Trade-off yang dapat dijelaskan','State bersama sederhana sesuai cakupan saat ini. Jika modul, tim, atau kebutuhan debugging state berkembang, pemisahan store dan tanggung jawab dapat ditinjau. Keberadaan ref bersama bukan bukti semua aplikasi membutuhkan library state tambahan.')))

    out.append(page('11 · FRONTEND','Vue Router dan pengalaman navigasi','URL menggambarkan posisi antarmuka, sedangkan API menentukan data yang berhak diterima.',
        p('Router proyek memakai <code>createWebHashHistory()</code>. Contoh alamatnya <code>/#/pipeline</code>. Bagian setelah tanda # ditangani browser dan tidak dikirim sebagai path request ke server. Mode ini mengurangi kebutuhan pengaturan fallback route pada server untuk navigasi SPA.')+cite('R1')+
        h('Guard yang ada pada proyek')+
        p('Sebelum navigasi, <code>beforeEach</code> menunggu inisialisasi sesi. Halaman selain login mengarah ke login ketika tidak ada pengguna yang sah pada state aplikasi. Setelah navigasi, judul dokumen diperbarui. Watcher sesi juga dapat mengarahkan kembali ke login setelah respons API 401.')+
        h('Guard bukan sistem otorisasi final')+
        p('Seorang pengguna dapat melewati antarmuka dan mengirim request langsung. Karena itu route guard meningkatkan pengalaman pengguna, sedangkan Sanctum dan controller backend menjaga akses data. Menyembunyikan menu saja tidak cukup melindungi endpoint.')+
        h('Panel dan kondisi formulir')+
        p('Detail dan formulir muncul melalui komponen drawer. Navigasi kembali atau penutupan tab ketika isian berubah dapat memicu konfirmasi. Menu ponsel mempunyai pengaturan fokus dan penutupan dengan Escape. Semua itu membantu mencegah kehilangan isian dan membuat penggunaan keyboard lebih terarah.')+
        note('Fakta kecil router','Hash history dan browser history bukan hal yang sama. Browser history menghasilkan path yang lebih bersih, tetapi perlu fallback server yang tepat. Pada aplikasi internal ini pencarian mesin pencari bukan tujuan utama, sehingga pilihan hash mempunyai konteks yang dapat dijelaskan.')+
        p('<strong>Latihan:</strong> jelaskan mengapa URL <code>/#/target</code> berbeda dari endpoint <code>/api/targets</code>. Yang pertama memilih layar; yang kedua meminta data target.')))

    out.append(page('11 · FRONTEND','Vite, Node.js, npm, dan hasil build','Tooling pengembangan frontend tidak sama dengan server API produksi.',
        p('Vite menyediakan dev server dan perintah build. Dokumentasi Vite 7 yang sesuai dengan versi proyek menjelaskan penggunaan native ES modules/HMR saat pengembangan serta Rollup untuk build produksi. Jangan mengambil rincian bundler dari dokumentasi mayor Vite lain lalu menganggapnya otomatis berlaku pada proyek ini.')+cite('T1')+
        p('Node.js adalah runtime JavaScript di luar browser. Pada proyek ini Node menjalankan Vite, pengujian logika, Playwright, dan script dokumentasi. API bisnis tetap dijalankan oleh PHP/Laravel; keberadaan Node tidak berarti proyek memakai backend Express.')+cite('N1')+
        table(['Perintah / berkas','Arti'],[
            ('npm run dev','Menjalankan Vite untuk pengembangan frontend.'),('npm run build','Menghasilkan aset frontend untuk penyajian produksi.'),
            ('npm test','Menjalankan tes logika JavaScript yang dikonfigurasi proyek.'),('package.json','Daftar dependensi dan scripts.'),
            ('package-lock.json','Versi dependensi yang telah diresolusikan.'),('vite.config.js','Plugin Vue, host lokal, dan proxy /api.')])+
        h('Apa fungsi proxy /api?')+
        p('Browser mengirim request ke alamat frontend dengan awalan /api. Vite meneruskannya ke Laravel pada port lokal backend. Proxy membantu alur pengembangan; backend tetap menerima request dan melakukan validasi. Proxy bukan lapisan keamanan dan bukan tanda API di internet sudah menggunakan HTTPS.')+
        note('Hasil pemeriksaan','Build Vite proyek berhasil. Hal ini membuktikan proses bundling yang dijalankan selesai, bukan membuktikan server publik, backup, dan hak akses produksi sudah benar.')+
        p('HMR membantu perubahan komponen terlihat cepat selama pengembangan. HMR bukan mekanisme distribusi pembaruan produksi dan bukan alasan menjalankan dev server sebagai server publik permanen.')))

    out.append(page('11 · FRONTEND','Chart.js, CSS, dan aksesibilitas','Grafik membantu membaca data; angka dan penjelasan teks tetap diperlukan.',
        p('Chart.js menyediakan visualisasi pada canvas. Proyek mendaftarkan controller, elemen, dan skala yang dipakai lalu membuat grafik dari props komponen. <code>ReportChart.vue</code> menggambar ulang saat data berubah dan menghancurkan instance sebelum komponen dilepas.')+cite('C1')+
        table(['Visual','Data yang dipakai','Hal yang harus dijelaskan'],[
            ('Batang','Target tahunan dan realisasi Won per produk dana.','Keduanya mempunyai satuan rupiah yang sama.'),
            ('Doughnut','Jumlah peluang aktif menurut Cold/Warm/Hot.','Persentase komposisi jumlah, bukan probabilitas closing.'),
            ('Garis','Nominal per bulan pencatatan dan realisasi per bulan closing.','Bukan saldo historis akhir bulan.'),
            ('Progress bar','Proporsi pencapaian terhadap target.','Angka persentase dapat melebihi 100% walau bar dibatasi panjangnya.')])+
        h('Canvas tidak otomatis dapat dibaca pembaca layar')+
        p('Dokumentasi Chart.js menjelaskan perlunya nama aksesibel atau konten alternatif. Komponen proyek menggunakan <code>role="img"</code>, <code>aria-label</code>, dan fallback teks pada canvas. Nilai ringkasan juga disajikan sebagai teks di halaman.')+cite('C2')+
        h('Responsif dan preferensi gerak')+
        p('CSS menyesuaikan grid, sidebar, kartu, dan daftar ketika lebar layar berubah. Komponen grafik memakai ukuran responsif dan mematikan animasi ketika perangkat meminta pengurangan gerak. Tes layout memeriksa lebar 1440, 390, dan 320 piksel pada tiga kelompok akun.')+
        note('Batas bukti aksesibilitas','Label dan pengaturan fokus merupakan praktik yang membantu akses. Tes yang ada belum membuktikan kepatuhan WCAG menyeluruh, termasuk semua kombinasi pembaca layar, kontras, zoom, dan perangkat input.')))

    out.append(page('12 · BACKEND','PHP dan lifecycle Laravel','Backend menerima request, menerapkan aturan, dan menghasilkan respons.',
        p('PHP merupakan bahasa scripting yang sesuai untuk pengembangan web dan dapat dijalankan pada server maupun CLI. Singkatan PHP bersifat rekursif: PHP: Hypertext Preprocessor. Pada proyek ini PHP mengeksekusi Laravel; tampilan utama pengguna dibangun dengan Vue, sehingga respons API bisnis umumnya berupa JSON.')+cite('H1')+
        p('Secara umum request Laravel masuk melalui <code>public/index.php</code>, bootstrap aplikasi, middleware, routing, dan controller. Respons berjalan kembali melalui middleware sebelum dikirim ke klien. Pemahaman alur ini membantu mengetahui di mana validasi atau autentikasi dilakukan.')+cite('L1')+
        table(['Bagian','Contoh dalam proyek'],[
            ('Routes','routes/api.php mendefinisikan alamat dan metode.'),('Middleware','auth:sanctum dan IdempotentWrite.'),
            ('Controller','OpportunityController, TargetController, ReportController, AuthController.'),('Layanan','DashboardReport untuk agregasi laporan.'),
            ('Model','Opportunity, User, AnnualTarget, AuditEvent, dan relasinya.'),('Konfigurasi','Database, timezone aplikasi, dan Sanctum.')])+
        h('Mengapa disebut API, bukan tampilan Blade utama?')+
        p('Laravel dapat membuat halaman HTML melalui Blade, tetapi pembagian tanggung jawab proyek ini memakai Vue sebagai UI. Backend mengembalikan data JSON yang dibaca composable. Menyebut Laravel “MVC” secara umum tidak mengharuskan setiap layar proyek memakai view Blade.')+
        note('Fakta kecil Artisan','Artisan adalah antarmuka perintah Laravel. Perintah seperti test, migrate, dan serve dijalankan lewat CLI. PHP tetap bahasa yang mengeksekusi perintah tersebut; Artisan bukan bahasa pemrograman baru.')+
        p('Jika penguji meminta contoh logika buatan proyek, tunjukkan pembatasan divisi, aturan Won/Lost, batch target, audit perubahan, dan replay request. Itu lebih menunjukkan pemahaman daripada hanya menyebut framework menyediakan banyak fitur.')))

    out.append(page('12 · BACKEND','Peta endpoint dan operasi bisnis','Tidak semua fitur adalah CRUD penuh: penghapusan peluang tidak disediakan pada endpoint utama.',
        table(['Metode','Endpoint','Fungsi'],[
            ('POST','/api/login','Login dan token baru.'),('GET / POST','/api/me · /api/logout','Identitas / pencabutan token aktif.'),
            ('GET','/api/divisions · /products · /pics','Referensi sesuai akses.'),('GET / POST','/api/opportunities','Daftar / pencatatan peluang.'),
            ('GET / PATCH','/api/opportunities/{id}','Detail timeline / pembaruan aktif.'),('POST','/api/opportunities/{id}/follow-up-completion','Menyelesaikan tindak lanjut.'),
            ('POST','/api/opportunities/{id}/closing','Satu operasi hasil closing.'),('GET','/api/targets?year=YYYY','Target dalam scope yang boleh dibaca.'),
            ('POST','/api/targets/batch','Simpan satu formulir target/layanan atomik.'),('GET','/api/dashboard?year=YYYY','Ringkasan dana dan tren.'),
            ('GET','/api/team','Rekap API PIC.'),('GET','/api/pics/{id}/opportunities','Peluang pernah ditangani PIC.')])+
        p('Endpoint kompatibilitas untuk target per produk, realisasi unit bulanan, serta target cabang tetap ada. Hal ini menjaga data/alur lama, tetapi tampilan terbaru menekankan target dana tahunan dan formulir batch. Jelaskan endpoint utama yang dipakai alur sekarang terlebih dahulu.')+
        h('Mengapa memakai PATCH untuk perubahan peluang?')+
        p('Metode tersebut membedakan perubahan resource yang sudah ada dari pencatatan melalui POST. Perintah closing dipisahkan agar aturan hasil akhir dapat diperiksa secara eksplisit; pengguna tidak cukup mengirim outcome Won melalui formulir peluang baru.')+
        note('Trace yang bagus untuk ujian','Pilih satu endpoint lalu telusuri route → middleware → controller → model/tabel → respons → composable → komponen. Hubungan konkret ini lebih bernilai daripada mencoba menghafal semua endpoint sekaligus.')+
        p('Nama endpoint di tabel bersumber dari <code>routes/api.php</code>. Ketiadaan tombol hapus adalah batas fitur saat ini; bukan bukti tidak ada pihak yang dapat menghapus data melalui hak database.')))

    out.append(page('12 · BACKEND','Eloquent ORM dan relasi','ORM mempermudah akses data, tetapi constraint dan aturan bisnis tetap harus dirancang.',
        p('Eloquent merepresentasikan tabel sebagai model dengan hubungan yang dapat diakses melalui kode. Relasi seperti belongsTo dan hasMany membantu memuat data terkait; eager loading dengan <code>with</code> mengurangi pemanggilan query satu per satu pada daftar terkait.')+cite('L4')+
        code("Opportunity::with(['division', 'pic', 'product'])\n  ->where('division_id', $divisionId)\n  ->where('outcome', 'Active')\n  ->paginate(20);")+
        p('Contoh ringkas ini memperlihatkan model, batas divisi, status, dan paginasi. Implementasi daftar proyek menyediakan pencarian, filter, whitelist pengurutan, serta pembatasan ukuran halaman maksimum 100. Query tidak boleh mengandalkan filter UI sebagai satu-satunya penjaga scope.')+
        h('Relasi utama yang perlu kamu pahami')+
        table(['Relasi','Makna'],[
            ('Opportunity belongsTo User melalui pic_id','Satu penanggung jawab saat ini/final.'),('Opportunity hasMany assignments','Beberapa riwayat penugasan sepanjang umur peluang.'),
            ('AnnualTarget hasMany monthlyTargets','Target tahunan dengan rincian target bulanan.'),('AnnualTarget hasMany unitRealizations','Total unit pada bulan-bulan tahun target yang sama.'),
            ('User belongsTo Division','PIC terhubung ke divisi; Head boleh tidak memiliki divisi tetap.')])+
        h('Keterbatasan yang masih terlihat')+
        p('Timeline menambahkan nama PIC/produk ke snapshot melalui pencarian berdasarkan ID. Pada timeline yang sangat panjang, jumlah query tambahan perlu diukur. ORM bukan jaminan bebas masalah N+1; jalur kode yang benar-benar dipakai tetap perlu ditinjau dan diprofilkan.')+
        note('SQL injection dan nama kolom','Query builder membantu parameter binding nilai. Nama kolom pengurutan tetap perlu whitelist karena nama kolom bukan sekadar nilai parameter. Controller daftar proyek membatasi sort ke daftar kolom yang diizinkan.')))

    out.append(page('12 · BACKEND','Validasi UI, API, dan database','Tiga lapisan pemeriksaan mempunyai tugas yang saling melengkapi.',
        p('Laravel menyediakan aturan validasi dan menghasilkan respons error terstruktur untuk request yang sesuai. Di proyek ini request API diatur untuk merespons JSON, termasuk kesalahan autentikasi dan validasi. Pengalaman isian tetap dibantu validasi frontend agar kesalahan umum segera terlihat.')+cite('L5')+
        table(['Lapisan','Contoh','Batasnya'],[
            ('Frontend','Isian wajib, rupiah aman, tanggal, pesan di bawah kolom.','Dapat dilewati dengan request API langsung.'),
            ('Backend','PIC/produk sesuai divisi, syarat closing, versi, scope target.','Perlu konsistensi ketika ada klien/endpoint baru.'),
            ('Database','PK, FK, UNIQUE, NOT NULL, transaksi.','Tidak semua aturan bisnis telah diwujudkan sebagai constraint SQL.')])+
        h('Contoh FK belum cukup')+
        p('Sebuah ID produk yang ada di products dan ID divisi yang ada di divisions masing-masing dapat valid sebagai FK. Namun kombinasi Giro–Konsumer tetap tidak diperbolehkan bisnis. Karena tidak ada FK komposit opportunity ke pasangan division_products untuk aturan itu, controller memeriksa kesesuaian produk/divisi secara eksplisit.')+
        h('Temuan yang perlu kamu sebut secara tepat')+
        ul('Kolom nonnegatif di migration menggunakan nama unsigned, tetapi tipe fisik PostgreSQL BIGINT tetap bertanda; validasi API menegakkan nilai minimum.',
           'Rentang bulan 1–12 dan tahun 2000–2100 diperiksa API; tidak ada CHECK SQL rentang tersebut pada katalog yang diperiksa.',
           'Frontend dan API mempunyai batas panjang teks yang berbeda; nominal aman Number belum diberlakukan dengan batas yang sama di API.')+
        note('Pernyataan yang tepat','“Integritas dijaga melalui kombinasi constraint relasional dan validasi aplikasi.” Hindari “semua kesalahan mustahil masuk karena database sudah otomatis memvalidasi seluruh aturan”.')))

    out.append(page('13 · DATABASE','Membaca 22 tabel tanpa menghafal semuanya','Kelompokkan tabel berdasarkan tanggung jawab, lalu pelajari tabel yang terlibat dalam satu alur.',
        table(['Kelompok','Tabel'],[
            ('Master / akun','divisions, users, products, division_products, target_scopes.'),
            ('Peluang / penugasan','opportunities, opportunity_assignments.'),
            ('Target / layanan','annual_targets, monthly_targets, unit_realizations, branch_targets.'),
            ('Jejak / retry','audit_events, request_receipts.'),('Token API','personal_access_tokens.'),
            ('Infrastruktur Laravel','password_reset_tokens, sessions, cache, cache_locks, jobs, job_batches, failed_jobs, migrations.')])+
        p('Jumlahnya adalah <strong>13 tabel domain</strong> jika akun/master, peluang, target, audit, dan receipt dikelompokkan sebagai domain; <strong>1 tabel token Sanctum</strong>; serta <strong>8 tabel infrastruktur</strong>. Pengelompokan ini untuk penjelasan proyek, bukan kategori bawaan PostgreSQL.')+
        h('Keberadaan tabel tidak sama dengan fitur UI')+
        p('Tabel password_reset_tokens tidak membuktikan ada halaman reset password yang siap dipakai. Tabel sessions tidak berarti SPA ini memakai sesi cookie. Tabel jobs tidak berarti simpan peluang harus menunggu queue worker. Periksa route, controller, dan antarmuka sebelum menyatakan suatu fitur tersedia.')+
        h('Apa yang diverifikasi?')+
        p('Katalog database aktif menunjukkan 22 tabel, 162 kolom, 22 primary key, 22 foreign key, dan 12 unique constraint. Daftar tabel, nama/tipe/nullability kolom, serta definisi constraint cocok dengan schema.json yang digunakan untuk dokumentasi. Pemeriksaan ini membaca metadata tanpa mengekspor record operasional atau kredensial.')+
        note('Cara menjawab jumlah tabel','Mulai dari tujuan kelompok, kemudian sebut jumlah. Jika hanya menghafal angka 22 tanpa mampu menelusuri peluang dan target, penjelasan desain masih sulit dipahami.')+
        p('Kamus seluruh kolom disertakan dalam lampiran buku. ERD lengkap berukuran besar juga tersedia sebagai berkas terpisah pada paket desain sistem.')))

    out.append(page('13 · DATABASE','Primary key, foreign key, UNIQUE, dan normalisasi','Hubungan tabel menjaga identitas serta keterkaitan; aturan bisnis melengkapi hubungan itu.',
        p('Primary key mengidentifikasi baris secara unik dan tidak null. Foreign key menjaga rujukan ke baris yang diizinkan ada pada tabel tujuan. UNIQUE membatasi duplikasi nilai atau kombinasi nilai. Ketiga konsep itu berbeda dari indeks biasa yang terutama membantu pencarian.')+cite('P2')+
        table(['Contoh proyek','Makna desain'],[
            ('opportunities.id','Identitas peluang tetap sama sebelum dan sesudah closing.'),
            ('opportunities.pic_id → users.id','Penanggung jawab harus merujuk akun yang ada; role/divisi diperiksa aplikasi.'),
            ('division_products PK gabungan','Pasangan divisi–produk yang sama tidak berulang.'),
            ('annual_targets UNIQUE scope, product, year','Satu target produk untuk satu scope dan tahun.'),
            ('monthly_targets UNIQUE target, month','Satu rincian target untuk bulan yang sama.'),
            ('request_receipts UNIQUE user, request_key','Satu pengenal retry tidak menghasilkan dua receipt untuk pengguna yang sama.')])+
        h('Mengapa memisahkan master produk?')+
        p('Jika nama dan satuan produk disalin ke setiap peluang, perubahan informasi master mudah tidak konsisten. Referensi ID membantu mengurangi pengulangan atribut. Rincian bulanan juga merujuk annual target sehingga tidak perlu mengulang tahun, scope, dan produk sebagai teks pada setiap baris.')+
        h('Normalisasi bukan lomba jumlah tabel')+
        p('Pemisahan berdasarkan entitas dan ketergantungan membantu integritas. Namun proyek juga sengaja menyimpan snapshot JSON pada audit untuk mempertahankan konteks perubahan. Tidak semua data turunan harus dipisah, dan audit ini tidak menyatakan seluruh skema telah dibuktikan formal memenuhi setiap bentuk normal.')+
        note('NULL dan hubungan opsional','division_id pada akun Head atau actor_id pada audit dapat kosong sesuai kebutuhan. Relasi nullable harus dijelaskan sebagai opsional, bukan dipaksa seolah semua record mempunyai induk yang wajib.')))

    out.append(page('13 · DATABASE','Tabel peluang dan riwayat penugasan','Satu record opportunity menyimpan keadaan bisnis saat ini dan hasil akhir ketika ditutup.',
        table(['Kelompok kolom opportunities','Peran'],[
            ('id, legacy_id','Identitas internal dan rujukan migrasi lama bila ada.'),('division_id, pic_id, product_id','Lingkup data, penanggung jawab, produk.'),
            ('customer_name, segment','Nama nasabah/perusahaan dan segmentasi.'),('nominal, interest_status, outcome','Potensi dana, minat, dan hasil.'),
            ('recorded_date, follow_up_date, follow_up_completed','Tanggal pencatatan dan pekerjaan tindak lanjut.'),
            ('closed_date, realization, lost_reason','Tanggal dan detail hasil closing.'),('notes, created_by, updated_by','Konteks dan pelaku pencatatan/pembaruan.'),
            ('version, created_at, updated_at','Versi perubahan dan waktu teknis record.')])+
        p('Ketika peluang masih Active, realisasi dimulai nol dan tanggal closing dapat kosong. Saat Won, realisasi diisi dengan nilai hasil. Saat Lost, alasan wajib dan realisasi nol. Status minat tetap merupakan dimensi terpisah. Perubahan keadaan ini dilakukan oleh controller, bukan trigger PostgreSQL yang menghitung sendiri hasilnya.')+
        h('Penugasan yang tidak hilang saat PIC berganti')+
        p('<code>opportunity_assignments</code> menyimpan ID peluang, PIC, waktu mulai/berakhir, pelaku perubahan, serta sumber. PIC lama tetap dapat ditelusuri. Pada data migrasi yang waktunya tidak diketahui, tanggal penugasan dapat kosong; dokumentasi tidak boleh menciptakan urutan historis yang tidak terbukti.')+
        h('Menjaga rujukan')+
        p('Rujukan utama seperti produk, divisi, dan PIC pada peluang memakai pembatasan penghapusan melalui FK. Beberapa rujukan pelaku boleh menjadi null jika akun dihapus. Di antarmuka utama tidak ada alur penghapusan opportunity; closing mempertahankan identitas dan jejaknya.')+
        note('Pertanyaan desain','Mengapa tidak membuat tabel won dan lost? Karena hasil adalah keadaan dari peluang yang sama. Memisahkan tanpa kebutuhan jelas dapat menambah perpindahan data dan risiko riwayat terputus.')))

    out.append(page('13 · DATABASE','Model target tahunan, bulanan, dan shared','Tahun dan produk berada pada target induk; rincian bulan merujuk identitas induknya.',
        table(['Tabel','Peran dan aturan'],[
            ('target_scopes','Kode konsumer, komersil, shared. Shared tidak merujuk satu divisi.'),
            ('annual_targets','Produk, scope, tahun, nilai target, pelaku, dan versi. Kombinasi scope/produk/tahun unik.'),
            ('monthly_targets','annual_target_id, bulan, nilai target. Kombinasi target/bulan unik.'),
            ('unit_realizations','annual_target_id, bulan, total units, pelaku, versi. Hanya untuk produk UNIT melalui validasi.'),
            ('branch_targets','Target cabang kompatibilitas; bukan sumber saldo atau transaksi bank.')])+
        p('CMS memakai annual target dengan scope shared. Bale Syariah dan QRIS mengikuti scope Konsumer. Produk dana memakai scope divisi dan realisasinya berasal dari peluang Won, sehingga tidak dibuat tabel realisasi dana bulanan yang dimasukkan manual untuk menggantikan perhitungan itu.')+
        h('Mengapa version untuk realisasi layanan juga ada?')+
        p('Karena isinya total bulan. Jika dua pengguna membuka total 15 dan masing-masing mengoreksi menjadi 18 dan 20, pembaruan lama tidak boleh diam-diam menimpa pembaruan terbaru. Version membantu mendeteksi bahwa dasar pengeditannya sudah berubah.')+
        h('Batch bukan hanya membuat request lebih sedikit')+
        p('Satu formulir dapat menyimpan beberapa produk atau 12 rincian bulan. Backend memvalidasi entri, mengunci scope target, memeriksa versi, lalu menyimpan perubahan serta audit dalam satu transaksi. Jika produk atau bulan berikutnya konflik, perubahan sebelumnya pada formulir yang sama dibatalkan.')+
        note('Fakta skema yang spesifik','target_scopes.division_id tidak mempunyai UNIQUE SQL. Seeder membuat satu scope per divisi saat ini, tetapi struktur fisiknya tidak menjamin selalu satu scope per divisi. Jangan mengubah relasi tersebut menjadi 1:1 wajib tanpa penjelasan.')))

    out.append(page('13 · DATABASE','Audit, receipt, dan hubungan logis','Log perkembangan bisnis dan penyimpanan hasil retry mempunyai tujuan yang berbeda.',
        table(['Aspek','audit_events','request_receipts'],[
            ('Tujuan','Merekam kejadian perubahan bisnis.','Memutar ulang respons sukses request yang sama.'),
            ('Identitas','resource_type/resource_id dan actor_id.','user_id + request_key UUID.'),
            ('Isi','Aksi, before_data, after_data, occurred_at, source.','Hash request, status_code, response_body, created_at.'),
            ('Dipakai pengguna','Timeline perkembangan peluang.','Tidak ditampilkan sebagai timeline bisnis.'),
            ('Saat retry identik','Tidak boleh menambah audit baru.','Receipt sukses sebelumnya dipakai kembali.')])+
        p('Hash pada receipt dibuat dari metode HTTP, path, dan body request. Tujuannya mendeteksi apakah key yang sama dikirim untuk payload berbeda. Hash ini bukan tanda tangan digital yang membuktikan seluruh database tidak pernah diubah.')+
        h('Relasi logis bukan selalu FK SQL')+
        p('Audit menyimpan berbagai jenis resource, sehingga pasangan resource_type/resource_id tidak menjadi FK tunggal ke seluruh tabel. Token Sanctum memakai pasangan polimorfik tokenable_type/tokenable_id; sessions.user_id juga tidak mempunyai FK SQL pada skema yang diperiksa. Dua relasi logis yang digambar pada ERD lengkap adalah pengaitan token dan sesi ke pengguna, dibedakan dari 22 FK SQL.')+
        h('Pekerjaan operasional selanjutnya')+
        p('Receipt memuat body respons yang dapat berisi data peluang. Audit memuat snapshot data bisnis. Karena itu kedua tabel memerlukan kebijakan akses dan retensi yang sesuai penggunaan instansi. Audit ini tidak menemukan implementasi jadwal pembersihan/retensi yang dapat diklaim sudah selesai.')+
        note('Jangan tertukar','Token login tidak disimpan sebagai plaintext di tabel token; hash token dipakai Sanctum. Sebaliknya response_body pada receipt memang merupakan isi respons untuk replay, bukan hash respons saja.')))

    out.append(page('13 · DATABASE','Rupiah, BIGINT, dan presisi angka','Tipe data yang tepat di database masih harus diikuti kebijakan angka pada PHP, JSON, dan JavaScript.',
        p('Skema fisik proyek memakai <strong>BIGINT</strong> untuk nominal dan target rupiah, bukan DECIMAL atau float. BIGINT menyimpan bilangan bulat. PostgreSQL tidak mempunyai BIGINT UNSIGNED; nama unsigned pada migration tidak menghasilkan tipe integer tak bertanda di PostgreSQL. NUMERIC/DECIMAL tersedia untuk kebutuhan desimal eksak, tetapi bukan tipe kolom dana pada implementasi ini.')+cite('P3')+
        p('JavaScript Number mempunyai batas bilangan bulat aman <strong>9.007.199.254.740.991</strong> atau 2^53−1. Di atas batas itu, dua integer berbeda dapat direpresentasikan sama. Batas aman ini lebih kecil daripada rentang BIGINT PostgreSQL.')+cite('J1')+
        h('Apa yang sudah ada?')+
        p('Validasi frontend menggunakan <code>Number.isSafeInteger</code> untuk nominal dan target dana. Backend memeriksa integer dan minimum, lalu frontend memetakan banyak nilai memakai Number. Agregasi dana utama dijalankan backend, tetapi total dan hasil JSON tetap perlu dilihat sebagai satu rantai presisi.')+
        h('Apa yang belum sepenuhnya selaras?')+
        p('API belum menetapkan maksimum yang sama dengan batas aman frontend. Klien API langsung masih dapat mengirim integer di luar kebijakan UI. Jumlah banyak record juga dapat melampaui batas aman walaupun setiap record aman. Karena itu “memakai BIGINT” saja belum cukup untuk mengklaim semua nilai keuangan arbitrer selalu eksak di seluruh lapisan.')+
        note('Pilihan pengembangan','Tetapkan batas bisnis dan agregat yang seragam, atau gunakan representasi desimal/string dan pustaka aritmetika yang sesuai pada seluruh jalur. Perubahan tersebut memerlukan penyesuaian kontrak API dan tes; belum diterapkan hanya dengan menulis rekomendasi ini.')+
        p('Untuk contoh belajar Rp600 juta atau Rp1 miliar, nilai masih jauh di dalam batas aman. Pemformatan “miliar” dilakukan pada penyajian, bukan disimpan sebagai teks “0,6 M” di database.')))

    out.append(page('14 · INTEGRITAS','Transaksi dan atomicity','Satu tindakan bisnis tidak boleh tersimpan setengah ketika bagian lain gagal.',
        p('Transaksi mengelompokkan operasi menjadi satu unit yang dapat diselesaikan atau dibatalkan. Pada proyek, pembaruan peluang dan audit, serta satu formulir batch target, menggunakan transaksi Laravel. Kesalahan di dalam blok transaksi menyebabkan perubahan terkait dibatalkan sesuai mekanisme database/framework.')+cite('L3','P8')+
        table(['Kasus','Hasil yang diharapkan'],[
            ('Peluang berhasil dibuat, audit gagal','Peluang dan penugasan terkait tidak ditinggalkan sebagai perubahan sukses sebagian.'),
            ('Catatan closing disimpan, hasil closing konflik','Satu operasi closing dibatalkan; catatan tidak menjadi perubahan terpisah.'),
            ('Produk pertama target berhasil, produk kedua konflik','Seluruh formulir dibatalkan.'),
            ('Bulan awal layanan tersimpan, versi bulan akhir konflik','Annual target, rincian bulan, realisasi, dan audit dalam formulir dibatalkan.'),
            ('Receipt gagal disimpan pada request ber-key','Perubahan bisnis dan receipt berada pada transaksi bersama, sehingga konsistensinya dijaga.')])+
        h('ACID sebagai pengingat konsep')+
        p('<strong>Atomicity:</strong> unit operasi selesai bersama atau batal. <strong>Consistency:</strong> perubahan mematuhi constraint dan aturan yang memang diberlakukan. <strong>Isolation:</strong> transaksi bersamaan mempunyai aturan visibilitas/interaksi. <strong>Durability:</strong> commit dirancang bertahan sesuai jaminan dan konfigurasi penyimpanan database. Backup tetap diperlukan untuk pemulihan bencana, kehilangan host, atau penghapusan yang sah.')+
        note('Transaksi bukan solusi semua hal','Transaksi tidak otomatis mencegah pengguna menimpa perubahan dengan isian lama. Transaksi juga tidak memberi klien kepastian ketika respons hilang. Masalah itu ditangani lagi dengan version checking dan idempotency key.')+
        p('Tes rollback lokal mencakup SQLite pada unit/feature backend dan kasus PostgreSQL melalui suite browser. Jangan menyamakan kesamaan hasil tes dengan seluruh perilaku semua engine pasti identik.')))

    out.append(page('14 · INTEGRITAS','Version, row lock, dan MVCC','Tiga mekanisme ini berkaitan, tetapi masing-masing menjawab masalah yang berbeda.',
        p('PostgreSQL memakai MVCC untuk mengelola visibilitas versi data antartransaksi. Pada tingkat isolasi Read Committed, statement membaca snapshot sesuai aturan tingkat isolasi tersebut. Snapshot pembacaan tidak otomatis membuat semua pembaruan bisnis kebal konflik atau semua transaksi menjadi serializable.')+cite('P4','P5')+
        p('Row lock eksplisit seperti SELECT FOR UPDATE dipakai ketika transaksi perlu mengoordinasikan perubahan pada baris tertentu. Kode Laravel proyek memanggil <code>lockForUpdate()</code> dalam alur penting seperti closing dan penyimpanan target.')+cite('P6')+
        h('Contoh dua pengguna')+
        table(['Waktu','Kejadian'],[
            ('1','A dan B membuka peluang pada version 3.'),('2','A mengubah nominal dan berhasil menyimpan; version menjadi 4.'),
            ('3','B mengirim isian lama dengan version 3.'),('4','Backend membaca kondisi terkini dan menolak konflik 409.'),
            ('5','B memuat ulang, memahami perubahan A, lalu menyimpan jika masih diperlukan.')])+
        p('<strong>Version</strong> mendeteksi bahwa pengguna mengedit berdasarkan keadaan lama. <strong>Row lock</strong> membantu mengoordinasikan transaksi yang sedang mengakses baris untuk perubahan. <strong>MVCC</strong> merupakan mekanisme database untuk pembacaan dan konsistensi antartransaksi. Menjelaskan ketiganya sebagai “database otomatis mengunci semuanya” akan terlalu menyederhanakan.')+
        note('Trade-off yang nyata','Middleware idempotensi mengunci baris pengguna untuk menserialisasi request tulis per akun. Ini membantu mencegah perlombaan pemakaian key pertama, tetapi dapat membatasi paralelisme penulisan oleh akun yang sama. Pengujian beban diperlukan sebelum mengubah strateginya.')+
        p('Version tidak menyatukan dua perubahan secara otomatis. Aplikasi mengembalikan konflik agar pengguna dapat memuat dan menilai data terbaru.')))

    out.append(page('14 · INTEGRITAS','Idempotency key dan retry yang aman','Respons yang hilang tidak sama dengan transaksi yang gagal.',
        h('Masalah yang ingin dicegah')+
        p('Pengguna menekan Simpan. Server berhasil menulis peluang, tetapi jaringan terputus sebelum respons diterima. Jika klien mengirim pencatatan baru tanpa identitas operasi yang sama, peluang dapat tercatat dua kali. Mematikan tombol selama loading saja tidak menyelesaikan kasus respons hilang.')+
        h('Cara proyek menanganinya')+
        ul('Frontend membuat UUID untuk operasi simpan data bisnis dan mempertahankan path/body selama hasil request belum pasti.',
           'Header <code>Idempotency-Key</code> dikirim. Server memeriksa format UUID dan mencari receipt berdasarkan pengguna + key.',
           'Jika belum ada, aksi dijalankan. Respons sukses dan perubahan bisnis disimpan dalam transaksi yang sama.',
           'Jika receipt sudah ada dan hash metode/path/body sama, respons disajikan kembali tanpa audit atau record baru.',
           'Jika key sama tetapi payload berbeda, server menolak 409. Klien tidak boleh memakai satu key untuk dua aksi berbeda.')+
        h('Mengapa body asli dipertahankan?')+
        p('Hash menggunakan isi body request. Perubahan payload dengan key lama bukan retry identik, meskipun pengguna menganggap maksudnya sama. <code>pendingWrites</code> di services/api.js mempertahankan operasi yang belum pasti agar tombol Coba lagi mengirim operasi yang sama.')+
        note('Batas penerapan','Header ini dipakai pada penyimpanan data bisnis terbaru. Login/logout tidak memakai key tersebut. Backend tetap mengizinkan request klien lama tanpa key, sehingga pengaman replay tidak boleh diklaim berlaku bagi semua request tulis tanpa syarat.')+
        p('<strong>Version vs key:</strong> version melindungi keadaan record dari isian lama. Key melindungi identitas satu operasi ketika diulang. Satu operasi dapat membutuhkan keduanya sekaligus.')+
        p('<strong>Acuan:</strong> <code>IdempotentWrite.php</code>, <code>request_receipts</code>, dan <code>services/api.js</code>.')))

    out.append(page('15 · KEAMANAN','Login, token Sanctum, dan password','Jelaskan mode yang benar-benar dipakai, bukan seluruh kemampuan yang dimiliki Sanctum.',
        p('Sanctum mendukung mode token API dan mode autentikasi SPA berbasis cookie. Proyek memakai token API: login menghasilkan token, klien mengirimnya dalam Authorization Bearer, dan middleware auth:sanctum mengenali pengguna. Token database di-hash SHA-256; mode ini bukan JWT yang cukup diverifikasi tanpa melihat penyimpanan token.')+cite('L2')+
        h('Alur login proyek')+
        ul('Username dinormalisasi; akun aktif dicari.', 'Password diperiksa dengan Hash::check.',
           'Token lama akun tersebut dicabut sebelum token baru dibuat.', 'Respons berisi token dan identitas/role/divisi.',
           'Frontend menyimpan token di localStorage bila Ingat saya dipilih, atau sessionStorage jika tidak.')+
        p('Password disimpan sebagai hash; driver lokal terverifikasi bcrypt. Hash berbeda dari enkripsi yang dirancang untuk dibalik dengan kunci. Laravel menyediakan fasilitas hashing dan verifikasi, termasuk penanganan salt melalui algoritmanya.')+cite('L6')+
        h('Logout dan 401')+
        p('Logout server mencabut token aktif. Frontend tetap membersihkan sesi lokal ketika jaringan gagal. Jika respons API menunjukkan 401, penanganan terpusat membersihkan token dan mengarahkan pengguna ke login. Bila logout gagal mencapai server, token yang sudah pernah diterbitkan belum tentu langsung dicabut di server.')+
        note('Umur token yang sebenarnya','Konfigurasi expiration Sanctum saat diperiksa bernilai null. Tidak ada batas umur global otomatis yang dapat dijanjikan dari konfigurasi ini. Token dapat tidak sah karena dicabut, bukan karena ada timeout sesi 15 menit. Timeout request 15 detik juga merupakan konsep berbeda.')+
        p('Login baru mencabut token lama akun itu, sehingga sesi lain yang memakai token lama dapat menerima 401. Fitur ini perlu dipahami ketika melakukan demo dua perangkat dengan satu akun.')))

    out.append(page('15 · KEAMANAN','Apa yang sudah dilindungi dan apa yang belum','Keamanan profesional berarti menyebut mekanisme sekaligus batas bukti yang tersedia.',
        table(['Sudah terlihat pada implementasi','Batas / pengembangan lanjutan'],[
            ('Password hash bcrypt dan token hash Sanctum.','Pengelolaan password operasional dan pembaruan runtime perlu kebijakan.'),
            ('Pembatasan divisi di controller.','Audit ini bukan uji penetrasi menyeluruh terhadap semua endpoint/serangan.'),
            ('Login throttle 10 percobaan per menit.','Bukan pengganti MFA atau proteksi infrastruktur.'),
            ('Validasi server, whitelist sort, query builder.','Kelengkapan batas angka/teks masih perlu diselaraskan.'),
            ('UI menghapus token lokal ketika 401/logout.','Token di storage browser dapat diakses JavaScript jika ada XSS.'),
            ('Contoh konfigurasi produksi disediakan.','HTTPS, backup, monitoring, dan deployment publik belum dibuktikan oleh file contoh.')])+
        h('Rekomendasi Sanctum untuk SPA milik sendiri')+
        p('Dokumentasi resmi menyarankan memakai autentikasi SPA berbasis sesi cookie untuk SPA milik sendiri. Karena proyek saat ini memakai bearer token, sebut ini sebagai pilihan implementasi yang perlu dievaluasi sebelum produksi. Jangan menyatakan proyek sudah memakai cookie HttpOnly atau proteksi CSRF sesi bila alurnya belum diterapkan.')+cite('L2')+
        h('Lindungi isi materi dan demo')+
        p('Gunakan data fiktif/database pengujian. Jangan menampilkan .env, password database, token aktif, atau data nasabah sungguhan saat presentasi. Buku ini menyebut struktur dan contoh sintetis; kredensial operasional tidak diperlukan untuk menjelaskan desain.')+
        note('Jawaban ketika ditanya “sudah aman?”','“Ada autentikasi, pembatasan divisi, validasi server, transaksi, dan pengaman konflik/retry yang sudah diuji. Untuk produksi, strategi sesi, hardening deployment, dan pengujian keamanan yang lebih luas masih harus diselesaikan.”')))

    out.append(page('16 · POSTGRESQL','Indeks, query, dan fakta kecil database','PostgreSQL menyediakan kemampuan yang kuat, tetapi desain query tetap menentukan hasil.',
        p('PostgreSQL merupakan sistem database objek-relasional sumber terbuka. Riwayat pengembangannya berakar pada proyek POSTGRES di University of California, Berkeley pada 1986. Dukungan relasi dan transaksi cocok dengan kebutuhan akun, peluang, penugasan, target, serta jejak perubahan pada proyek ini.')+cite('P1')+
        p('Indeks membantu database menemukan baris yang relevan, tetapi membutuhkan ruang serta pekerjaan tambahan ketika data berubah. Planner tidak wajib memilih indeks jika pemindaian tabel dinilai lebih efisien. Karena itu klaim “setiap query pasti cepat karena ada indeks” tidak tepat.')+cite('P7')+
        table(['Indeks / pembatasan yang terlihat','Tujuan'],[
            ('opportunities: division_id, outcome, updated_at','Mendukung akses peluang menurut divisi/hasil serta urutan waktu.'),
            ('opportunities: pic_id, outcome, closed_date','Mendukung rekap/akses berdasarkan PIC, hasil, dan tanggal closing.'),
            ('audit_events: resource_type, resource_id','Mendukung pemuatan timeline untuk resource tertentu.'),
            ('UNIQUE pada target dan receipt','Menjaga kombinasi tidak berulang; PostgreSQL juga menyediakan struktur indeks untuk constraint terkait.')])+
        h('Langkah optimasi yang dapat dipertanggungjawabkan')+
        p('Ukur query dan jumlah data, identifikasi bottleneck, lalu tinjau execution plan dan indeks. Jangan menambah semua indeks yang mungkin tanpa melihat pola akses. Daftar peluang API dipaginasi, tetapi usePipeline saat ini mengambil semua halaman scoped untuk state browser; itu dapat menjadi batas pada volume besar.')+
        note('Kapasitas yang belum dibuktikan','Audit tidak menyajikan benchmark jumlah pengguna simultan atau jutaan peluang. PostgreSQL mampu dipakai pada banyak skala, tetapi kemampuan produk database bukan bukti aplikasi ini telah diuji pada skala tersebut.')))

    out.append(page('16 · POSTGRESQL','Tanggal bisnis dan zona waktu','DATE, waktu kejadian, waktu perangkat, dan konfigurasi koneksi tidak boleh dicampur begitu saja.',
        p('DATE menyimpan tanggal. Timestamp without time zone menyimpan nilai tanggal dan jam tanpa mempertahankan nama zona atau offset. Timestamp with time zone mempunyai semantik yang berbeda. Tipe timestamp tidak otomatis membuktikan seluruh waktu proyek disimpan UTC.')+cite('P9')+
        table(['Bagian proyek','Hasil pemeriksaan'],[
            ('recorded_date, follow_up_date, closed_date','Tipe DATE untuk tanggal bisnis.'),('created_at, updated_at, occurred_at','Timestamp without time zone pada metadata PostgreSQL.'),
            ('Timezone aplikasi','Asia/Jakarta pada pemeriksaan lokal.'),('Timezone koneksi PostgreSQL','Asia/Bangkok pada pemeriksaan lokal.'),
            ('Tanggal “hari ini” UI','Dapat mengikuti zona perangkat lewat fungsi tanggal JavaScript.'),('Tanggal “hari ini” server','Mengikuti konfigurasi aplikasi saat validasi/perhitungan server.')])+
        p('Kedua nama zona lokal tersebut mempunyai offset yang sama pada pemeriksaan ini, tetapi nama konfigurasi tetap berbeda. Yang perlu ditetapkan untuk deployment adalah konvensi penulisan, pembacaan, pengiriman JSON, dan tampilan waktu. Kolom tanpa zona tidak menyimpan informasi yang dapat dipakai untuk menebak asal waktu secara andal.')+
        h('Contoh persoalan praktis')+
        p('Pengguna dekat pergantian hari atau di zona lain dapat melihat “hari ini” berbeda dari server. Jika UI mengizinkan tanggal berdasarkan perangkat tetapi server menolaknya, pesan error perlu dipahami sebagai perbedaan dasar waktu. Aturan bisnis sebaiknya memakai zona yang disepakati untuk operasional cabang.')+
        note('Kalimat yang harus dihindari','“Semua tanggal pasti mengikuti jam laptop” dan “semua timestamp pasti UTC” sama-sama terlalu luas untuk implementasi ini. Jelaskan field mana yang berupa tanggal bisnis dan field mana yang berupa waktu teknis.')+
        p('Gunakan contoh tanggal yang valid saat demo; jangan mengubah jam sistem hanya untuk meloloskan aturan closing.')))
    return out
