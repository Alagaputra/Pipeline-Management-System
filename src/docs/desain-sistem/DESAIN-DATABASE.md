# Desain database — Pipeline Funding Management

Versi implementasi: **19 Oktober 2026**. Disusun dari metadata PostgreSQL lokal dan migration Laravel, bukan rancangan MySQL lama.

Database memuat **22 tabel dan 162 kolom**: 13 tabel domain, 1 tabel autentikasi Sanctum, dan 8 tabel infrastruktur Laravel. Tidak ada isi record atau kredensial yang diekspor.

## Diagram

- [ERD gabungan seluruh 22 tabel dalam satu gambar](ERD-LENGKAP.png)
- [PDF ERD gabungan satu halaman](ERD-LENGKAP.pdf)
- [ERD master dan pipeline](erd-pipeline.png)
- [ERD target dan realisasi](erd-target.png)
- [ERD autentikasi dan audit](erd-keamanan.png)
- [Sumber Mermaid lengkap, 22 tabel](erd-lengkap.mmd)

Gambar menampilkan atribut dan relasi utama supaya terbaca. Kamus berikut mencakup setiap kolom, FK, UNIQUE, dan indeks. Garis putus-putus berarti hubungan logis yang tidak ditegakkan sebagai FK SQL.

## Relasi dan ketentuan utama

1. Divisi memiliki banyak akun dan peluang. `users.division_id` boleh NULL; akun Head pada konfigurasi saat ini tidak mempunyai satu divisi tetap.
2. Produk dan divisi berelasi banyak-ke-banyak melalui `division_products`. Kesesuaian PIC/produk/divisi diperiksa controller; FK individual saja tidak menjamin pasangan tersebut.
3. Peluang dana merujuk satu divisi, produk IDR, dan PIC. Perpindahan PIC dicatat pada `opportunity_assignments`.
4. Won/Lost tetap berada di `opportunities`. Halaman Riwayat, Dashboard, dan Tim tidak mempunyai tabel salinan.
5. `annual_targets` unik pada `(scope_code, product_id, year)`. `monthly_targets` dan `unit_realizations` masing-masing unik pada `(annual_target_id, month)`.
6. Rentang bulan 1–12 dan tahun 2000–2100 ditegakkan validasi API. Tidak ada CHECK SQL rentang tersebut pada skema yang diperiksa.
7. CMS menggunakan scope `shared`, dihitung satu kali. Bale Syariah dan QRIS milik Konsumer. Dana dan unit tidak dijumlahkan.
8. `target_scopes.division_id` tidak mempunyai UNIQUE SQL: satu divisi secara struktur dapat dirujuk beberapa scope, walaupun seeder saat ini membuat satu scope per divisi.
9. `version` menjaga konflik pembaruan. Simpan satu formulir target serta closing berlangsung dalam transaksi; konflik membatalkan perubahan formulir.
10. `request_receipts` unik pada `(user_id, request_key)`. Hasil sukses dan perubahan bisnis disimpan di transaksi yang sama; key yang sama dengan payload berbeda ditolak.
11. `audit_events.resource_type/resource_id` adalah referensi logis, bukan FK. `actor_id` adalah FK yang boleh NULL.
12. `personal_access_tokens.tokenable_type/tokenable_id` merupakan relasi polimorfik Sanctum tanpa FK SQL ke `users`. `sessions.user_id` juga hanya berindeks, bukan FK.

## Tipe data fisik dan validasi

Nilai dana/target disimpan sebagai **bigint**, bukan DECIMAL atau float. PostgreSQL tidak memiliki BIGINT UNSIGNED: aturan nonnegatif diterapkan pada validasi API. Status dan role disimpan sebagai varchar, bukan tipe ENUM PostgreSQL. Snapshot audit memakai `json`. Kolom waktu menggunakan `timestamp without time zone`; DATE dipakai untuk tanggal bisnis. Tipe dan panjang persis per kolom tercantum di bawah.

