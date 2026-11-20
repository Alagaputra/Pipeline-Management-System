# Pipeline Funding API

Laravel REST API dengan PostgreSQL untuk Vue di `../frontend`.

## Konfigurasi

Aktifkan PostgreSQL, buat database `pipeline_funding` milik pengguna aplikasi, dan isi `.env`:
```dotenv
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=pipeline_funding
DB_USERNAME=postgres
DB_PASSWORD=
```

Sesuaikan pengguna/password dengan instalasi lokal. Jangan simpan kredensial lokal dalam dokumentasi atau commit.

```powershell
composer install
.\php.cmd artisan key:generate
.\php.cmd artisan migrate --seed
.\php.cmd artisan serve
```

Windows: `php.cmd` mengaktifkan `pdo_pgsql` melalui `php-conf.d/postgresql.ini` tanpa mengubah PHP global. PHP harus menyediakan ekstensi tersebut. Pada platform lain, aktifkan ekstensi melalui instalasi PHP dan gunakan `php artisan`.

API: http://127.0.0.1:8000/api. Pada `APP_ENV=local` atau `testing`, seeder membuat akun `suci`, `cacan`, `dharma`, `nisa`, dan `head` dengan password `demo123` jika belum ada. Seed ulang tidak mengubah akun yang sudah ada. Di produksi atau lingkungan lain, seeder hanya menyiapkan master data tanpa membuat akun demo; sediakan akun produksi secara terpisah. Akun demo lama tidak dihapus otomatis, sehingga kredensialnya perlu diganti atau akunnya dinonaktifkan sebelum penggunaan publik.

Autentikasi memakai bearer token Laravel Sanctum dengan masa berlaku 480 menit (8 jam). Atur `SANCTUM_EXPIRATION` untuk mengubah batas umur (minimal 1 menit); token lama tanpa `expires_at` juga mengikuti batas ini. Setiap request terproteksi memeriksa akun aktif sebelum controller dan replay idempotensi. Penonaktifan melalui model `User` mencabut seluruh token; perubahan langsung di database ditolak dan token dicabut pada akses API berikutnya. Login ulang mencabut seluruh token lama dan logout mencabut token saat ini.

Sesudah deployment perubahan konfigurasi, bangun ulang cache konfigurasi (`php.cmd artisan config:cache`) jika server menggunakannya. Perubahan ini tidak memerlukan seed ulang dan tidak mengubah kredensial akun yang sudah ada.

## Laporan dan riwayat

`GET /api/dashboard?year=YYYY&division_id=ID` menghitung ringkasan, target/realisasi per produk, distribusi status, prioritas follow-up, dan tren bulanan di backend. PIC selalu dibatasi divisinya; Head Funding dapat memfilter divisi.

`GET /api/opportunities/{id}` menyertakan `timeline` audit dengan pelaku dan perubahan. Target tahunan dapat disimpan tanpa mengirim target bulanan; data bulanan lama tetap dipertahankan.

`POST /api/targets/batch` menerima `{scope, year, targets: [{product, target_value, version, monthly?}]}`. Untuk layanan, `monthly` berisi 12 objek `{month, target_value, units, version}`. Semua perubahan target, realisasi, dan audit berada dalam satu transaksi; konflik versi menghasilkan 409 tanpa perubahan sebagian.

`POST /api/opportunities/{id}/closing` menerima catatan opsional bersama hasil closing dan realisasi. Realisasi Won harus berupa rupiah bulat lebih dari nol dan boleh melebihi nominal potensi. Contoh: potensi Rp1 miliar dapat ditutup dengan realisasi Rp1,2 miliar; nominal potensi tetap Rp1 miliar, sedangkan laporan menghitung realisasi Rp1,2 miliar. Setiap permintaan tulis dapat memakai UUID pada header `Idempotency-Key`. Server menyimpan hasil sukses pada `request_receipts` di transaksi yang sama. Pengulangan pengguna/key/payload yang identik mengembalikan hasil tersebut; penggunaan key yang sama untuk payload lain ditolak 409. Header ini tidak diwajibkan untuk klien versi lama, tetapi selalu dikirim pada penyimpanan dari antarmuka terbaru.

Jalankan `php.cmd artisan migrate --force` saat memperbarui instalasi yang sudah ada; migration menambahkan tabel pencatatan permintaan. Tidak diperlukan pengosongan database. Contoh konfigurasi server publik ada di `.env.production.example`; `.env` lokal tetap dipakai untuk pengembangan.

## Menyalin data MySQL lama

Jalankan migration PostgreSQL tanpa seed terlebih dahulu. Database tujuan harus masih kosong; perintah menolak menimpa tabel yang sudah berisi data.
```powershell
.\php.cmd artisan migrate
.\php.cmd artisan pipeline:import-mysql --database=pipeline_funding --username=root
```

Sumber MySQL tetap utuh. Jika sumber memakai password, gunakan variabel lingkungan `LEGACY_MYSQL_PASSWORD`. Token dan sesi lama tidak disalin; login kembali setelah perpindahan.

## Pengujian

`php.cmd artisan test` memakai SQLite in-memory sebagai default. Untuk menguji PostgreSQL, buat database terpisah `pipeline_funding_test`, lalu:
```powershell
$env:DB_CONNECTION='pgsql'
$env:DB_DATABASE='pipeline_funding_test'
.\php.cmd artisan test
Remove-Item Env:DB_CONNECTION
Remove-Item Env:DB_DATABASE
```

Gunakan hanya database pengujian: suite mengelola ulang skema dan fixture.
