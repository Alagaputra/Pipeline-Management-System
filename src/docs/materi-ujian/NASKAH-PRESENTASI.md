





# Naskah presentasi — Sistem Manajemen Pipeline Funding BSN KC Bekasi

Pembaruan 23 Oktober 2026. Durasi panduan: sekitar 10–12 menit, bergantung pada tempo dan waktu demonstrasi. Setiap bagian memuat **isi slide singkat** dan **kalimat yang diucapkan** agar mudah dipelajari. Angka pengujian mengacu pada catatan pemeriksaan 20 Oktober 2026; pengujian tidak dijalankan ulang dalam pembaruan materi ini.

Pegangan utama: **catat peluang → tindak lanjuti → catat hasil → bandingkan dengan target**. Untuk pertanyaan teknologi, pelajari [Perbandingan tech stack dan jawaban lisan](PERBANDINGAN-TECH-STACK.md).

Bagian dalam tanda siku adalah petunjuk tindakan, bukan kalimat yang dibacakan. Contoh nasabah dan angka di bawah bersifat fiktif. Gunakan data demonstrasi yang diizinkan dan cocokkan narasi dengan angka yang benar-benar tampil. Jika waktu terbatas, jelaskan salah satu dari Won/Lost dan ringkas pembahasan database.

## 1. Pembukaan dan arah presentasi

**Isi slide:** aplikasi untuk mengetahui peluang pendanaan, penanggung jawab, tindak lanjut, dan hasilnya.

[Tampilkan judul. Tatap audiens sebelum berpindah ke layar.]

“Assalamu’alaikum warahmatullahi wabarakatuh. Selamat pagi/siang, Bapak dan Ibu penguji.

Pada kesempatan ini, saya akan mempresentasikan Sistem Manajemen Pipeline Funding untuk BSN KC Bekasi.

Pertanyaan utama yang ingin dijawab aplikasi ini adalah: peluang pendanaan apa yang sedang ditangani, siapa penanggung jawabnya, mana yang perlu segera ditindaklanjuti, dan berapa hasil yang sudah tercapai dibandingkan target?

Saya akan menjelaskan kebutuhannya, memperagakan satu contoh penggunaan, lalu menjelaskan teknologi yang dipakai dan cara menjaga datanya.”

## 2. Masalah bisnis dan tujuan

**Isi slide:** informasi peluang dicatat bersama → perkembangan dapat ditelusuri → hasil dapat dibandingkan dengan target.

“Pipeline berarti daftar peluang penghimpunan dana yang sedang ditangani. Misalnya ada calon nasabah yang tertarik menempatkan deposito. Kita perlu tahu perkiraan dananya, siapa yang menangani, dan kapan perlu dihubungi kembali.

Kalau pencatatannya tidak seragam, pemantauan menjadi sulit. Aplikasi ini menyatukan pencatatan peluang, tindak lanjut, hasil akhir, dan target dalam satu alur.

Manfaat yang dituju adalah pencatatan lebih teratur dan pemantauan lebih mudah. Besarnya penghematan waktu masih perlu diukur langsung bersama pengguna.”

## 3. Pengguna dan batas akses

**Isi slide:** PIC mengakses divisinya; Head Funding memantau Komersil dan Konsumer. PIC berarti penanggung jawab peluang.

[Tunjukkan akun atau pilihan divisi yang tersedia.]

“Pengguna utama sistem adalah PIC dan Head Funding. PIC mengakses peluang dalam divisinya, termasuk peluang PIC lain di divisi yang sama. Head Funding dapat memantau divisi Komersil dan Konsumer, baik secara terpisah maupun gabungan.

Pembatasan tersebut diperiksa di server. Jadi, mengganti pilihan divisi dari browser tidak otomatis memberikan akses ke divisi lain.

Produk juga mengikuti divisinya. Sebagai contoh, Giro tersedia untuk Komersil, sedangkan pada Konsumer produk dan layanan yang tersedia mengikuti konfigurasi divisi tersebut.”

## 4. Dashboard: dari informasi menuju tindakan

**Isi slide:** pekerjaan yang perlu ditindaklanjuti + pencapaian terhadap target. **Hot masih potensi; Won sudah mempunyai realisasi.**

[Buka Dashboard. Tunjuk antrean follow-up, peluang aktif, dan kartu target.]