Target nol berarti belum ditetapkan. Realisasi dana berasal dari Won menurut tahun tanggal closing. Realisasi unit berasal dari jumlah `unit_realizations.units` dalam satu tahun. Total target bulanan tidak diwajibkan sama dengan target tahunan pada aturan saat ini.

## Ringkasan tabel

| Tabel | Kelompok | Fungsi |
| --- | --- | --- |
| `divisions` | Domain | Master divisi Konsumer dan Komersil. |
| `users` | Domain | Akun PIC dan Head Funding. Password berupa hash pada kolom password. |
| `products` | Domain | Master produk dana (IDR) dan layanan (UNIT). |
| `division_products` | Domain | Pasangan produk yang tersedia untuk setiap divisi; PK komposit. |
| `opportunities` | Domain | Peluang dana, status ketertarikan, tindak lanjut, hasil closing, dan realisasi. |
| `opportunity_assignments` | Domain | Riwayat penugasan/pergantian PIC pada peluang. |
| `target_scopes` | Domain | Lingkup komersil, konsumer, atau shared. Shared tidak terikat satu divisi. |
| `annual_targets` | Domain | Satu target per lingkup, produk, dan tahun. |
| `monthly_targets` | Domain | Rincian target bulanan dari target tahunan. |
| `unit_realizations` | Domain | Realisasi layanan dalam unit per bulan; bukan realisasi dana Won. |
| `branch_targets` | Domain | Target cabang kompatibilitas versi lama; bukan penyebut target dana utama. |
| `audit_events` | Domain | Pelaku, waktu, aksi, dan snapshot sebelum/sesudah perubahan. |
| `request_receipts` | Domain | Hasil sukses permintaan tulis untuk percobaan ulang yang aman. |
| `personal_access_tokens` | Autentikasi | Token Laravel Sanctum yang disimpan sebagai hash. |
| `password_reset_tokens` | Infrastruktur | Struktur bawaan Laravel untuk token reset password; tidak berarti ada fitur reset di UI. |
| `sessions` | Infrastruktur | Penyimpanan sesi bawaan Laravel; autentikasi SPA ini menggunakan bearer token Sanctum. |
| `cache` | Infrastruktur | Penyimpanan cache Laravel. |
| `cache_locks` | Infrastruktur | Kunci cache Laravel. |
| `jobs` | Infrastruktur | Antrean pekerjaan Laravel; bukan jalur wajib simpan peluang/target saat ini. |
| `job_batches` | Infrastruktur | Metadata kelompok pekerjaan Laravel. |
| `failed_jobs` | Infrastruktur | Catatan pekerjaan antrean yang gagal. |
| `migrations` | Infrastruktur | Riwayat migration yang sudah dijalankan. |

## Kamus kolom, constraint, dan indeks

### divisions

Master divisi Konsumer dan Komersil.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('divisions_id_seq'::regclass)` |
| `code` | `varchar(30)` | Tidak | `—` |
| `name` | `varchar(80)` | Tidak | `—` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `UNIQUE (code)`
- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX divisions_code_unique ON public.divisions USING btree (code);
CREATE UNIQUE INDEX divisions_pkey ON public.divisions USING btree (id);
```

### users

Akun PIC dan Head Funding. Password berupa hash pada kolom password.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('users_id_seq'::regclass)` |
| `division_id` | `bigint` | Ya | `—` |
| `username` | `varchar(50)` | Tidak | `—` |
| `name` | `varchar(255)` | Tidak | `—` |
| `email` | `varchar(255)` | Ya | `—` |
| `email_verified_at` | `timestamp without time zone` | Ya | `—` |
| `password` | `varchar(255)` | Tidak | `—` |
| `role` | `varchar(20)` | Tidak | `'pic'::character varying` |
| `is_active` | `boolean` | Tidak | `true` |
| `remember_token` | `varchar(100)` | Ya | `—` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE RESTRICT`
- `UNIQUE (email)`
- `PRIMARY KEY (id)`
- `UNIQUE (username)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX users_email_unique ON public.users USING btree (email);
CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id);
CREATE UNIQUE INDEX users_username_unique ON public.users USING btree (username);
```

### products

