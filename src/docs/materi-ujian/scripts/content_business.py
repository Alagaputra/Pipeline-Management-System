from book_common import *


def pages():
    out = []
    out.append(page('PANDUAN BELAJAR','Memahami proyek sampai bisa menjelaskannya','Gunakan buku ini untuk memahami hubungan kebutuhan bisnis, antarmuka, API, dan database.',
        p('Proyek yang dipelajari adalah <strong>Sistem Manajemen Pipeline Funding BSN KC Bekasi</strong>. Buku ini disusun dari kode yang tersedia dan pemeriksaan lokal pada 20 Oktober 2026. Tujuannya membantu kamu menerangkan apa yang dibangun, bagaimana data bergerak, mengapa aturan tertentu dipilih, dan di mana batas implementasinya.')+
        h('Urutan belajar yang disarankan')+
        table(['Tahap','Yang harus bisa kamu jelaskan'],[
            ('1 · Bisnis','Masalah pencatatan peluang, pengguna, produk, status, target, dan hasil closing.'),
            ('2 · Alur','Satu peluang dari pencatatan sampai Won/Lost; perubahan apa yang masuk audit.'),
            ('3 · Teknis','Vue → HTTP JSON → Laravel → PostgreSQL → data laporan → grafik.'),
            ('4 · Integritas','Perbedaan validasi, foreign key, transaksi, version, dan idempotency key.'),
            ('5 · Pembuktian','Apa yang diperiksa tes; apa yang belum dibuktikan oleh audit ini.')])+
        h('Cara memakai setiap bab')+
        p('Baca penjelasan, telusuri berkas acuannya, lalu tutup buku dan terangkan kembali dengan bahasa sendiri. Jika belum dapat memberi contoh, ulangi contoh perhitungan dan kasus dua pengguna mengedit data. Tujuannya menguasai sebab-akibat, bukan menghafal nama fungsi.')+
        note('Tiga label yang perlu dibedakan','<strong>Implementasi</strong> berarti terlihat pada kode atau konfigurasi. <strong>Konsep</strong> adalah penjelasan teknologi dari dokumentasi resmi. <strong>Pengembangan</strong> adalah saran yang belum menjadi fitur. Jangan menyampaikan ketiganya seolah sudah diterapkan.')+
        p('Lampiran diagram memakai halaman A3 agar teks tetap terbaca. Bab belajar memakai A4. Gunakan daftar isi dan pencarian PDF untuk kembali ke istilah tertentu; tautan sumber resmi dapat diklik.')))

    out.append(page('01 · HASIL PENINJAUAN','Apakah sudah profesional?','Layak sebagai dokumentasi teknis dan bahan ujian magang, dengan catatan produksi yang dijelaskan secara terbuka.',
        p('Penilaian dilakukan melalui kecocokan diagram dengan kode, verifikasi katalog PostgreSQL, pemeriksaan tata letak, tes otomatis proyek, dan build frontend. Kata “profesional” di sini merupakan penilaian berbasis kriteria tersebut; tidak berarti sertifikasi ISO, audit kepatuhan bank, penetration test menyeluruh, atau persetujuan operasional dari instansi.')+
        table(['Aspek','Hasil dan dasar penilaian'],[
            ('DFD','Konteks dan Level 1–3 tersedia. PIC/Head terpisah, proses bernomor, panah bernama. Pembacaan referensi hasil closing/tindak lanjut dilengkapi.'),
            ('Database','22 tabel, 162 kolom, 22 FK, 12 UNIQUE, dan 22 PK cocok dengan katalog database aktif. Dua relasi logis pada ERD lengkap dibedakan dari FK SQL.'),
            ('Arsitektur','Vue + Chart.js, Laravel REST API, PostgreSQL sesuai implementasi. Deployment lokal dibedakan dari server publik.'),
            ('Tata letak','PDF DFD empat halaman A3; tidak ditemukan teks terpotong, label bertumpuk, atau ujung panah terlepas pada pemeriksaan renderer.'),
            ('Pengujian','Hasil terbaru dan batas cakupannya dicatat pada bab pengujian. Kelulusan tes bukan bukti bahwa seluruh risiko sudah hilang.')])+
        h('Hal yang tetap perlu ditingkatkan untuk penggunaan produksi')+
        ul('Autentikasi SPA masih memakai bearer token di penyimpanan browser. Evaluasi sesi cookie HttpOnly sesuai rekomendasi Sanctum untuk SPA milik sendiri.',
           'Batas bilangan aman JavaScript sudah dijaga pada UI, tetapi API dan total agregat memerlukan kebijakan presisi yang konsisten.',
           'Kebijakan retensi audit/receipt, backup-restore, pembaruan runtime, pengujian beban, dan validasi pengguna operasional perlu dibuktikan terpisah.')+
        note('Kalimat yang aman saat ujian','“Aplikasi dan dokumentasi sudah diuji pada lingkungan lokal untuk kebutuhan proyek magang. Kesiapan produksi memerlukan pengujian dan pengaturan operasional tambahan.”')))

    out.append(page('02 · KONTEKS BISNIS','Masalah yang ingin diselesaikan','Pipeline adalah daftar peluang pendanaan yang sedang dikelola, bukan saldo rekening bank.',
        p('Dalam konteks aplikasi ini, satu pipeline atau opportunity merepresentasikan peluang funding dari seorang nasabah/perusahaan untuk produk tertentu. Di dalamnya terdapat nominal potensi, PIC penanggung jawab, tingkat ketertarikan, tanggal tindak lanjut, dan hasil akhir. Data membantu tim mengetahui pekerjaan yang harus ditindaklanjuti dan melihat pencapaian terhadap target.')+
        h('Kebutuhan yang dijawab aplikasi')+
        ul('<strong>Pencatatan seragam:</strong> setiap peluang mempunyai struktur data yang sama sehingga dapat dicari dan diringkas.',
           '<strong>Pemantauan:</strong> peluang aktif, nominal potensi, Hot, dan tindak lanjut terlihat pada Dashboard.',
           '<strong>Akuntabilitas:</strong> perubahan serta perpindahan penanggung jawab dapat ditelusuri.',
           '<strong>Perbandingan:</strong> realisasi Won dapat dibandingkan dengan target pada produk, tahun, dan lingkup yang sesuai.',
           '<strong>Pembatasan akses:</strong> pengguna PIC dibatasi divisinya; Head Funding dapat memantau kedua divisi.')+
        h('Mengapa tidak cukup membuat tabel biasa?')+
        p('Tabel dapat mencatat angka, tetapi aplikasi ini menambahkan aturan bersama: produk mengikuti divisi, closing mempunyai persyaratan, perubahan dicegah ketika versinya sudah tertinggal, dan laporan dihitung dengan definisi yang sama. Manfaat tersebut berasal dari aturan serta penyimpanan terpusat, bukan sekadar mengganti tampilan spreadsheet menjadi halaman web.')+
        note('Batas klaim manfaat','Efisiensi waktu, pengurangan kesalahan, atau kepuasan pengguna belum dinyatakan dalam persentase karena tidak ada pengukuran lapangan yang diverifikasi pada peninjauan ini. Jelaskan sebagai tujuan/manfaat yang diharapkan, bukan hasil statistik.')+
        p('<strong>Latihan lisan:</strong> jelaskan perbedaan “nominal peluang Rp1 miliar” dengan “realisasi Won Rp600 juta”. Yang pertama potensi; yang kedua hasil closing yang dicatat pengguna.')))

    out.append(page('02 · KONTEKS BISNIS','Tujuan, ruang lingkup, dan batas sistem','Cakupan yang jelas membuat penjelasan proyek dapat dipertanggungjawabkan.',
        table(['Sudah menjadi cakupan aplikasi','Bukan fitur yang ditunjukkan implementasi saat ini'],[
            ('Login dan pembatasan divisi','Single sign-on perusahaan atau multi-factor authentication.'),
            ('Pencatatan, pembaruan, tindak lanjut, closing','Eksekusi transfer, pembukaan rekening, atau transaksi sistem inti bank.'),
            ('Dashboard, target, riwayat, informasi PIC','Prediksi peluang otomatis berbasis AI atau notifikasi WhatsApp/email otomatis.'),
            ('Target dana IDR dan layanan UNIT','Penyamaan unit layanan menjadi nominal dana.'),
            ('Audit perkembangan dan riwayat PIC','Bukti bahwa log kebal manipulasi oleh administrator database.'),
            ('Tampilan responsif dan tes otomatis lokal','Jaminan seluruh browser, beban produksi, dan deployment publik sudah diuji.')])+
        h('Tujuan teknis yang dapat ditunjukkan')+
        p('Data bisnis disimpan di PostgreSQL melalui API. Frontend memfokuskan interaksi, sedangkan backend menentukan akses dan validasi final. Penulisan penting memakai transaksi, version checking, dan pengenal retry. Dokumentasi menjelaskan model data serta arus informasi agar pengembang lain dapat memahami hasilnya.')+
        h('Pengguna bukan selalu entitas data')+
        p('Nasabah ada sebagai <code>customer_name</code> pada peluang, tetapi tidak mempunyai akun aplikasi dalam alur ini. Karena tidak berinteraksi langsung, nasabah tidak digambar sebagai entitas eksternal DFD. Tabel master nasabah juga belum ada; nama yang sama pada dua peluang belum otomatis dianggap satu identitas nasabah.')+
        note('Jika ditanya pembimbing','Gunakan “sistem pencatatan dan pemantauan pipeline funding”. Hindari menyebutnya “sistem perbankan penuh” karena aplikasi tidak menjalankan fungsi inti perbankan.')+
        p('Untuk pengembangan selanjutnya, kebutuhan identitas nasabah terstruktur, approval target, perubahan closing, dan ekspor laporan harus dirumuskan bersama pengguna. Jangan menambahkan aturan bisnis hanya berdasarkan asumsi teknis.')))

    out.append(page('03 · PENGGUNA DAN PRODUK','Hak akses dan penanggung jawab','Role dan divisi menentukan lingkup data; PIC bukan berarti hanya dapat membaca peluang miliknya sendiri.',
        table(['Aspek','PIC Komersil','PIC Konsumer','Head Funding'],[
            ('Peluang','Divisi sendiri','Divisi sendiri','Kedua divisi'),
            ('Melihat PIC lain','Ya, dalam divisinya','Ya, dalam divisinya','Ya, sesuai filter'),
            ('Produk dana','Tabungan, Giro, Deposito','Tabungan, Deposito','Mengikuti divisi'),
            ('Layanan','CMS bersama','Bale Syariah, QRIS, CMS','Gabungan / per lingkup'),
            ('Ubah data dana','Divisi sendiri','Divisi sendiri','UI memilih satu divisi'),
            ('Ubah CMS','Diizinkan','Diizinkan','Diizinkan'),
            ('Ubah closing final','Tidak tersedia','Tidak tersedia','Tidak tersedia')])+
        h('Autentikasi dan otorisasi berbeda')+
        p('<strong>Autentikasi</strong> menjawab siapa pengguna yang masuk. <strong>Otorisasi</strong> menentukan data atau tindakan yang boleh diaksesnya. Token yang sah tidak berarti pengguna boleh membaca semua divisi. Controller tetap membatasi query atau memeriksa resource yang diminta.')+
        p('Contoh: PIC Konsumer mengubah parameter <code>division_id</code> menjadi ID Komersil. Pada endpoint yang menggunakan lingkup akun PIC, parameter itu tidak memperluas hak akses. Produk Giro dan PIC Komersil juga ditolak ketika dipakai untuk peluang Konsumer. Aturan ini diperiksa pada server, bukan hanya melalui pilihan dropdown.')+
        h('Mengapa Head tidak mempunyai divisi tetap?')+
        p('Kolom <code>users.division_id</code> dapat kosong untuk akun Head. Fungsi <code>isHead()</code> mengidentifikasi role <code>head</code>. Tampilan gabungan berguna untuk pemantauan; saat menulis peluang atau target dana, antarmuka meminta konteks divisi yang jelas.')+
        note('Acuan kode','<code>AuthorizesDivision.php</code>, <code>TargetController::authorizeWrite</code>, <code>LookupController</code>, dan <code>usePipeline.js</code>. CMS adalah pengecualian bisnis yang menggunakan lingkup shared, bukan celah akses.')))

    out.append(page('03 · PENGGUNA DAN PRODUK','Membedakan dana dan layanan','Satuan yang berbeda tidak boleh dijumlahkan menjadi satu ukuran pencapaian.',
        table(['Produk','Satuan','Lingkup yang dipakai'],[
            ('Tabungan','IDR / rupiah','Konsumer dan Komersil'),('Giro','IDR / rupiah','Komersil'),
            ('Deposito','IDR / rupiah','Konsumer dan Komersil'),('Bale Syariah','UNIT','Konsumer'),
            ('QRIS','UNIT','Konsumer'),('CMS','UNIT','shared / bersama')])+
        p('Produk ditentukan pada tabel <code>products</code>. Kolom <code>measure</code> membedakan IDR dengan UNIT. Ketersediaan produk per divisi berada pada pivot <code>division_products</code>. Peluang dana hanya menerima produk IDR; produk layanan dicatat melalui target dan realisasi layanan bulanan.')+
        h('Satu CMS untuk dua divisi')+
        p('Scope <code>shared</code> tidak terikat pada satu divisi. Akun Komersil dan Konsumer melihat record CMS yang sama. Jika target CMS 100 unit dan realisasi 40 unit, tampilan gabungan tetap 100 dan 40; tidak menjadi 200 dan 80. Ini mencegah penghitungan ganda akibat sekadar menjumlahkan layar dua divisi.')+
        h('Dua sumber realisasi')+
        ul('<strong>Dana:</strong> dihitung dari nilai <code>realization</code> pada peluang Won berdasarkan tanggal closing.',
           '<strong>Layanan:</strong> total unit bulanan dimasukkan pengguna dan disimpan di <code>unit_realizations</code>. Pembaruan mengganti total bulan yang bersangkutan, bukan otomatis menambah transaksi baru.')+
        note('Contoh salah dan benar','Salah: Rp800 juta + 40 CMS = 800.000.040 pencapaian. Benar: pencapaian dana 20% dan pencapaian CMS 40% ditampilkan pada indikator masing-masing.')+
        p('Buku ini membahas cara aplikasi mencatat layanan, bukan prosedur resmi pembukaan atau aktivasi layanan bank. Definisi operasional unit perlu mengikuti kebijakan instansi.')))

    out.append(page('04 · ALUR PELUANG','Dua jenis status yang harus dibedakan','Cold/Warm/Hot menunjukkan ketertarikan; Active/Won/Lost menunjukkan hasil peluang.',
        table(['Dimensi','Nilai','Makna dalam aplikasi'],[
            ('Ketertarikan','Cold','Kategori ketertarikan yang dipilih pengguna.'),('Ketertarikan','Warm','Kategori ketertarikan yang dipilih pengguna.'),
            ('Ketertarikan','Hot','Kategori ketertarikan yang dipilih pengguna; dihitung tersendiri di Dashboard.'),
            ('Hasil','Active','Peluang masih dapat dikelola dan ditindaklanjuti.'),('Hasil','Won','Closing berhasil dengan realisasi dana yang valid.'),
            ('Hasil','Lost','Closing tidak berhasil, dengan alasan dan realisasi nol.')])+
        p('Peluang baru selalu dibuat <strong>Active</strong>. Sistem tidak mengubah Hot otomatis menjadi Won. Seorang pengguna masih harus mengirim hasil closing, tanggal, dan realisasi atau alasan Lost. Tidak ada perhitungan probabilitas keberhasilan otomatis untuk kategori minat tersebut.')+
        h('Alur bisnis yang ditunjukkan kode')+
        p('Catat peluang → perbarui informasi atau penanggung jawab → jadwalkan/selesaikan tindak lanjut → tentukan closing Won atau Lost. Peluang yang sudah closing tetap ada pada record yang sama dan ditampilkan pada Riwayat. Peluang itu tidak dipindahkan ke tabel hasil terpisah.')+
        h('Tindak lanjut selesai bukan closing')+
        p('Tombol penyelesaian tindak lanjut memperbarui <code>follow_up_completed</code>. Outcome tetap Active. Jika jadwal tindak lanjut diubah melalui pembaruan peluang, penanda penyelesaiannya dapat direset agar jadwal baru kembali membutuhkan perhatian.')+
        note('Kasus untuk latihan','Peluang Hot sudah ditelepon dan tindak lanjut ditandai selesai, tetapi nasabah belum memberikan keputusan. Hasil yang benar masih Active dengan interest Hot, bukan Won.')+
        p('Istilah “final” pada closing merupakan perilaku versi aplikasi ini. Jika instansi membutuhkan pembatalan closing, desain approval, koreksi realisasi, dan audit perubahan hasil perlu dibuat terlebih dahulu.')))

    out.append(page('04 · ALUR PELUANG','Pencatatan dan perubahan peluang','Formulir menghubungkan kebutuhan bisnis dengan kolom database yang konkret.',
        table(['Isian','Arti dan aturan utama'],[
            ('Nasabah / perusahaan','Teks nama; belum merujuk master nasabah.'),('PIC dan produk','PIC aktif serta produk dana yang tersedia pada divisi peluang.'),
            ('Segmentasi','Mid atau Large untuk data baru. Small lama dipertahankan agar record lama tetap dapat diperbarui.'),
            ('Tanggal pencatatan','Tanggal valid dan tidak melebihi hari ini.'),('Nominal','Rupiah bulat lebih dari nol.'),
            ('Cold/Warm/Hot','Kategori minat yang dipilih pengguna.'),('Jadwal tindak lanjut','Opsional; tidak sebelum tanggal pencatatan.'),
            ('Catatan','Keterangan perkembangan peluang.'),('Version','Versi record untuk mencegah pembaruan dari isian yang sudah tertinggal.')])+
        h('Apa yang terjadi saat data baru disimpan?')+
        p('Frontend memvalidasi isian dan mengirim JSON. Backend menentukan divisi yang diizinkan, memeriksa PIC/produk, membuat opportunity Active, membuat penugasan PIC awal, dan mencatat audit pembuatan. Penulisan terkait berada dalam transaksi sehingga tidak meninggalkan peluang tanpa catatan penugasan/audit ketika bagian operasi gagal.')+
        h('Apa yang terjadi jika PIC berubah?')+
        p('Kolom <code>opportunities.pic_id</code> berubah menjadi penanggung jawab saat ini. Penugasan lama yang masih terbuka ditutup melalui <code>unassigned_at</code>, lalu penugasan baru dibuat. Dengan demikian, “PIC saat ini” dan “pernah ditangani oleh PIC” bisa menjawab dua pertanyaan yang berbeda.')+
        note('Perbedaan batas isian yang ditemukan','UI membatasi nama 120 karakter, catatan 2.000, dan alasan Lost 1.000. API menerima batas lebih longgar: 160, 5.000, dan 2.000. Keduanya masih memvalidasi, tetapi penyelarasan batas merupakan pekerjaan perapian yang dicatat dalam audit.')+
        p('<strong>Acuan:</strong> <code>pipelineFieldErrors</code> dan <code>OpportunityController::store/update/validated</code>.')))

    out.append(page('04 · ALUR PELUANG','Closing Won/Lost secara rinci','Closing adalah satu operasi bisnis yang menyimpan keputusan, nilai, catatan, dan audit.',
        h('Ketentuan Won')+
        ul('Outcome sebelumnya harus Active dan pengguna berhak mengakses peluang.', 'Versi isian harus sama dengan versi record yang terkunci di database.',
           'Realisasi berupa bilangan bulat, lebih dari nol, dan tidak melebihi nominal peluang.', 'Tanggal closing tidak sebelum tanggal pencatatan dan tidak melebihi hari ini.',
           'Alasan Lost dikosongkan; catatan dapat dikirim bersama hasil closing.')+
        h('Ketentuan Lost')+
        p('Tanggal dan versi tetap diperiksa. Pengguna wajib memberikan alasan Lost. Backend memaksa realisasi menjadi nol agar nilai yang tidak semestinya dikirim klien tidak masuk ke hasil Lost. Catatan opsional tetap dapat disimpan sebagai konteks.')+
        h('Mengapa mengambil row lock?')+
        p('Peluang dibaca dengan <code>lockForUpdate()</code> di dalam transaksi. Permintaan lain yang ingin mengubah baris tersebut harus menunggu akses yang sesuai. Setelah giliran didapat, outcome dan versi diperiksa. Dua permintaan tidak boleh sama-sama menutup peluang berdasarkan kondisi awal yang sudah tidak berlaku.')+
        note('Contoh bisnis','Nominal peluang Rp1 miliar, realisasi Won Rp600 juta: diperbolehkan. Nominal tetap Rp1 miliar sebagai potensi awal; realisasi Rp600 juta sebagai hasil. Selisih Rp400 juta tidak otomatis dibuat menjadi peluang baru karena closing bersifat final.')+
        p('Setelah pembaruan, audit menyimpan snapshot sebelum/sesudah dan pelakunya. Jika penulisan audit gagal, transaksi membatalkan perubahan peluang. Respons sukses baru berarti transaksi berhasil. Relasi PIC, produk, dan divisi dimuat untuk hasil tampilan.')+
        p('<strong>Latihan:</strong> alasan penolakan HTTP 409 berbeda dari 422. 409 menunjukkan kondisi/versi konflik; 422 menunjukkan isian tidak memenuhi ketentuan.')))

    out.append(page('05 · FITUR DAN NAVIGASI','Lima halaman utama aplikasi','Jelaskan halaman berdasarkan keputusan yang dibantu, kemudian hubungkan dengan sumber datanya.',
        table(['Halaman / route','Pertanyaan pengguna','Data utama'],[
            ('Dashboard · /','Apa yang harus dipantau dan ditindaklanjuti?','Ringkasan peluang, target/realisasi, minat, tindak lanjut, tren.'),
            ('Pipeline · /pipeline','Peluang aktif apa yang harus dikelola?','Opportunity aktif, pencarian/filter, formulir dan detail.'),
            ('Target · /target','Berapa target dan pencapaian produk?','Annual target, rincian layanan bulanan, hasil Won.'),
            ('Riwayat · /history','Peluang mana yang sudah Won/Lost?','Opportunity yang sudah closing dan timeline detail.'),
            ('Tim · /tim','Siapa menangani peluang dan bagaimana rekapnya?','PIC, peluang aktif/final, dan riwayat penugasan.')])+
        h('Halaman tidak sama dengan tabel')+
        p('Dashboard, Tim, dan Riwayat merupakan penyajian/query dari data operasional. Tidak ada tabel dashboard, history, atau team yang menduplikasi semua peluang. Perubahan pada opportunity yang sama menjadi dasar tampilan aktif maupun hasil closing. Ini mengurangi risiko dua tabel terpisah tidak sinkron.')+
        h('Detail sebagai pusat tindakan')+
        p('Panel detail dipakai untuk melihat informasi peluang, melakukan tindak lanjut, mengubah peluang aktif, memeriksa timeline, dan melakukan closing. Pilihan tindakan mengikuti kondisi record dan hak akses. Formulir yang berubah dilindungi ketika pengguna berpindah atau menutup halaman.')+
        h('Apa yang tersimpan di URL?')+
        p('Pencarian, filter, pengurutan, dan halaman daftar dapat disimpan pada query di dalam hash route. Refresh atau tombol kembali dapat mengembalikan konteks daftar. Penyimpanan ini membantu navigasi; tidak menggantikan penyimpanan data bisnis di PostgreSQL.')+
        note('Urutan demo yang mudah diikuti','Dashboard → Pipeline → detail/tindak lanjut → closing → Riwayat → Target → Tim. Gunakan satu contoh peluang yang sama agar penguji melihat hubungan antarfungsi.')))

    out.append(page('05 · FITUR DAN NAVIGASI','Membaca Dashboard tanpa salah tafsir','Angka yang tampil harus dibaca bersama satuan, lingkup, periode, dan definisinya.',
        table(['Indikator','Definisi implementasi'],[
            ('Jumlah / nominal aktif','Opportunity Active pada lingkup terpilih, mencakup seluruh tahun pencatatan.'),
            ('Hot aktif','Peluang Active dengan interest_status Hot; bukan seluruh record yang pernah Hot.'),
            ('Tindak lanjut jatuh tempo','Active, mempunyai jadwal ≤ hari ini, dan belum selesai. Ringkasan backend menampilkan maksimal lima item.'),
            ('Realisasi dana','Jumlah realization dari Won pada tahun closed_date terpilih.'),
            ('Target tahunan','Target produk dana menurut scope divisi dan tahun.'),
            ('Persentase','Realisasi / target × 100; null bila target nol.'),
            ('Sisa target','Maksimum antara nol dan target dikurangi realisasi.')])+
        h('Mengapa tahun tidak menyaring seluruh kartu?')+
        p('Tahun dipakai untuk target/realisasi dan tren, sedangkan pekerjaan aktif tetap perlu ditangani walaupun dicatat tahun lalu. Jika semua peluang aktif disaring berdasarkan tahun pencatatan, pekerjaan lama yang belum selesai dapat tersembunyi. Karena itu antarmuka menjelaskan “semua periode” pada indikator aktif.')+
        h('Tiga bentuk grafik')+
        p('Doughnut memperlihatkan komposisi jumlah peluang Active menurut Cold/Warm/Hot. Grafik perbandingan batang memperlihatkan target dan realisasi produk dana. Grafik garis memperlihatkan nominal peluang menurut bulan pencatatan serta realisasi Won menurut bulan closing. Grafik garis tersebut bukan rekaman saldo pipeline pada akhir setiap bulan.')+
        note('Ketika data tidak tersedia','Target nol berarti belum ditetapkan; bukan kinerja nol persen yang dapat dibagi begitu saja. Bulan yang belum berlangsung diberi null pada tren backend agar tidak ditafsirkan sebagai realisasi nol yang sudah final.')+
        p('<strong>Acuan:</strong> <code>DashboardReport::build</code> dan <code>DashboardView.vue</code>.')))

    out.append(page('06 · PERHITUNGAN','Contoh data untuk latihan','Seluruh nama/angka pada contoh ini fiktif dan dipakai untuk memahami rumus.',
        table(['Peluang','Produk','Dicatat','Hasil / closing','Nominal','Realisasi'],[
            ('A','Tabungan','Nov 2025','Active · Hot','Rp1 miliar','Rp0'),
            ('B','Tabungan','Des 2025','Won · Jan 2026','Rp800 juta','Rp600 juta'),
            ('C','Giro','Jan 2026','Lost · Jan 2026','Rp500 juta','Rp0'),
            ('D','Deposito','Feb 2026','Won · Feb 2026','Rp200 juta','Rp200 juta'),
            ('E','Tabungan','Mar 2026','Active · Cold','Rp300 juta','Rp0')])+
        p('Asumsikan kelima peluang berada pada divisi Komersil. Target 2026: Tabungan Rp2 miliar, Giro Rp1 miliar, Deposito Rp1 miliar. Data dinilai pada 2026 setelah bulan Maret. Contoh ini sengaja mempunyai peluang tahun lalu agar perbedaan tahun pencatatan dan tahun closing terlihat.')+
        h('Ringkasan aktif')+
        p('Peluang Active adalah A dan E: jumlah <strong>2</strong>, nominal potensi <strong>Rp1,3 miliar</strong>. Peluang A tetap masuk walaupun dicatat 2025. Hot aktif hanya A: jumlah <strong>1</strong>, nominal <strong>Rp1 miliar</strong>. Komposisi minat aktif menjadi Cold 50%, Warm 0%, Hot 50%.')+
        h('Ringkasan closing 2026')+
        p('Peluang Won adalah B dan D: jumlah <strong>2</strong>, realisasi <strong>Rp800 juta</strong>. Peluang Lost adalah C: jumlah <strong>1</strong> dan tidak menambah realisasi. B masuk realisasi 2026 karena ditutup pada Januari 2026, walaupun dicatat Desember 2025.')+
        note('Pertanyaan untuk diri sendiri','Jika tahun laporan diubah menjadi 2025, apakah A hilang dari kartu aktif? Tidak. Apakah B menambah realisasi 2025? Tidak, karena tahun closing B adalah 2026.')+
        p('Dalam aplikasi, rupiah disimpan sebagai bilangan bulat. Tulisan “Rp1,3 M” hanya pemformatan penyajian dengan M bermakna miliar pada antarmuka ini.')))

    out.append(page('06 · PERHITUNGAN','Mencapai dan melampaui target','Persentase, sisa target, dan progress bar tidak selalu menunjukkan nilai yang identik.',
        table(['Produk','Target 2026','Realisasi Won','Pencapaian','Sisa'],[
            ('Tabungan','Rp2 miliar','Rp600 juta','30%','Rp1,4 miliar'),('Giro','Rp1 miliar','Rp0','0%','Rp1 miliar'),
            ('Deposito','Rp1 miliar','Rp200 juta','20%','Rp800 juta'),('Total dana','Rp4 miliar','Rp800 juta','20%','Rp3,2 miliar')])+
        code('persentase = realisasi / target × 100, jika target > 0\nsisa       = max(0, target - realisasi)\naktif      = jumlah nominal peluang dengan outcome Active')+
        p('Persentase total dihitung dari total realisasi dibagi total target, bukan rata-rata sederhana dari persentase tiga produk. Pada contoh ini (30% + 0% + 20%) / 3 = 16,67% akan salah karena besar target produknya berbeda.')+
        h('Target nol')+
        p('Jika suatu produk belum mempunyai target atau targetnya nol, persentase dikembalikan sebagai null. Antarmuka dapat menampilkan “Belum ada target”. Tidak ada pembagian nol. Realisasi tetap boleh ditampilkan sebagai informasi, tetapi belum menjadi persentase pencapaian yang bermakna.')+
        h('Target terlampaui')+
        p('Target Rp1 miliar dan realisasi Rp1,2 miliar menghasilkan 120%. Sisa target tetap nol. Progress bar visual dapat dibatasi pada panjang penuh, sementara angka 120% tetap menunjukkan kelebihan pencapaian. Panjang bar adalah bentuk penyajian; rumus angka utama tidak perlu dipaksa menjadi maksimum 100%.')+
        note('Kesalahan yang sering terjadi','Nominal peluang Won bukan otomatis realisasi. B mempunyai nominal Rp800 juta tetapi realisasi Rp600 juta, sehingga perhitungan harus memakai kolom realization.')+
        p('Rumus dana memakai satuan IDR. Nilai layanan tidak masuk penyebut maupun pembilang target dana.')))

    out.append(page('06 · PERHITUNGAN','Tahun, tren, dan realisasi layanan','Satu sistem dapat memakai tanggal yang berbeda untuk pertanyaan bisnis yang berbeda.',
        table(['Pertanyaan','Dasar waktu'],[
            ('Kapan peluang masuk pencatatan?','recorded_date'),('Kapan peluang menghasilkan realisasi?','closed_date dan outcome Won'),
            ('Kapan tindakan perlu dilakukan?','follow_up_date dan penanda selesai'),('Kapan record diubah?','updated_at'),
            ('Kapan kejadian audit tercatat?','occurred_at')])+
        p('Pada contoh A–E, tren nominal pencatatan 2026 mencatat C Rp500 juta pada Januari, D Rp200 juta pada Februari, dan E Rp300 juta pada Maret. Total nominal tercatat 2026 adalah Rp1 miliar. Realisasi Januari Rp600 juta berasal dari B; Februari Rp200 juta dari D. Nilai ini menjawab pertanyaan berbeda sehingga kedua garis tidak harus sama.')+
        h('Layanan CMS sebagai contoh')+
        p('Anggap target CMS tahunan 100 unit, total aktual Januari 25 unit dan Februari 15 unit. Realisasi tahunan 40 unit, pencapaian 40%, sisa 60 unit. Jika Februari dikoreksi menjadi 18 unit, total tahunan menjadi 43, bukan 58; record Februari diganti dari 15 menjadi 18.')+
        h('Tahunan dan bulanan tidak dipaksa sama')+
        p('Target tahunan dan target bulanan dicatat terpisah. Aturan saat ini belum mewajibkan jumlah target 12 bulan sama dengan target tahunan. Hal ini perlu dijelaskan apa adanya. Bila instansi membutuhkan rekonsiliasi otomatis, aturan validasi tersebut harus ditambahkan setelah kebutuhannya ditetapkan.')+
        note('Bedakan nol dan belum ada data','Angka nol berarti nilai total yang diketahui nol. Null pada grafik bulan mendatang berarti nilai belum disajikan. Pada API target, nilai version 0 juga dipakai untuk menyatakan record baru belum ada; artinya berbeda dari nilai target 0.')+
        p('Realisasi layanan adalah input manual; aplikasi ini tidak menarik bukti aktivasi QRIS, Bale Syariah, atau CMS dari sistem operasional bank.')))

    out.append(page('07 · RIWAYAT DAN TIM','Riwayat hasil, audit, dan penugasan','Tiga jenis riwayat menjawab tiga pertanyaan yang berbeda.',
        table(['Jenis informasi','Pertanyaan','Sumber'],[
            ('Riwayat closing','Peluang apa yang sudah selesai dan hasilnya apa?','opportunities dengan outcome Won/Lost.'),
            ('Timeline perkembangan','Siapa mengubah apa, kapan, dan nilai apa yang berubah?','audit_events untuk resource peluang.'),
            ('Riwayat penugasan','PIC mana yang pernah menangani peluang ini?','opportunity_assignments dan PIC saat ini/final.')])+
        p('Satu peluang bisa berganti PIC beberapa kali. Daftar pernah ditangani dapat tetap menyebut PIC lama, tetapi rekap hasil Won/Lost memakai PIC pada opportunity saat ini/final. Dengan demikian, “pernah menangani” bukan berarti setiap PIC tersebut memperoleh penghitungan penuh realisasi yang sama.')+
        h('Rekap Tim pada antarmuka')+
        p('<code>TeamView.vue</code> menyusun rekap dari data scoped yang dimuat oleh <code>usePipeline</code>: aktif seluruh periode, sedangkan Won/Lost dan realisasi mengikuti tahun closing. API juga memiliki endpoint rekap Tim dan peluang pernah ditangani PIC. Keberadaan endpoint tidak berarti setiap angka pada layar langsung berasal dari endpoint tersebut; jalur data UI harus ditelusuri.')+
        h('Audit bukan salinan lengkap database')+
        p('Audit menyimpan pelaku, jenis resource, ID resource, aksi, waktu, serta snapshot sebelum/sesudah perubahan yang dicatat aplikasi. Token dan password tidak menjadi isi audit bisnis. Hubungan <code>resource_type/resource_id</code> adalah referensi logis sehingga dapat menunjuk beberapa tipe resource; bukan satu foreign key lintas tabel.')+
        note('Batas kekuatan bukti','Aplikasi menambahkan audit dalam alur tulis normal, tetapi skema tidak menunjukkan mekanisme kriptografis atau proteksi database yang menjadikannya kebal perubahan oleh pihak dengan hak database. Hindari klaim “audit tidak mungkin dimanipulasi”.')+
        p('<strong>Latihan:</strong> jelaskan mengapa mengganti PIC saja tidak cukup dilakukan dengan menimpa nama PIC pada satu kolom teks.')))

    out.append(page('08 · ARSITEKTUR','Tiga lapisan dan satu backend Laravel','Pembagian tanggung jawab membantu memahami keseluruhan sistem.',
        table(['Lapisan','Komponen proyek','Tanggung jawab'],[
            ('Presentasi','Vue, Vue Router, komponen, CSS, Chart.js','Interaksi, formulir, navigasi, tampilan responsif, grafik.'),
            ('Aplikasi','Laravel routes, middleware, controller, DashboardReport','Autentikasi, akses, validasi final, transaksi, perhitungan utama, respons JSON.'),
            ('Penyimpanan','PostgreSQL dan model Eloquent','Record, hubungan, constraint, pencarian, dan penyimpanan yang dipakai aplikasi.')])+
        p('Backend merupakan satu aplikasi Laravel. Pembagian tiga lapis tidak berarti tiga microservice. Browser tidak terhubung langsung ke PostgreSQL dan tidak menyimpan kata sandi database. Jalur data operasional melalui API sehingga aturan akses dapat diterapkan secara konsisten.')+
        h('Satu permintaan ringkasan')+
        code('Vue → GET /api/dashboard?year=2026\n    → Sanctum mengenali pengguna\n    → controller menentukan divisi\n    → DashboardReport membaca dan menghitung\n    → JSON dikembalikan\n    → komponen Vue / Chart.js menampilkan hasil')+
        h('Mengapa logika tidak seluruhnya di browser?')+
        p('Jika akses hanya difilter di browser, pengguna dapat mengubah kode/parameter dan meminta data lain. Jika perhitungan utama hanya ada di masing-masing layar, definisi dapat berbeda. Backend menjadi tempat pemeriksaan final dan agregasi dana utama, sementara frontend tetap mengolah data yang telah dibatasi akses untuk format, filter tampilan, layanan, dan beberapa rekap Tim.')+
        note('Kalimat penjelasan','“Vue menangani interaksi, Laravel menangani aturan dan API, PostgreSQL menyimpan data relasional. Chart.js menggambar hasil, bukan sumber utama angka bisnis.”')+
        p('Gambar arsitektur yang lebih besar disertakan pada lampiran. Port lokal dan contoh konfigurasi adalah pengaturan pengembangan, bukan bukti aplikasi sudah dipublikasikan.')))

    out.append(page('08 · ARSITEKTUR','HTTP, JSON, dan kontrak API','Frontend dan backend berkomunikasi melalui permintaan dan respons yang terstruktur.',
        p('HTTP menyediakan metode, alamat endpoint, header, dan status respons. JSON menjadi format data. API memungkinkan antarmuka meminta data atau melakukan tindakan tanpa mengakses tabel database secara langsung. Istilah REST API pada proyek merujuk API berbasis resource dan HTTP; beberapa operasi khusus seperti closing memakai endpoint tindakan.')+
        code('POST /api/opportunities/123/closing\nAuthorization: Bearer <token pengguna>\nContent-Type: application/json\nIdempotency-Key: <UUID permintaan>\n\n{\n  "outcome": "Won",\n  "realization": 600000000,\n  "closed_date": "2026-10-20",\n  "version": 3,\n  "notes": "Contoh belajar, bukan data operasional"\n}')+
        table(['Status','Makna yang relevan pada aplikasi'],[
            ('200 / 201','Permintaan berhasil / resource baru dibuat.'),('204','Logout berhasil tanpa body.'),
            ('401','Tidak memiliki autentikasi yang sah.'),('403 / 404','Akses ditolak atau resource tidak tersedia pada lingkup pengguna.'),
            ('409','Konflik versi, sudah closing, atau key dipakai dengan payload berbeda.'),('422','Isian tidak memenuhi validasi.'),
            ('429','Terlalu banyak percobaan login.'),('5xx','Gangguan server; hasil tulis dapat belum pasti bagi klien.')])+
        note('Pahami batas timeout','Frontend memakai timeout 15 detik secara default. Koneksi yang terputus tidak membuktikan transaksi gagal. Karena itu retry memakai request key yang sama agar hasil sukses sebelumnya dapat diputar ulang.')+
        p('Contoh body di atas bersifat ilustrasi; ID, versi, dan tanggal harus mengikuti data yang memang tersedia ketika demo. Token asli tidak perlu ditunjukkan pada slide atau materi belajar.')))

    out.append(page('09 · MEMBACA DIAGRAM','DFD, ERD, dan arsitektur mempunyai fokus berbeda','Gunakan diagram yang sesuai untuk menjawab jenis pertanyaan penguji.',
        table(['Diagram','Yang dijelaskan','Contoh pertanyaan'],[
            ('DFD','Asal, transformasi, penyimpanan, dan tujuan data.','Data closing masuk ke proses mana, lalu disimpan di mana?'),
            ('ERD','Entitas/tabel, atribut, hubungan, dan kardinalitas.','Mengapa satu target dapat memiliki 12 record bulanan?'),
            ('Arsitektur','Komponen dan pembagian tanggung jawab teknis.','Di mana validasi final dan perhitungan laporan dijalankan?'),
            ('Sequence','Pertukaran pesan menurut interaksi/waktu.','Apa yang terjadi ketika request tulis diulang?')])+
        h('Hierarki DFD proyek')+
        ul('<strong>Konteks:</strong> satu proses 0, berinteraksi dengan E1 PIC dan E2 Head Funding.',
           '<strong>Level 1:</strong> 1.0 autentikasi, 2.0 referensi, 3.0 pipeline, 4.0 target/layanan, 5.0 laporan.',
           '<strong>Level 2:</strong> menguraikan 3.0 menjadi baca detail, catat, ubah, tindak lanjut, dan closing.',
           '<strong>Level 3:</strong> menguraikan 3.5 closing menjadi verifikasi, validasi hasil, simpan, audit, dan penyajian hasil.')+
        p('Penomoran tingkat dapat berbeda pada pedoman kampus; dokumen ini menyatakannya secara eksplisit. Level 3 tersedia untuk proses closing, bukan klaim bahwa semua proses Level 1 sudah didekomposisi sampai kedalaman yang sama.')+
        h('Keseimbangan antarlevel')+
        p('Ketika proses diuraikan, masukan/keluaran gabungan anak harus tetap menjelaskan batas proses induk. Aliran internal dapat bertambah, tetapi entitas atau penyimpanan eksternal tidak boleh muncul tanpa konsistensi dengan induknya. Karena hasil closing memuat PIC, produk, dan divisi, pembacaan referensi tersebut ditunjukkan pada diagram yang ditinjau.')+
        note('Cara menerangkan panah','Sebutkan paket datanya, misalnya “snapshot sebelum/sesudah dan identitas pelaku”. Jangan membaca panah DFD sekadar sebagai perintah “lanjut ke langkah berikutnya”.')))
    return out
