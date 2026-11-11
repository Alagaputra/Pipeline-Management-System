# Arsitektur aplikasi — Pipeline Funding Management

Dokumentasi implementasi per **19 Oktober 2026**. Diagram utama: [PNG](arsitektur-sistem.png), [SVG](arsitektur-sistem.svg), dan [Mermaid](arsitektur-sistem.mmd).

Ditinjau ulang **20 Oktober 2026** terhadap kode dan katalog PostgreSQL aktif. Temuan, hasil tes terbaru, serta batas kesiapan produksi dicatat di [audit materi ujian](../materi-ujian/AUDIT-PROFESIONAL.md).

## Pola arsitektur

Aplikasi menggunakan pola **client–server tiga lapis**: antarmuka Vue.js pada browser, logika aplikasi pada Laravel REST API, dan penyimpanan pada PostgreSQL. Backend merupakan satu aplikasi Laravel dengan controller, layanan laporan, model, middleware, dan pencatatan audit. Batas tiga lapis ini merupakan pembagian tanggung jawab, bukan tiga layanan microservice yang dideploy terpisah.

| Lapis | Komponen nyata | Tanggung jawab |
| --- | --- | --- |
| Presentasi | Vue.js, Vue Router, komponen halaman/formulir, Chart.js | Tampilan, input, validasi awal, navigasi, dan visualisasi |
| State dan komunikasi browser | `usePipeline`, `useSession`, `services/api.js` | Sesi, data halaman, scope/tahun, HTTP JSON, timeout, dan identitas retry |
| Aplikasi/API | Routes, Sanctum, `IdempotentWrite`, controller, `DashboardReport`, `WritesAudit` | Autentikasi, otorisasi, validasi final, transaksi, perhitungan laporan, dan audit |
| Akses data | Eloquent Models dan query Laravel | Query, relasi, row lock, serta pemeriksaan versi |
| Penyimpanan | PostgreSQL | Record peluang/target, constraint relasional, token hash, audit, dan receipt |

## Alur permintaan

1. Pengguna membuka halaman melalui Vue Router dengan hash route, misalnya `/#/pipeline`.
2. Login mengirim username/password ke `/api/login`; Laravel memeriksa hash password dan menghasilkan bearer token Sanctum. Login saat ini menghapus token lama akun tersebut sebelum membuat token baru.
3. Token disimpan di `localStorage` bila Ingat saya dipilih, atau `sessionStorage` untuk sesi browser. Data operasional dimuat dari API dan tidak menggunakan browser sebagai database utama.
4. `services/api.js` mengirim `Authorization: Bearer ...`. Operasi simpan data bisnis dari antarmuka menyertakan `Idempotency-Key` berupa UUID; login/logout tidak memakai key ini.
5. Sanctum memeriksa token. `IdempotentWrite` melewati request baca dan menangani replay/transaksi untuk request tulis yang memiliki key.
6. Controller memeriksa divisi, produk, PIC, tanggal, nominal, hasil closing, dan versi record. Pembatasan akses di backend tetap berlaku walaupun parameter browser diubah.
7. Eloquent/query membaca atau menulis PostgreSQL. Penulisan bisnis dan audit berada dalam transaksi yang sama; satu formulir target berisi banyak produk/bulan tidak boleh tersimpan sebagian.
8. Backend mengembalikan JSON. `usePipeline` memperbarui state dan ringkasan, lalu Chart.js merender grafik dari data laporan tersebut di browser.

Alur rinci transaksi dan retry tersedia pada [alur-penyimpanan.mmd](alur-penyimpanan.mmd).

## Pembagian modul backend

| Berkas/komponen | Fungsi |
| --- | --- |
| `routes/api.php` | Mendefinisikan endpoint API; login dibatasi percobaannya, endpoint data memakai Sanctum |
| `AuthController` | Login, identitas pengguna, logout |
| `LookupController` | Master divisi, produk, dan PIC |
| `OpportunityController` | Daftar/detail peluang, tambah/ubah, penyelesaian tindak lanjut, closing Won/Lost |
| `TargetController` | Target tahunan, batch target/realisasi, serta endpoint kompatibilitas bulanan/cabang |
| `ReportController` | Laporan Dashboard, Tim, dan peluang yang pernah ditangani PIC |
| `DashboardReport` | Ringkasan target/realisasi, distribusi status, tindak lanjut, tren bulanan |
| `AuthorizesDivision` | Batas divisi dan visibilitas peluang |
| `IdempotentWrite` | Menyimpan atau memutar ulang hasil request sukses berdasarkan pengguna/key/hash |
| `WritesAudit` | Snapshot perubahan dan pelakunya pada `audit_events` |
| Model Eloquent | Pemetaan tabel dan relasi |

## Endpoint utama

| Metode | Endpoint | Kegunaan |
| --- | --- | --- |
| POST | `/api/login` | Autentikasi |
| GET / POST | `/api/me`, `/api/logout` | Identitas / keluar |
| GET | `/api/divisions`, `/api/products`, `/api/pics` | Master |
| GET / POST | `/api/opportunities` | Daftar / pencatatan peluang |
| GET / PATCH | `/api/opportunities/{id}` | Detail beserta timeline / perubahan |
| POST | `/api/opportunities/{id}/follow-up-completion` | Selesaikan tindak lanjut |
| POST | `/api/opportunities/{id}/closing` | Closing, catatan, dan realisasi atomik |
| GET | `/api/targets?year=YYYY` | Target sesuai scope pengguna |
| POST | `/api/targets/batch` | Simpan satu formulir target dana/layanan dalam satu transaksi |
| GET | `/api/dashboard?year=YYYY` | Ringkasan dan tren |
| GET | `/api/team` | Rekap PIC |
| GET | `/api/pics/{id}/opportunities` | Peluang pernah ditangani PIC |

