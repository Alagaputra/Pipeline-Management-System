from book_common import *


def pages():
    out=[]
    out.append(page('17 · DEVELOPMENT','Composer, migration, dan seeder','Dependensi, struktur database, dan data awal adalah tiga hal yang berbeda.',
        table(['Bagian','Arti pada proyek','Contoh'],[
            ('Composer','Mengelola dependensi PHP dan autoload kelas.','composer.json mendeklarasikan kebutuhan; composer.lock mencatat versi resolusi.'),
            ('Migration','Riwayat perubahan skema yang dijalankan terurut.','Membuat opportunities atau menambahkan request_receipts.'),
            ('Seeder','Kode pengisian/pembaruan data awal.','Divisi, produk, scope, serta akun pengembangan.'),
            ('Eloquent model','Representasi tabel dan relasi untuk kode aplikasi.','Opportunity, AnnualTarget, User.'),
            ('Metadata skema','Deskripsi struktur yang sudah ada.','schema.json berisi tabel, kolom, constraint, dan indeks; bukan record nasabah.')])+
        p('Laravel migration berfungsi sebagai riwayat struktur database yang dapat dikelola bersama kode. Filename memiliki urutan waktu agar perubahan dapat dijalankan sesuai urutannya. Tabel migrations mencatat migration yang telah diterapkan. Hal ini berbeda dari menyimpan seluruh data sebagai file SQL yang selalu diimpor ulang.')+cite('L7')+
        h('Mengapa tidak selalu menjalankan migrate:fresh?')+
        p('Perintah yang membangun ulang skema dapat menghapus data. Untuk instalasi yang sudah berisi data, perubahan biasanya diterapkan dengan migration baru tanpa mengosongkan tabel operasional. README proyek membedakan instalasi awal, lingkungan pengujian, dan pembaruan instalasi yang sudah ada.')+
        h('Seeder proyek bukan pembuat akun produksi')+
        p('DatabaseSeeder menggunakan updateOrCreate dan menetapkan password akun contoh. Menjalankannya pada database operasional dapat mengubah akun yang namanya cocok. Karena itu jangan menjadikannya langkah pembaruan produksi yang dilakukan otomatis tanpa rencana.')+
        note('Latihan lisan','“Migration mengatur bentuk tabel; seeder mengatur data awal; model mengatur akses data melalui kode; Composer menyediakan dependensi PHP yang menjalankannya.”')))

    out.append(page('18 · PENGUJIAN','Apa yang telah diuji?','Hasil terbaru dijalankan kembali pada 20 Oktober 2026.',
        table(['Pemeriksaan','Hasil','Batas interpretasi'],[
            ('Logika frontend','9 tes lulus.','Meliputi validasi, perhitungan tahun closing, tanggal/tindak lanjut, dan kompatibilitas migrasi.'),
            ('Backend','17 tes, 129 assertion lulus.','SQLite in-memory; dua tes adalah contoh dasar framework.'),
            ('Browser end-to-end','29 tes lulus, sekitar 2,9 menit.','Edge/Chromium lokal, backend Laravel dan PostgreSQL pengujian.'),
            ('Layout','45 kombinasi halaman/akun/lebar.','Diperiksa di dalam tiga tes layout; bukan 45 tes terpisah di luar angka 29.'),
            ('Build','Vite build berhasil.','Membuktikan bundling selesai; bukan deployment publik.'),
            ('Dokumentasi','ERD, arsitektur, DFD, PDF dirender/diperiksa.','Keterbacaan dan kecocokan metadata; bukan audit kepatuhan formal.')])+
        h('Lapisan tes saling melengkapi')+
        p('Tes logika cepat memeriksa fungsi tertentu. Tes backend memeriksa request, akses, penyimpanan, dan hasil API. Tes browser memeriksa alur yang benar-benar dipakai pengguna, termasuk render, formulir, jaringan, dan reload. Satu lapisan yang lulus belum menggantikan kebutuhan lapisan lain.')+
        p('Playwright menggunakan browser context untuk memisahkan penyimpanan/cookie antartes. Namun isolasi browser tidak otomatis mengosongkan database yang dipakai server. Karena itu proyek menyediakan database pengujian tersendiri dan memakai port API/frontend terpisah.')+cite('E1')+
        note('Pernyataan yang tepat','“Tes membuktikan skenario yang diuji pada lingkungan yang dijalankan.” Tidak sama dengan “tidak ada bug lagi”. Belum ada hasil uji beban, semua browser, pentest penuh, atau UAT operasional yang dapat diklaim selesai.')+
        p('<strong>Lokasi:</strong> <code>frontend/tests</code>, <code>frontend/src/tests</code>, <code>frontend/tests/e2e</code>, dan <code>backend/tests</code>.')))

    out.append(page('18 · PENGUJIAN','Menguji kegagalan, bukan hanya jalur berhasil','Keandalan terlihat ketika jaringan atau keadaan data tidak sesuai harapan.',
        table(['Skenario','Mengapa penting','Hasil yang diuji'],[
            ('Respons simpan hilang','Server bisa sudah commit walau klien belum tahu.','Retry tidak menggandakan peluang/audit.'),
            ('Refresh laporan gagal setelah simpan','Kegagalan baca dapat disalahartikan sebagai gagal simpan.','Formulir sukses tetap selesai; tidak membuka pencatatan ulang.'),
            ('Produk/bulan akhir konflik','Bagian awal formulir sudah mulai ditulis.','Transaksi PostgreSQL membatalkan seluruh formulir.'),
            ('Head cepat mengganti divisi/tahun','Respons lama dapat tiba belakangan.','Data lama tidak menimpa pilihan terbaru.'),
            ('Token tidak sah','UI bisa tetap mempunyai state pengguna.','401 menghapus sesi lokal dan mengarah ke login.'),
            ('Logout tanpa jaringan','Server tidak dapat dihubungi.','Pengguna tetap keluar dari state lokal.'),
            ('Navigasi dengan isian berubah','Pekerjaan pengguna dapat hilang.','Konfirmasi pembatalan/back menjaga keputusan pengguna.')])+
        h('Pisahkan jenis kegagalan')+
        p('<strong>Validasi</strong> berarti request ditolak karena data tidak memenuhi aturan. <strong>Konflik</strong> berarti keadaan server sudah berubah. <strong>Gangguan transport</strong> berarti klien tidak menerima hasil yang pasti. Pengguna membutuhkan tindakan berbeda: memperbaiki isian, memuat data terbaru, atau mengulang operasi yang sama dengan key yang dipertahankan.')+
        h('Tes akses yang bernilai')+
        p('Memeriksa bahwa PIC Konsumer tidak dapat memakai Giro atau PIC Komersil membuktikan aturan server, bukan sekadar dropdown tampilan. Memeriksa bahwa timeline tidak dapat dibaca divisi lain membantu memastikan jejak perubahan tidak bocor melalui endpoint detail.')+
        note('Prinsip belajar','Untuk setiap pengaman, tanyakan: kondisi awalnya apa, kegagalannya bagaimana, data apa yang seharusnya tetap, dan bukti apa yang diperiksa tes? Ini membuat jawaban ujian konkret.')))

    out.append(page('19 · MENELUSURI KODE','Telusuri satu penyimpanan dari layar sampai tabel','Gunakan satu alur yang sama ketika menjelaskan tanggung jawab setiap lapisan.',
        table(['Urutan','Tempat yang dibaca','Pertanyaan yang dijawab'],[
            ('1','OpportunityDrawer.vue','Isian apa yang ditampilkan dan kapan tombol simpan/closing aktif?'),
            ('2','utils/pipeline.js','Validasi awal apa yang membantu pengguna?'),
            ('3','usePipeline.js','Bagaimana field tampilan dipetakan menjadi payload dan konteks divisi?'),
            ('4','services/api.js','Bagaimana token, key, timeout, serta error ditangani?'),
            ('5','routes/api.php','Endpoint mana menuju method controller?'),
            ('6','IdempotentWrite + Sanctum','Apakah pengguna sah dan apakah operasi pernah sukses?'),
            ('7','OpportunityController + AuthorizesDivision','Apakah peluang terlihat, aktif, versinya cocok, dan isian valid?'),
            ('8','Model + PostgreSQL + WritesAudit','Record/relasi apa yang berubah dan di mana transaksi berlaku?'),
            ('9','Respons → composable → komponen','Bagaimana UI menampilkan hasil serta memuat ringkasan terbaru?')])+
        h('Contoh penjelasan closing')+
        p('Pengguna memeriksa ringkasan lalu mengirim hasil. Backend membaca peluang yang diizinkan dengan lock, memvalidasi versi dan hasil, menulis outcome/realisasi/catatan, lalu membuat audit. Hasil terkait PIC/produk/divisi dimuat, transaksi diselesaikan, dan JSON dikembalikan. Frontend menyajikan hasil serta memperbarui data yang diperlukan.')+
        note('Jika diminta membuka kode','Buka route dan method close terlebih dahulu, lalu middleware idempotensi. Jangan mulai dari file vendor yang sangat panjang; penguji biasanya ingin memahami logika proyek yang kamu terapkan.')+
        p('Diagram Level 3 menunjukkan aliran data pada proses closing tersebut. Nama paket di gambar merupakan ringkasan; tabel penjelasan DFD.md menguraikan isinya.')))

    out.append(page('20 · MENJALANKAN PROYEK','Menjalankan, membangun, dan menyiapkan demo','Perintah berikut menjelaskan susunan lokal; gunakan database yang sesuai konteks.',
        h('Dua proses utama saat pengembangan')+
        code('# Terminal backend dari direktori utama\ncd src/backend\n.\\php.cmd artisan serve\n\n# Terminal frontend dari direktori utama\nnpm.cmd run dev')+
        p('Alamat frontend lokal umumnya 127.0.0.1:5173; API Laravel 127.0.0.1:8000/api. PostgreSQL harus berjalan. File php.cmd lokal menambahkan konfigurasi PDO PostgreSQL pada Windows. Di platform lain, ekstensi dan perintah PHP dapat diatur melalui instalasi sistem.')+
        h('Perintah pemeriksaan')+
        code('# Dari direktori utama\nnpm.cmd test\nnpm.cmd run build\nnpm.cmd run test:e2e\n\n# Dari src/backend, konfigurasi tes terpisah\n.\\php.cmd artisan test')+
        h('Hal yang diperiksa sebelum demo')+
        ul('Gunakan data fiktif yang kamu pahami; siapkan akun pada scope yang akan dijelaskan.',
           'Periksa koneksi frontend, API, dan database. Pastikan tahun serta divisi terpilih benar.',
           'Tentukan satu peluang Active untuk contoh tindak lanjut/closing. Closing final; rencanakan demonstrasinya.',
           'Simpan PDF/diagram dan screenshot sebagai bahan penjelasan ketika layanan lokal bermasalah.')+
        note('Instalasi awal berbeda dari penggunaan harian','composer install dan npm install menyediakan dependensi. Migration menerapkan struktur. Seeder contoh tidak perlu dijalankan setiap kali membuka aplikasi dan tidak boleh dianggap langkah aman untuk database operasional yang sudah berisi data.')+
        p('Jangan menampilkan isi .env atau token aktif saat menjelaskan koneksi. Struktur konfigurasi dapat diterangkan tanpa mengungkap password.')))

    out.append(page('20 · MENJALANKAN PROYEK','Deployment dan pekerjaan berikutnya','Server lokal yang berhasil diakses belum membuktikan kesiapan layanan produksi.',
        table(['Area','Yang sudah ada','Pekerjaan berikutnya'],[
            ('Penyajian frontend','Aset dist hasil build Vite.','Konfigurasi penyajian aset, domain, cache, dan distribusi versi.'),
            ('Backend','Laravel API dan contoh .env.production.example.','Web server/PHP process manager, debug off, konfigurasi rahasia, HTTPS.'),
            ('Autentikasi','Mode bearer token berjalan.','Evaluasi sesi cookie SPA, umur sesi, pencabutan, dan kebijakan akun.'),
            ('Data','PostgreSQL, migration, constraint, transaksi.','Hak database minimum, backup terjadwal, bukti restore, retensi audit/receipt.'),
            ('Skala','Scope dan API pagination tersedia.','Profil query, pindahkan pemuatan seluruh daftar bila volume besar, uji beban.'),
            ('Penerimaan pengguna','Alur otomatis lokal diuji.','UAT bersama pihak operasional dan keputusan aturan bisnis yang belum ditetapkan.')])+
        h('Jangan menambah arsitektur tanpa kebutuhan')+
        p('Redis, queue, Docker, atau microservice dapat berguna pada kebutuhan tertentu, tetapi tidak otomatis dibutuhkan untuk membuat proyek terlihat profesional. Setiap komponen menambah tanggung jawab operasional. Usulkan berdasarkan bottleneck atau kebutuhan, lalu sertakan ukuran keberhasilannya.')+
        h('Contoh prioritas rasional')+
        p('Pertama tetapkan kontrak angka, strategi sesi, dan tata kelola akses. Kedua buktikan backup-restore serta lingkungan deployment. Ketiga ukur beban nyata dan optimasi jalur yang terbukti lambat. Keempat tambahkan fitur bisnis seperti approval atau koreksi closing jika memang diperlukan pengguna.')+
        note('Batas manfaat yang belum diukur','Tidak ada dasar untuk menyebut aplikasi meningkatkan efisiensi 80%, aman 100%, atau mampu melayani jumlah pengguna tertentu dari hasil audit ini. Tujuan dan hasil terukur harus dibedakan.')))

    out.append(page('21 · LATIHAN PENJELASAN','Susun cerita proyek dalam 90 detik','Latihan ini membantu merangkum tanpa menghilangkan hubungan bisnis dan teknis.',
        note('Contoh penjelasan singkat','“Saya mengembangkan website untuk mencatat dan memantau pipeline funding. PIC mengelola data pada divisinya, sedangkan Head Funding dapat memantau kedua divisi. Peluang dicatat sebagai aktif, diberi tingkat ketertarikan dan jadwal tindak lanjut, lalu dapat ditutup Won atau Lost. Realisasi dana dihitung dari Won berdasarkan tahun closing. Target layanan dihitung dalam unit dan dipisahkan dari dana. Frontend menggunakan Vue dan Chart.js, backend Laravel API, serta PostgreSQL sebagai penyimpanan. Aturan akses dan validasi final dijalankan di server. Untuk menjaga konsistensi, saya memakai transaksi, pemeriksaan versi, audit, dan pengenal retry. Fungsinya sudah diuji pada lingkungan lokal; kesiapan produksi masih memerlukan penguatan sesi, operasional data, dan pengujian lebih lanjut.”')+
        h('Jika diberi waktu lebih panjang')+
        table(['Bagian','Fokus penjelasan'],[
            ('Pembukaan','Masalah pencatatan, pengguna, dan tujuan.'),('Alur bisnis','Satu contoh peluang dari Active sampai closing dan Riwayat.'),
            ('Data dan laporan','Bedakan nominal, realisasi, tahun, target, serta unit layanan.'),('Desain teknis','Jelaskan tiga lapis dan satu endpoint sampai tabel.'),
            ('Keandalan','Berikan contoh konflik versi dan respons hilang.'),('Bukti dan refleksi','Hasil tes, koreksi dokumentasi, batas produksi, dan rencana pengembangan.')])+
        p('Sesuaikan durasi tiap bagian dengan waktu yang diberikan penguji. Jangan menyebut seluruh nama tabel sebelum menjelaskan masalah bisnisnya. Ketika pertanyaan berpindah ke teknis, gunakan diagram atau kode yang tepat untuk menjawabnya.')+
        note('Cara berlatih','Rekam penjelasanmu, dengarkan kembali, dan tandai kalimat yang terlalu abstrak. Ubah “datanya terintegrasi” menjadi contoh konkret tentang record opportunity yang dibaca Dashboard, Tim, dan Riwayat.')))

    out.append(page('22 · TANYA JAWAB','Pertanyaan tentang bisnis dan fitur','Jawaban berikut adalah model belajar; pahami alasannya agar dapat menjawab pertanyaan lanjutan.',
        qa('1. Apa perbedaan pipeline dengan realisasi?','Pipeline adalah potensi peluang yang dikelola. Realisasi dana adalah nilai hasil Won yang dicatat saat closing. Potensi Rp1 miliar tidak otomatis menjadi realisasi Rp1 miliar.')+
        qa('2. Mengapa Hot tidak otomatis Won?','Hot adalah kategori ketertarikan, sedangkan Won adalah hasil. Closing memerlukan keputusan pengguna, tanggal valid, dan nilai realisasi yang memenuhi aturan. Tidak ada model prediksi closing otomatis.')+
        qa('3. Apakah PIC hanya dapat melihat peluang miliknya?','Tidak. Batas utama PIC adalah divisi sendiri, termasuk peluang PIC lain di divisi yang sama. Head Funding dapat mengakses kedua divisi sesuai konteks.')+
        qa('4. Mengapa peluang tahun lalu masih muncul saat memilih tahun ini?','Daftar/indikator aktif mencakup seluruh periode agar pekerjaan lama yang belum selesai tidak tersembunyi. Target dan hasil closing memakai tahun laporan.')+
        qa('5. Mengapa nasabah tidak menjadi aktor pada DFD?','Nasabah tidak memakai aplikasi secara langsung dalam implementasi ini. Nama nasabah merupakan bagian data yang dimasukkan PIC/Head. Aktor eksternalnya adalah kedua pengguna aplikasi tersebut.')+
        qa('6. Mengapa CMS tidak dijumlahkan dari dua divisi?','CMS disimpan pada scope shared dan dilihat bersama. Kedua divisi mengakses record yang sama, sehingga menjumlahkan layar keduanya akan menggandakan target dan realisasi.')+
        note('Latihan lanjutan','Jelaskan fitur yang belum ada: koreksi closing, notifikasi otomatis, integrasi sistem inti bank, dan approval tidak boleh ditunjukkan seolah sudah diimplementasikan.')))

    out.append(page('22 · TANYA JAWAB','Pertanyaan tentang frontend dan API','Hubungkan konsep umum dengan berkas yang digunakan proyek.',
        qa('7. Mengapa memakai Vue?','UI mempunyai komponen dan state dinamis seperti formulir, panel, kartu target, dan grafik. Vue membantu merangkai tampilan reaktif. Ini alasan kecocokan proyek, bukan klaim Vue selalu unggul dari alternatif.')+
        qa('8. Apakah proyek memakai Pinia atau TypeScript?','State utama yang ditinjau berada pada composable berbasis ref/computed, dan kode frontend menggunakan JavaScript. Jangan menyebut Pinia/TypeScript sebagai teknologi yang dipakai hanya karena populer di ekosistem Vue.')+
        qa('9. Apakah ref otomatis menyimpan ke database?','Tidak. Ref mengubah state browser. Penyimpanan permanen terjadi melalui request API yang berhasil menjalankan transaksi database.')+
        qa('10. Apa fungsi Vite dan Node jika backend-nya PHP?','Node menjalankan tooling seperti Vite dan tes JavaScript. Vite menyediakan dev server/build. PHP menjalankan Laravel untuk API bisnis. Ketiganya mempunyai peran berbeda.')+
        qa('11. Mengapa URL memakai #?','Router memakai hash history. Bagian hash ditangani browser sehingga navigasi SPA tidak memerlukan fallback path server yang sama dengan HTML5 history. API tetap mempunyai path /api terpisah.')+
        qa('12. Apakah Chart.js yang menghitung seluruh pencapaian?','Tidak. Agregasi dana utama berasal dari backend, sedangkan frontend mengolah penyajian dan sebagian rekap/layanan dari data API scoped. Chart.js merender dataset yang diberikan.')+
        note('Buka berkas untuk membuktikan','router/index.js, services/api.js, usePipeline.js, useSession.js, DashboardView.vue, dan ReportChart.vue adalah titik awal yang baik.')))

    out.append(page('22 · TANYA JAWAB','Pertanyaan tentang database dan laporan','Jawaban yang baik membedakan struktur fisik, aturan bisnis, dan penyajian.',
        qa('13. Mengapa menggunakan database relasional?','Peluang, pengguna, produk, divisi, penugasan, dan target mempunyai hubungan yang jelas. PK/FK/UNIQUE serta transaksi membantu menjaga keterkaitannya. Bukan berarti database lain mustahil dipakai.')+
        qa('14. Apakah History mempunyai tabel sendiri?','Tidak. Riwayat closing menyaring peluang Won/Lost pada opportunities. Timeline detail membaca audit_events. Riwayat PIC membaca penugasan. Ketiganya berbeda.')+
        qa('15. Apakah nominal disimpan sebagai DECIMAL?','Pada skema yang diperiksa, nominal dan target dana memakai BIGINT rupiah bulat. PostgreSQL menyediakan NUMERIC/DECIMAL, tetapi itu bukan tipe fisik dana yang sedang digunakan.')+
        qa('16. Apakah FK sudah memastikan Giro tidak masuk Konsumer?','Tidak sendirian. FK produk dan divisi memastikan ID terkait ada. Kesesuaian pasangan serta satuan produk diperiksa controller; tidak ada FK komposit opportunity ke pasangan produk/divisi untuk seluruh aturan tersebut.')+
        qa('17. Mengapa persentase target nol bukan 0%?','Karena target belum ditetapkan dan pembagian nol tidak bermakna. Backend mengembalikan null untuk persentase; realisasi masih dapat ditampilkan sebagai nilai tersendiri.')+
        qa('18. Bagaimana menghitung persentase total?','Jumlahkan realisasi dana dan target pada scope/tahun yang sesuai, kemudian bagi total realisasi dengan total target. Jangan merata-ratakan persentase produk dengan target berbeda.')+
        note('Soal cepat','Target Tabungan Rp2 miliar, realisasi Rp600 juta: 30%. Target Giro Rp1 miliar, realisasi nol: 0%. Rata-rata 15% bukan pencapaian gabungan; gabungannya Rp600 juta/Rp3 miliar = 20%.')))

    out.append(page('22 · TANYA JAWAB','Pertanyaan tentang integritas dan keamanan','Siapkan contoh konkret untuk istilah yang tampak mirip.',
        qa('19. Apa bedanya transaksi, version, dan idempotency key?','Transaksi menjaga satu unit tulis selesai bersama/batal. Version mendeteksi isian berdasarkan record lama. Key menandai satu operasi agar pengulangan request tidak menambah hasil yang sama lagi.')+
        qa('20. Kalau koneksi terputus, apakah data pasti gagal tersimpan?','Tidak. Server mungkin sudah commit. Klien mengulang operasi identik dengan key yang sama agar server dapat mengembalikan receipt sukses tanpa duplikasi.')+
        qa('21. Apakah token Sanctum proyek ini JWT?','Mode yang ditinjau menggunakan personal access token Sanctum dengan penyimpanan hash token dan autentikasi Bearer. Jangan menyamakannya dengan JWT tanpa penyimpanan token.')+
        qa('22. Mengapa login di perangkat lain bisa mengeluarkan sesi lama?','AuthController menghapus token lama akun sebelum membuat token baru. Permintaan berikutnya memakai token lama dapat ditolak 401.')+
        qa('23. Apakah log audit pasti tidak dapat diubah?','Tidak ada bukti mekanisme database/kriptografi yang membuatnya kebal pihak dengan hak tinggi. Aplikasi menulis audit dalam alur normal, tetapi klaim tamper-proof memerlukan kontrol tambahan.')+
        qa('24. Mengapa masih merekomendasikan penguatan sesi?','Token berada pada storage yang dapat diakses JavaScript, dan umur global token belum ditentukan. Mode sesi cookie SPA, kebijakan pencabutan, serta hardening deployment perlu dievaluasi sebelum produksi.')+
        note('Jawaban aman bukan jawaban menghindar','Sebutkan pengaman yang sudah dibuat, bukti pengujiannya, lalu batas yang belum selesai. Memahami keterbatasan menunjukkan penguasaan desain.')))

    out.append(page('22 · TANYA JAWAB','Pertanyaan tentang pengujian dan evaluasi','Jangan mengubah hasil tes menjadi klaim yang lebih besar daripada buktinya.',
        qa('25. Mengapa tes backend menggunakan SQLite tetapi aplikasi PostgreSQL?','SQLite in-memory membuat tes backend cepat dan terisolasi. Suite browser juga menguji alur dengan PostgreSQL, termasuk rollback. Tetap perlu membedakan perilaku khusus engine dan tidak menganggap satu engine mewakili semuanya.')+
        qa('26. Apakah 45 kombinasi layout berarti ada 45 tes browser?','Tidak. Tiga tes layout masing-masing memeriksa beberapa halaman dan lebar pada akun terkait. Total suite yang dijalankan adalah 29 tes, dan 45 adalah kombinasi tampilan di dalamnya.')+
        qa('27. Apakah lulus build berarti siap produksi?','Tidak. Build membuktikan bundling selesai. Produksi memerlukan konfigurasi server, HTTPS, akun/rahasia, backup, monitoring, dan pengujian yang sesuai.')+
        qa('28. Berapa persen efisiensi yang meningkat?','Belum ada pengukuran lapangan terverifikasi untuk menyebut persentase. Jelaskan tujuan seperti pencatatan terpusat dan pemantauan yang konsisten, lalu usulkan evaluasi sebelum-sesudah dengan indikator yang jelas.')+
        qa('29. Apa keterbatasan paling penting yang kamu temukan?','Strategi sesi, keselarasan batas angka/teks, retensi data jejak, pemuatan seluruh daftar di UI, serta bukti produksi/UAT. Pilih yang relevan dan jelaskan rencana perbaikannya.')+
        qa('30. Apa yang diperbaiki dalam peninjauan dokumentasi?','Pembacaan D1/D2 pada hasil tindak lanjut dan closing ditampilkan pada DFD, batas idempotensi login/logout diperjelas, dan fakta versi/tipe data diikat ke lockfile serta katalog aktif.')))

    out.append(page('23 · LATIHAN AKTIF','Enam kasus untuk menguji pemahaman','Coba jawab tanpa melihat bagian bawah tabel terlebih dahulu.',
        table(['Kasus','Jawaban dan alasan'],[
            ('Peluang dicatat 2025, Won pada Januari 2026. Ke tahun mana realisasinya masuk?','2026, karena realisasi dana mengikuti closed_date, bukan recorded_date.'),
            ('Nominal Rp500 juta, pengguna mengirim Won Rp600 juta.','Ditolak karena realisasi melebihi nominal. Status minat Hot tidak mengubah batas itu.'),
            ('A menyimpan version 4 menjadi 5. B mengirim version 4.','Konflik 409; muat ulang. Jangan otomatis menimpa data A.'),
            ('Simpan sukses di server tetapi respons hilang. Pengguna menekan Coba lagi.','Gunakan key/path/body yang sama. Receipt memutar ulang hasil tanpa record/audit baru.'),
            ('CMS shared target 100, realisasi 40. Kedua divisi menampilkan nilai sama.','Gabungan tetap 100 dan 40, bukan 200 dan 80.'),
            ('Target dana Rp1 miliar, realisasi Rp1,2 miliar.','Persentase 120%; sisa target nol. Bar visual dapat tetap hanya sepanjang 100%.')])+
        h('Tugas penelusuran')+
        ul('Temukan route closing, lalu tunjukkan baris yang memeriksa outcome Active, version, dan realisasi.',
           'Temukan tempat peluang Won tetap berada pada model Opportunity, bukan dipindahkan ke model/tabel Won.',
           'Temukan pemeriksaan scope shared pada TargetController, lalu jelaskan mengapa CMS tidak ditulis per divisi.',
           'Temukan context/request sequence pada loader, lalu jelaskan kasus respons tahun lama.')+
        note('Rubrik belajar sederhana','Untuk setiap jawaban, sebut keadaan awal, aturan yang berlaku, tempat aturan dijalankan, dan hasil yang diterima pengguna. Empat bagian itu cukup untuk menjawab banyak pertanyaan lanjutan.')+
        p('Jika belum dapat menunjukkan acuan kode, tandai topik tersebut untuk dibaca kembali. Buku ini bukan pengganti mencoba menelusuri alur pada proyek sendiri.')))

    out.append(page('24 · FAKTA KECIL','Fakta kecil yang berguna saat menjelaskan','Pilih fakta yang menerangkan desain, bukan trivia yang terlepas dari aplikasi.',
        table(['Fakta','Hubungannya dengan proyek'],[
            ('Vue diucapkan “view”.','Menguatkan konteksnya sebagai teknologi antarmuka.'),
            ('Reaktivitas tidak sama dengan penyimpanan permanen.','Ref dapat berubah sebelum request simpan berhasil.'),
            ('Vite menyediakan dev server dan build.','Versi proyek 7 memakai rincian toolchain yang harus dibaca pada dokumentasi mayor 7.'),
            ('PHP adalah singkatan rekursif.','Nama lengkapnya PHP: Hypertext Preprocessor; dipakai mengeksekusi Laravel.'),
            ('Node.js bukan sinonim backend aplikasi.','Di proyek ini Node menjalankan tooling, sedangkan API dijalankan PHP.'),
            ('PostgreSQL tidak mempunyai BIGINT UNSIGNED.','Aturan nonnegatif proyek berada pada validasi API.'),
            ('JSON dan JSONB bukan tipe yang identik.','Snapshot pada skema proyek bertipe json; jangan otomatis menyebut jsonb.'),
            ('Indeks menambah biaya tulis dan ruang.','Indeks dipilih berdasarkan pola akses dan pengukuran.'),
            ('Satu scope shared mencegah penghitungan ganda.','CMS yang dilihat dua divisi tetap satu target.'),
            ('Timestamp tanpa zona tidak menyimpan offset.','Konvensi waktu perlu ditetapkan lintas browser, aplikasi, dan database.'),
            ('Jumlah tes dan kombinasi tampilan berbeda.','29 tes suite mencakup 45 kombinasi layout dalam tes terkait.'),
            ('Token hash berbeda dari password hash.','Sanctum memakai SHA-256 untuk token; driver password lokal bcrypt.')])+
        p('Fakta tentang konfigurasi dan tipe fisik berasal dari pemeriksaan proyek. Fakta umum teknologi mengikuti rujukan resmi pada bab terkait. Tidak ada klaim bahwa proyek memakai setiap kemampuan yang tersedia pada framework/database.')+
        cite('V1','T1','H1','N1','P3','P7','P9','L2','L6')))

    glossary=[
        ('API','Kontrak yang memungkinkan komponen meminta data atau menjalankan operasi melalui antarmuka yang ditentukan.'),
        ('HTTP','Protokol request/response yang dipakai browser dan API pada proyek.'),('JSON','Format pertukaran data terstruktur yang digunakan respons dan body API.'),
        ('SPA','Single-Page Application: navigasi antarmuka dikelola aplikasi browser tanpa selalu memuat dokumen HTML baru.'),
        ('DOM','Representasi dokumen halaman yang dapat diperbarui browser/JavaScript.'),('Komponen','Bagian antarmuka yang mengemas tampilan dan perilaku agar dapat disusun/dipakai ulang.'),
        ('Composable','Fungsi yang mengemas logika reaktif Vue untuk dipakai kembali.'),('Reaktivitas','Mekanisme dependensi yang membuat nilai/tampilan mengikuti perubahan state.'),
        ('State','Keadaan data yang sedang dikelola aplikasi, misalnya pengguna, tahun, atau peluang.'),('Props','Data yang diberikan komponen induk kepada komponen anak.'),
        ('Middleware','Lapisan pemeriksaan/pengolahan request dan response sebelum/sesudah handler terkait.'),('Controller','Kode yang menerima request terkait dan mengoordinasikan aturan/respons.'),
        ('ORM','Object-Relational Mapping: pola mengakses data relasional melalui model/objek kode.'),('Scope','Lingkup data atau target, misalnya Konsumer, Komersil, atau shared.'),
        ('Autentikasi','Pemeriksaan identitas pengguna; pada proyek API memakai Sanctum.'),('Otorisasi','Pemeriksaan tindakan/data yang diizinkan bagi pengguna yang dikenali.'),
        ('Bearer token','Kredensial yang dikirim pada Authorization header untuk akses API.'),('Hash','Ringkasan satu arah; password dan token tidak dijelaskan sebagai enkripsi yang dapat dibalik.'),
        ('Skema','Struktur tabel, kolom, tipe, constraint, dan hubungan database.'),('Primary key','Identitas unik dan tidak null untuk record tabel.'),
        ('Foreign key','Constraint yang menjaga rujukan ke record terkait.'),('UNIQUE','Pembatasan agar nilai atau kombinasi tertentu tidak duplikat.'),
        ('Kardinalitas','Jumlah hubungan yang mungkin, misalnya satu target ke banyak rincian bulan.'),('Indeks','Struktur pendukung pencarian yang juga menambah biaya ruang/tulis.'),
        ('Transaksi','Unit operasi database yang dapat commit bersama atau rollback.'),('Commit','Penyelesaian transaksi sehingga perubahan menjadi hasil transaksi yang disahkan.'),
        ('Rollback','Pembatalan perubahan transaksi yang belum diselesaikan.'),('Row lock','Penguncian eksplisit baris untuk mengoordinasikan akses perubahan antartransaksi.'),
        ('MVCC','Multiversion Concurrency Control: mekanisme visibilitas beberapa versi data antartransaksi.'),('Version','Angka versi record aplikasi untuk memeriksa isian yang sudah tertinggal.'),
        ('Idempotency key','Pengenal satu operasi agar pengulangan identik tidak menambah efek bisnis lagi.'),('Receipt','Record hasil respons sukses yang digunakan untuk replay request.'),
        ('Migration','Riwayat perubahan struktur database yang dikelola bersama kode.'),('Seeder','Kode pengisian/pembaruan data awal, berbeda dari perubahan struktur.'),
        ('XSS','Eksekusi script tidak semestinya pada konteks halaman; relevan terhadap token yang dapat dibaca JavaScript.'),('CSRF','Request yang dipicu melalui konteks pengguna tanpa persetujuan yang semestinya; relevan saat merancang autentikasi sesi cookie.'),
    ]
    for n in range(2):
        out.append(page('25 · GLOSARIUM',f'Istilah penting · {n+1}/2','Arti praktis istilah yang muncul dalam buku dan kode proyek.',
            table(['Istilah','Makna untuk belajar'],glossary[n*18:(n+1)*18])+note('Belajar dengan contoh','Setelah memahami istilah, sebutkan satu contoh berkas atau kasus proyeknya. Contoh: version → dua PIC mengedit record yang sama; receipt → respons simpan hilang lalu diulang.')))

    out.append(page('26 · RINGKASAN BELAJAR','Satu halaman sebelum latihan presentasi','Gunakan sebagai pengingat hubungan konsep; jangan dibaca sebagai naskah hafalan.',
        table(['Topik','Yang perlu diingat'],[
            ('Masalah','Pencatatan, tindak lanjut, pemantauan, target, dan riwayat pipeline funding.'),
            ('Pengguna','PIC dibatasi divisi; Head kedua divisi; nasabah bukan pengguna langsung.'),
            ('Status','Cold/Warm/Hot ≠ Active/Won/Lost. Peluang baru Active; closing final.'),
            ('Dana','Realisasi dari Won menurut tahun closing; nominal merupakan potensi.'),
            ('Layanan','Total unit bulanan manual; CMS shared; unit tidak dijumlahkan dengan rupiah.'),
            ('UI','Vue + Router + CSS; Chart.js merender grafik; composable menyusun state/operasi.'),
            ('Backend','Laravel API; server menentukan akses dan validasi final.'),
            ('Database','PostgreSQL 18.4; 22 tabel, 162 kolom; peluang/history tidak diduplikasi.'),
            ('Integritas','Transaksi = satu unit; version = konflik keadaan; key = identitas retry.'),
            ('Keamanan','Bearer Sanctum; password bcrypt; perkuat strategi sesi sebelum produksi.'),
            ('Bukti','9 tes frontend; 17 backend/129 assertion; 29 browser; 45 kombinasi layout.'),
            ('Batas','Tidak ada klaim integrasi core banking, AI scoring, sertifikasi keamanan, atau efisiensi terukur.')])+
        note('Tiga contoh yang wajib bisa dijelaskan','Satu peluang dari Active ke Won/Lost; satu perhitungan target berdasarkan tahun closing; satu kegagalan jaringan atau konflik versi beserta cara pemulihannya.')+
        p('Jika ditanya hal yang belum dibuat, jelaskan statusnya dan arah desain yang masuk akal. Lebih baik jawaban terbatas tetapi sesuai implementasi daripada mengklaim fitur atau jaminan yang tidak ada.')))

    out.append(page('SUMBER DAN BUKTI','Peta berkas untuk membuka bukti','Gunakan nama berkas sebagai pintu masuk saat ingin memahami cara kerja sebenarnya.',
        table(['Berkas / lokasi relatif proyek','Yang dipelajari'],[
            ('src/frontend/src/router/index.js','Mode hash, guard login, halaman dan redirect.'),('src/frontend/src/services/api.js','Token, fetch, timeout, requestKey, dan error.'),
            ('src/frontend/src/composables/useSession.js','Login/logout, identitas pengguna, 401.'),('src/frontend/src/composables/usePipeline.js','Konteks, loader, state, pemetaan dan penyimpanan.'),
            ('src/frontend/src/utils/pipeline.js','Validasi UI, tanggal, status, rupiah, perhitungan.'),('src/frontend/src/components/OpportunityDrawer.vue','Formulir, review closing, detail.'),
            ('src/frontend/src/components/ReportChart.vue','Canvas, registrasi Chart.js, lifecycle, aksesibilitas.'),('src/backend/routes/api.php','Endpoint dan middleware.'),
            ('src/backend/app/Http/Controllers','Aturan request bisnis dan scope.'),('src/backend/app/Services/DashboardReport.php','Definisi perhitungan dana dan tren.'),
            ('src/backend/app/Http/Middleware/IdempotentWrite.php','Replay, hash request, receipt, transaksi.'),('src/backend/app/Support/WritesAudit.php','Aksi, snapshot, pelaku, waktu audit.'),
            ('src/backend/database/migrations','Struktur dan constraint yang dibangun.'),('src/docs/desain-sistem/schema.json','Metadata fisik terverifikasi, tanpa record operasional.')])+
        p('Paket <code>src/docs/evaluation</code> merupakan arsip versi September yang masih membahas MySQL. Materi ini mengikuti implementasi PostgreSQL yang diperiksa, dengan acuan desain terbaru di <code>src/docs/desain-sistem</code>.')+
        note('Lokasi hasil peninjauan','Lihat AUDIT-PROFESIONAL.md pada folder materi ini. Bukti metadata lokal berada di .runtime/study-audit/inspection.json; laporan verifikasi diagram dan materi berada di folder dokumentasi masing-masing.')))
    return out
