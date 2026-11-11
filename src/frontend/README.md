# Pipeline Funding frontend

Vue.js + Vite + Chart.js, terhubung ke Laravel REST API dan PostgreSQL.

```powershell
npm.cmd install
npm.cmd run dev
npm.cmd run build
npm.cmd test
```

Backend berjalan di port 8000; Vite meneruskan `/api` ke backend. Browser menyimpan token login, sedangkan data operasional berada di PostgreSQL.

Dashboard dan Target menggunakan ringkasan backend. Grafik Chart.js menampilkan target/realisasi, komposisi Cold/Warm/Hot, dan nominal peluang/realisasi per bulan. Target dana ditampilkan tahunan per produk. Target layanan Bale Syariah dan QRIS tersedia untuk Konsumer, sedangkan CMS merupakan target bersama kedua divisi. Ketiganya ditampilkan dalam unit pada Dashboard dan dapat dikelola di halaman Target, termasuk target dan realisasi bulanannya. Detail opportunity menampilkan riwayat perkembangan untuk peluang aktif maupun closing.

Tes browser: `npm.cmd run test:e2e`. Siapkan PostgreSQL `pipeline_funding_test` beserta migration/seed dahulu. Tes memakai port 8001 dan 5174; database aplikasi tidak diubah. `PIPELINE_API_TARGET` dapat mengganti tujuan proxy saat pengujian.

Lihat [panduan proyek](../../README.md). Pemetaan proposal dan dokumentasi tambahan disimpan secara lokal di `../docs/` dan tidak disertakan di Git.

Formulir peluang dan target menampilkan pemisah ribuan saat mengetik, validasi di bawah kolom, serta pengaman simpan ganda. Closing Won/Lost memerlukan pemeriksaan ringkasan sebelum konfirmasi. Rincian setiap kejadian di riwayat dapat dibuka sesuai kebutuhan.

Pencarian, filter, urutan, dan halaman daftar tersimpan pada query URL (di dalam hash route), sehingga pulih setelah refresh atau navigasi kembali. Target yang belum ditetapkan di Dashboard memiliki tautan langsung ke formulir produk dan tahun yang dipilih.

Snapshot sebelum perubahan formulir dan cadangan desain awal disimpan secara lokal di `../../arsip-lokal/`, di bawah direktori `files/backups/` pada arsip perapian. Folder tersebut tidak disertakan di Git; `manifest.json` pada arsip mencatat lokasi asal dan checksum setiap berkas.

Dashboard dan halaman Target menggunakan komponen TargetCard yang sama untuk dana dan layanan di Komersil maupun Konsumer. Urutan informasi selalu pencapaian tahunan, target, realisasi, progress bar, dan sisa target. Grid menyesuaikan jumlah produk; jenis produk dan izin tetap mengikuti divisi, dengan CMS bersama.