Endpoint kompatibilitas untuk target per produk, realisasi per bulan, dan target cabang masih tersedia pada `routes/api.php`.

## Hak akses dan cakupan produk

| Aspek | PIC Komersil | PIC Konsumer | Head Funding |
| --- | --- | --- | --- |
| Data peluang | Divisi sendiri, termasuk PIC lain dalam divisi | Divisi sendiri, termasuk PIC lain dalam divisi | Kedua divisi; filter tersedia |
| Produk dana | Tabungan, Giro, Deposito | Tabungan, Deposito | Mengikuti divisi yang dipilih |
| Layanan | CMS bersama | Bale Syariah, QRIS, CMS bersama | Gabungan / mengikuti divisi |
| Ubah peluang dan target dana | Divisi sendiri | Divisi sendiri | Di UI harus memilih satu divisi |
| Ubah CMS | Diizinkan | Diizinkan | Diizinkan, termasuk tampilan gabungan |
| Ubah hasil closing | Tidak tersedia | Tidak tersedia | Tidak tersedia |

Tidak ada role administrator terpisah pada model role yang dipakai UI sekarang. Head dapat memantau gabungan; controller tetap memeriksa resource dan scope setiap penulisan.

## Perhitungan dan integritas

- Peluang aktif dan tindak lanjut mencakup semua periode. Realisasi dana mengikuti tahun `closed_date` dengan hasil Won; bukan nominal peluang atau tahun pencatatan.
- Tren bulanan menjumlahkan nominal menurut `recorded_date` dan realisasi Won menurut `closed_date`. Ini bukan snapshot historis saldo pipeline.
- Grafik dan angka utama berasal dari perhitungan backend. Halaman Tim juga mengolah data scoped yang telah dimuat ke browser untuk kebutuhan tampilan/filter.
- Target layanan bersatuan UNIT tidak masuk penyebut pencapaian dana IDR. CMS menggunakan satu scope `shared` untuk kedua divisi.
- Version conflict menghasilkan HTTP 409. FK dan UNIQUE menjaga integritas struktur; validasi API melengkapi aturan bisnis.
- `request_receipts` menyimpan hasil sukses dan hash method/path/body per pengguna/key. Pengulangan identik tidak menambah record, versi, atau audit. Payload berbeda pada key yang sama ditolak.
- Respons pemuatan lama hanya diterapkan bila pengguna, divisi, tahun, dan identitas permintaan masih sesuai.
- Sesi 401 diarahkan ke login; logout lokal tetap selesai ketika koneksi gagal. Formulir berubah dilindungi guard navigasi dan `beforeunload`.

## Catatan hasil peninjauan

- Aplikasi menggunakan mode token API Sanctum, bukan autentikasi SPA berbasis cookie. Dokumentasi resmi Sanctum merekomendasikan autentikasi sesi cookie untuk SPA milik sendiri; ini merupakan pertimbangan penguatan sebelum produksi, bukan fitur yang sudah diterapkan.
- `config/sanctum.php` menetapkan expiration NULL. Token tidak mempunyai batas umur global otomatis pada konfigurasi ini; login baru mencabut token lama dan logout server mencabut token aktif. Pesan UI “sesi berakhir” juga dapat disebabkan token dicabut/tidak valid, bukan bukti adanya timeout sesi tertentu.
- Validasi frontend memakai bilangan aman JavaScript untuk nominal/target; validasi integer API belum menetapkan batas yang sama dan agregat juga perlu kebijakan presisi. Jangan menyamakan kapasitas BIGINT PostgreSQL dengan batas aman Number JavaScript.
- Pada pemeriksaan lokal: timezone aplikasi Asia/Jakarta, koneksi database Asia/Bangkok. Kolom timestamp without time zone tidak menyimpan nama zona/offset; konvensi penulisan dan pembacaan waktu perlu dipastikan untuk deployment.

## Susunan lokal dan deployment

```text
Browser
  └─ http://127.0.0.1:5173  Vue + Vite
       └─ /api (proxy Vite)
            └─ http://127.0.0.1:8000  Laravel
                 └─ PostgreSQL lokal (konfigurasi proyek)
```

Port 5432 pada gambar adalah port PostgreSQL lokal standar yang digunakan konfigurasi proyek. `PIPELINE_API_TARGET` dapat mengganti tujuan proxy. Suite browser menggunakan frontend 5174, API 8001, dan database pengujian terpisah.

Vite dan `artisan serve` pada diagram merupakan susunan pengembangan lokal, bukan pernyataan bahwa deployment publik sudah berjalan. Contoh `.env.production.example` tersedia, tetapi diagram ini tidak menambahkan Nginx, Docker, Redis, microservice, atau integrasi sistem inti bank yang tidak dibutuhkan alur saat ini. Tabel antrean Laravel tersedia; simpan peluang dan target tidak menunggu pekerja antrean.

## Acuan kode

- `src/frontend/src/router/index.js`, `src/frontend/src/main.js`
- `src/frontend/src/composables/usePipeline.js`, `useSession.js`, `useUnsavedChanges.js`
- `src/frontend/src/services/api.js`, `src/frontend/vite.config.js`
- `src/backend/routes/api.php`, `src/backend/app/Http/Controllers/`
- `src/backend/app/Http/Middleware/IdempotentWrite.php`
- `src/backend/app/Services/DashboardReport.php`, `src/backend/app/Support/WritesAudit.php`
- `src/backend/app/Models/`, `src/backend/database/migrations/`, `src/backend/database/seeders/DatabaseSeeder.php`