Master produk dana (IDR) dan layanan (UNIT).

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('products_id_seq'::regclass)` |
| `code` | `varchar(40)` | Tidak | `—` |
| `name` | `varchar(80)` | Tidak | `—` |
| `measure` | `varchar(10)` | Tidak | `—` |
| `is_active` | `boolean` | Tidak | `true` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `UNIQUE (code)`
- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX products_code_unique ON public.products USING btree (code);
CREATE UNIQUE INDEX products_pkey ON public.products USING btree (id);
```

### division_products

Pasangan produk yang tersedia untuk setiap divisi; PK komposit.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `division_id` | `bigint` | Tidak | `—` |
| `product_id` | `bigint` | Tidak | `—` |

Constraint SQL:

- `FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE`
- `PRIMARY KEY (division_id, product_id)`
- `FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE`

Indeks fisik:

```sql
CREATE UNIQUE INDEX division_products_pkey ON public.division_products USING btree (division_id, product_id);
```

### opportunities

Peluang dana, status ketertarikan, tindak lanjut, hasil closing, dan realisasi.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('opportunities_id_seq'::regclass)` |
| `legacy_id` | `varchar(255)` | Ya | `—` |
| `division_id` | `bigint` | Tidak | `—` |
| `pic_id` | `bigint` | Tidak | `—` |
| `product_id` | `bigint` | Tidak | `—` |
| `customer_name` | `varchar(160)` | Tidak | `—` |
| `segment` | `varchar(20)` | Tidak | `—` |
| `nominal` | `bigint` | Tidak | `—` |
| `interest_status` | `varchar(10)` | Tidak | `—` |
| `outcome` | `varchar(10)` | Tidak | `'Active'::character varying` |
| `recorded_date` | `date` | Tidak | `—` |
| `follow_up_date` | `date` | Ya | `—` |
| `follow_up_completed` | `boolean` | Tidak | `false` |
| `closed_date` | `date` | Ya | `—` |
| `realization` | `bigint` | Tidak | `'0'::bigint` |
| `notes` | `text` | Ya | `—` |
| `lost_reason` | `text` | Ya | `—` |
| `created_by` | `bigint` | Ya | `—` |
| `updated_by` | `bigint` | Ya | `—` |
| `version` | `bigint` | Tidak | `'1'::bigint` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL`
- `FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE RESTRICT`
- `UNIQUE (legacy_id)`
- `FOREIGN KEY (pic_id) REFERENCES users(id) ON DELETE RESTRICT`
- `PRIMARY KEY (id)`
- `FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT`
- `FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL`

Indeks fisik:

```sql
CREATE INDEX opportunities_division_id_outcome_updated_at_index ON public.opportunities USING btree (division_id, outcome, updated_at);
CREATE UNIQUE INDEX opportunities_legacy_id_unique ON public.opportunities USING btree (legacy_id);
CREATE INDEX opportunities_pic_id_outcome_closed_date_index ON public.opportunities USING btree (pic_id, outcome, closed_date);
CREATE UNIQUE INDEX opportunities_pkey ON public.opportunities USING btree (id);
```

### opportunity_assignments

Riwayat penugasan/pergantian PIC pada peluang.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('opportunity_assignments_id_seq'::regclass)` |
| `opportunity_id` | `bigint` | Tidak | `—` |
| `pic_id` | `bigint` | Tidak | `—` |
| `assigned_at` | `timestamp without time zone` | Ya | `—` |
| `unassigned_at` | `timestamp without time zone` | Ya | `—` |
| `changed_by` | `bigint` | Ya | `—` |
| `source` | `varchar(20)` | Tidak | `'app'::character varying` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL`
- `FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE`
- `FOREIGN KEY (pic_id) REFERENCES users(id) ON DELETE RESTRICT`
- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX opportunity_assignments_pkey ON public.opportunity_assignments USING btree (id);
```

### target_scopes

Lingkup komersil, konsumer, atau shared. Shared tidak terikat satu divisi.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `code` | `varchar(30)` | Tidak | `—` |
| `division_id` | `bigint` | Ya | `—` |
| `label` | `varchar(80)` | Tidak | `—` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE RESTRICT`
- `PRIMARY KEY (code)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX target_scopes_pkey ON public.target_scopes USING btree (code);
```

