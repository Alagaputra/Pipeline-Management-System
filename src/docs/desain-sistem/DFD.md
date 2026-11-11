# Data Flow Diagram — Sistem Manajemen Pipeline Funding

Disusun pada **20 Oktober 2026** berdasarkan kode aplikasi Vue.js dan Laravel yang tersedia di proyek. DFD menunjukkan data yang masuk, diproses, disimpan, dan disajikan kepada pengguna.

**Revisi 02, ditinjau 20 Oktober 2026:** seluruh diagram ditata untuk lampiran laporan A3 landscape, dengan blok identitas dokumen, nomor halaman, legenda notasi, entitas PIC/Head yang terpisah, dan simbol pengulangan. Aliran referensi pada tindak lanjut dan closing telah dicocokkan kembali dengan pemuatan relasi controller. PDF dan SVG mempertahankan teks serta garis sebagai vektor. PNG beresolusi **5040 × 3570 piksel** per diagram.

## Berkas siap digunakan

- [DFD.pdf](DFD.pdf): empat halaman A3 landscape, satu diagram per halaman.
- [DFD.html](DFD.html): penampil offline dengan perbesaran dan tautan unduh.
- Diagram konteks: [PNG](dfd-konteks.png), [SVG](dfd-konteks.svg), [Mermaid](dfd-konteks.mmd).
- DFD Level 1: [PNG](dfd-level-1.png), [SVG](dfd-level-1.svg), [Mermaid](dfd-level-1.mmd).
- DFD Level 2 proses 3.0: [PNG](dfd-level-2-pipeline.png), [SVG](dfd-level-2-pipeline.svg), [Mermaid](dfd-level-2-pipeline.mmd).
- DFD Level 3 proses 3.5: [PNG](dfd-level-3-closing.png), [SVG](dfd-level-3-closing.svg), [Mermaid](dfd-level-3-closing.mmd).

## Konvensi dan batas sistem

Dokumen ini menggunakan **diagram konteks dengan proses 0**, **DFD Level 1 dengan proses 1.0–5.0**, **DFD Level 2 yang menguraikan proses 3.0**, dan **DFD Level 3 yang menguraikan proses 3.5**. Penamaan tingkat dapat berbeda di pedoman kampus; penomoran di sini dinyatakan agar tidak ambigu.

SVG, PNG, dan PDF menggunakan notasi Gane–Sarson: persegi untuk entitas eksternal, persegi membulat bernomor untuk proses, kotak terbuka dengan kode D untuk penyimpanan, dan panah bernama untuk aliran data. Mermaid mempertahankan proses serta aliran yang sama, menggunakan bentuk penyimpanan bawaan Mermaid.

Entitas dan penyimpanan sengaja digambar berulang untuk menjaga keterbacaan. **Simbol dengan ID sama menunjuk entitas atau penyimpanan yang sama**, bukan salinan data. Dua garis miring pada sudut simbol menandai pengulangan. **E1 PIC Funding dan E2 Head Funding selalu digambar sebagai entitas terpisah**, termasuk pada Level 1–3; aliran masing-masing mengikuti hak aksesnya.

| Entitas | Interaksi dan batas akses |
| --- | --- |
| E1 — PIC Konsumer / Komersil | Login, melihat referensi, mengelola peluang dan target, membaca laporan divisi sendiri. CMS menggunakan scope bersama. |
| E2 — Head Funding | Login, melihat kedua divisi, mengelola data sesuai divisi/scope, dan membaca laporan gabungan atau per divisi. |

Nama nasabah/perusahaan adalah bagian data peluang yang dimasukkan pengguna. Nasabah tidak mengirim atau menerima data secara langsung melalui aplikasi sehingga tidak menjadi entitas eksternal pada DFD implementasi ini. Sistem inti bank juga tidak menjadi entitas karena tidak terdapat integrasi tersebut. Tidak ada peran administrator terpisah dalam alur aplikasi saat ini.

## DFD Level 1 dan kamus aliran batas sistem

Diagram konteks meringkas masukan sebagai **Data akses, referensi, pipeline, target dan permintaan laporan**, serta keluaran sebagai **Hasil akses, referensi, pipeline, target dan laporan**, untuk masing-masing E1 dan E2. Kelima pasangan paket pembentuknya dijabarkan pada Level 1 dan tabel berikut. Pengguna mengirim kriteria atau isian, proses mengembalikan data hasil maupun hasil validasi. Paket tidak menyatakan urutan eksekusi.

