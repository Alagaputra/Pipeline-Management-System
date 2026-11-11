# Kesesuaian aplikasi dengan proposal MBKM

Pembaruan 19 Oktober 2026. Acuan: **Proposal MBKM Ajipati Alaga Putra**, bagian 1.5, 3.8–3.12, dan 4.3.

## Cakupan aplikasi

Sistem berbasis web untuk pencatatan, pemantauan, dan rekapitulasi pipeline Funding BSN KC Bekasi. Tidak terhubung dengan sistem utama bank dan tidak menjalankan transaksi keuangan.

| Kebutuhan | Implementasi |
| --- | --- |
| Autentikasi dan hak akses | Laravel Sanctum; PIC mengakses divisinya, Head Funding dapat memantau kedua divisi |
| Data pipeline | Tanggal, PIC, produk, segmentasi, nasabah/perusahaan, nominal, status, follow-up, dan catatan |
| Cold/Warm/Hot | Validasi server dan indikator pada antarmuka |
| Riwayat perkembangan | Audit pembuatan, perubahan, follow-up, dan closing; timeline menampilkan waktu, pelaku, serta nilai sebelum/sesudah |
| Won/Lost | Dipisahkan dari peluang aktif tanpa penghapusan; closing final dan baca saja |
| Target tahunan berdasarkan produk | Halaman Target berisi target, realisasi Won, persentase, dan sisa target per produk |
| Informasi PIC | Halaman Team dan riwayat penanganan PIC |
| Pencarian dan filter | Pipeline dan History |
| Vue.js | Antarmuka berbasis komponen |
| Laravel REST API | Validasi, otorisasi, logika bisnis, audit, dan laporan |
| PostgreSQL | Penyimpanan relasional; migration, foreign key, transaksi, dan unique constraint |
| Chart.js | Grafik batang target/realisasi, doughnut status, dan garis nilai bulanan |

Tampilan utama target di Dashboard berupa kartu per produk yang menampilkan progress bar, nominal target, realisasi Won, dan sisa target. Grafik batang tetap tersedia pada bagian “Lihat perbandingan grafik” yang dapat dibuka saat diperlukan.

## Definisi perhitungan

`GET /api/dashboard?year=YYYY&division_id=ID` menghasilkan ringkasan dan grafik melalui `DashboardReport`. Untuk PIC, divisi pada akun selalu menjadi batas akses meskipun parameter divisi lain dikirim. Head Funding dapat memilih satu divisi atau gabungan.

- Peluang aktif, nominal potensi, Hot, dan prioritas follow-up mencakup seluruh tahun.
- Realisasi berasal dari nominal **realisasi Won**, mengikuti tahun **tanggal closing**, bukan tanggal pencatatan atau nominal peluang.
- Target adalah jumlah target tahunan per produk dana dalam divisi yang dapat diakses.
- Target nol berarti belum ditetapkan. Persentase dapat melebihi 100%; sisa target minimum nol.
- Grafik garis menunjukkan nominal peluang menurut bulan pencatatan dan realisasi Won menurut bulan closing. Ini bukan snapshot historis saldo peluang aktif. Bulan yang belum berlangsung ditampilkan sebagai data belum tersedia.
- Frontend menampilkan laporan backend; konversi rupiah ke miliar dan pemformatan angka dilakukan hanya untuk penyajian.

## Penyimpanan lama

Target dana utama ditampilkan tahunan per produk. Target layanan Bale Syariah dan QRIS (Konsumer) serta CMS (bersama kedua divisi) tetap ditampilkan di Dashboard dan halaman Target dalam satuan unit, dengan target dan realisasi bulanan. Target layanan tidak dijumlahkan dengan target dana. Data target bulanan dana dan target cabang versi sebelumnya tetap disimpan.

Perintah `pipeline:import-mysql` menyalin tabel operasional ke PostgreSQL yang masih kosong. ID, relasi, target lama, dan audit dipertahankan; sumber MySQL tidak diubah. Token login lama tidak disalin sehingga pengguna perlu login kembali.

## Dokumentasi perancangan dan pengujian

- DFD implementasi terbaru: [diagram konteks, Level 1, Level 2 pipeline, dan Level 3 closing](desain-sistem/DFD.pdf), dengan [kamus aliran dan pemetaan penyimpanan](desain-sistem/DFD.md). Sumber Mermaid, PNG/SVG, dan penampil offline tersedia di folder yang sama.
- ERD dan alur yang sudah tersedia: `evaluation/erd.mmd`, `evaluation/activity.mmd`, dan `evaluation/closing-sequence.mmd`. ERD memuat tabel kompatibilitas versi lama.
- Arsitektur: Vue.js + Chart.js → Laravel REST API → PostgreSQL.
- Tes backend memeriksa autentikasi, validasi, akses divisi, Won/Lost, audit, penghitungan berdasarkan tahun closing, tren bulanan, dan pembaruan target tahunan.
- Tes browser memeriksa penyimpanan dan reload, riwayat closing, target tahunan, pilihan produk, serta grafik desktop/mobile.
- Pemeriksaan 19 Oktober: 17 tes backend (129 assertion) menggunakan SQLite in-memory dan 9 tes logika frontend lulus. Suite browser memakai Laravel dan PostgreSQL terpisah; meliputi alur operasional, retry aman, rollback transaksi, respons terlambat, pemulihan sesi, perlindungan isian, dan 45 kombinasi tampilan desktop/ponsel. Hasil rinci semula berada di `.runtime/fixes-20261019/`; saat perapian repo, hasil tersebut dipindahkan ke `arsip-lokal/`, di bawah `files/.runtime/fixes-20261019/` pada arsip perapian, dan tidak disertakan di Git.
- Paket `evaluation/` yang bertanggal September adalah catatan evaluasi versi sebelumnya; acuan perilaku terbaru adalah dokumen ini dan kode aplikasi.

Evaluasi langsung bersama pengguna, validasi rancangan Figma, serta persetujuan penyerahan mengikuti tahapan magang dan tidak dapat digantikan oleh pengujian otomatis.

Closing menyimpan catatan dan hasil dalam satu transaksi. Satu formulir target dana/layanan disimpan sekaligus; konflik pada satu produk atau bulan membatalkan seluruh formulir. `Idempotency-Key` memastikan percobaan ulang permintaan yang sama tidak menambah data atau audit. Penambahan tabel `request_receipts` melalui migration tidak mengubah record operasional yang sudah ada. Respons lama diabaikan ketika divisi atau tahun yang dipilih telah berubah.

Referensi teknis: [integrasi Chart.js](https://www.chartjs.org/docs/latest/getting-started/integration.html) dan [PostgreSQL untuk Windows](https://www.postgresql.org/download/windows/).