### annual_targets

Satu target per lingkup, produk, dan tahun.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('annual_targets_id_seq'::regclass)` |
| `scope_code` | `varchar(30)` | Tidak | `—` |
| `product_id` | `bigint` | Tidak | `—` |
| `year` | `smallint` | Tidak | `—` |
| `target_value` | `bigint` | Tidak | `'0'::bigint` |
| `updated_by` | `bigint` | Ya | `—` |
| `version` | `bigint` | Tidak | `'1'::bigint` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `PRIMARY KEY (id)`
- `FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT`
- `FOREIGN KEY (scope_code) REFERENCES target_scopes(code) ON DELETE RESTRICT`
- `UNIQUE (scope_code, product_id, year)`
- `FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL`

Indeks fisik:

```sql
CREATE UNIQUE INDEX annual_targets_pkey ON public.annual_targets USING btree (id);
CREATE UNIQUE INDEX annual_targets_scope_code_product_id_year_unique ON public.annual_targets USING btree (scope_code, product_id, year);
```

### monthly_targets

Rincian target bulanan dari target tahunan.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('monthly_targets_id_seq'::regclass)` |
| `annual_target_id` | `bigint` | Tidak | `—` |
| `month` | `smallint` | Tidak | `—` |
| `target_value` | `bigint` | Tidak | `'0'::bigint` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `FOREIGN KEY (annual_target_id) REFERENCES annual_targets(id) ON DELETE CASCADE`
- `UNIQUE (annual_target_id, month)`
- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX monthly_targets_annual_target_id_month_unique ON public.monthly_targets USING btree (annual_target_id, month);
CREATE UNIQUE INDEX monthly_targets_pkey ON public.monthly_targets USING btree (id);
```

### unit_realizations

Realisasi layanan dalam unit per bulan; bukan realisasi dana Won.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('unit_realizations_id_seq'::regclass)` |
| `annual_target_id` | `bigint` | Tidak | `—` |
| `month` | `smallint` | Tidak | `—` |
| `units` | `bigint` | Tidak | `'0'::bigint` |
| `updated_by` | `bigint` | Ya | `—` |
| `version` | `bigint` | Tidak | `'1'::bigint` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `FOREIGN KEY (annual_target_id) REFERENCES annual_targets(id) ON DELETE CASCADE`
- `UNIQUE (annual_target_id, month)`
- `PRIMARY KEY (id)`
- `FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL`

Indeks fisik:

```sql
CREATE UNIQUE INDEX unit_realizations_annual_target_id_month_unique ON public.unit_realizations USING btree (annual_target_id, month);
CREATE UNIQUE INDEX unit_realizations_pkey ON public.unit_realizations USING btree (id);
```

### branch_targets

Target cabang kompatibilitas versi lama; bukan penyebut target dana utama.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('branch_targets_id_seq'::regclass)` |
| `division_id` | `bigint` | Tidak | `—` |
| `branch_code` | `varchar(40)` | Tidak | `—` |
| `year` | `smallint` | Tidak | `—` |
| `target_value` | `bigint` | Tidak | `'0'::bigint` |
| `updated_by` | `bigint` | Ya | `—` |
| `version` | `bigint` | Tidak | `'1'::bigint` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `UNIQUE (division_id, branch_code, year)`
- `FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE RESTRICT`
- `PRIMARY KEY (id)`
- `FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL`

Indeks fisik:

```sql
CREATE UNIQUE INDEX branch_targets_division_id_branch_code_year_unique ON public.branch_targets USING btree (division_id, branch_code, year);
CREATE UNIQUE INDEX branch_targets_pkey ON public.branch_targets USING btree (id);
```

### audit_events

Pelaku, waktu, aksi, dan snapshot sebelum/sesudah perubahan.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('audit_events_id_seq'::regclass)` |
| `actor_id` | `bigint` | Ya | `—` |
| `resource_type` | `varchar(80)` | Tidak | `—` |
| `resource_id` | `varchar(80)` | Tidak | `—` |
| `action` | `varchar(60)` | Tidak | `—` |
| `before_data` | `json` | Ya | `—` |
| `after_data` | `json` | Ya | `—` |
| `occurred_at` | `timestamp without time zone` | Tidak | `—` |
| `source` | `varchar(20)` | Tidak | `'api'::character varying` |