| Proses | Paket masukan | Isi masukan | Paket keluaran | Isi keluaran |
| --- | --- | --- | --- | --- |
| 1.0 Autentikasi dan sesi | Akses dan sesi | Username/password untuk login; token untuk identitas atau logout. | Hasil akses dan sesi | Token, identitas, role/divisi, konfirmasi logout atau hasil validasi. |
| 2.0 Sajikan data referensi | Permintaan referensi | Jenis referensi dan divisi bila berlaku. | Daftar referensi | Divisi, produk yang tersedia, dan PIC aktif sesuai akses. |
| 3.0 Kelola pipeline | Data dan permintaan pipeline | Pencarian/filter/ID peluang; isian peluang; perubahan PIC; penyelesaian tindak lanjut; hasil closing dan versi record. | Hasil dan informasi pipeline | Daftar/detail peluang aktif atau Won/Lost, penugasan, timeline, hasil simpan dan versi baru, atau hasil validasi. |
| 4.0 Kelola target dan layanan | Data dan permintaan target | Tahun, produk, scope/divisi, nilai target, target bulanan, total realisasi layanan bulanan, dan versi record. Endpoint kompatibilitas juga menerima target cabang. | Hasil dan informasi target | Target dan realisasi layanan sesuai scope/tahun, hasil simpan, versi baru, atau hasil validasi. |
| 5.0 Sajikan laporan dan rekap | Permintaan laporan | Tahun/divisi untuk Dashboard; divisi untuk rekap Tim; ID PIC untuk peluang yang pernah ditangani. Filter tambahan pada tampilan dapat diolah frontend dari data yang sudah dibatasi aksesnya. | Laporan dan rekap | Ringkasan peluang, Cold/Warm/Hot, tindak lanjut, target dan pencapaian, tren bulanan, realisasi layanan, rekap PIC, dan daftar peluang yang pernah ditangani. |

Setiap proses data memerlukan sesi yang sah. Middleware autentikasi dan pembatasan akses berlaku pada request terkait. Pembatasan ini tidak digambar sebagai rangkaian kontrol atau panah urutan antarproses pada DFD logis.

## Penyimpanan logis dan pemetaan tabel

| ID | Penyimpanan logis | Tabel implementasi | Penggunaan |
| --- | --- | --- | --- |
| D1 | Akun dan token | `users`, `personal_access_tokens` | Membaca akun/PIC/pelaku dan token; membuat atau mencabut token melalui autentikasi. |
| D2 | Referensi bisnis | `divisions`, `products`, `division_products`, `target_scopes` | Divisi, produk, pasangan produk–divisi, dan scope target. Dibaca oleh proses; pengelolaan master melalui UI tidak tersedia. |
| D3 | Peluang dan penugasan | `opportunities`, `opportunity_assignments` | Data peluang, nominal, status minat, tindak lanjut, hasil closing, realisasi dana, PIC saat ini/final, dan riwayat penanganan. |
| D4 | Target dan realisasi layanan | `annual_targets`, `monthly_targets`, `unit_realizations`, `branch_targets` | Target tahunan/bulanan, total realisasi layanan per bulan, dan target cabang kompatibilitas. |
| D5 | Riwayat perubahan | `audit_events` | Pelaku, waktu, tindakan, dan snapshot sebelum/sesudah perubahan. Timeline detail peluang membaca audit yang relevan. |

Penyimpanan ini merupakan pengelompokan **logis**, bukan lima tabel fisik. Detail struktur database tersedia di [DESAIN-DATABASE.md](DESAIN-DATABASE.md). Tabel infrastruktur Laravel dan `request_receipts` tidak ditampilkan sebagai penyimpanan bisnis pada DFD ini. Receipt menangani replay request, bukan sumber realisasi atau laporan.

## DFD Level 2 — proses 3.0 Kelola pipeline

Level 2 merinci proses pipeline karena mencakup pencatatan sampai closing. Proses 1.0, 2.0, 4.0, dan 5.0 tetap dijelaskan pada Level 1.

