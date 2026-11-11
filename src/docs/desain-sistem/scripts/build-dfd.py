"""Build logical DFDs as editable SVG, Mermaid, and an offline HTML viewer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STORES = {
    'D1': ('Akun dan token', 'users; personal_access_tokens'),
    'D2': ('Referensi bisnis', 'divisions; products; division_products; target_scopes'),
    'D3': ('Peluang dan penugasan', 'opportunities; opportunity_assignments'),
    'D4': ('Target dan realisasi layanan', 'annual_targets; monthly_targets; unit_realizations; branch_targets'),
    'D5': ('Riwayat perubahan', 'audit_events'),
}

# A row is a process and its external boundary packet, plus actual logical reads/writes.
LEVEL1 = [
    ('1.0', 'Autentikasi dan sesi', 'Akses dan sesi', 'Hasil akses dan sesi', [
        ('D1', 'Akun dan token tersimpan', 'Token baru / pencabutan token')]),
    ('2.0', 'Sajikan data referensi', 'Permintaan referensi', 'Daftar referensi', [
        ('D2', 'Divisi dan produk tersedia', None), ('D1', 'Daftar PIC sesuai divisi', None)]),
    ('3.0', 'Kelola pipeline', 'Data dan permintaan pipeline', 'Hasil dan informasi pipeline', [
        ('D2', 'Referensi produk dan divisi', None),
        ('D1', 'PIC dan nama pelaku', None),
        ('D3', 'Peluang dan penugasan', 'Peluang / penugasan baru atau berubah'),
        ('D5', 'Timeline perubahan peluang', 'Audit pembuatan / perubahan / closing')]),
    ('4.0', 'Kelola target dan layanan', 'Data dan permintaan target', 'Hasil dan informasi target', [
        ('D2', 'Produk, divisi, dan scope', None),
        ('D4', 'Target dan realisasi tersimpan', 'Target / realisasi layanan tersimpan'),
        ('D5', None, 'Audit target / realisasi layanan')]),
    ('5.0', 'Sajikan laporan dan rekap', 'Permintaan laporan', 'Laporan dan rekap', [
        ('D1', 'Identitas PIC dan divisi', None),
        ('D2', 'Referensi divisi dan produk', None),
        ('D3', 'Peluang dan riwayat penugasan', None),
        ('D4', 'Target dan realisasi layanan', None)]),
]

LEVEL2 = [
    ('3.1', 'Sajikan daftar dan detail', 'Kriteria pencarian / ID peluang', 'Daftar, detail, dan timeline', [
        ('D1', 'PIC dan nama pelaku', None), ('D2', 'Nama produk dan divisi', None),
        ('D3', 'Peluang dan penugasan', None), ('D5', 'Timeline perubahan peluang', None)]),
    ('3.2', 'Catat peluang baru', 'Data peluang baru', 'Peluang Active / hasil validasi', [
        ('D1', 'PIC aktif pada divisi', None), ('D2', 'Produk dana dan divisi', None),
        ('D3', None, 'Peluang Active dan penugasan awal'), ('D5', None, 'Audit pembuatan peluang')]),
    ('3.3', 'Ubah peluang dan PIC', 'Perubahan peluang dan versi', 'Peluang terbaru / hasil validasi', [
        ('D1', 'PIC aktif pada divisi', None), ('D2', 'Produk dana dan divisi', None),
        ('D3', 'Peluang dan penugasan saat ini', 'Peluang dan perubahan penugasan'),
        ('D5', None, 'Audit perubahan peluang')]),
    ('3.4', 'Selesaikan tindak lanjut', 'ID peluang dan versi', 'Hasil penyelesaian tindak lanjut', [
        ('D1', 'Identitas PIC', None), ('D2', 'Nama produk dan divisi', None),
        ('D3', 'Peluang dan jadwal tindak lanjut', 'Status tindak lanjut dan versi baru'),
        ('D5', None, 'Audit penyelesaian tindak lanjut')]),
    ('3.5', 'Tutup peluang Won / Lost', 'Hasil closing, tanggal, nilai / alasan, versi', 'Hasil closing / hasil validasi', [
        ('D1', 'Identitas PIC', None), ('D2', 'Nama produk dan divisi', None),
        ('D3', 'Peluang aktif dan versi saat ini', 'Won / Lost, realisasi, tanggal, catatan'),
        ('D5', None, 'Audit closing Won / Lost')]),
]

LEVEL3 = [
    ('P351', '3.5.1', 'Periksa peluang dan versi'),
    ('P352', '3.5.2', 'Validasi Won / Lost'),
    ('P353', '3.5.3', 'Simpan hasil closing'),
    ('P354', '3.5.4', 'Catat audit closing'),
    ('P355', '3.5.5', 'Sajikan hasil closing'),
]

# Boundary flow labels are taken from the parent instead of relying on store order.
CLOSING_STORES = {code: (read, write) for code, read, write in LEVEL2[-1][4]}
LEVEL3_EDGES = [
    ('E1', 'P351', LEVEL2[-1][2]),
    ('E2', 'P351', LEVEL2[-1][2]),
    ('D3', 'P351', CLOSING_STORES['D3'][0]),
    ('P351', 'E1', 'Hasil validasi / konflik'),
    ('P351', 'E2', 'Hasil validasi / konflik'),
    ('P351', 'P352', 'Data closing terverifikasi dan peluang awal'),
    ('P352', 'E1', 'Hasil validasi Won / Lost'),
    ('P352', 'E2', 'Hasil validasi Won / Lost'),
    ('P352', 'P353', 'Data closing valid dan snapshot awal'),
    ('P353', 'D3', CLOSING_STORES['D3'][1]),
    ('P353', 'P354', 'Snapshot sebelum / sesudah dan pelaku'),
    ('P354', 'D5', CLOSING_STORES['D5'][1]),
    ('P354', 'P355', 'Data hasil closing yang tersimpan'),
    ('D1', 'P355', CLOSING_STORES['D1'][0]),
    ('D2', 'P355', CLOSING_STORES['D2'][0]),
    ('P355', 'E1', 'Hasil closing dan versi baru'),
    ('P355', 'E2', 'Hasil closing dan versi baru'),
]


if __name__ == "__main__":
    from dfd_layout import build
    build(ROOT, LEVEL1, LEVEL2, LEVEL3, LEVEL3_EDGES, STORES)
