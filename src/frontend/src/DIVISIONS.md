# Akun dan target divisi

Vue mengambil data melalui Laravel REST API. Data operasional disimpan di database PostgreSQL `pipeline_funding`; browser hanya menyimpan token login Sanctum. Password seluruh akun pengembangan saat ini adalah `demo123` dan harus diganti sebelum sistem dipakai dengan data nyata.

Akun awal dibuat oleh seeder backend: `suci`, `cacan`, dan `dharma` berada di Komersil; `nisa` berada di Konsumer; `head` memiliki role Head Funding. Penempatan PIC dapat diubah melalui database ketika pembagian sebenarnya sudah ditetapkan.

- PIC melihat dan mengelola opportunity serta target divisinya. Laravel memeriksa divisi PIC pada setiap operasi.
- Head Funding dapat melihat gabungan atau memilih satu divisi untuk melakukan perubahan.
- Konsumer memiliki Tabungan dan Deposito. Komersil memiliki Tabungan, Giro, dan Deposito.
- Target dana tahunan dan bulanan terpisah per divisi, disimpan dalam rupiah, lalu ditampilkan dengan satuan M.
- Bale Syariah dan QRIS hanya tersedia untuk Konsumer dan menggunakan satuan unit.
- CMS menggunakan satu scope `shared`. Kedua divisi dan Head Funding membaca serta mengubah record yang sama.
- Dashboard membaca opportunity dan target dari API. History menampilkan record opportunity yang sudah Won atau Lost; closing tidak menghapus record.
- Audit perubahan baru disimpan pada `audit_events`, sedangkan riwayat PIC disimpan pada `opportunity_assignments`.
- Data prototipe lama pada key `funding-pipeline-v3` tidak dibaca dan tidak diimpor otomatis ke PostgreSQL.

Jalankan aplikasi dari dua terminal:

```text
cd backend
php artisan serve --host=127.0.0.1 --port=8000

cd frontend
npm run dev
```

PostgreSQL dijalankan melalui layanan PostgreSQL lokal. Pengujian browser ada di `frontend/tests/e2e/workflow.spec.js` dan memakai konteks browser terpisah.
