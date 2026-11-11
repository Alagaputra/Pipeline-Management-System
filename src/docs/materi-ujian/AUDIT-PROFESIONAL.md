# Peninjauan profesional — Pipeline Funding Management

Tanggal: **20 Oktober 2026**. Lingkup: dokumentasi DFD/ERD/arsitektur, kecocokan dengan implementasi, katalog PostgreSQL aktif, pengujian otomatis lokal, dan keterbacaan keluaran dokumen. Peninjauan ini tidak mengubah aturan atau data aplikasi utama; tes browser mengubah fixture pada `pipeline_funding_test`.

## Kesimpulan

**Layak sebagai dokumentasi teknis dan bahan belajar/ujian magang setelah koreksi dokumentasi di bawah.** Penilaian didasarkan pada kriteria keterlacakan kode, konsistensi antarlevel, notasi, struktur data, pengujian, dan keterbacaan. Tidak merupakan sertifikasi standar tertentu, persetujuan operasional bank, pentest lengkap, atau pernyataan siap produksi tanpa catatan.

## Hasil pemeriksaan

| Area | Hasil | Bukti |
| --- | --- | --- |
| Metadata database | Cocok: 22 tabel, 162 kolom, 22 PK, 22 FK, 12 UNIQUE, tanpa CHECK SQL pada katalog yang diperiksa | `.runtime/study-audit/inspection.json`, `desain-sistem/schema.json` |
| ERD lengkap | 22 tabel/162 kolom, 22 FK SQL dan 2 relasi logis; tidak ada teks kolom terpotong | `ERD-LENGKAP.verifikasi.json`, renderer dijalankan kembali |
| Diagram per bagian | Arsitektur dan tiga ERD bagian lolos pemeriksaan clipping; PDF 4 halaman; tautan dan zoom berfungsi | `desain-sistem/VERIFIKASI.json` |
| DFD | Entitas PIC/Head terpisah; konteks dan Level 1–3; nomor hierarkis dan panah data; teks/label tidak tumpang tindih; ujung panah terhubung | `desain-sistem/DFD.verifikasi.json` |
| Batas Level 2/3 | Pembacaan referensi identitas PIC dan produk/divisi pada hasil tindak lanjut/closing dilengkapi | `OpportunityController::completeFollowUp/close`, spesifikasi DFD |
| Frontend | 9 tes lulus | `npm.cmd test` |
| Backend | 17 tes lulus, 129 assertion; SQLite in-memory | `php.cmd artisan test`, env DB_CONNECTION=sqlite, DB_DATABASE=:memory: |
| Browser + PostgreSQL | 29 tes lulus, sekitar 2,9 menit | `npm.cmd run test:e2e`; database pengujian, API 8001, frontend 5174 |
| Layout UI | 5 halaman × 3 kelompok akun × 3 lebar = 45 kombinasi diperiksa di dalam 3 tes layout | `tests/e2e/layout.spec.js` dan screenshot hasil terbaru |
| Build produksi | Berhasil dengan Vite 7.3.6; 1.648 modul ditransformasi, termasuk dependensi | `npm.cmd run build` |

Build dan server tes browser awalnya tertahan pembatasan akses sandbox esbuild. Keduanya dijalankan ulang melalui izin eksekusi di luar sandbox dan berhasil. Ini hambatan lingkungan pengujian, bukan perubahan source aplikasi untuk mengakali kegagalan build.

## Koreksi yang diselesaikan

1. **Keterlacakan DFD:** proses 3.4 dan 3.5 sekarang membaca D1 identitas PIC serta D2 nama produk/divisi, sesuai pemuatan relasi controller. Pada Level 3, pembacaan tersebut masuk ke proses 3.5.5. Batas induk/anak sekarang sama: E1, E2, D1, D2, D3, D5.
2. **Batas idempotensi:** README dan arsitektur diperjelas bahwa key dipakai pada penyimpanan data bisnis dari UI, bukan login/logout; klien API lama tanpa key tetap diperbolehkan.
3. **Mode autentikasi dan umur token:** dokumentasi menyebut bearer token secara eksplisit dan expiration Sanctum NULL. Tidak ada klaim proyek memakai cookie HttpOnly atau masa kedaluwarsa global tertentu.
4. **Versi dan tipe fisik:** materi memakai versi lockfile/runtime aktual. PostgreSQL menyimpan nilai dana sebagai BIGINT; timestamp tanpa zona; status berupa varchar; JSON audit berupa json. Nama unsigned pada migration tidak diartikan sebagai tipe UNSIGNED PostgreSQL.
5. **Pemisahan bukti:** hasil tes terbaru dipisahkan dari dokumentasi evaluasi September yang berstatus arsip; fitur yang belum ada diposisikan sebagai pengembangan.

