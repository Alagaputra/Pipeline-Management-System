# Evaluasi Pipeline Funding Management

> Arsip evaluasi versi September 2026. Aplikasi telah disesuaikan dengan proposal pada Oktober: PostgreSQL, Chart.js, timeline perkembangan, dan target tahunan per produk. Lihat [pemetaan proposal terbaru](../PROPOSAL-ALIGNMENT.md) serta panduan utama proyek untuk perilaku dan konfigurasi saat ini.

Tanggal pemeriksaan: **14 September 2026**. Dokumen ini disusun dari kode proyek, bukan hasil pemeriksaan database produksi.

**Buka [index.html](index.html) untuk melihat diagram secara visual dan offline.** Dokumen Markdown berikut memberikan rincian teknis:

1. [Model data dan ERD](DATA-MODEL.md) — tabel, hubungan, batasan data, dan pemetaan penyimpanan lama.
2. [Arsitektur dan alur](FLOWS.md) — arsitektur terintegrasi, alur PIC, dan proses closing.
3. [Rancangan API dan pengujian](API-AND-TESTS.md) — kontrak awal dan skenario penerimaan.

## Kesimpulan untuk evaluasi

Frontend Vue sekarang terhubung ke Laravel REST API dan database MySQL `pipeline_funding`. Login menggunakan token Sanctum, aturan divisi/produk diperiksa di server, dan perubahan opportunity serta target disimpan di MySQL. ERD di paket ini menggambarkan struktur yang sudah diterapkan melalui migration Laravel.

Stack yang menjadi dasar rancangan: Vue 3 + Laravel REST API + MySQL. Diagram aplikasi tetap dapat menggunakan CSS. Docker dan Chart.js tidak menjadi prasyarat rancangan ini.

## Cakupan yang sudah ada

| Halaman | Perilaku saat ini |
|---|---|
| Dashboard | Ringkasan peluang aktif, nominal, Hot, realisasi Won, target dana, target unit, dan follow-up prioritas |
| Pipeline | Daftar aktif; pencarian/filter/sort; detail dan form drawer; follow-up; closing Won/Lost |
| Target | Target dana tahunan/bulanan per divisi; Konsolidasi; target KCP Bekasi; Bale Syariah, QRIS, CMS dalam unit |
| Team | Diagram komposisi produk per PIC; jumlah aktif dan Won/Lost; daftar opportunity yang pernah ditangani |
| History | Daftar opportunity Won/Lost; filter PIC, produk, hasil, dan tanggal closing; detail tanpa edit |

Target dana disimpan sebagai rupiah penuh, ditampilkan dalam M. Target layanan menggunakan unit. Keduanya tidak boleh dijumlahkan menjadi satu nominal.

## Aktor dan matriks akses

Secara model data, **role** adalah `pic` atau `head`; **divisi** adalah Konsumer atau Komersil. Tiga pengalaman login tidak berarti harus ada tiga role terpisah.

| Kegiatan | PIC Konsumer | PIC Komersil | Head Funding |
|---|---|---|---|
| Melihat pipeline/History | Divisi sendiri | Divisi sendiri | Kedua divisi atau filter |
| Membuat/edit/closing aktif | Divisi sendiri | Divisi sendiri | Setelah memilih satu divisi |
| Menentukan PIC | PIC divisi sendiri | PIC divisi sendiri | PIC divisi yang dipilih |
| Produk dana | Tabungan, Deposito | Tabungan, Giro, Deposito | Mengikuti filter divisi |
| Mengubah target dana | Divisi sendiri | Divisi sendiri | Setelah memilih satu divisi |
| Bale Syariah dan QRIS | Tampil dan dapat dikelola | Tidak tampil di UI | Tampil pada Konsumer/gabungan; pengubahan pada satu divisi yang tersedia |
| CMS bersama | Melihat dan mengelola | Melihat dan mengelola | Melihat dan mengelola, termasuk saat filter gabungan |
| Edit opportunity yang sudah closing | Tidak tersedia | Tidak tersedia | Tidak tersedia |
| Monitoring Dashboard | Ya | Ya | Ya |

PIC saat ini dapat mengelola opportunity PIC lain **dalam divisi yang sama**. Pembatasan hanya milik pribadi belum diterapkan. Penempatan akun contoh belum berarti penempatan pegawai sebenarnya: Suci/Cacan/Dharma sementara Komersil, Nisa contoh Konsumer, `head` Head Funding.