Constraint SQL:

- `FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE SET NULL`
- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX audit_events_pkey ON public.audit_events USING btree (id);
CREATE INDEX audit_events_resource_type_resource_id_index ON public.audit_events USING btree (resource_type, resource_id);
```

### request_receipts

Hasil sukses permintaan tulis untuk percobaan ulang yang aman.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('request_receipts_id_seq'::regclass)` |
| `user_id` | `bigint` | Tidak | `—` |
| `request_key` | `uuid` | Tidak | `—` |
| `request_hash` | `varchar(64)` | Tidak | `—` |
| `status_code` | `smallint` | Tidak | `—` |
| `response_body` | `text` | Tidak | `—` |
| `created_at` | `timestamp without time zone` | Tidak | `—` |

Constraint SQL:

- `PRIMARY KEY (id)`
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`
- `UNIQUE (user_id, request_key)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX request_receipts_pkey ON public.request_receipts USING btree (id);
CREATE UNIQUE INDEX request_receipts_user_id_request_key_unique ON public.request_receipts USING btree (user_id, request_key);
```

### personal_access_tokens

Token Laravel Sanctum yang disimpan sebagai hash.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('personal_access_tokens_id_seq'::regclass)` |
| `tokenable_type` | `varchar(255)` | Tidak | `—` |
| `tokenable_id` | `bigint` | Tidak | `—` |
| `name` | `text` | Tidak | `—` |
| `token` | `varchar(64)` | Tidak | `—` |
| `abilities` | `text` | Ya | `—` |
| `last_used_at` | `timestamp without time zone` | Ya | `—` |
| `expires_at` | `timestamp without time zone` | Ya | `—` |
| `created_at` | `timestamp without time zone` | Ya | `—` |
| `updated_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `PRIMARY KEY (id)`
- `UNIQUE (token)`

Indeks fisik:

```sql
CREATE INDEX personal_access_tokens_expires_at_index ON public.personal_access_tokens USING btree (expires_at);
CREATE UNIQUE INDEX personal_access_tokens_pkey ON public.personal_access_tokens USING btree (id);
CREATE UNIQUE INDEX personal_access_tokens_token_unique ON public.personal_access_tokens USING btree (token);
CREATE INDEX personal_access_tokens_tokenable_type_tokenable_id_index ON public.personal_access_tokens USING btree (tokenable_type, tokenable_id);
```

### password_reset_tokens

Struktur bawaan Laravel untuk token reset password; tidak berarti ada fitur reset di UI.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `email` | `varchar(255)` | Tidak | `—` |
| `token` | `varchar(255)` | Tidak | `—` |
| `created_at` | `timestamp without time zone` | Ya | `—` |

Constraint SQL:

- `PRIMARY KEY (email)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX password_reset_tokens_pkey ON public.password_reset_tokens USING btree (email);
```

### sessions

Penyimpanan sesi bawaan Laravel; autentikasi SPA ini menggunakan bearer token Sanctum.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `varchar(255)` | Tidak | `—` |
| `user_id` | `bigint` | Ya | `—` |
| `ip_address` | `varchar(45)` | Ya | `—` |
| `user_agent` | `text` | Ya | `—` |
| `payload` | `text` | Tidak | `—` |
| `last_activity` | `integer` | Tidak | `—` |

Constraint SQL:

- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE INDEX sessions_last_activity_index ON public.sessions USING btree (last_activity);
CREATE UNIQUE INDEX sessions_pkey ON public.sessions USING btree (id);
CREATE INDEX sessions_user_id_index ON public.sessions USING btree (user_id);
```

### cache

Penyimpanan cache Laravel.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `key` | `varchar(255)` | Tidak | `—` |
| `value` | `text` | Tidak | `—` |
| `expiration` | `integer` | Tidak | `—` |

