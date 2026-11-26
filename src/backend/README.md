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

Autentikasi memakai bearer token Laravel Sanctum dengan masa berlaku 480 menit (8 jam). Atur `SANCTUM_EXPIRATION` untuk mengubah batas umur (minimal 1 menit); token lama tanpa `expires_at` juga mengikuti batas ini. Setiap request terproteksi memeriksa akun aktif serta peran/divisi valid sebelum controller dan replay idempotensi. PIC harus memiliki divisi valid; peran yang diizinkan adalah `pic` dan `head`. Penonaktifan atau perubahan peran/divisi melalui model `User` mencabut seluruh token. Penonaktifan atau akses tidak valid yang diatur lewat query database langsung ditolak dan token dicabut pada akses API berikutnya. Login ulang mencabut seluruh token lama dan logout mencabut token saat ini.

Sesudah deployment perubahan konfigurasi, bangun ulang cache konfigurasi (`php.cmd artisan config:cache`) jika server menggunakannya. Perubahan ini tidak memerlukan seed ulang dan tidak mengubah kredensial akun yang sudah ada.

## Laporan dan riwayat

Total laporan dijumlahkan dengan integer presisi penuh. Nilai agregat sampai
9.007.199.254.740.991 dikirim sebagai JSON number; nilai yang lebih besar dikirim
sebagai string desimal agar tidak dibulatkan oleh JavaScript. Ini berlaku pada
nominal aktif/Hot, realisasi, target, sisa target, tren bulanan, dan nominal aktif
endpoint tim. Contoh: `"active_nominal":"9007199254740993"`. Persentase tetap
berupa angka pecahan; batas input per field tidak berubah. Respons pembuatan
peluang selalu menyertakan `version: 1` untuk penyimpanan berikutnya.

Jumlah peluang dan nominal pada endpoint tim mengikuti divisi pengguna yang
membaca, termasuk setelah PIC pindah divisi. Head tetap dapat melihat gabungan
lintas divisi.

`GET /api/dashboard?year=YYYY&division_id=ID` menghitung ringkasan, target/realisasi per produk, distribusi status, prioritas follow-up, dan tren bulanan di backend. PIC selalu dibatasi divisinya; Head Funding dapat memfilter divisi.

Pada laporan dashboard, `realized_units` menghitung peluang layanan Won pada tahun dan divisi laporan. `service_realizations` menyediakan jumlah Won per produk dan bulan untuk pencapaian target layanan. CMS menggunakan cakupan bersama kedua divisi pada pencapaian target. Setiap produk dana di `summary` menyertakan `monthly_realizations` berdasarkan bulan closing. Frontend menggabungkan data laporan dengan target bulanan dan realisasi unit manual yang sudah tersimpan.

`GET /api/opportunities/{id}` menyertakan `timeline` audit dengan pelaku dan perubahan. Target tahunan dapat disimpan tanpa mengirim target bulanan; data bulanan lama tetap dipertahankan.

`GET /api/pics/{id}/opportunities` membatasi peluang dan riwayat penugasan pada divisi pengguna yang membaca. Memindahkan PIC ke divisi lain tidak membuka akses ke peluang divisi lamanya. Head tetap dapat membaca lintas divisi.

`POST /api/targets/batch` menerima `{scope, year, targets: [{product, target_value, version, monthly?}]}`. Untuk layanan, `monthly` berisi 12 objek `{month, target_value, units, version}`. Semua perubahan target, realisasi, dan audit berada dalam satu transaksi; konflik versi menghasilkan 409 tanpa perubahan sebagian.

`POST /api/opportunities/{id}/closing` menerima catatan opsional bersama hasil closing dan realisasi. Untuk produk layanan, Won menghasilkan satu unit dan Lost menghasilkan nol. Untuk produk dana, realisasi Won harus berupa rupiah bulat lebih dari nol dan boleh melebihi nominal potensi. Contoh: potensi Rp1 miliar dapat ditutup dengan realisasi Rp1,2 miliar; nominal potensi tetap Rp1 miliar, sedangkan laporan menghitung realisasi Rp1,2 miliar. Setiap permintaan tulis dapat memakai UUID pada header `Idempotency-Key`. Server menyimpan hasil sukses pada `request_receipts` di transaksi yang sama. Replay memerlukan pengguna, key, metode, URI beserta query, payload, dan konteks peran/divisi yang sama. Ketidaksesuaian menghasilkan 409. Header ini tidak diwajibkan untuk klien versi lama, tetapi selalu dikirim pada penyimpanan dari antarmuka terbaru.

