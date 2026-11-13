<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Concerns\AuthorizesDivision;
use App\Models\Opportunity;
use App\Models\OpportunityAssignment;
use App\Models\AuditEvent;
use App\Models\Product;
use App\Models\User;
use App\Support\WritesAudit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;

class OpportunityController extends Controller
{
    use AuthorizesDivision, WritesAudit;

    public function index(Request $request)
    {
        // Muat relasi untuk frontend, batasi divisi, lalu terapkan filter/sort/paginasi.
        $query = Opportunity::with(['division:id,code,name', 'pic:id,name,username', 'product:id,code,name,measure', 'assignments.pic:id,name']);
        if (!$request->user()->isHead()) $query->where('division_id', $request->user()->division_id);
        elseif ($request->filled('division_id')) $query->where('division_id', $request->integer('division_id'));
        if ($request->filled('outcome')) $query->whereIn('outcome', (array) $request->input('outcome'));
        if ($request->filled('pic_id')) $query->where('pic_id', $request->integer('pic_id'));
        if ($request->filled('product_id')) $query->where('product_id', $request->integer('product_id'));
        if ($request->filled('search')) {
            $term = '%'.str_replace(['%', '_'], ['\\%', '\\_'], $request->string('search')).'%';
            $query->where(fn ($q) => $q->where('customer_name', 'like', $term)->orWhere('legacy_id', 'like', $term));
        }
        $sort = in_array($request->input('sort'), ['updated_at', 'recorded_date', 'nominal', 'customer_name'], true) ? $request->input('sort') : 'updated_at';
        $direction = $request->input('direction') === 'asc' ? 'asc' : 'desc';
        return $query->orderBy($sort, $direction)->paginate(min(max($request->integer('per_page', 20), 1), 100));
    }

    public function show(Request $request, int $id)
    {
        // Detail mencakup timeline audit; ID PIC/produk pada snapshot dilengkapi nama.
        $opportunity = $this->visibleOpportunity($request, $id)->load(['division', 'pic', 'product', 'assignments.pic']);
        $opportunity->setAttribute('timeline', AuditEvent::with('actor:id,name')->where('resource_type', 'opportunity')->where('resource_id', (string) $id)->orderBy('occurred_at')->orderBy('id')->get());
        $opportunity->timeline->each(function ($event) {
            foreach (['before_data', 'after_data'] as $side) {
                $snapshot = $event->{$side};
                if (!$snapshot) continue;
                if (isset($snapshot['pic_id'])) $snapshot['pic'] = ['name' => User::whereKey($snapshot['pic_id'])->value('name')];
                if (isset($snapshot['product_id'])) $snapshot['product'] = ['name' => Product::whereKey($snapshot['product_id'])->value('name')];
                $event->{$side} = $snapshot;
            }
        });
        return $opportunity;
    }

    public function store(Request $request)
    {
        // Peluang baru selalu Active. Peluang, penugasan PIC, dan audit dibuat
        // dalam satu transaksi agar tidak ada catatan pendukung yang tertinggal.
        $divisionId = $this->divisionId($request);
        $data = $this->validated($request, $divisionId);
        return DB::transaction(function () use ($request, $divisionId, $data) {
            $opportunity = Opportunity::create([...$data, 'division_id' => $divisionId, 'outcome' => 'Active', 'realization' => 0, 'created_by' => $request->user()->id, 'updated_by' => $request->user()->id]);
            OpportunityAssignment::create(['opportunity_id' => $opportunity->id, 'pic_id' => $opportunity->pic_id, 'assigned_at' => now(), 'changed_by' => $request->user()->id]);
            $this->audit($request->user()->id, 'opportunity', $opportunity->id, 'created', null, $opportunity->toArray());
            return response()->json($opportunity->load(['division', 'pic', 'product']), 201);
        });
    }

    public function update(Request $request, int $id)
    {
        // Hanya peluang aktif yang dapat diedit. version dari frontend harus cocok
        // dengan versi terkini agar perubahan pengguna lain tidak tertimpa.
        $opportunity = $this->visibleOpportunity($request, $id);
        abort_if($opportunity->outcome !== 'Active', 409, 'Opportunity sudah closing.');
        $request->validate(['version' => ['required', 'integer', 'min:1']]);
        abort_if((int) $request->version !== (int) $opportunity->version, 409, 'Data telah berubah. Muat ulang sebelum menyimpan.');
        $divisionId = $this->divisionId($request, $opportunity->division_id);
        $data = $this->validated($request, $divisionId, $opportunity->segment === 'Small');
        if (($data['follow_up_date'] ?? null) !== $opportunity->follow_up_date?->format('Y-m-d')) {
            // Jadwal yang berubah menjadi tugas follow-up baru yang belum selesai.
            $data['follow_up_completed'] = false;
        }
        return DB::transaction(function () use ($request, $opportunity, $data) {
            // Periksa ulang setelah row terkunci: data bisa berubah sejak validasi awal.
            $opportunity = $this->visibleOpportunity($request, $opportunity->id, true);
            abort_if($opportunity->outcome !== 'Active' || (int) $request->version !== (int) $opportunity->version, 409, 'Data telah berubah. Muat ulang.');
            $before = $opportunity->toArray();
            $oldPic = $opportunity->pic_id;
            $opportunity->update([...$data, 'updated_by' => $request->user()->id, 'version' => $opportunity->version + 1]);
            if ($oldPic !== $opportunity->pic_id) {
                // Tutup penugasan lama dan buat penugasan baru, tanpa menghapus riwayat PIC.
                OpportunityAssignment::where('opportunity_id', $opportunity->id)->whereNull('unassigned_at')->update(['unassigned_at' => now()]);
                OpportunityAssignment::create(['opportunity_id' => $opportunity->id, 'pic_id' => $opportunity->pic_id, 'assigned_at' => now(), 'changed_by' => $request->user()->id]);
            }
            $this->audit($request->user()->id, 'opportunity', $opportunity->id, 'updated', $before, $opportunity->toArray());
            return $opportunity->load(['division', 'pic', 'product']);
        });
    }

