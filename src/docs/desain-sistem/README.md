# Desain database dan arsitektur web

**Lokasi:** `src/docs/desain-sistem/`, di dalam direktori proyek Pipeline Management system.

Dokumen mengikuti implementasi **Vue.js + Chart.js + Laravel REST API + PostgreSQL per 19 Oktober 2026**. Metadata diverifikasi langsung: 22 tabel dan 162 kolom. Pembuatan dokumentasi tidak mengubah data atau aplikasi.

## Mulai dari sini

- **[Buku belajar ujian magang — PDF 88 halaman](../materi-ujian/MATERI-BELAJAR-UJIAN-MAGANG.pdf)** memuat penjelasan website dan teknologi, contoh hitung, tanya jawab, kamus kolom, dan lampiran diagram. [Hasil peninjauan 20 Oktober](../materi-ujian/AUDIT-PROFESIONAL.md) menjelaskan koreksi dan catatan produksi yang masih terbuka.
- **[DFD.pdf](DFD.pdf):** diagram konteks, DFD Level 1, Level 2 proses pipeline, dan Level 3 proses closing Won/Lost, empat halaman A3 landscape. [Buka penampil offline](DFD.html) atau [baca kamus aliran dan penjelasannya](DFD.md). DFD disusun 20 Oktober 2026 berdasarkan implementasi aplikasi.

  Revisi 02 memakai notasi Gane–Sarson dengan entitas PIC/Head terpisah, blok identitas dokumen, penomoran halaman, dan legenda. PNG DFD beresolusi 5040 × 3570 piksel; PDF/SVG berupa vektor.
- **[ERD-LENGKAP.png](ERD-LENGKAP.png): ERD gabungan 22 tabel, 162 kolom, seluruh 22 FK SQL, dan 2 relasi logis dalam satu gambar.**
- **[ERD-LENGKAP.pdf](ERD-LENGKAP.pdf):** ERD gabungan satu halaman A1 landscape; dapat diperbesar tanpa pecah.
- **[ERD-LENGKAP.html](ERD-LENGKAP.html):** ERD gabungan dengan perbesaran dan sorotan relasi ketika tabel diklik.
- **[index.html](index.html):** buka di browser untuk melihat semua diagram, memperbesar, dan mencetak. Dapat dibuka tanpa internet.
- **[desain-database-dan-arsitektur.pdf](desain-database-dan-arsitektur.pdf):** empat halaman A3 landscape, siap dibagikan atau dijadikan lampiran.
- **[DESAIN-DATABASE.md](DESAIN-DATABASE.md):** kamus lengkap 22 tabel, 162 kolom, nullable/default, PK, FK, UNIQUE, dan indeks.
- **[ARSITEKTUR.md](ARSITEKTUR.md):** penjelasan lapisan, modul, alur API, cakupan produk, dan transaksi.

## Gambar untuk laporan

| Isi | PNG | SVG vektor |
| --- | --- | --- |
| Diagram konteks DFD | [dfd-konteks.png](dfd-konteks.png) | [dfd-konteks.svg](dfd-konteks.svg) |
| DFD Level 1 | [dfd-level-1.png](dfd-level-1.png) | [dfd-level-1.svg](dfd-level-1.svg) |
| DFD Level 2 — pipeline | [dfd-level-2-pipeline.png](dfd-level-2-pipeline.png) | [dfd-level-2-pipeline.svg](dfd-level-2-pipeline.svg) |
| DFD Level 3 — closing Won/Lost | [dfd-level-3-closing.png](dfd-level-3-closing.png) | [dfd-level-3-closing.svg](dfd-level-3-closing.svg) |
| **ERD gabungan seluruh database** | **[ERD-LENGKAP.png](ERD-LENGKAP.png)** | **[ERD-LENGKAP.svg](ERD-LENGKAP.svg)** |
| Arsitektur sistem | [arsitektur-sistem.png](arsitektur-sistem.png) | [arsitektur-sistem.svg](arsitektur-sistem.svg) |
| ERD master dan pipeline | [erd-pipeline.png](erd-pipeline.png) | [erd-pipeline.svg](erd-pipeline.svg) |
| ERD target dan realisasi | [erd-target.png](erd-target.png) | [erd-target.svg](erd-target.svg) |
| ERD autentikasi, audit, dan retry | [erd-keamanan.png](erd-keamanan.png) | [erd-keamanan.svg](erd-keamanan.svg) |

ERD gabungan beresolusi **6880 × 5200 piksel** dan memuat seluruh kolom. Empat gambar per bagian beresolusi 3200 × 2240 piksel dengan atribut utama. SVG tetap tajam saat diperbesar. Garis putus-putus adalah referensi logis, bukan FK SQL.

## Sumber yang dapat diedit

- [dfd-konteks.mmd](dfd-konteks.mmd), [dfd-level-1.mmd](dfd-level-1.mmd), [dfd-level-2-pipeline.mmd](dfd-level-2-pipeline.mmd), dan [dfd-level-3-closing.mmd](dfd-level-3-closing.mmd): sumber Mermaid DFD.
- [scripts/build-dfd.py](scripts/build-dfd.py) dan [scripts/render-dfd.mjs](scripts/render-dfd.mjs): pembentuk dan renderer paket DFD. Regenerasi dijelaskan di [DFD.md](DFD.md).
- [scripts/dfd_layout.py](scripts/dfd_layout.py): komponen notasi, tata letak cetak A3, dan penampil DFD revisi 02.
- [erd-lengkap.mmd](erd-lengkap.mmd): Mermaid lengkap seluruh 22 tabel dan seluruh FK, termasuk hubungan token/sesi yang bersifat logis.
- [arsitektur-sistem.mmd](arsitektur-sistem.mmd): Mermaid arsitektur.
- [alur-penyimpanan.mmd](alur-penyimpanan.mmd): sequence simpan, transaksi, serta retry.
- [schema.json](schema.json): metadata PostgreSQL tanpa record operasional dan tanpa kredensial.
- [scripts/build.py](scripts/build.py): pembentuk diagram SVG, kamus, Mermaid ERD, dan halaman HTML.
- [scripts/render.mjs](scripts/render.mjs): ekspor PNG/PDF serta verifikasi visual dasar.

Untuk membaca Mermaid, gunakan preview Mermaid pada editor yang mendukungnya. Berkas HTML dan gambar tidak membutuhkan ekstensi tersebut.

## Memperbarui dokumentasi

Dari direktori utama proyek, dengan PostgreSQL dan dependensi lokal tersedia:

```powershell
cd src/backend
.\php.cmd ..\docs\desain-sistem\scripts\export-schema.php
cd ../..
python src/docs/desain-sistem/scripts/build.py
node src/docs/desain-sistem/scripts/render.mjs
python src/docs/desain-sistem/scripts/build-erd.py
node src/docs/desain-sistem/scripts/render-erd.mjs
```

Exporter hanya membaca katalog skema. Renderer memakai Playwright dan Microsoft Edge yang sudah digunakan proyek. Jika struktur/modul berubah, tinjau pula penjelasan arsitektur, penempatan tabel, serta sumber Mermaid arsitektur dan sequence.

Folder `../evaluation/` menyimpan dokumen versi terdahulu yang masih memuat rancangan MySQL. Gunakan folder **desain-sistem** ini sebagai acuan struktur terbaru.