Nama nasabah maksimal 160 karakter, catatan 5.000 karakter, dan alasan Lost 2.000 karakter. Produk unit nonaktif tidak menerima penulisan realisasi melalui endpoint `PUT /api/unit-realizations/{scope}/{product}/{year}/{month}`. Lihat langkah migration pada [memperbarui instalasi](#memperbarui-instalasi). Contoh konfigurasi server publik ada di `.env.production.example`; `.env` lokal tetap dipakai untuk pengembangan.

## Menyalin data MySQL lama

Jalankan migration PostgreSQL tanpa seed terlebih dahulu. Database tujuan harus masih kosong; perintah menolak menimpa tabel yang sudah berisi data.
```powershell
.\php.cmd artisan migrate
.\php.cmd artisan pipeline:import-mysql --database=pipeline_funding --username=root
```

Sumber MySQL tetap utuh. Jika sumber memakai password, gunakan variabel lingkungan `LEGACY_MYSQL_PASSWORD`. Token dan sesi lama tidak disalin; login kembali setelah perpindahan.

## Memperbarui instalasi

Seed ulang mempertahankan akun, status produk, atribut master, dan relasi
produk/divisi yang sudah ada. Relasi bawaan hanya dibuat untuk divisi baru.
Pembaruan perhitungan eksak memakai dependensi `brick/math` yang tercantum pada
lockfile; tidak memerlukan migration tambahan di luar migration akses berikut.

Setelah memperbarui sumber aplikasi, pasang dependensi sesuai lockfile dan
bangun frontend dari direktori utama proyek:

```powershell
npm.cmd --prefix src/frontend ci
npm.cmd run build
```

Jalankan dari direktori `src/backend` sebelum membuka kembali akses aplikasi:

```powershell
composer install --no-dev --optimize-autoloader
.\php.cmd artisan migrate --force
```

Migration `2026_11_20_000001_add_authorization_context_to_request_receipts`
menambahkan `authorization_context` pada `request_receipts` tanpa menghapus data.
Tidak diperlukan seed ulang atau pengosongan database. Jika memakai cache
konfigurasi, bangun ulang dengan `.\php.cmd artisan config:cache`.

Frontend yang diperbarui mempertahankan draft dan payload retry jika respons
sukses berisi JSON atau bentuk data yang tidak valid. Respons sesi lama
diabaikan; retry closing tetap mencapai receipt meskipun refresh sudah menemukan
hasil Won/Lost tersimpan. Total besar dipertahankan secara eksak di frontend;
angka pecahan hanya digunakan untuk skala grafik dan persentase. Klien API lain
perlu mempertahankan string desimal laporan atau memakai integer presisi penuh.

Receipt lama tanpa konteks, atau receipt dari peran/divisi yang sudah berubah,
menghasilkan 409. Periksa data terbaru sebelum menyimpan kembali; jangan otomatis
mengganti request key untuk operasi yang hasilnya belum pasti. Perubahan peran atau
divisi melalui model `User` mencabut token, sehingga pengguna harus login kembali.
Akun PIC tanpa divisi valid atau dengan peran tidak dikenal ditolak dengan 401.

Riwayat PIC mengikuti divisi pemanggil saat ini. Produk unit nonaktif menolak
penulisan realisasi. API membatasi nominal, realisasi, target, dan unit maksimal
9.007.199.254.740.991 agar sesuai integer aman frontend; input yang lebih besar
ditolak 422 dan data lama tidak diubah otomatis. Form target memakai versi saat
dibuka; pilih tahun melalui filter halaman sebelum membuka formulir.

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

Tes regresi `AccessBoundaryTest` mencakup riwayat PIC setelah pindah divisi,
akun tanpa divisi/peran valid, pencabutan token saat perubahan akses, penolakan
receipt lama atau konteks berbeda, produk unit nonaktif, serta batas angka.
Hasil verifikasi terakhir tersedia pada [README utama](../../README.md#build-dan-pengujian).