“Dashboard menyajikan dua kebutuhan: pekerjaan yang perlu ditindaklanjuti dan pencapaian yang perlu dipantau.

Pengguna dapat melihat peluang aktif, nominal potensinya, distribusi Cold, Warm, dan Hot, serta tindak lanjut yang sudah jatuh tempo. Pada bagian pencapaian, tersedia target dan realisasi per produk.

Ada dua kelompok status yang perlu dibedakan. Cold, Warm, dan Hot menunjukkan tingkat ketertarikan. Active, Won, dan Lost menunjukkan keadaan atau hasil akhir peluang. Jadi, peluang yang Hot masih merupakan potensi sampai dilakukan closing Won dengan nilai realisasi.

Filter tahun digunakan untuk target dan realisasi. Sementara itu, peluang aktif serta antrean tindak lanjut tetap mencakup seluruh periode, sehingga pekerjaan yang belum selesai tidak hilang hanya karena pergantian tahun.”

## 5. Demo satu peluang: pencatatan sampai closing

**Isi slide:** catat peluang → tindak lanjut → closing Won/Lost → Riwayat. Contoh fiktif: potensi Rp1 miliar, hasil Won Rp600 juta.

[Buka Pipeline. Siapkan peluang contoh di lingkungan demonstrasi.]

“Saya gunakan contoh fiktif agar alurnya mudah diikuti. Misalnya terdapat peluang Deposito dengan potensi Rp1 miliar.

Pengguna mencatat nasabah, produk, PIC, nominal, dan informasi pendukung, termasuk jadwal tindak lanjut bila diperlukan. Peluang baru dimulai sebagai Active, artinya masih ditangani.

Sistem memeriksa kelengkapan dan kesesuaian data. Misalnya, produk dan PIC harus sesuai dengan divisi. Pemeriksaan pada formulir membantu pengguna, sedangkan validasi final dilakukan di backend.

Selama peluang masih aktif, pengguna memperbarui perkembangan dan tindak lanjutnya. Riwayat perubahan menunjukkan siapa yang mengubah, kapan, dan apa yang berubah.

Ketika hasilnya sudah diperoleh, dilakukan closing. Jika Won, nilai realisasi harus lebih dari nol dan tidak boleh melebihi nominal potensi yang tercatat. Jika Lost, alasan harus diisi dan realisasinya menjadi nol.

Misalnya, dari potensi Rp1 miliar, hasil yang dicatat adalah Rp600 juta. Maka nilai yang masuk pencapaian adalah Rp600 juta. Selisihnya tidak otomatis menjadi peluang baru.

Peluang yang sudah closing ditampilkan pada Riwayat tanpa menghapus datanya. Pada implementasi saat ini, closing bersifat final sehingga pemeriksaan sebelum menyimpan menjadi penting.”

## 6. Target dan ketepatan perhitungan

**Isi slide:** contoh berikut memakai peluang yang sama dan menganggap belum ada realisasi Won lainnya.

| Angka contoh | Nilai |
| --- | --- |
| Potensi peluang | Rp1 miliar |
| Hasil closing Won | Rp600 juta |
| Target produk | Rp2 miliar |
| Pencapaian | Rp600 juta ÷ Rp2 miliar × 100% = **30%** |
| Sisa target | **Rp1,4 miliar** |

[Buka Target. Gunakan contoh secara lisan jika angka di layar berbeda.]

“Perhitungan pencapaian menggunakan nilai realisasi Won dibagi target, kemudian dikalikan seratus persen.

Melanjutkan contoh tadi, jika target produk Rp2 miliar dan belum ada realisasi lainnya, hasil Rp600 juta berarti pencapaian 30 persen. Sisa targetnya Rp1,4 miliar.

Periode realisasi mengikuti tanggal closing. Jadi, peluang yang dicatat pada Desember dan baru Won pada Januari masuk ke realisasi tahun Januari tersebut.

Target nol diperlakukan sebagai target yang belum ditetapkan sehingga persentasenya tidak dihitung dengan membagi nol. Jika realisasi melampaui target, persentasenya dapat melebihi seratus persen, sementara sisa target minimum nol.

Target dana dalam rupiah juga dipisahkan dari target layanan dalam unit, seperti Bale Syariah, QRIS, dan CMS. Keduanya tidak dijumlahkan karena satuan dan maknanya berbeda.

Definisi angka ini penting agar dashboard dapat dibaca dengan benar: nominal potensi, realisasi, target, dan unit layanan mempunyai arti yang berbeda.”

