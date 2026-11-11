# Buku belajar pribadi — Pipeline Funding Management

Disusun dari kode, skema PostgreSQL aktif, pengujian lokal **20 Oktober 2026**, dan dokumentasi resmi teknologi. Materi mengikuti permintaan belajar pribadi tanpa identitas pada sampul.

- **[MATERI-BELAJAR-UJIAN-MAGANG.pdf](MATERI-BELAJAR-UJIAN-MAGANG.pdf)** — 88 halaman: materi A4 dan 8 lampiran diagram A3. Teks dapat dicari, daftar isi dan rujukan dapat diklik.
- **[Versi HTML offline](MATERI-BELAJAR-UJIAN-MAGANG.html)** — isi dan tata letak yang sama, dapat dibuka tanpa internet.
- **[MATERI-BELAJAR.md](MATERI-BELAJAR.md)** — salinan teks untuk pencarian/catatan; gunakan PDF/HTML untuk format lengkap dan diagram.
- **[AUDIT-PROFESIONAL.md](AUDIT-PROFESIONAL.md)** — hasil peninjauan, koreksi dokumentasi, hasil tes, serta pekerjaan yang masih terbuka sebelum produksi.
- [materi.verifikasi.json](materi.verifikasi.json) — hasil pemeriksaan halaman, tabel/kolom, tautan, dan PDF.

## Isi

Konteks bisnis; tujuan dan batas sistem; pengguna dan produk; Active/Won/Lost versus Cold/Warm/Hot; pencatatan, tindak lanjut dan closing; Dashboard, Target, Tim dan Riwayat; contoh hitung fiktif; arsitektur; HTTP/JSON dan endpoint; Vue, Router, Vite, Node, Chart.js, PHP, Laravel dan Sanctum; Eloquent; 22 tabel dan 162 kolom; PK/FK/UNIQUE, angka dan zona waktu; transaksi, version, idempotensi; keamanan dan pengujian; Composer, migration dan seeder; penelusuran kode; menjalankan proyek; batas produksi; contoh penjelasan; 30 tanya jawab; latihan; fakta kecil; glosarium; ringkasan; 28 rujukan resmi; screenshot pengujian dan diagram.

Audit menyimpulkan dokumentasi **layak untuk bahan belajar dan ujian magang setelah koreksi yang dicatat**, bukan sertifikasi atau pernyataan siap produksi tanpa catatan. Aplikasi tetap menggunakan bearer token; rekomendasi mode sesi cookie untuk SPA, kebijakan presisi/retensi, serta kesiapan deployment dibahas sebagai pengembangan.

## Membaca cepat

Untuk persiapan presentasi, mulai dari **[NASKAH-PRESENTASI.md](NASKAH-PRESENTASI.md)**: 10 bagian dengan isi slide singkat, kalimat yang diucapkan, satu contoh hitung, dan 17 bekal tanya jawab. Perkiraan penyampaian 10–12 menit termasuk demo singkat.

Pelajari **[PERBANDINGAN-TECH-STACK.md](PERBANDINGAN-TECH-STACK.md)** untuk alasan pemilihan Vue, Laravel, PostgreSQL, Chart.js, Vite, serta mode autentikasi Sanctum. Perbandingan memuat alternatif, konsekuensi, contoh kode, jawaban lisan, dan kartu hafalan. Pembaruan presentasi 23 Oktober 2026 tersedia pada dua berkas tersebut; buku PDF/HTML 88 halaman tetap menjadi rujukan lengkap sebelumnya.

Mulai dari alur peluang dan contoh perhitungan; lanjutkan arsitektur serta transaksi/version/idempotensi. Gunakan tanya jawab dan latihan untuk menguji pemahaman. Kamus kolom dan lampiran diagram menjadi rujukan ketika ingin menelusuri desain lebih jauh.

Screenshot diambil oleh suite tes pada database pengujian, bukan bukti angka kinerja cabang. Contoh A–E dalam bab perhitungan adalah data fiktif terpisah dari angka screenshot.

## Memperbarui materi

```powershell
python src/docs/materi-ujian/scripts/build-study.py
node src/docs/materi-ujian/scripts/render-study.mjs
```

Spesifikasi isi berada pada `scripts/content_business.py`, `content_technical.py`, dan `content_learning.py`. Komponen/sumber konsep berada pada `book_common.py`; struktur/tema pada `build-study.py`. Diagram diambil dari paket `../desain-sistem/`; screenshot dari hasil tes UI terakhir dan disalin ke `assets/`. Tidak diperlukan koneksi internet untuk membangun atau membaca versi offline.

Renderer memeriksa isi tidak melampaui halaman, kelengkapan 22 tabel/162 kolom, tautan lokal/daftar isi, jumlah halaman, serta ukuran A4 dan A3. Semua halaman dirender ke `previews/page-*.png` dan tersedia dalam contact sheet untuk tinjauan visual. Hasil preview tidak disertakan di Git; salinan sebelum perapian berada di `arsip-lokal/`, di bawah `files/src/docs/materi-ujian/previews/` pada arsip perapian. Jalankan renderer untuk membuat ulang preview. Halaman yang padat memakai variasi tipografi yang tetap dapat dibaca; pilihan itu disimpan pada HTML akhir.
