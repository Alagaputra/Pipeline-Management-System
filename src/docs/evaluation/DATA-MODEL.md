# Model data dan ERD

**Status: sudah diimplementasikan dengan migration Laravel dan MySQL.** Diagram visual tersedia di [index.html](index.html); sumber yang dapat diedit ada di [erd.mmd](erd.mmd).

## Sumber data prototipe sebelum integrasi

```text
funding-pipeline-v3
  rows[]                       opportunity, PIC berupa nama, divisi berupa teks
  targets[divisi][tahun]        target produk dana, bekasi, monthly[1..12]
  unitTargets[divisi][tahun]    Bale Syariah / QRIS: target dan monthly
  unitTargets.shared[tahun]    CMS: target dan monthly

funding-demo-session            ID akun demo dan atribut akun
data/access.js                 daftar akun, divisi, dan produk dalam kode
```

Objek browser tersebut adalah format prototipe lama dan tidak lagi dibaca aplikasi. Data operasional sekarang berada di tabel MySQL. Nama nasabah tetap berupa teks bebas; tidak ada master nasabah, sehingga nama yang sama belum otomatis dianggap nasabah yang sama.

## Struktur yang diterapkan

PK = primary key/identitas unik. FK = foreign key/rujukan ke tabel lain. `1 → 0..N` berarti satu record bisa memiliki nol atau banyak record terkait. `NULL` berarti nilai memang boleh tidak diketahui/tidak berlaku.

| Tabel | Kolom utama | Fungsi dan batasan |
|---|---|---|
| `divisions` | `id` PK, `code` UNIQUE, `name` | Dua divisi: Konsumer, Komersil. |
| `users` | `id` PK, `division_id` FK nullable, `username` UNIQUE, `name`, `password_hash`, `role`, `is_active` | Role `pic` wajib punya divisi; `head` tanpa divisi. Username stabil, nama tampilan tidak menjadi kunci. |
| `products` | `id` PK, `code` UNIQUE, `name`, `measure`, `is_active` | `measure`: `IDR` untuk Tabungan/Giro/Deposito, `UNIT` untuk Bale Syariah/QRIS/CMS. CMS tetap satu produk. |
| `division_products` | `division_id` PK/FK, `product_id` PK/FK | Produk yang boleh digunakan tiap divisi. PK gabungan mencegah pasangan ganda. Usulan data baru: Konsumer Tabungan/Deposito/Bale Syariah/QRIS/CMS; Komersil Tabungan/Giro/Deposito/CMS. |
| `opportunities` | `id` PK, `legacy_id` UNIQUE nullable, `division_id` FK, `product_id` FK, `pic_id` FK, `customer_name`, `segment`, `recorded_date`, `nominal`, `interest_status`, `outcome`, `follow_up_date`, `follow_up_completed`, `notes`, `closed_date`, `realization`, `lost_reason`, `created_by` FK nullable, `updated_by` FK nullable, `version` | Hanya produk IDR. Tetap satu record ketika closing. Simpan tanggal/angka sebagai data, bukan string tampilan M. |
| `opportunity_assignments` | `id` PK, `opportunity_id` FK, `pic_id` FK, `assigned_at` nullable, `unassigned_at` nullable, `changed_by` FK nullable, `source` | Riwayat PIC; `pic_id` pada opportunity menentukan PIC saat ini/final. Timestamp yang tidak diketahui saat migrasi dibiarkan NULL. |
| `target_scopes` | `code` PK, `division_id` FK nullable, `label` | Tepat tiga scope awal: `konsumer`, `komersil`, `shared`. Scope shared tidak mempunyai divisi. CMS memiliki satu target shared, tidak disalin ke masing-masing divisi. |
| `annual_targets` | `id` PK, `scope_code` FK, `product_id` FK, `year`, `target_value`, `updated_by` FK nullable, `version` | UNIQUE `(scope_code, product_id, year)`. Target dana dan unit menggunakan tabel yang sama, satuan berasal dari products. Scope shared hanya untuk CMS. |
| `monthly_targets` | `id` PK, `annual_target_id` FK, `month`, `target_value` | UNIQUE `(annual_target_id, month)`; bulan 1–12. Tidak menyimpan ulang tahun/produk/divisi. |
| `unit_realizations` | `id` PK, `annual_target_id` FK, `month`, `units`, `updated_by` FK nullable, `version` | UNIQUE `(annual_target_id, month)`; hanya produk UNIT. Isinya total bulan, update mengganti total sebelumnya. Realisasi tahunan hasil SUM. |
| `branch_targets` | `id` PK, `division_id` FK, `branch_code`, `year`, `target_value`, `updated_by` FK nullable, `version` | Menampung target Bekasi yang sekarang ada, tanpa mengarang sumber realisasi cabang. UNIQUE `(division_id, branch_code, year)`. Kebijakan konsolidasi perlu keputusan. |
| `audit_events` | `id` PK, `actor_id` FK nullable, `resource_type`, `resource_id`, `action`, `before_data`, `after_data`, `occurred_at`, `source` | Log append-only untuk create/update/closing/target. `resource_type` + `resource_id` referensi logis, bukan FK SQL lintas beberapa tabel. Jangan catat password atau cookie sesi. |