## 7. Arsitektur dan aliran data

**Isi slide:**

**Pengguna → Vue → Laravel API → PostgreSQL**. Respons data berjalan kembali ke Vue; Chart.js menggambar grafiknya.

| Teknologi | Tugas sederhana | Alasan untuk proyek ini |
| --- | --- | --- |
| Vue.js | Tampilan dan interaksi | Formulir, kartu, dan daftar dapat dibuat sebagai komponen yang digunakan ulang |
| Laravel | Pemeriksaan aturan dan API | Menyediakan struktur validasi, akses database, dan integrasi autentikasi |
| PostgreSQL | Penyimpanan data | Sesuai untuk hubungan peluang–PIC–produk dan penyimpanan dengan transaksi |
| Chart.js | Grafik | Menyediakan batang, garis, dan doughnut yang dibutuhkan dashboard |

[Tampilkan diagram arsitektur jika tersedia.]

“Pembagian teknologinya bisa diingat sebagai tampilan, pemeriksa aturan, penyimpanan, dan grafik.

Vue menangani tampilan. Laravel memeriksa login, hak akses, isian, dan aturan bisnis, serta menghitung laporan. PostgreSQL menyimpan data yang saling berhubungan. Chart.js menggambar grafik.

Ketika tombol Simpan ditekan, Vue mengirim data ke Laravel melalui API. API adalah jalur komunikasi antara tampilan dan server. Setelah data diperiksa, Laravel menyimpannya ke PostgreSQL lalu mengirim hasilnya kembali untuk memperbarui tampilan.

Stack ini mengikuti teknologi yang tercatat dalam dokumen kesesuaian proposal dan cocok dengan kebutuhan aplikasi. React, Express, dan MySQL juga dapat dipakai. Pertimbangannya adalah kecocokan kebutuhan dan konsistensi proyek; belum ada benchmark yang membuktikan stack ini paling cepat.

Konsekuensinya, proyek mengelola JavaScript dan PHP, serta perlu menjaga format data dan aturan frontend–backend tetap selaras. Pada database, peluang dihubungkan ke divisi, produk, dan PIC. Riwayat penugasan serta audit membantu menelusuri perkembangan data.”