| Subproses | Masukan pengguna | Transformasi dan penyimpanan | Keluaran pengguna |
| --- | --- | --- | --- |
| 3.1 Sajikan daftar dan detail | Kriteria pencarian/filter atau ID peluang. | Membaca D1, D2, D3, dan D5; menyaring akses serta menyusun detail/timeline. | Daftar, detail, penugasan, dan timeline peluang. |
| 3.2 Catat peluang baru | Nasabah, segmentasi, produk, PIC, nominal, status minat, tanggal, tindak lanjut, dan catatan. | Memvalidasi PIC/produk/divisi melalui D1/D2; menulis peluang `Active` dan penugasan awal ke D3; menulis audit ke D5. | Peluang baru atau hasil validasi. |
| 3.3 Ubah peluang dan PIC | ID, isian perubahan, dan versi record. | Membaca D1/D2/D3; memeriksa akses, versi, dan outcome; memperbarui peluang dan penugasan pada D3; mencatat audit pada D5. | Peluang terbaru dengan versi baru atau hasil validasi/konflik. |
| 3.4 Selesaikan tindak lanjut | ID peluang dan versi record. | Membaca D3; memeriksa peluang aktif, jadwal, dan versi; memperbarui status penyelesaian/versi pada D3; menulis audit pada D5; membaca identitas PIC dari D1 dan produk/divisi dari D2 untuk hasil. | Hasil penyelesaian atau hasil validasi/konflik. |
| 3.5 Tutup peluang Won / Lost | ID, Won/Lost, tanggal closing, realisasi atau alasan Lost, catatan bila dikirim, dan versi. | Membaca D3; memeriksa akses, versi, dan ketentuan closing; menyimpan hasil serta realisasi pada D3; menulis audit pada D5; membaca identitas PIC dari D1 dan produk/divisi dari D2 untuk hasil. | Hasil closing atau hasil validasi/konflik. |

Keseimbangan dengan proses 3.0 dipertahankan:

- Masukan gabungan lima subproses adalah paket **Data dan permintaan pipeline**.
- Keluaran gabungannya adalah paket **Hasil dan informasi pipeline**.
- Penyimpanan yang diakses tetap **D1, D2, D3, D5**; Level 2 tidak menambahkan entitas atau penyimpanan di luar batas proses induk.
- Nama nasabah, angka, tanggal, versi, catatan, serta filter merupakan rincian paket induk, bukan aliran batas sistem baru.

## DFD Level 3 — proses 3.5 Tutup peluang Won / Lost

Level 3 menguraikan **proses 3.5 pada Level 2** menjadi proses 3.5.1–3.5.5. Rincian mengikuti `OpportunityController::close`, pemeriksaan akses dalam `AuthorizesDivision`, dan pencatatan `WritesAudit`. Diagram ini merinci closing; subproses Level 2 lainnya tetap dijelaskan pada diagram induk.

| Subproses | Masukan | Pengolahan dan penyimpanan | Keluaran |
| --- | --- | --- | --- |
| 3.5.1 Periksa peluang dan versi | Paket **Hasil closing, tanggal, nilai / alasan, versi** dari E1/E2, termasuk ID pada alamat request; peluang dan versi saat ini dari D3. | Mengambil peluang sesuai akses divisi dengan row lock, memastikan masih `Active`, memeriksa bentuk isian, tanggal closing, serta kecocokan versi. | Data closing terverifikasi beserta peluang awal ke 3.5.2; hasil validasi/akses/konflik ke E1/E2 bila ditolak. |
| 3.5.2 Validasi Won / Lost | Data closing terverifikasi dan peluang awal. | Won: realisasi lebih dari nol, tidak melebihi nominal, dan alasan Lost dikosongkan. Lost: alasan wajib dan realisasi dinormalisasi menjadi nol. | Data closing valid dan snapshot awal ke 3.5.3; hasil validasi Won/Lost ke E1/E2 bila ditolak. |
| 3.5.3 Simpan hasil closing | Data closing valid dan snapshot awal. | Memperbarui outcome, realisasi, tanggal, alasan Lost, catatan bila dikirim, pelaku pembaruan, dan versi pada peluang yang sama di D3. | Data **Won / Lost, realisasi, tanggal, catatan** ke D3, termasuk alasan, pelaku, dan versi; snapshot sebelum/sesudah serta pelaku ke 3.5.4. |
| 3.5.4 Catat audit closing | Snapshot sebelum/sesudah dan pelaku. | Membentuk audit `closed_won` / `closed_lost`, identitas peluang, waktu, dan sumber `api`. Audit disimpan pada D5 dalam transaksi yang sama dengan perubahan D3. | Paket **Audit closing Won / Lost** ke D5; data hasil closing tersimpan ke 3.5.5. |
| 3.5.5 Sajikan hasil closing | Data hasil closing tersimpan; identitas PIC dari D1; nama produk dan divisi dari D2. | Menyusun data peluang hasil closing beserta relasinya untuk tampilan. Respons sukses diberikan setelah transaksi berhasil. | Hasil closing dan versi baru ke E1/E2. |

