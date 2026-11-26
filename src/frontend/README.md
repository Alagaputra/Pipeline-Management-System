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

## Dashboard, Pipeline, dan Target

- Dashboard menampilkan realisasi dana Won dalam juta rupiah, realisasi layanan Won dalam unit, dan potensi dana aktif. Grafik bulanan membandingkan nominal yang dicatat dan realisasi pada tanggal closing. Diagram lingkaran menunjukkan ketertarikan nasabah untuk peluang aktif.
- Progres target ditampilkan per produk. Mode **Tahunan** memakai seluruh tahun laporan. Mode **Bulanan** memakai target dan realisasi bulan pilihan. Tombol **Tetapkan target** membuka form untuk produk dan tahun tersebut. Pada mode bulanan, fokus langsung menuju kolom bulan pilihan.
- Saat mencatat pipeline dana, masukkan nominal dalam rupiah. Satu peluang Bale Syariah, QRIS, atau CMS mewakili satu unit tanpa segmentasi. Jika dua PIC bernama sama, pilih berdasarkan username. Form menyimpan ID akun yang dipilih.
- Pada halaman Target, kartu dana menampilkan jumlah dalam juta rupiah. Form target menerima nilai tahunan dan alokasi bulanan dalam rupiah penuh atau unit sesuai produk. Bale Syariah dan QRIS tersedia untuk Konsumer, sedangkan CMS memakai satu target bersama lintas divisi.
- Closing Won menambah realisasi pada bulan closing. Untuk layanan, pencapaian target mencakup unit Won dan jumlah manual yang telah tersimpan. Kartu realisasi unit Won di dashboard menghitung pipeline Won saja.

Tes browser: `npm.cmd run test:e2e`. Siapkan PostgreSQL `pipeline_funding_test` beserta migration/seed dahulu. Tes memakai port 8001 dan 5174; database aplikasi tidak diubah. `PIPELINE_API_TARGET` dapat mengganti tujuan proxy saat pengujian.

Lihat [panduan proyek](../../README.md). Pemetaan proposal dan dokumentasi tambahan disimpan secara lokal di `../docs/` dan tidak disertakan di Git.

Formulir peluang dan target menampilkan pemisah ribuan saat mengetik, validasi di bawah kolom, serta pengaman simpan ganda. Closing Won/Lost memerlukan pemeriksaan ringkasan sebelum konfirmasi. Rincian setiap kejadian di riwayat dapat dibuka sesuai kebutuhan.

Pencarian, filter, urutan, dan halaman daftar tersimpan pada query URL (di dalam hash route), sehingga pulih setelah refresh atau navigasi kembali.

Snapshot sebelum perubahan formulir dan cadangan desain awal disimpan secara lokal di `../../arsip-lokal/`, di bawah direktori `files/backups/` pada arsip perapian. Folder tersebut tidak disertakan di Git; `manifest.json` pada arsip mencatat lokasi asal dan checksum setiap berkas.

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
- Form peluang, target dana, dan target layanan mempertahankan
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

Respons HTTP sukses dengan JSON rusak atau bentuk data penyimpanan yang tidak
sesuai ditolak dan diperlakukan sebagai hasil belum pasti. Draft tetap terbuka;
retry memakai key dan payload asli, termasuk ketika refresh sudah menemukan
closing tersimpan. Respons request sesi lama tidak menghapus token atau profil
akun yang baru login.

Agregasi nominal, target, dan unit memakai integer eksak. Total besar disimpan
sebagai string desimal dan diformat tanpa pembulatan rupiah/unit; konversi ke
angka pecahan hanya untuk persentase dan skala grafik. Saat total melampaui batas
integer aman JavaScript, tampilan rupiah memakai nilai lengkap.

`npm.cmd test` mencakup validasi, migrasi data lokal, draft peluang/closing,
konflik versi target rupiah dan unit, serta perubahan konteks divisi/tahun.
Tes tambahan memverifikasi presisi total besar, respons rusak, isolasi sesi,
dan retry closing setelah refresh. Suite browser mencakup navigasi riwayat
serta respons HTML 200 tanpa kehilangan draft. Tes browser juga memeriksa penyimpanan ID untuk dua pilihan PIC bernama sama dan fokus isian April untuk Deposito serta CMS.
Hasil verifikasi dan batas pemeriksaan terakhir tersedia pada
[README utama](../../README.md#build-dan-pengujian).

Saat memperbarui instalasi, jalankan `npm.cmd ci` dan `npm.cmd run build`.
Pembaruan backend memerlukan migration konteks otorisasi sebelum aplikasi
dibuka kembali; ikuti [panduan pembaruan instalasi](../backend/README.md#memperbarui-instalasi).