Sumber kemampuan umum: [Vue](https://vuejs.org/guide/introduction.html), [Laravel](https://laravel.com/docs/12.x/validation), [PostgreSQL](https://www.postgresql.org/docs/18/tutorial-transactions.html), dan [Chart.js](https://www.chartjs.org/docs/latest/). Penilaian kecocokan adalah pertimbangan desain proyek. Untuk menjawab perbandingan lebih jauh, gunakan [panduan tech stack](PERBANDINGAN-TECH-STACK.md).

## 8. Menjaga konsistensi saat terjadi masalah

**Isi slide:**

| Masalah | Cara menangani | Nama teknis |
| --- | --- | --- |
| Sebagian proses gagal | Simpan satu rangkaian perubahan secara utuh atau batalkan bersama | Transaksi |
| Dua orang mengubah data yang sama | Periksa apakah versi data masih terbaru | Pemeriksaan versi |
| Data tersimpan tetapi respons terputus | Coba lagi dengan pengenal permintaan yang sama | Idempotensi |

[Perlambat tempo. Jelaskan setiap mekanisme dengan satu contoh.]

“Ada tiga mekanisme penting untuk menjaga penyimpanan data.

Pertama, transaksi database. Perubahan yang merupakan satu kesatuan disimpan bersama. Contohnya, hasil closing dan audit harus sama-sama berhasil. Jika terjadi kegagalan di tengah proses, perubahan dalam transaksi dibatalkan. Prinsip yang sama digunakan ketika satu formulir target menyimpan beberapa isian sekaligus.

Kedua, pemeriksaan versi record. Misalnya dua pengguna membuka peluang yang sama. Setelah pengguna pertama menyimpan perubahan, versi data bertambah. Jika pengguna kedua menyimpan dari versi lama, sistem menolak dan meminta pemuatan ulang. Dengan demikian, perubahan terbaru tidak langsung tertimpa.

Ketiga, perlindungan saat mencoba menyimpan ulang, disebut idempotensi. Ada kemungkinan data sudah tersimpan tetapi respons terputus. Tombol Coba lagi memakai pengenal permintaan yang sama, sehingga server dapat mengembalikan hasil sebelumnya tanpa membuat data atau audit kedua.

Ketiga mekanisme tersebut menangani masalah berbeda: penyimpanan sebagian, perubahan yang saling menimpa, dan permintaan ulang yang berpotensi menggandakan data.”

## 9. Pengujian dan pengembangan

**Isi slide:** logika, API, dan alur browser diuji. Catatan 20 Oktober 2026: 9 tes frontend, 17 tes backend, 29 tes browser lulus. Lanjutan: validasi pengguna, penguatan sesi, uji beban, dan uji pemulihan backup.

“Pengujian mencakup logika frontend, aturan backend, dan alur penggunaan melalui browser. Skenarionya antara lain pembatasan divisi, validasi closing, perhitungan berdasarkan tahun closing, konflik perubahan, serta percobaan ulang penyimpanan.

Berdasarkan catatan pemeriksaan 20 Oktober 2026, terdapat 9 tes frontend, 17 tes backend dengan 129 assertion, dan 29 tes browser yang lulus. Tes backend tersebut menggunakan SQLite in-memory, sedangkan tes browser menggunakan PostgreSQL pada database pengujian terpisah. Build frontend juga tercatat berhasil.

Hasil itu memberikan bukti untuk skenario yang diuji. Sebelum penggunaan operasional, langkah berikutnya adalah validasi bersama pengguna, penguatan pengelolaan sesi, pengujian beban, serta pembuktian backup dan pemulihan data.”

## 10. Penutup

**Isi slide:** peluang → penanggung jawab → tindak lanjut → hasil → pencapaian target.

[Kembali menatap audiens.]

“Melalui proyek ini, pencatatan peluang dihubungkan dengan penanggung jawab, tindak lanjut, hasil closing, dan pencapaian target.

Hal yang ingin saya tekankan adalah kesesuaian alur bisnis dan ketepatan makna datanya. Potensi dibedakan dari realisasi, hak akses diperiksa di server, dan proses penyimpanan dilindungi agar tetap konsisten ketika terjadi konflik atau gangguan koneksi.

Demikian presentasi saya. Terima kasih atas perhatian Bapak dan Ibu. Saya siap menerima pertanyaan dan masukan.

Wassalamu’alaikum warahmatullahi wabarakatuh.”

---

## Bekal menjawab pertanyaan penguji

Gunakan pola: jawab inti pertanyaan, beri contoh, kemudian jelaskan batasnya jika diperlukan. Tidak semua detail perlu dimasukkan ke presentasi utama.

### 1. Apa kelebihan sistem ini dibandingkan Excel?

“Kebutuhan yang dijawab adalah aturan bersama dan keterlacakan: produk serta PIC diperiksa sesuai divisi, closing divalidasi, realisasi memakai definisi yang konsisten, dan perubahan mempunyai timeline. Sistem juga menangani konflik edit dan retry. Jadi, alasan memakai aplikasi adalah kebutuhan proses tersebut.”

### 2. Mengapa menggunakan Vue, Laravel, dan PostgreSQL?

“Vue untuk tampilan, Laravel untuk aturan dan API, serta PostgreSQL untuk data yang saling berhubungan. Chart.js dipakai untuk grafik. Stack ini selaras dengan teknologi yang tercatat dalam dokumen kesesuaian proposal dan kebutuhan proyek. Alternatif juga layak; belum ada benchmark yang membuktikan stack ini paling cepat.”

Jika diminta membandingkan, jawab satu pilihan dahulu:

| Pertanyaan | Jawaban singkat |
| --- | --- |
| Mengapa Vue, bukan React? | “Keduanya berbasis komponen. Struktur `.vue` cocok untuk menyusun formulir dan tampilan berulang di proyek ini. React tetap layak, terutama jika tim sudah menggunakannya.” |
| Mengapa Laravel, bukan Node.js? | “Perbandingan setaranya Laravel dengan framework seperti Express yang berjalan di Node.js. Laravel menyediakan fasilitas backend yang dipakai proyek; Express lebih minimal dan memberi keleluasaan memilih paket. Konsekuensinya proyek ini mengelola PHP dan JavaScript.” |
| Mengapa PostgreSQL, bukan MySQL? | “Keduanya layak. PostgreSQL sesuai rancangan dan model data proyek. MySQL dengan InnoDB juga memiliki transaksi dan foreign key, jadi itu bukan keunggulan eksklusif PostgreSQL.” |
| Mengapa Chart.js, bukan D3? | “Dashboard membutuhkan grafik batang, garis, dan doughnut yang sudah tersedia di Chart.js. D3 memberi kontrol untuk visual yang lebih khusus, dengan lebih banyak detail yang perlu dirancang.” |
| Apa kekurangannya? | “Aturan dan format API di dua lapisan harus selaras, proyek mengelola dua bahasa, dan database memerlukan backup serta pemeliharaan. Untuk grafik yang sangat khusus, Chart.js dapat memerlukan kode tambahan.” |

Dasar perbandingan, konsekuensi, serta contoh kode: [PERBANDINGAN-TECH-STACK.md](PERBANDINGAN-TECH-STACK.md).

### 3. Apa perbedaan autentikasi dan otorisasi?

“Autentikasi memastikan siapa penggunanya, sedangkan otorisasi memeriksa data atau tindakan apa yang boleh diakses. Di sini, Sanctum memeriksa token, kemudian backend membatasi akses sesuai peran dan divisi.”

### 4. Apakah PIC hanya dapat melihat data miliknya sendiri?

“Batas akses PIC pada implementasi ini adalah divisi. PIC dapat melihat peluang PIC lain dalam divisi yang sama. Head Funding dapat memantau kedua divisi.”

### 5. Apakah Hot sudah dihitung sebagai realisasi?

“Belum. Hot adalah tingkat ketertarikan. Realisasi dana berasal dari nilai realisasi peluang yang sudah closing Won, dengan periode sesuai tanggal closing.”

### 6. Apakah transaksi database sudah cukup menangani dua pengguna?

“Transaksi menjaga satu rangkaian perubahan tersimpan utuh. Untuk mencegah pengguna menimpa data dari versi lama, sistem juga memeriksa version. Di dalam proses perubahan digunakan row lock dan pemeriksaan ulang. Fungsinya saling melengkapi.”

### 7. Apa yang terjadi jika tombol simpan dicoba lagi setelah koneksi terputus?

“Permintaan simpan data bisnis dari UI membawa Idempotency-Key. Jika percobaan ulang memakai key dan isi permintaan yang sama setelah penyimpanan berhasil, backend mengembalikan hasil sebelumnya. Isi berbeda dengan key yang sama ditolak. Mekanisme ini memerlukan key yang dipertahankan saat retry; bukan penggabungan otomatis semua data yang mirip.”

### 8. Mengapa closing tidak dapat diubah?

“Implementasi saat ini menetapkan closing sebagai hasil final. Ini menjaga hasil yang sudah masuk laporan tidak berubah lewat edit biasa. Jika dibutuhkan koreksi operasional, pengembangannya perlu menyediakan prosedur koreksi dengan kewenangan dan audit yang jelas.”

### 9. Bagaimana membaca grafik garis?

“Grafik membandingkan nominal peluang menurut bulan pencatatan dengan realisasi Won menurut bulan closing pada tahun terpilih. Grafik tersebut bukan rekonstruksi saldo peluang aktif pada setiap bulan.”

### 10. Bagaimana struktur databasenya?

“Relasi utamanya menghubungkan opportunities dengan users sebagai PIC, products, dan divisions. opportunity_assignments menyimpan riwayat penugasan, sedangkan audit_events menyimpan jejak perubahan. Target dana tahunan dan realisasi unit layanan mempunyai penyimpanan sesuai kebutuhannya. Dokumentasi pemeriksaan mencatat 22 tabel secara keseluruhan, termasuk tabel infrastruktur Laravel; bukan 22 tabel bisnis.”

### 11. Apakah sistem sudah terhubung dengan transaksi bank?

“Cakupannya adalah pencatatan dan pemantauan pipeline funding. Realisasi dicatat melalui proses closing pengguna. Integrasi dengan sistem inti bank belum menjadi fitur implementasi ini.”

### 12. Apakah aman dan siap produksi?

“Kontrol yang sudah ada antara lain autentikasi, pembatasan akses backend, validasi, audit, transaksi, serta perlindungan konflik dan retry. Kesiapan produksi tetap membutuhkan verifikasi operasional. Salah satu pengembangan penting adalah pengelolaan sesi; versi saat ini menggunakan bearer token di penyimpanan browser. Pengujian beban, pemulihan backup, dan validasi pengguna juga perlu dilakukan.”

### 13. Apa bukti keberhasilan proyeknya?

“Bukti teknis yang tersedia adalah alur fitur yang dapat diperagakan, dokumentasi yang dipetakan ke implementasi, dan catatan pengujian otomatis. Untuk bukti dampak bisnis seperti penghematan waktu atau pengurangan kesalahan dalam persentase, diperlukan pengukuran lapangan.”

### 14. Apa prioritas jika data dan pengguna bertambah?

“Saya akan mulai dari pengukuran: bagian query, waktu respons, dan pemuatan data mana yang menjadi hambatan. API daftar sudah mempunyai pagination, tetapi UI saat ini memuat seluruh halaman dalam lingkup aksesnya. Karena itu, pagination dan filter langsung di server pada alur UI menjadi salah satu kandidat perbaikan.”

### 15. Bagian mana yang kamu kerjakan sendiri?

Jawab sesuai kontribusi nyata. Isi kerangka ini sebelum latihan:

“Kontribusi langsung saya adalah [bagian yang benar-benar dikerjakan]. Untuk [bagian lain], saya menggunakan [framework/template/bantuan yang memang digunakan], kemudian melakukan [penyesuaian, penelusuran atau verifikasi yang benar-benar dilakukan]. Alur yang dapat saya jelaskan dari implementasinya adalah [contoh konkret].”

Jangan mengaku melakukan observasi, wawancara, pengujian, atau penulisan seluruh kode jika tidak dilakukan. Pemahaman lebih mudah dibuktikan dengan menelusuri satu alur nyata dari formulir, endpoint, validasi, penyimpanan, sampai laporan.

### 16. Apa fungsi Vite dan Node.js jika backend memakai Laravel?

“Vite membantu menjalankan pengembangan dan membangun aset frontend. Node.js menjalankan alat JavaScript tersebut. API bisnis proyek tetap memakai PHP/Laravel. Jadi, alat pengembangan frontend dan backend bisnis mempunyai tugas berbeda.”

### 17. Mengapa memakai Sanctum, dan apakah pengaturannya sudah ideal?

“Sanctum terintegrasi dengan Laravel untuk autentikasi API. Versi sekarang memakai bearer token yang disimpan di browser. Untuk SPA milik sendiri, dokumentasi Sanctum menyarankan sesi cookie. Peralihan itu menjadi pekerjaan lanjutan, termasuk konfigurasi CSRF dan pengujian.” Sumber: [Sanctum: SPA authentication](https://laravel.com/docs/12.x/sanctum#spa-authentication).

## Pegangan singkat saat latihan

- Hafalkan alur: masalah → pengguna → dashboard → satu peluang → target → arsitektur → integritas → pengujian → penutup.
- Ingat lima pembeda: Hot ≠ Won; potensi ≠ realisasi; tahun closing ≠ tahun pencatatan; rupiah ≠ unit; transaksi ≠ version ≠ idempotensi.
- Saat demo, jelaskan tujuan setiap tindakan. Berhenti berbicara sejenak ketika mengisi formulir atau menunggu tampilan.
- Ketika menjawab, gunakan satu contoh konkret sebelum menambahkan istilah teknis.
- Untuk setiap teknologi, ingat **tugas → alasan → alternatif → kekurangan**. Kesesuaian dengan proposal adalah salah satu alasan; tetap jelaskan hubungannya dengan kebutuhan aplikasi.
- Jika belum mengetahui jawaban: “Bagian itu belum saya pastikan. Pada implementasi yang dapat saya jelaskan saat ini, perilakunya adalah …; untuk memastikan detail tersebut saya perlu memeriksa ….”
- Jika belum ada pengukuran: “Belum ada pengukuran yang bisa saya jadikan dasar angka tersebut. Bukti yang tersedia saat ini adalah ….”

## Acuan lokal

- `README.md` pada direktori utama proyek.
- `src/docs/PROPOSAL-ALIGNMENT.md`.
- `src/docs/desain-sistem/ARSITEKTUR.md`.
- `src/docs/materi-ujian/AUDIT-PROFESIONAL.md`, pemeriksaan 20 Oktober 2026.
- `src/backend/routes/api.php`.
- `src/backend/app/Http/Controllers/OpportunityController.php`.
- `src/backend/app/Http/Controllers/Concerns/AuthorizesDivision.php`.
- `src/backend/app/Services/DashboardReport.php`.