Panah antarproses membawa data yang dijelaskan pada tabel, bukan perintah, keputusan Ya/Tidak, atau urutan kontrol. Pemeriksaan, penyimpanan peluang, dan audit merupakan satu transaksi; kegagalan penulisan atau audit membatalkan perubahan sehingga hasil closing sukses tidak disajikan.

Keseimbangan dengan proses induk **3.5**:

- Masukan pengguna tetap satu paket closing dari E1/E2. ID peluang berasal dari alamat request, sedangkan outcome, tanggal, nilai/alasan, versi, dan catatan bila dikirim berasal dari isian.
- Keluaran ke pengguna adalah rincian dari **Hasil closing / hasil validasi**: hasil closing dengan versi baru atau hasil validasi/akses/konflik.
- Pembacaan D3 tetap **Peluang aktif dan versi saat ini**. Penulisan D3 tetap **Won / Lost, realisasi, tanggal, catatan**; penulisan D5 tetap **Audit closing Won / Lost**.
- Pembacaan referensi D1 dan D2 pada 3.5.5 sesuai pemuatan `division`, `pic`, dan `product` pada controller.
- Tidak ada entitas atau penyimpanan baru: hanya **E1, E2, D1, D2, D3, D5**, sama dengan batas proses 3.5. Snapshot dan pelaku diteruskan sebagai paket internal.
- D3 mengelompokkan peluang dan penugasan, tetapi closing hanya mengubah `opportunities`; closing tidak membuat penugasan baru. D5 menerima record `audit_events`.

## Aturan yang memengaruhi makna data

- Pencatatan baru selalu menghasilkan `Active`. `Cold/Warm/Hot` adalah status minat, terpisah dari outcome `Active/Won/Lost`.
- Penyelesaian tindak lanjut mempertahankan outcome aktif. Perubahan jadwal melalui perubahan peluang dapat mereset status penyelesaiannya.
- Won memerlukan realisasi lebih dari nol dan tidak melebihi nominal peluang. Lost memerlukan alasan dan menyimpan realisasi nol. Tanggal closing berada antara tanggal pencatatan dan hari ini.
- Closing bersifat final. Peluang Won/Lost tetap berada di D3; History adalah tampilan dari data tersebut, bukan penyimpanan tambahan.
- Realisasi dana laporan dihitung dari Won berdasarkan tahun `closed_date`. Tidak ada input realisasi dana terpisah pada proses 4.0.
- Realisasi layanan UNIT dicatat manual sebagai total bulanan di D4. CMS memiliki scope `shared` dan dihitung sekali; angka unit tidak dijumlahkan dengan nominal dana.
- Peluang aktif dan tindak lanjut mencakup seluruh tahun. Tren nominal berdasarkan bulan pencatatan dan realisasi berdasarkan bulan closing, bukan snapshot saldo historis.
- Ringkasan dana dihitung backend; data layanan dan beberapa filter/rekap tampilan juga disusun frontend dari data API yang sudah dibatasi scope. Proses 5.0 adalah fungsi logis lintas lapisan tersebut.
- Penulisan bisnis dan audit berada dalam transaksi. Pemeriksaan versi menolak penimpaan perubahan; `request_receipts` menjaga retry dengan `Idempotency-Key` agar tidak menambah record/audit ganda. Mekanisme teknisnya dirinci dalam [ARSITEKTUR.md](ARSITEKTUR.md) dan [alur-penyimpanan.mmd](alur-penyimpanan.mmd).

## Acuan implementasi dan regenerasi

Acuan: `src/backend/routes/api.php`, `AuthController`, `LookupController`, `OpportunityController`, `TargetController`, `ReportController`, `DashboardReport`, `AuthorizesDivision`, `WritesAudit`, `IdempotentWrite`, serta `src/frontend/src/composables/usePipeline.js`.

Dari direktori utama proyek:

```powershell
python src/docs/desain-sistem/scripts/build-dfd.py
node src/docs/desain-sistem/scripts/render-dfd.mjs
```

Pembentuk diagram memakai Python standar. Renderer memakai Playwright dan Microsoft Edge lokal seperti renderer dokumentasi yang sudah tersedia. Spesifikasi logis berada di [scripts/build-dfd.py](scripts/build-dfd.py); komponen gambar, tata letak cetak, dan penampil berada di [scripts/dfd_layout.py](scripts/dfd_layout.py). Berkas Mermaid disediakan untuk penyuntingan alternatif; label ringkas pada gambar dijabarkan dalam kamus aliran di atas.
