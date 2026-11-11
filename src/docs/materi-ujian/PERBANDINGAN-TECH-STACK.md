# Bekal tanya jawab — alasan memilih tech stack

Disusun 23 Oktober 2026 dari kode proyek dan dokumentasi resmi. Gunakan bersama [naskah presentasi](NASKAH-PRESENTASI.md). Panduan ini menjelaskan alasan pemilihan, alternatif, konsekuensi, dan contoh yang dapat ditunjukkan saat ditanya penguji.

**Pola menjawab: kebutuhan → pilihan → contoh → kekurangan.** Penilaian “cocok untuk proyek ini” merupakan pertimbangan desain berdasarkan implementasi, bukan hasil percobaan yang membandingkan semua alternatif. Jangan mengaku memiliki hasil benchmark atau pengalaman tim yang belum dibuktikan.

## 1. Jawaban 30 detik

“Aplikasi ini membutuhkan tampilan interaktif, pemeriksaan aturan bisnis di server, penyimpanan data yang saling berhubungan, dan grafik laporan. Karena itu, saya menggunakan Vue untuk tampilan, Laravel untuk API dan aturan bisnis, PostgreSQL untuk database, serta Chart.js untuk grafik. Stack tersebut juga sesuai dengan teknologi yang tercatat dalam dokumen kesesuaian proposal. React, Express, dan MySQL dapat dipakai juga. Pertimbangan saya adalah kecocokan kebutuhan dan konsistensi proyek, tanpa klaim bahwa stack ini paling cepat.”

Acuan pilihan dalam proyek: [PROPOSAL-ALIGNMENT.md](../PROPOSAL-ALIGNMENT.md). Materi ini tidak menganggap alternatif sudah pernah diuji hanya karena dapat dibandingkan secara konsep.

## 2. Pahami tugasnya dulu

| Bagian | Teknologi proyek | Arti sederhana | Contoh pemakaian |
| --- | --- | --- | --- |
| Bahasa frontend | JavaScript | Bahasa untuk logika di browser | Mengolah isian dan respons API |
| Antarmuka | Vue 3 | Menyusun tampilan yang bereaksi terhadap perubahan data | Form peluang, filter, kartu target |
| Navigasi | Vue Router | Mengatur perpindahan halaman aplikasi | Dashboard, Pipeline, Target, Tim, Riwayat |
| Grafik | Chart.js | Mengubah data menjadi grafik | Batang, garis, doughnut |
| Bahasa server | PHP | Bahasa yang menjalankan backend ini | Menjalankan Laravel |
| Backend | Laravel 12 | Framework untuk menerima permintaan dan menjalankan aturan | Login, akses divisi, closing, laporan |
| Autentikasi | Laravel Sanctum | Paket autentikasi yang terintegrasi dengan Laravel | Memeriksa bearer token API saat ini |
| Database | PostgreSQL | Menyimpan data dalam tabel yang saling terhubung | Peluang, PIC, produk, target, audit |
| Alat pengembangan | Vite 7 | Menjalankan server pengembangan dan membangun aset frontend | Perintah dev dan build |
| Lingkungan alat frontend | Node.js dan npm | Menjalankan alat JavaScript dan mengelola paket | Menjalankan Vite dan memasang dependensi |

**Jangan tertukar:** Node.js dipakai untuk alat frontend, sedangkan API bisnis berjalan dengan PHP/Laravel. Vue membentuk UI, sementara Vite membantu mengembangkan dan membangun asetnya. Versi mayor mengikuti manifest proyek, bukan klaim versi terbaru.

Bukti lokal: `src/frontend/package.json` dan `src/backend/composer.json`.

## 3. Vue dibandingkan React dan JavaScript langsung