Constraint SQL:

- `PRIMARY KEY (key)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX cache_pkey ON public.cache USING btree (key);
```

### cache_locks

Kunci cache Laravel.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `key` | `varchar(255)` | Tidak | `—` |
| `owner` | `varchar(255)` | Tidak | `—` |
| `expiration` | `integer` | Tidak | `—` |

Constraint SQL:

- `PRIMARY KEY (key)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX cache_locks_pkey ON public.cache_locks USING btree (key);
```

### jobs

Antrean pekerjaan Laravel; bukan jalur wajib simpan peluang/target saat ini.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('jobs_id_seq'::regclass)` |
| `queue` | `varchar(255)` | Tidak | `—` |
| `payload` | `text` | Tidak | `—` |
| `attempts` | `smallint` | Tidak | `—` |
| `reserved_at` | `integer` | Ya | `—` |
| `available_at` | `integer` | Tidak | `—` |
| `created_at` | `integer` | Tidak | `—` |

Constraint SQL:

- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX jobs_pkey ON public.jobs USING btree (id);
CREATE INDEX jobs_queue_index ON public.jobs USING btree (queue);
```

### job_batches

Metadata kelompok pekerjaan Laravel.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `varchar(255)` | Tidak | `—` |
| `name` | `varchar(255)` | Tidak | `—` |
| `total_jobs` | `integer` | Tidak | `—` |
| `pending_jobs` | `integer` | Tidak | `—` |
| `failed_jobs` | `integer` | Tidak | `—` |
| `failed_job_ids` | `text` | Tidak | `—` |
| `options` | `text` | Ya | `—` |
| `cancelled_at` | `integer` | Ya | `—` |
| `created_at` | `integer` | Tidak | `—` |
| `finished_at` | `integer` | Ya | `—` |

Constraint SQL:

- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX job_batches_pkey ON public.job_batches USING btree (id);
```

### failed_jobs

Catatan pekerjaan antrean yang gagal.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `bigint` | Tidak | `nextval('failed_jobs_id_seq'::regclass)` |
| `uuid` | `varchar(255)` | Tidak | `—` |
| `connection` | `text` | Tidak | `—` |
| `queue` | `text` | Tidak | `—` |
| `payload` | `text` | Tidak | `—` |
| `exception` | `text` | Tidak | `—` |
| `failed_at` | `timestamp without time zone` | Tidak | `CURRENT_TIMESTAMP` |

Constraint SQL:

- `PRIMARY KEY (id)`
- `UNIQUE (uuid)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX failed_jobs_pkey ON public.failed_jobs USING btree (id);
CREATE UNIQUE INDEX failed_jobs_uuid_unique ON public.failed_jobs USING btree (uuid);
```

### migrations

Riwayat migration yang sudah dijalankan.

| Kolom | Tipe PostgreSQL | NULL | Default |
| --- | --- | --- | --- |
| `id` | `integer` | Tidak | `nextval('migrations_id_seq'::regclass)` |
| `migration` | `varchar(255)` | Tidak | `—` |
| `batch` | `integer` | Tidak | `—` |

Constraint SQL:

- `PRIMARY KEY (id)`

Indeks fisik:

```sql
CREATE UNIQUE INDEX migrations_pkey ON public.migrations USING btree (id);
```

## Sumber implementasi

- `src/backend/database/migrations/0001_01_01_000000_create_users_table.php`
- `src/backend/database/migrations/0001_01_01_000001_create_cache_table.php`
- `src/backend/database/migrations/0001_01_01_000002_create_jobs_table.php`
- `src/backend/database/migrations/2026_09_14_073227_create_personal_access_tokens_table.php`
- `src/backend/database/migrations/2026_09_14_080000_create_pipeline_tables.php`
- `src/backend/database/migrations/2026_10_19_000001_create_request_receipts_table.php`
- `src/backend/database/seeders/DatabaseSeeder.php`
- Metadata aktual: `schema.json`; dapat diperbarui memakai `scripts/export-schema.php`.