## Temuan yang perlu dievaluasi

Prioritas P1 berarti perlu diselesaikan sebelum pemakaian bersama dengan data nyata. P2 berarti penting untuk ketepatan laporan dan pengembangan berikutnya. Temuan berasal dari inspeksi statis; bukan audit keamanan menyeluruh.

| ID | Prioritas | Bukti dalam kode | Dampak dan tindak lanjut |
|---|---|---|---|
| E01 | Selesai | [useSession.js](../../frontend/src/composables/useSession.js) dan Laravel Sanctum | Password diverifikasi server; token browser hanya menjadi kredensial sesi. |
| E02 | Selesai | [usePipeline.js](../../frontend/src/composables/usePipeline.js) memakai REST API | Data terpusat di MySQL dan update memakai pemeriksaan `version` untuk mencegah penimpaan diam-diam. |
| E03 | Selesai | Aturan produk di migration, seeder, dan controller backend | Konsumer tidak memiliki Giro; Komersil tidak memiliki QRIS/Bale Syariah; CMS memakai scope bersama. |
| E04 | Perlu keputusan | [TargetView.vue](../../frontend/src/views/TargetView.vue) dan Dashboard | Definisi target KCP Bekasi terhadap target produk perlu disepakati agar penyebut pencapaian konsisten. |
| E05 | Selesai | Scope `shared` pada `annual_targets` | CMS disimpan satu kali dan dapat dikelola kedua divisi. |
| E06 | Selesai untuk operasi baru | Tabel `audit_events` dan `opportunity_assignments` | Perubahan baru memiliki actor, waktu, serta nilai sebelum/sesudah. Data lama tetap memerlukan aturan migrasi. |
| E07 | Perlu keputusan | [UnitTargets.vue](../../frontend/src/components/UnitTargets.vue) | Realisasi unit masih rekap bulanan; tentukan apakah perlu bukti tiap nasabah/aktivasi. |
| E08 | Perlu keputusan | [TargetView.vue](../../frontend/src/views/TargetView.vue) | Target tahunan dan bulanan masih boleh berbeda sesuai perilaku yang disepakati sebelumnya. |

## Keputusan yang perlu kamu evaluasi

- [ ] Nama dan pembagian PIC sebenarnya; siapa yang berwenang membuat/menonaktifkan akun.
- [ ] Apakah setiap PIC boleh mengedit seluruh pipeline divisinya, atau hanya pipeline yang ditangani.
- [ ] Apakah PIC boleh mengatur target, atau target ditetapkan Head Funding. Saat ini PIC dapat mengatur target divisinya.
- [ ] QRIS/Bale Syariah benar-benar khusus Konsumer atau hanya disembunyikan dari Komersil; bagaimana nasib data lama.
- [ ] Makna target KCP Bekasi dan sumber realisasinya; jangan menghitung target yang sama dua kali.
- [ ] Target tahunan harus sama dengan jumlah bulanan atau boleh berbeda.
- [ ] CMS satu target bersama sudah disepakati; apakah perlu rincian kontribusi tiap divisi. Saat ini hanya total bersama.
- [ ] Apakah perlu koreksi closing oleh Head Funding; saat ini closing tidak dapat dibuka kembali.
- [ ] Realisasi layanan cukup rekap unit bulanan atau perlu catatan nasabah/tanggal aktivasi.
- [ ] Server tujuan, pengguna serentak, dan penanggung jawab backup ketika mulai dipakai nyata.

## Pekerjaan lanjutan yang perlu dievaluasi

1. Sepakati keputusan bisnis yang masih terbuka pada daftar di atas.
2. Tentukan apakah data prototipe lama di browser perlu diimpor ke MySQL.
3. Ganti akun dan password demo sebelum dipakai dengan data nyata.
4. Tentukan server tujuan, backup database, dan proses pemulihan.
5. Jalankan uji penerimaan bersama PIC menggunakan skenario pada dokumen API dan pengujian.

## Bukti dan batas pemeriksaan

Sumber utama: `frontend/src`, route/controller/model/migration di `backend`, serta hasil pengujian otomatis. Lihat [hasil pemeriksaan](CHECKS.md) untuk ringkasan validasi terbaru.