Vue mendukung komponen dan template deklaratif; format `.vue` dapat menempatkan template, logika, dan gaya dalam satu file. React juga menyusun UI dari komponen; pola pengantarnya menggunakan fungsi JavaScript dan JSX. Sumber: [pengantar Vue](https://vuejs.org/guide/introduction.html) dan [Quick Start React](https://react.dev/learn).

| Pertimbangan | Vue, pilihan proyek | React | JavaScript langsung |
| --- | --- | --- | --- |
| Menyusun UI | Komponen `.vue` dengan template dan logika | Komponen fungsi; JSX lazim digunakan | Struktur dan pembaruan tampilan diatur sendiri |
| Kebutuhan aplikasi | Form, drawer, dan kartu dapat digunakan ulang | Bisa membangun fitur yang sama | Bisa dipakai; pola UI berulang perlu dirancang sendiri |
| Pertimbangan pilihan | Selaras dengan komponen dan composable yang sudah digunakan | Menarik jika tim/produk sudah memiliki komponen React | Menarik untuk interaksi sederhana dengan lingkup kecil |
| Hal yang dikelola | Reaktivitas, state, dan pembagian komponen | State, aliran data, dan integrasi | Sinkronisasi data dan tampilan ketika interaksi bertambah |

**Jawaban lisan:**

“Vue cocok karena aplikasi mempunyai bagian berulang, seperti formulir peluang dan kartu target. Bagian itu dijadikan komponen. React juga mampu melakukan hal yang sama; Vue dipakai agar selaras dengan rancangan dan implementasi proyek.”

**Contoh yang bisa ditunjukkan:** `OpportunityDrawer.vue`, `TargetCard.vue`, dan `usePipeline.js` dalam `src/frontend/src/`.

**Kalau ditanya ‘lebih cepat atau lebih mudah?’**

“Belum ada pengukuran waktu belajar atau performa dibanding React. Yang dapat saya tunjukkan adalah kecocokan struktur komponen dengan kebutuhan tampilan.”

## 4. Laravel dibandingkan Express dan PHP tanpa framework

Laravel menyediakan fasilitas validasi, akses database melalui Eloquent, dan migration. Express adalah framework web minimal yang berjalan di Node.js. Pengembang dapat memilih paket tambahan dan struktur sesuai kebutuhan. Sumber: [validasi Laravel](https://laravel.com/docs/12.x/validation), [Eloquent](https://laravel.com/docs/12.x/eloquent), [migration](https://laravel.com/docs/12.x/migrations), dan [Express](https://expressjs.com/).

| Pertimbangan | Laravel, pilihan proyek | Express di Node.js | PHP tanpa framework |
| --- | --- | --- | --- |
| Bahasa | PHP | JavaScript | PHP |
| Struktur | Konvensi route, middleware, controller, model | Minimal; struktur dan paket tambahan dipilih pengembang | Struktur dibuat sendiri |
| Kebutuhan proyek | Validasi, model, migration, integrasi Sanctum | Dapat dipenuhi dengan susunan paket yang sesuai | Dapat dibuat; fasilitas pendukung perlu dirancang/dipilih sendiri |
| Alternatif masuk akal ketika… | Mempertahankan pola backend proyek ini | Tim mengutamakan satu bahasa JavaScript dan sudah memiliki standar backend | Lingkup kecil dengan kebutuhan kerangka terbatas |
| Konsekuensi | Memahami konvensi Laravel; mengelola PHP dan JavaScript | Menyelaraskan pilihan paket dan struktur | Tanggung jawab desain fasilitas dasar lebih besar |

**Jawaban lisan:**

“Laravel dipakai karena aplikasi membutuhkan banyak aturan: produk harus sesuai divisi, closing harus valid, dan perubahan perlu dicatat. Laravel menyediakan struktur untuk menempatkan logika itu. Express juga bisa, tetapi pendekatannya lebih minimal dan pemilihan fasilitas lebih banyak ditentukan pengembang.”

**Contoh kode:** `OpportunityController.php` memakai validasi dan transaksi; `DashboardReport.php` menghitung laporan. Aturan divisi dan Won/Lost dibuat khusus oleh proyek. Framework tidak otomatis mengetahui aturan bisnis bank.

**Kalau ditanya ‘kenapa bukan Node.js agar satu bahasa?’**

“Satu bahasa merupakan keuntungan pendekatan Express/Node.js. Proyek ini memakai struktur Laravel sesuai rancangan. Konsekuensinya, saya perlu mengelola JavaScript untuk frontend dan PHP untuk backend. Pilihan itu tidak membuktikan salah satu bahasa selalu lebih baik.”

## 5. PostgreSQL dibandingkan MySQL dengan InnoDB

PostgreSQL menyediakan constraint seperti primary key, foreign key, UNIQUE, serta transaksi. MySQL dengan InnoDB juga mendukung transaksi, foreign key, dan penguncian baris. Sumber: [constraint PostgreSQL](https://www.postgresql.org/docs/18/ddl-constraints.html), [transaksi PostgreSQL](https://www.postgresql.org/docs/18/tutorial-transactions.html), dan [fitur InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-introduction.html).

| Pertimbangan | PostgreSQL, pilihan proyek | MySQL dengan InnoDB |
| --- | --- | --- |
| Data relasional | Dapat menghubungkan peluang, PIC, produk, divisi | Dapat memenuhi kebutuhan hubungan yang sama |
| Integritas | PK, FK, UNIQUE, transaksi tersedia | PK, FK, UNIQUE, transaksi tersedia |
| Contoh kebutuhan | Closing dan audit disimpan dalam satu transaksi | Pola transaksi serupa dapat diterapkan |
| Pertimbangan proyek | Selaras dengan rancangan dan database yang dipakai | Layak jika standar tim/operasional menggunakan MySQL |
| Perpindahan teknologi | Driver, migration, query, dan pengujian harus sesuai | Perlu memeriksa perbedaan tipe, SQL, migration, dan perilaku penguncian |

**Jawaban lisan:**

“PostgreSQL sesuai karena data peluang terhubung ke PIC, produk, dan divisi. Proses closing juga membutuhkan penyimpanan yang utuh. MySQL dengan InnoDB dapat memenuhi kebutuhan tersebut. PostgreSQL dipakai sesuai rancangan proyek; transaksi bukan fitur eksklusif PostgreSQL.”

**Konsekuensi pilihan:** perlu mengelola server database, akses, backup, pemulihan, dan query ketika data bertambah. Memilih PostgreSQL sendiri tidak menyelesaikan pekerjaan operasional itu.

**Kalau ditanya ‘kenapa bukan database dokumen?’**

“Aplikasi ini memiliki entitas dan hubungan yang jelas serta laporan agregat. Model relasional cocok untuk itu. Belum ada kebutuhan proyek yang membenarkan perubahan model. Saya tidak menyatakan semua database dokumen tidak memiliki transaksi.”

**Contoh kode:** migration `2026_09_14_080000_create_pipeline_tables.php` serta `OpportunityController.php`. Tidak semua aturan bisnis menjadi constraint SQL; kecocokan produk dan divisi juga diperiksa aplikasi.

## 6. Chart.js dibandingkan D3

Chart.js menyediakan jenis grafik umum dan opsi konfigurasi. D3 menyediakan alat visualisasi yang lebih mendasar agar pengembang dapat menyusun bentuk dan interaksi khusus. Sumber: [fitur Chart.js](https://www.chartjs.org/docs/latest/) dan [penjelasan D3](https://d3js.org/what-is-d3).

| Pertimbangan | Chart.js, pilihan proyek | D3 |
| --- | --- | --- |
| Pendekatan | Mengatur data dan konfigurasi jenis grafik | Menyusun visual dari skala, sumbu, bentuk, dan bagian lain |
| Kebutuhan yang cocok | Batang, garis, doughnut pada dashboard ini | Bentuk atau interaksi visual yang sangat khusus |
| Pengerjaan | Jenis grafik yang diperlukan sudah tersedia | Lebih banyak detail visual perlu dirancang |
| Konsekuensi | Kebutuhan di luar pola tersedia dapat memerlukan plugin/kode tambahan | Kontrol lebih rinci disertai tanggung jawab implementasi lebih besar |

**Jawaban lisan:**

“Dashboard membutuhkan batang untuk perbandingan, garis untuk nilai bulanan, dan doughnut untuk komposisi status. Chart.js sudah menyediakan jenis tersebut. D3 menarik jika bentuk visualnya sangat khusus. Untuk kebutuhan sekarang, Chart.js sudah sesuai.”

**Contoh kode:** `src/frontend/src/components/ReportChart.vue`. Chart.js menggambar data; nilai utama laporan dihitung oleh backend.

## 7. Vite dibandingkan webpack

Vite menyediakan server pengembangan dan perintah build. webpack merupakan bundler yang membangun keluaran dari dependensi aplikasi dan menyediakan pengaturan loader serta plugin. Sumber: [panduan Vite](https://vite.dev/guide/) dan [konsep webpack](https://webpack.js.org/concepts/).

| Pertimbangan | Vite, pilihan proyek | webpack |
| --- | --- | --- |
| Tugas | Membantu pengembangan dan membangun aset frontend | Membundel modul dan aset dengan konfigurasi yang dapat disesuaikan |
| Dalam proyek | Menggunakan plugin Vue dan proxy API saat pengembangan | Dapat dipakai jika proyek membutuhkan/telah memiliki konfigurasi webpack |
| Konsekuensi | Plugin, build, dan perbedaan dev/produksi perlu dipahami | Konfigurasi yang digunakan perlu dipelihara |

**Jawaban lisan:**

“Vite membantu pengembangan Vue dan menghasilkan aset untuk deployment. webpack juga layak. Saya mempertahankan Vite karena integrasi yang dibutuhkan sudah tersedia dan digunakan. Belum ada pengukuran perbandingan build dalam proyek ini.”

**Contoh kode:** `src/frontend/vite.config.js` dan `src/frontend/package.json`. Materi ini tidak menyamakan detail versi Vite terbaru di situs dokumentasi dengan Vite 7 yang digunakan proyek.

## 8. Sanctum: paket autentikasi dan mode sesi adalah dua keputusan

Sanctum mendukung token API serta autentikasi SPA berbasis sesi cookie. Dokumentasinya menyarankan autentikasi berbasis cookie untuk SPA milik sendiri. Sumber: [Laravel Sanctum](https://laravel.com/docs/12.x/sanctum#spa-authentication).

| Aspek | Implementasi saat ini | Arah pengembangan untuk SPA milik sendiri |
| --- | --- | --- |
| Bukti login saat request | Bearer token pada header `Authorization` | Sesi berbasis cookie sesuai alur Sanctum |
| Penyimpanan browser | `localStorage` atau `sessionStorage` | Konfigurasi cookie sesi HttpOnly dan alur CSRF |
| Konsekuensi | Token dapat dibaca JavaScript; pengelolaan sesi perlu diperkuat | Cookie, origin, dan CSRF perlu dikonfigurasi dengan benar |
| Status proyek | Sudah digunakan | Belum diterapkan |

**Jawaban lisan:**

“Sanctum dipakai karena terintegrasi dengan Laravel untuk autentikasi API. Versi sekarang menggunakan bearer token. Untuk SPA milik sendiri, dokumentasi menyarankan sesi cookie. Jadi, saya membedakan fasilitas paket yang dipilih dengan pengaturan sesi yang masih perlu diperbaiki.”

Sanctum tidak otomatis membuat aplikasi kebal XSS atau siap produksi. Hak akses peran/divisi tetap diperiksa kode proyek. Bukti: `AuthController.php`, `AuthorizesDivision.php`, dan `src/frontend/src/services/api.js`.

## 9. Mengapa Vue terpisah dari Laravel API?

Pertimbangan desain proyek: interaksi tampilan berada di Vue, sementara validasi, hak akses, dan laporan berada di backend. Keduanya bertukar data JSON melalui HTTP.

| Pilihan | Manfaat untuk kebutuhan ini | Konsekuensi |
| --- | --- | --- |
| Vue + Laravel API, implementasi proyek | Tanggung jawab UI dan aturan server jelas; form dan filter dapat dibuat sebagai komponen | Format data, error, sesi, dan validasi lintas lapisan harus selaras |
| Halaman dari backend, misalnya Laravel Blade | Pengelolaan halaman dan backend dapat lebih terpusat; masuk akal untuk interaksi sederhana | Interaksi yang bertambah tetap membutuhkan rancangan frontend yang sesuai |

**Jawaban lisan:**

“Aplikasi mempunyai formulir, filter, panel detail, dan grafik yang berubah sesuai data. Vue menangani interaksi itu, sedangkan Laravel memeriksa aturan dan menghasilkan data. Konsekuensinya saya perlu menjaga kontrak API dan perilaku error di kedua sisi. Untuk aplikasi dengan interaksi sederhana, halaman langsung dari backend juga masuk akal.”

Pemisahan ini tidak otomatis membuat aplikasi lebih cepat atau lebih aman. Hal itu tetap bergantung pada implementasi dan pengujian.

## 10. Pertanyaan lanjutan yang mungkin muncul

| Pertanyaan | Jawaban yang bisa dipakai |
| --- | --- |
| Jadi stack lain tidak bisa? | “Bisa. Saya menjelaskan kecocokan stack yang dipilih dengan kebutuhan dan implementasi proyek.” |
| Apa buktinya lebih cepat? | “Belum ada benchmark antarstack. Bukti yang tersedia adalah fungsi dan pengujian proyek ini.” |
| Jika teknologinya tercatat dalam proposal, di mana pertimbanganmu? | “Saya menjelaskan hubungan pilihannya dengan UI interaktif, aturan server, data relasional, dan grafik. Saya juga menjelaskan konsekuensi serta alternatifnya.” |
| Apa kekurangan paling nyata? | “Aturan frontend dan API harus selaras. Audit juga mencatat perbaikan sesi, batas angka, dan pemuatan seluruh halaman oleh UI.” |
| Kenapa tidak mengganti stack sekarang? | “Perubahan perlu didasarkan pada masalah terukur atau kebutuhan operasional berbeda. Mengganti stack memerlukan penyesuaian dan pengujian ulang.” |
| Apa yang disediakan framework dan apa yang dirancang proyek? | “Framework menyediakan fasilitas umum. Aturan produk sesuai divisi, Won/Lost, tahun realisasi, pemeriksaan versi, dan replay permintaan diterapkan dalam kode proyek. Kontribusi pribadi saya jelaskan sesuai pekerjaan nyata.” |

Rincian temuan: [AUDIT-PROFESIONAL.md](AUDIT-PROFESIONAL.md). Pembaruan ini memperbaiki penjelasan presentasi; temuan aplikasi tetap mengikuti catatan audit tersebut.

## 11. Kartu hafalan

| Teknologi | Tugas | Alasan | Alternatif | Konsekuensi |
| --- | --- | --- | --- | --- |
| Vue | Tampilan | Komponen untuk UI berulang | React | Mengelola state dan reaktivitas |
| Laravel | Aturan dan API | Fasilitas backend tersusun | Express | Mengelola PHP dan JavaScript |
| PostgreSQL | Penyimpanan | Data relasional dan transaksi | MySQL/InnoDB | Mengelola database dan backup |
| Chart.js | Grafik | Jenis grafik sesuai dashboard | D3 | Visual khusus dapat memerlukan tambahan |
| Vite | Dev dan build | Integrasi Vue sudah digunakan | webpack | Memahami konfigurasi dev/produksi |
| Sanctum | Autentikasi | Terintegrasi dengan Laravel | Evaluasi mode sesi cookie dalam Sanctum | Mode token browser saat ini perlu diperbaiki |

Latihan: tutup dokumen, lalu jelaskan setiap baris dalam dua kalimat. Mulai dari tugas dan contoh; tambahkan alternatif serta konsekuensi ketika ditanya.
