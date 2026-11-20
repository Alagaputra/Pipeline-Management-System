# Pipeline Funding frontend

Vue.js + Vite + Chart.js, terhubung ke Laravel REST API dan PostgreSQL.

Jalankan dari direktori `src/frontend`:

```powershell
npm.cmd ci
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

## Sesi dan hak akses

Token berlaku 8 jam secara default, mengikuti `SANCTUM_EXPIRATION` pada backend.
Respons 401 membersihkan sesi browser dan mengarahkan pengguna ke login.
Penonaktifan atau perubahan peran/divisi melalui model `User` di backend mencabut
token. PIC tanpa divisi valid dan akun dengan peran tidak dikenal ditolak.
Riwayat PIC mengikuti divisi pengguna yang membaca, termasuk setelah PIC pindah
divisi; backend tetap menjadi sumber aturan otorisasi.

## Draft, konflik, dan retry

- Pilih tahun dari filter halaman sebelum membuka form target. Kolom tahun di
  dalam form target dana hanya untuk dibaca.
- Form peluang, target dana, target layanan, dan realisasi bulanan mempertahankan
  versi ketika form dibuka. Pembaruan state tidak mengganti versi draft lama.
- Perubahan divisi/tahun saat form target terbuka memblokir penyimpanan sampai
  data dimuat ulang. Konflik versi menghasilkan 409 dan tombol **Muat data terbaru**.
- Jika jaringan putus atau timeout, retry mempertahankan request key dan payload
  asli. Receipt lama tanpa konteks akses atau dari peran/divisi berbeda ditolak
  backend dengan 409. Periksa data terbaru sebelum membuat permintaan baru untuk
  operasi yang hasilnya belum pasti.

Nama nasabah maksimal 160 karakter, catatan 5.000 karakter, dan alasan Lost
2.000 karakter; penghitungan Unicode mengikuti API. Nominal, realisasi, target,
dan unit maksimal 9.007.199.254.740.991, dengan nilai minimum sesuai aturan field.
API menolak input di atas batas tersebut dengan 422 tanpa mengubah data lama.

## Verifikasi dan pembaruan

`npm.cmd test` mencakup validasi, migrasi data lokal, draft peluang/closing,
konflik versi target rupiah dan unit, serta perubahan konteks divisi/tahun.
Hasil verifikasi dan batas pemeriksaan terakhir tersedia pada
[README utama](../../README.md#build-dan-pengujian).

Saat memperbarui instalasi, jalankan `npm.cmd ci` dan `npm.cmd run build`.
Pembaruan backend memerlukan migration konteks otorisasi sebelum aplikasi
dibuka kembali; ikuti [panduan deployment](../../README.md#memperbarui-instalasi).