    public function completeFollowUp(Request $request, int $id)
    {
        // Penyelesaian tugas tidak menutup peluang; cukup ubah penanda dan naikkan version.
        return DB::transaction(function () use ($request, $id) {
            $opportunity = $this->visibleOpportunity($request, $id, true);
            $data = $request->validate(['version' => ['required', 'integer', 'min:1']]);
            abort_if($opportunity->outcome !== 'Active' || !$opportunity->follow_up_date || $opportunity->follow_up_completed, 409, 'Follow-up tidak dapat diselesaikan.');
            abort_if($data['version'] !== $opportunity->version, 409, 'Data telah berubah. Muat ulang.');
            $before = $opportunity->toArray();
            $opportunity->update(['follow_up_completed' => true, 'updated_by' => $request->user()->id, 'version' => $opportunity->version + 1]);
            $this->audit($request->user()->id, 'opportunity', $id, 'follow_up_completed', $before, $opportunity->toArray());
            return $opportunity->load(['division', 'pic', 'product', 'assignments.pic']);
        });
    }

    public function close(Request $request, int $id)
    {
        // Closing bersifat final di API ini: Won wajib realisasi positif,
        // Lost wajib alasan dan realisasi nol. Peluang selesai tampil di Riwayat.
        return DB::transaction(function () use ($request, $id) {
            $opportunity = $this->visibleOpportunity($request, $id, true);
            abort_if($opportunity->outcome !== 'Active', 409, 'Opportunity sudah closing.');
            $data = $request->validate([
                'outcome' => ['required', Rule::in(['Won', 'Lost'])],
                'realization' => ['nullable', 'integer', 'min:0'],
                'closed_date' => ['required', 'date', 'after_or_equal:'.$opportunity->recorded_date->format('Y-m-d'), 'before_or_equal:today'],
                'lost_reason' => ['nullable', 'string', 'max:2000'],
                'version' => ['required', 'integer', 'min:1'],
                'notes' => ['sometimes', 'nullable', 'string', 'max:5000'],
            ]);
            abort_if($data['version'] !== $opportunity->version, 409, 'Data telah berubah. Muat ulang.');
            if ($data['outcome'] === 'Won') {
                abort_unless(($data['realization'] ?? 0) > 0, 422, 'Realisasi Won harus lebih dari nol.');
                $data['lost_reason'] = null;
            } else {
                abort_if(blank($data['lost_reason'] ?? null), 422, 'Alasan Lost wajib diisi.');
                $data['realization'] = 0;
            }
            unset($data['version']);
            $before = $opportunity->toArray();
            $opportunity->update([...$data, 'updated_by' => $request->user()->id, 'version' => $opportunity->version + 1]);
            $this->audit($request->user()->id, 'opportunity', $id, 'closed_'.strtolower($opportunity->outcome), $before, $opportunity->toArray());
            return $opportunity->load(['division', 'pic', 'product']);
        });
    }

    private function validated(Request $request, int $divisionId, bool $legacySmall = false): array
    {
        // Selain format input, pastikan PIC aktif dan produk rupiah tersedia di divisi.
        // Segmen Small hanya diizinkan untuk mempertahankan data lama yang sudah memakainya.
        $data = $request->validate([
            'pic_id' => ['required', 'integer'], 'product_id' => ['required', 'integer'],
            'customer_name' => ['required', 'string', 'max:160'], 'segment' => ['required', Rule::in($legacySmall ? ['Small', 'Mid', 'Large'] : ['Mid', 'Large'])],
            'nominal' => ['required', 'integer', 'min:1'], 'interest_status' => ['required', Rule::in(['Cold', 'Warm', 'Hot'])],
            'recorded_date' => ['required', 'date', 'before_or_equal:today'], 'follow_up_date' => ['nullable', 'date', 'after_or_equal:recorded_date'],
            'notes' => ['nullable', 'string', 'max:5000'],
        ]);
        abort_unless(User::whereKey($data['pic_id'])->where('role', 'pic')->where('is_active', true)->where('division_id', $divisionId)->exists(), 422, 'PIC tidak tersedia untuk divisi ini.');
        abort_unless(Product::whereKey($data['product_id'])->where('measure', 'IDR')->where('is_active', true)->whereHas('divisions', fn ($q) => $q->whereKey($divisionId))->exists(), 422, 'Produk tidak tersedia untuk divisi ini.');
        return $data;
    }
}
