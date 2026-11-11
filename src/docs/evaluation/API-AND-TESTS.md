# Rancangan API dan rencana pengujian

**Seluruh endpoint berikut adalah usulan, belum tersedia di proyek.** Nama route Laravel final dapat disesuaikan saat implementasi setelah review model dan kewenangan. API menggunakan JSON, nominal rupiah berupa string digit, unit berupa bilangan bulat, dan tanggal bisnis `YYYY-MM-DD`.

## Endpoint awal yang diusulkan

| Method / path | Kegunaan | Akses |
|---|---|---|
| POST `/login`, POST `/logout`, GET `/api/me` | Login sesi, logout, identitas pengguna | Login publik; sisanya sesi valid |
| GET `/api/divisions`, GET `/api/products`, GET `/api/pics` | Opsi yang diizinkan untuk pengguna | Disaring server sesuai akses |
| GET `/api/opportunities` | List aktif/closed, search, filter, sort, pagination | Divisi sendiri atau Head |
| POST `/api/opportunities` | Membuat peluang | Satu divisi; PIC dan produk harus cocok |
| GET/PATCH `/api/opportunities/{id}` | Detail dan perubahan data aktif | Record divisi yang diizinkan; PATCH memerlukan version |
| POST `/api/opportunities/{id}/follow-up-completion` | Menandai selesai follow-up | Active dan follow-up tersedia |
| POST `/api/opportunities/{id}/closing` | Closing Won/Lost | Active, version cocok; perubahan + audit dalam transaksi |
| GET `/api/targets?scope=...&year=...` | Target dan rekap dana/unit | Scope yang diizinkan; shared CMS sekali |
| PUT `/api/targets/{scope}/{product}/{year}` | Ganti target tahunan dan 12 target bulanan | PIC divisi sendiri; Head satu divisi; semua aktor untuk CMS shared |
| PUT `/api/unit-realizations/{scope}/{product}/{year}/{month}` | Ganti total realisasi unit sebulan | Mengikuti produk dan scope; version untuk mencegah overwrite |
| GET `/api/dashboard?scope=...&year=...&month=...` | Ringkasan server untuk Dashboard | Read-only, mengikuti akses |
| GET `/api/team?scope=...&year=...` | Statistik per PIC | Read-only, mengikuti akses |
| GET `/api/pics/{id}/opportunities` | History penanganan PIC | Divisi yang diizinkan |

Tidak perlu tabel atau endpoint CRUD terpisah untuk History: gunakan daftar opportunity dengan outcome Won/Lost. Target Bekasi memerlukan kontrak tambahan setelah definisi bisnisnya disepakati; jangan menyamarkannya sebagai produk dana.

## Contoh permintaan closing

```json
{
  "outcome": "Won",
  "realization": "700000000",
  "closed_date": "2026-09-14",
  "version": 3
}
```

Server mengambil identitas pelaku dari sesi, bukan mempercayai `updated_by`, role, atau divisi yang dikirim browser. Nama nasabah dapat berupa teks; product_id/pic_id memakai identitas master. Response mengembalikan record hasil simpan dan version baru. Untuk Lost, realisasi nol dan `lost_reason` wajib diisi.

## Contoh target dan realisasi

```json
{
  "target_value": "1000000000",
  "monthly": [
    { "month": 1, "target_value": "100000000" },
    { "month": 2, "target_value": "50000000" }
  ],
  "version": 2
}
```

Untuk PUT target, form produksi mengirim seluruh 12 bulan; contoh hanya memendekkan daftar. Bulan yang belum diisi bernilai nol. Tahunan tetap input mandiri seperti prototipe. Jika record belum ada, gunakan `version: 0`; jika sudah ada, cocokkan versi database. Record target tahunan nol boleh dibuat untuk menampung realisasi unit meski target belum ditetapkan.