Tambahkan `created_at`/`updated_at` pada tabel data operasional selain log audit yang menggunakan `occurred_at`. Tabel sesi autentikasi dan reset password milik framework tidak digambar dalam ERD bisnis ini.

## Penjelasan hubungan antar tabel

Diagram memakai notasi kardinalitas. `1` berarti wajib tepat satu, `0..1` berarti opsional paling banyak satu, `0..N` berarti nol atau banyak, dan `0..12` berarti nol sampai dua belas baris bulanan. Contoh: satu baris `opportunities` menunjuk ke satu `divisions`, sedangkan satu divisi dapat memiliki banyak opportunity.

| Relasi | Kardinalitas | Makna dalam sistem |
|---|---|---|
| `divisions` → `users` | Satu divisi ke nol atau banyak akun; satu PIC memiliki satu divisi, akun Head tidak punya divisi | Menentukan batas data yang dapat dikelola PIC. |
| `divisions` ↔ `products` melalui `division_products` | Banyak-ke-banyak | Pivot ini hanya mengizinkan produk tertentu di tiap divisi; Konsumer tidak mendapat Giro. |
| `divisions` → `opportunities` | Satu divisi ke nol atau banyak opportunity | Setiap opportunity tercatat di satu divisi agar filter, izin, dan laporan konsisten. |
| `users` → `opportunities` melalui `pic_id` | Satu PIC ke nol atau banyak opportunity; setiap opportunity punya satu PIC saat ini | `pic_id` menunjukkan penanggung jawab aktif/final. |
| `products` → `opportunities` | Satu produk ke nol atau banyak opportunity | Setiap opportunity dana memakai satu produk. Produk unit seperti QRIS tidak masuk pipeline nominal dana. |
| `opportunities` → `opportunity_assignments` | Satu opportunity ke nol atau banyak riwayat penugasan | Pergantian PIC menambah baris riwayat; data penugasan sebelumnya tidak ditimpa. |
| `target_scopes` dan `products` → `annual_targets` | Masing-masing satu scope/produk ke nol atau banyak target tahunan | Kombinasi scope, produk, dan tahun unik. Scope `shared` menampung satu target CMS untuk dipakai kedua divisi. |
| `annual_targets` → `monthly_targets` | Satu target tahunan ke nol sampai 12 target bulanan | Satu baris menyimpan target untuk satu bulan; nilai tahunan dan bulanan tetap dicatat terpisah. |
| `annual_targets` → `unit_realizations` | Satu target tahunan ke nol sampai 12 realisasi bulanan | Khusus produk bersatuan UNIT; angka tahunan adalah penjumlahan realisasi bulanan. |
| `divisions` → `branch_targets` | Satu divisi ke nol atau banyak target cabang | Menyimpan target Bekasi per divisi, cabang, dan tahun. |
| `users` → `audit_events` | Satu akun ke nol atau banyak peristiwa; pelaku pada satu peristiwa boleh kosong | Mencatat siapa yang mengubah data. `resource_type` + `resource_id` adalah rujukan logis, bukan foreign key SQL. |

`History`, Dashboard, Team, dan Konsolidasi tidak mempunyai tabel salinan. Halaman tersebut membaca `opportunities` dan target yang sama, lalu menyaring atau menghitung hasilnya. Opportunity Won/Lost tetap tersimpan di `opportunities`; status hasil dan tanggal closing yang membedakannya dari pipeline aktif.

## Relasi dan konsistensi

- Satu divisi memiliki banyak PIC dan opportunity. Head Funding boleh tidak terhubung dengan divisi.
- Divisi dan produk berelasi banyak-ke-banyak melalui `division_products`.
- Setiap opportunity memiliki tepat satu produk dana dan satu PIC final/saat ini. Produk dan PIC harus diizinkan untuk divisi opportunity.
- Satu opportunity bisa punya banyak catatan penugasan. Riwayat lama tidak berubah ketika PIC saat ini berganti.
- Satu scope memiliki banyak target tahunan; satu target tahunan punya maksimal 12 target bulanan dan, untuk UNIT, maksimal 12 realisasi bulanan.
- Rekap CMS menggunakan scope shared **satu kali**, walaupun dua divisi mendapat izin pengelolaan.
- `History`, `Dashboard`, `Team`, dan `Konsolidasi` adalah hasil query/perhitungan; **bukan tabel duplikat**.
- Penonaktifan akun mempertahankan FK dan history. Jangan menghapus pengguna/produk/divisi yang sudah dipakai transaksi dengan cascade delete.

