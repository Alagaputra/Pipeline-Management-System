# Pipeline Management System

Aplikasi pengelolaan pipeline funding, target, tindak lanjut, dan riwayat peluang.
Frontend menggunakan Vue 3 dan Vite; backend menggunakan Laravel, Sanctum, dan PostgreSQL.

## Struktur proyek

- `src/frontend/`: aplikasi, aset ikon, konfigurasi, dan pengujian frontend.
- `src/backend/`: REST API, migration, seeder, dan pengujian backend.
- `src/docs/`: dokumentasi sistem, diagram, dan materi pendukung.
- `Figma/`: referensi desain antarmuka.
- `package.json` di root: pintasan perintah frontend.

## Menjalankan secara lokal

Siapkan Node.js yang mendukung Vite 7, PHP 8.2 atau lebih baru, Composer,
dan PostgreSQL. Panduan backend lengkap ada di [src/backend/README.md](src/backend/README.md).

Dari direktori utama, siapkan backend:

```powershell
cd src/backend
composer install
Copy-Item .env.example .env
```

Isi koneksi PostgreSQL di `.env` dan buat database tujuan, lalu jalankan:

```powershell
.\php.cmd artisan key:generate
.\php.cmd artisan migrate --seed
.\php.cmd artisan serve
```

Pada sistem selain Windows, gunakan `php` sebagai pengganti `.\php.cmd`
dan aktifkan ekstensi PostgreSQL pada PHP. Seeder menyediakan akun demo
untuk pengembangan; lihat panduan backend sebelum menyiapkan server publik.

Di terminal lain, dari direktori utama:

```powershell
npm.cmd --prefix src/frontend ci
Copy-Item src/frontend/.env.example src/frontend/.env
npm.cmd run dev
```

Frontend berjalan di `http://127.0.0.1:5173`; proxy `/api` mengarah ke
backend di `http://127.0.0.1:8000`.

## Build dan pengujian frontend

```powershell
npm.cmd run build
npm.cmd test
```

Panduan tes browser beserta database pengujian terpisah ada di
[panduan frontend](src/frontend/README.md).

## Berkas lokal

`arsip-lokal/` mengumpulkan backup, log, hasil review, cache, serta salinan
frontend lama yang dipindahkan saat perapian. Folder ini diabaikan Git.
Setiap arsip dilengkapi `manifest.json` berisi lokasi asal dan checksum SHA-256.

Dependensi, hasil build, hasil tes, dan konfigurasi `.env` juga diabaikan Git.
Templat `.env.example` dan `.env.production.example` tetap disertakan.