Untuk CMS: scope `shared`, product `cms`. `PUT /api/unit-realizations/shared/cms/2026/1` menerima `{ "units": 9, "version": 1 }`. Nilai 9 mengganti total Januari, bukan menambah 9. Realisasi dana tidak menggunakan endpoint ini; asalnya closing Won.

## Respons dan kegagalan

- `401`: sesi tidak valid; arahkan ke login, jangan tampilkan sukses simpan.
- `403`: pengguna tidak boleh melakukan tindakan itu. Untuk ID record di luar cakupan, usulan respons `404` agar record tidak terungkap.
- `422`: input salah; field error tampil di drawer dan input tetap tersedia.
- `409`: versi record berubah atau opportunity sudah closing; jangan menimpa, minta muat ulang data.
- Gangguan koneksi: tampilkan status belum tersimpan; jangan menganggap gagal kirim berarti pasti gagal commit. Setelah reconnect, ambil record terbaru sebelum mengulangi closing.
- Sukses simpan: response sumber kebenaran adalah server; refresh list dan ringkasan yang terpengaruh.

## Skenario penerimaan

| ID | Skenario | Hasil yang harus diperiksa |
|---|---|---|
| A01 | Login PIC Konsumer, Komersil, Head | Cakupan sesuai akun; username salah/password salah ditolak |
| A02 | PIC mengirim division_id/role milik divisi lain secara manual | Server menolak; tidak bergantung pada kartu yang disembunyikan |
| A03 | Konsumer mencoba membuat Giro | Ditolak pada API dan opsi UI tidak tersedia |
| A04 | QRIS/Bale Syariah pada akun Komersil | Tidak ada di Dashboard/Target; aturan backend data baru mengikuti keputusan produk |
| A05 | Komersil mengubah CMS, Konsumer membaca/mengubahnya | Angka bersama konsisten, audit actor sesuai akun, tidak dihitung dua kali pada Head |
| A06 | Set target dana Januari Rp1 juta | Bulan yang diubah ditampilkan; angka Rp 0,001 M; reload tetap ada |
| A07 | Target tahun berikutnya diisi | Tahun sebelumnya dan divisi lain tidak berubah |
| A08 | Won Rp700 juta dari nominal Rp1 miliar | History terisi, Active berkurang, realisasi bertambah Rp700 juta pada tahun/bulan closing |
| A09 | Won nol/melebihi nominal/tanggal tidak valid; Lost tanpa alasan | Validasi menolak dan record tetap Active |
| A10 | Follow-up selesai | Outcome tetap Active; tidak lagi perlu follow-up untuk jadwal itu |
| A11 | PIC dialihkan sebelum closing | PIC final menerima realisasi; PIC lama tetap memiliki history penanganan |
| A12 | Dua PIC mengedit CMS/opportunity bersamaan | Satu versi baru tersimpan; permintaan stale menerima 409, tanpa silent overwrite |
| A13 | Target unit pecahan/negatif atau bulan 13 | Ditolak; unit tahunan adalah SUM realisasi bulanan |
| A14 | Migrasi v1/v2/v3 | Catatan, outcome, nominal, seluruh tahun/bulan, dan backup utuh; daftar ambigu tidak diimpor diam-diam |
| A15 | Filter Head Semua/Konsumer/Komersil | Dana hanya scope terpilih; CMS shared sekali; dana dan unit tetap terpisah |
| A16 | Tampilan mobile | Tabel bisa digulir dalam wadah, card tidak keluar layar, drawer tetap bisa ditutup |

A01/A03–A11/A13–A16 sebagian telah mempunyai pengujian prototipe, tetapi **kelulusan frontend tidak membuktikan API server aman**. Uji HTTP, transaksi database, conflict, dan otorisasi perlu dibuat setelah Laravel tersedia.

## Batas pengembangan tahap pertama

Usulan tahap pertama mempertahankan lima halaman, tanpa microservices, Docker wajib, impor Excel, master nasabah lengkap, atau pembukaan kembali closing. Pengelolaan akun nyata, kebijakan backup, target cabang, dan otorisasi final perlu disepakati sebelum deployment.