## Tipe data dan aturan

| Data | Usulan penyimpanan |
|---|---|
| ID internal | BIGINT unsigned; public identifier boleh berupa UUID bila nanti diperlukan |
| Nominal/target dana | DECIMAL(20,0), rupiah bulat nonnegatif; nominal peluang wajib lebih dari nol |
| Nilai target UNIT | DECIMAL(20,0) pada target; validasi unit bulat. `units` pada realisasi BIGINT unsigned |
| Tahun/bulan | SMALLINT unsigned / TINYINT unsigned; tahun 2000–2100, bulan 1–12 |
| Tanggal bisnis | DATE untuk pencatatan, follow-up, closing |
| Waktu audit | DATETIME dalam UTC; konversi zona waktu laporan dikonfigurasi saat implementasi |
| Versi update | BIGINT unsigned, naik setiap update yang berhasil |
| Status | Nilai terbatas: Cold/Warm/Hot dan Active/Won/Lost; keduanya berbeda makna |

Untuk kompatibilitas frontend yang masih memakai JavaScript Number, batasi input nominal sampai `Number.MAX_SAFE_INTEGER` pada tahap integrasi awal. API mengirim nilai rupiah sebagai string digit. Penjumlahan dan persentase laporan utama dihitung server; jangan menghitung saldo besar memakai float database.

Validasi bisnis melengkapi FK/UNIQUE: role PIC harus memiliki divisi, PIC dan opportunity satu divisi, produk harus ada di pasangan `division_products`, hanya CMS pada shared, UNIT tidak boleh menjadi nominal pipeline dana. Jika perlu jaminan DB untuk pasangan divisi-produk, gunakan FK komposit ke `division_products`; larangan IDR/UNIT dan role tetap diperiksa service.

Won membutuhkan realisasi `> 0` dan `<= nominal`, serta tanggal closing antara tanggal pencatatan dan hari ini. Lost membutuhkan alasan dan tanggal yang valid, realisasi dana nol. Closing bersifat final pada versi awal. Selesai follow-up tetap Active. Target nol berarti belum ditetapkan; persentase NULL, bukan pembagian nol; sisa minimum nol.

## Pemetaan migrasi

| Sumber saat ini | Tujuan | Perhatian |
|---|---|---|
| Akun `data/access.js` | users + divisions | Konfirmasi PIC asli; jangan membawa password demo ke lingkungan nyata. |
| `rows[].pic` | opportunities.pic_id | Petakan nama ke akun melalui daftar yang direview; jangan otomatis menggabungkan nama ambigu. |
| `rows[].customer` | opportunities.customer_name | Pertahankan teks dan ejaan lama. |
| `rows[].handledBy` | opportunity_assignments | Hanya bukti pernah menangani; waktu dan urutan penugasan tidak diketahui. Simpan source legacy, tanggal NULL. |
| `rows[].createdBy/updatedBy` | FK pembuat/editor bila dapat diverifikasi | Jangan menebak pembuat pada record lama. Simpan payload sumber untuk rekonsiliasi. |
| `targets[divisi][tahun][produk]` | annual_targets | Tetapkan scope divisi. |
| `targets[divisi][tahun].monthly[bulan]` | monthly_targets | Tahunan dan bulanan tetap independen seperti sekarang. |
| `unitTargets[scope][tahun][produk]` | annual_targets + monthly_targets + unit_realizations | Pisahkan target dari aktual; shared CMS tidak digandakan. |
| `targets[divisi][tahun].bekasi` | branch_targets | Jangan dipindahkan menjadi produk baru. |
| Record QRIS/Bale Syariah Komersil lama | Arsip staging migrasi | Tidak dihapus dan tidak otomatis dipindah ke Konsumer. Pemilik data memutuskan pemetaan sebelum masuk skema aktif yang diusulkan. |

Migrasi usulan: ekspor browser ke berkas cadangan → validasi dan laporan preview → cocokkan PIC/divisi/produk → import transaksi dengan legacy_id/idempotency → bandingkan jumlah record dan total setiap tahun/bulan → simpan laporan selisih. Jangan menjalankan migrasi hanya berdasarkan dokumen ini.

## Indeks awal

Usulan indeks daftar aktif: `(division_id, outcome, updated_at)`; history: `(division_id, outcome, closed_date)`; rekap PIC: `(pic_id, outcome, closed_date)`; follow-up: `(division_id, outcome, follow_up_date)`. Tambahkan indeks FK dan UNIQUE yang tercantum di kamus tabel. Tinjau kembali memakai query nyata saat backend sudah ada.
