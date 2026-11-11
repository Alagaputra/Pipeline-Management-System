# Pemeriksaan paket evaluasi

Tanggal: 14 September 2026.

## Aplikasi

Perintah yang dijalankan dari folder `src`:

```text
cd frontend
npm test
npx playwright test

cd ../backend
php artisan test
```

Hasil terakhir: pengujian logika frontend lulus, **3 skenario E2E browser lulus**, dan backend lulus **7 test dengan 24 assertion**. Skenario E2E mencakup closing Won yang tetap ada setelah reload, target/realisasi dari MySQL, serta larangan Giro pada Konsumer.

Migration Laravel berstatus `Ran`, frontend berhasil dibangun untuk produksi, dan alur E2E dijalankan terhadap Laravel serta MySQL Laragon. Pemeriksaan ini bukan pentest atau uji performa.

## Dokumen

- Diagram SVG dan HTML dibangun dari `build.mjs` tanpa CDN atau dependency diagram baru.
- `verify.mjs` memeriksa tautan lokal, halaman HTML offline, tombol perbesaran, struktur entitas Mermaid, dan overflow mobile; menghasilkan screenshot review serta PDF dari tampilan HTML.
- PDF adalah salinan visual dokumen ringkas. Detail kolom, endpoint, dan asumsi tetap ada pada Markdown.
- Diagram dan penjelasan sudah diperbarui untuk mencerminkan implementasi Laravel–MySQL.

Hasil verifikasi dokumen: **lulus** untuk 12 entitas dalam satu ERD, tautan lokal, tiga SVG (ERD gabungan, arsitektur, dan alur), pembukaan HTML offline, kontrol zoom, dan lebar mobile. Tidak ada JavaScript pageerror. PDF berhasil dibuat dari HTML; diagram dibatasi tinggi saat cetak agar muat pada kertas A4 landscape. Tidak dilakukan render ulang PDF menggunakan aplikasi PDF terpisah.

Jalankan kembali dari `src` jika dokumen diedit:

```text
node docs/evaluation/build.mjs
node docs/evaluation/verify.mjs
```

Verifikasi HTML memakai Playwright dan Edge yang sudah tersedia di proyek. Diagram Mermaid diperiksa secara struktural; paket tidak memasang renderer Mermaid. Diagram yang ditampilkan dan diperiksa secara visual adalah SVG lokal.