## Catatan pengembangan yang belum diselesaikan

| ID | Prioritas/konteks | Temuan dan konsekuensi | Arah perbaikan |
| --- | --- | --- | --- |
| P01 | Penting sebelum produksi | Token autentikasi SPA berada di localStorage/sessionStorage; JavaScript dapat mengaksesnya. Sanctum merekomendasikan sesi cookie untuk SPA milik sendiri. | Evaluasi mode sesi cookie HttpOnly beserta CSRF, kebijakan origin, dan uji regresi. [Dokumentasi Sanctum](https://laravel.com/framework/docs/12.x/sanctum). |
| P02 | Penting sebelum memperbesar volume/nilai | UI memeriksa Number.isSafeInteger, tetapi API tidak menetapkan maksimum yang sama dan agregat bisa melampaui batas Number. | Tetapkan batas bisnis/agregat atau kontrak decimal/string dengan aritmetika yang konsisten; tambahkan tes batas. |
| P03 | Konsistensi formulir | UI dan API memakai maksimum teks berbeda: nama 120/160, catatan 2.000/5.000, alasan Lost 1.000/2.000. | Selaraskan aturan sesuai kebutuhan; saat ini klien API dapat menerima teks yang lebih panjang daripada UI. |
| P04 | Operasional | Expiration token global NULL; logout lokal saat offline tidak membuktikan pencabutan token server. | Tentukan umur token, pencabutan, perubahan status akun, dan tata kelola sesi. |
| P05 | Operasional data | Receipt menyimpan body respons; audit menyimpan snapshot. Tidak ada bukti kebijakan retensi/cleanup dan audit tahan manipulasi sudah diterapkan. | Atur retensi, pembatasan hak, backup, serta kebutuhan integritas jejak. |
| P06 | Skala | API daftar dipaginasi, tetapi frontend memuat seluruh halaman scoped. Pengayaan timeline dapat memicu pencarian berulang. | Profilkan; pertimbangkan filter/paginasi server di jalur UI dan pemuatan relasi yang lebih efisien. |
| P07 | Integritas lintas klien | Nonnegatif, rentang bulan/tahun, dan beberapa kesesuaian bisnis ditegakkan di API; tidak seluruhnya melalui CHECK/FK komposit. | Evaluasi constraint tambahan tanpa menghapus validasi API. |
| P08 | Waktu | Timezone aplikasi Asia/Jakarta, koneksi DB Asia/Bangkok, timestamp without time zone; UI tanggal memakai perangkat. | Tetapkan konvensi waktu lintas lapisan dan uji batas pergantian hari/zona. |
| P09 | Produksi dan bukti eksternal | Belum ada bukti deployment publik, hasil beban, audit keamanan penuh, uji restore, Firefox/Safari, atau persetujuan UAT operasional. | Verifikasi terpisah sesuai penggunaan; jangan mengarang SLA, skala, atau persentase manfaat. |

Temuan di atas dicatat, bukan diam-diam dianggap selesai. Tidak dilakukan migrasi mode autentikasi atau perubahan aturan aplikasi sebagai bagian pembuatan materi belajar.

## Versi yang digunakan materi

Vue 3.5.42; Vue Router 4.6.4; Vite 7.3.6; Chart.js 4.5.1; Laravel 12.69.2; Sanctum 4.3.3; PHP lokal 8.2.12; PostgreSQL lokal 18.4; Node lokal 24.15.0; Playwright Test 1.63.0; PHPUnit 11.5.56; Prettier 3.9.6. Versi ini bersumber dari lockfile dan inspeksi lokal, bukan daftar versi terbaru.

## Batas kesimpulan

- Kelulusan tes terbatas pada skenario dan lingkungan yang dijalankan. Dua tes backend adalah contoh dasar; jumlah total bukan ukuran tunggal kedalaman pengujian.
- Tidak ada pengukuran lapangan yang mendukung klaim manfaat persentase, kecepatan dibanding produk lain, atau kepuasan pengguna.
- DFD Level 2 merinci pipeline dan Level 3 merinci closing; bukan seluruh proses didekomposisi ke kedalaman identik.
- ERD berisi struktur fisik; record database utama tidak diekspor untuk materi. Screenshot UI berasal dari database pengujian dan harus dibaca sebagai ilustrasi tampilan, bukan bukti kinerja operasional cabang.

Materi lengkap dan sumber konsep tersedia pada `MATERI-BELAJAR-UJIAN-MAGANG.pdf` dan versi HTML pada folder ini.
