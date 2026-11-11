<script setup>
import { computed, reactive, ref, nextTick } from 'vue'
import { confirmAction } from '../composables/useConfirm'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import MoneyInput from './MoneyInput.vue'
import AppDrawer from './AppDrawer.vue'
import AppIcon from './AppIcon.vue'
import StatusBadge from './StatusBadge.vue'
import OpportunityTimeline from './OpportunityTimeline.vue'
import { usePipeline } from '../composables/usePipeline'
import { useSession } from '../composables/useSession'
import {
  pipelineFieldErrors,
  STATUSES,
  SEGMENTS,
  money,
  compactMoney,
  dateLabel,
  timeLabel,
  localDate,
  isClosed,
} from '../utils/pipeline'
const props = defineProps({
  id: { type: String, default: '' },
  initialAction: { type: String, default: '' },
})
const emit = defineEmits(['close', 'saved'])
const {
  rows,
  save,
  complete,
  products: PRODUCTS,
  people: PEOPLE,
  canEdit,
  refresh,
  storageError,
} = usePipeline()
const current = computed(() => rows.value.find((row) => row.id === props.id))
const editing = ref(!props.id || props.initialAction === 'followup')
const closing = ref(false)
const followupOnly = ref(props.initialAction === 'followup')
const error = ref('')
const success = ref('')
const saving = ref(false)
const uncertain = ref(false)
const conflict = ref(false)
const requestKey = ref(crypto.randomUUID())
const followupKey = ref(crypto.randomUUID())
const reviewing = ref(false)
const fieldErrors = ref({})
const formElement = ref(null)
const fieldAttrs = (key) => ({
  name: key,
  'aria-invalid': Boolean(fieldErrors.value[key]),
  'aria-describedby': fieldErrors.value[key] ? `error-${key}` : undefined,
})
async function focusError() {
  await nextTick()
  formElement.value?.querySelector('[aria-invalid="true"]')?.focus()
}
const form = reactive({ ...blank(), ...(current.value || {}) })
let baseline = JSON.stringify(form)
const dirty = computed(
  () => editing.value && (uncertain.value || JSON.stringify(form) !== baseline),
)
useUnsavedChanges(dirty, saving)
function blank() {
  return {
    customer: '',
    date: localDate(),
    pic: PEOPLE.value.includes(useSession().user.value?.name)
      ? useSession().user.value.name
      : PEOPLE.value[0],
    product: 'Tabungan',
    segment: 'Mid',
    nominal: '',
    status: 'Cold',
    outcome: 'Active',
    followUpDate: '',
    notes: '',
    completed: false,
    closedDate: '',
    realization: '',
    lostReason: '',
  }
}
async function requestClose() {
  if (saving.value) return
  if (
    !dirty.value ||
    (await confirmAction({
      title: 'Tutup formulir?',
      message: uncertain.value
        ? 'Penyimpanan belum dapat dipastikan. Coba lagi untuk memastikan hasilnya sebelum menutup formulir.'
        : 'Perubahan yang belum disimpan akan hilang.',
      confirmLabel: 'Tutup formulir',
    }))
  )
    emit('close')
}
function edit(outcome, action = '') {
  if (saving.value) return
  reviewing.value = false
  uncertain.value = false
  conflict.value = false
  requestKey.value = crypto.randomUUID()
  fieldErrors.value = {}
  closing.value = Boolean(outcome)
  followupOnly.value = action === 'followup'
  Object.assign(form, current.value)
  baseline = JSON.stringify(form)
  editing.value = true
  error.value = ''
  success.value = ''
  if (outcome) {
    form.outcome = outcome
    form.closedDate = localDate()
    form.realization = outcome === 'Won' ? form.nominal : 0
  }
}
async function cancel() {
  if (saving.value) return
  if (dirty.value && !(await confirmAction())) return
  if (!props.id) emit('close')
  else {
    editing.value = false
    error.value = ''
  }
}
async function submit() {
  if (saving.value) return
  const value = { ...form, nominal: Number(form.nominal), realization: Number(form.realization) }
  fieldErrors.value = pipelineFieldErrors(value, {
    legacy: current.value?.segment === 'Small',
    people: PEOPLE.value,
    products: PRODUCTS.value,
  })
  error.value = ''
  if (Object.keys(fieldErrors.value).length) {
    reviewing.value = false
    await focusError()
    return
  }
  if (closing.value && !reviewing.value) {
    reviewing.value = true
    await nextTick()
    formElement.value?.querySelector('[data-review-heading]')?.focus()
    return
  }
  saving.value = true
  try {
    const saved = await save(value, { requestKey: requestKey.value })
    emit('saved', saved)
    emit('close')
  } catch (e) {
    error.value = e.message
    uncertain.value = Boolean(e.uncertain)
    conflict.value = e.status === 409
    const names = {
      customer_name: 'customer',
      recorded_date: 'date',
      pic_id: 'pic',
      product_id: 'product',
      interest_status: 'status',
      follow_up_date: 'followUpDate',
      closed_date: 'closedDate',
      lost_reason: 'lostReason',
    }
    fieldErrors.value = Object.fromEntries(
      Object.entries(e.fields || {}).map(([key, messages]) => [
        names[key] || key,
        Array.isArray(messages) ? messages[0] : messages,
      ]),
    )
    if (Object.keys(fieldErrors.value).length) {
      reviewing.value = false
      await focusError()
    }
  } finally {
    saving.value = false
  }
}
async function finishFollowup() {
  if (saving.value) return
  saving.value = true
  error.value = ''
  try {
    await complete(props.id, { requestKey: followupKey.value })
    followupKey.value = crypto.randomUUID()
    success.value = 'Tindak lanjut ditandai selesai. Peluang tetap aktif.'
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
async function reloadConflict() {
  if (
    !(await confirmAction({
      title: 'Muat data terbaru?',
      message: 'Isian saat ini akan diganti dengan data terbaru.',
      confirmLabel: 'Muat data terbaru',
    }))
  )
    return
  const outcome = closing.value ? form.outcome : undefined
  const action = followupOnly.value ? 'followup' : ''
  await refresh()
  if (storageError.value) {
    error.value = storageError.value
    return
  }
  edit(outcome, action)
}
</script>
<template>
  <AppDrawer
    :title="
      editing
        ? closing
          ? 'Selesaikan peluang'
          : followupOnly
            ? 'Catat tindak lanjut'
            : id
              ? 'Ubah peluang'
              : 'Catat peluang'
        : 'Detail peluang'
    "
    :subtitle="id || 'PIPELINE FUNDING'"
    @close="requestClose"
  >
    <div v-if="id && !current" class="empty-state">Peluang tidak ditemukan.</div>
    <form
      v-else-if="editing"
      ref="formElement"
      novalidate
      :aria-busy="saving"
      @submit.prevent="submit"
    >
      <section v-if="reviewing" class="closing-review" aria-label="Konfirmasi closing">
        <h3 tabindex="-1" data-review-heading>Periksa closing {{ form.outcome }}</h3>
        <p>Pastikan hasil berikut sudah benar sebelum disimpan.</p>
        <dl class="detail-grid">
          <div class="full">
            <dt>Nasabah</dt>
            <dd>{{ form.customer }}</dd>
          </div>
          <div>
            <dt>Produk</dt>
            <dd>{{ form.product }}</dd>
          </div>
          <div>
            <dt>PIC saat closing</dt>
            <dd>{{ form.pic }}</dd>
          </div>
          <div>
            <dt>Tanggal closing</dt>
            <dd>{{ dateLabel(form.closedDate) }}</dd>
          </div>
          <div>
            <dt>Nominal peluang</dt>
            <dd>{{ money(form.nominal) }}</dd>
          </div>
          <div v-if="form.outcome === 'Won'" class="full">
            <dt>Realisasi dana</dt>
            <dd>{{ money(form.realization) }}</dd>
          </div>
          <div v-else class="full">
            <dt>Alasan Lost</dt>
            <dd class="notes">{{ form.lostReason }}</dd>
          </div>
          <div v-if="form.notes" class="full">
            <dt>Catatan</dt>
            <dd class="notes">{{ form.notes }}</dd>
          </div>
        </dl>
        <p class="notice closing-note">
          Peluang akan masuk Riwayat dan tidak bisa diedit setelah closing disimpan.
        </p>
        <p
          v-if="form.outcome === 'Won' && Number(form.realization) < Number(form.nominal)"
          class="notice closing-note"
        >
          Closing akan menutup seluruh peluang; selisih nominal tidak dibuat menjadi peluang aktif
          secara otomatis.
        </p>
      </section>
      <fieldset v-else class="form-fields" :disabled="saving || uncertain">
        <div v-if="!closing && !followupOnly" class="section-heading">
          <span class="section-number">01</span>
          <div>
            <h3>Informasi peluang</h3>
          </div>
        </div>
        <div v-if="!closing && !followupOnly" class="form-grid">
          <label class="full"
            >Nama nasabah<input
              v-model="form.customer"
              required
              maxlength="120"
              placeholder="Contoh: PT Metland"
              v-bind="fieldAttrs('customer')"
            /><small v-if="fieldErrors.customer" :id="'error-customer'" class="field-error">{{
              fieldErrors.customer
            }}</small></label
          >
          <label
            >Tanggal pencatatan<input
              v-model="form.date"
              type="date"
              :max="localDate()"
              required
              v-bind="fieldAttrs('date')"
            /><small v-if="fieldErrors.date" :id="'error-date'" class="field-error">{{
              fieldErrors.date
            }}</small></label
          >
          <label
            >PIC<select v-model="form.pic" aria-label="PIC" v-bind="fieldAttrs('pic')">
              <option v-for="person in PEOPLE" :key="person">{{ person }}</option></select
            ><small v-if="fieldErrors.pic" :id="'error-pic'" class="field-error">{{
              fieldErrors.pic
            }}</small></label
          >
          <label
            >Produk<select v-model="form.product" v-bind="fieldAttrs('product')">
              <option v-for="product in PRODUCTS" :key="product">{{ product }}</option></select
            ><small v-if="fieldErrors.product" :id="'error-product'" class="field-error">{{
              fieldErrors.product
            }}</small></label
          >
          <label
            >Segmentasi<select v-model="form.segment" v-bind="fieldAttrs('segment')">
              <option v-if="form.segment === 'Small'" value="Small">Small (data lama)</option>
              <option v-for="segment in SEGMENTS" :key="segment">{{ segment }}</option></select
            ><small v-if="fieldErrors.segment" :id="'error-segment'" class="field-error">{{
              fieldErrors.segment
            }}</small></label
          >
          <label
            >Nominal peluang (rupiah)<MoneyInput
              v-model="form.nominal"
              aria-label="Nominal peluang (rupiah)"
              required
              v-bind="fieldAttrs('nominal')"
            /><small>{{ compactMoney(Number(form.nominal) || 0) }}</small
            ><small v-if="fieldErrors.nominal" :id="'error-nominal'" class="field-error">{{
              fieldErrors.nominal
            }}</small></label
          >
          <label
            >Status ketertarikan<select v-model="form.status" v-bind="fieldAttrs('status')">
              <option v-for="status in STATUSES" :key="status">{{ status }}</option></select
            ><small v-if="fieldErrors.status" :id="'error-status'" class="field-error">{{
              fieldErrors.status
            }}</small></label
          >
        </div>
        <div v-if="closing || followupOnly" class="drawer-context">
          <h3>{{ current?.customer }}</h3>
          <p>
            {{ current?.product }} · {{ compactMoney(current?.nominal || 0) }} · {{ current?.pic }}
          </p>
        </div>
        <div class="section-heading followup-section">
          <span class="section-number">02</span>
          <div>
            <h3>{{ closing ? 'Hasil peluang' : 'Tindak lanjut' }}</h3>
          </div>
        </div>
        <div class="form-grid">
          <label v-if="closing" class="full"
            >Hasil peluang<select v-model="form.outcome" v-bind="fieldAttrs('outcome')">
              <option value="Won">Won — berhasil</option>
              <option value="Lost">Lost — tidak berlanjut</option></select
            ><small v-if="fieldErrors.outcome" :id="'error-outcome'" class="field-error">{{
              fieldErrors.outcome
            }}</small></label
          >
          <template v-if="form.outcome === 'Active'"
            ><label class="full"
              >Jadwal tindak lanjut<input
                v-model="form.followUpDate"
                type="date"
                :min="form.date"
                v-bind="fieldAttrs('followUpDate')"
              /><small
                v-if="fieldErrors.followUpDate"
                :id="'error-followUpDate'"
                class="field-error"
                >{{ fieldErrors.followUpDate }}</small
              ></label
            ></template
          >
          <template v-else
            ><label
              >Tanggal closing<input
                v-model="form.closedDate"
                required
                type="date"
                :min="form.date"
                :max="localDate()"
                v-bind="fieldAttrs('closedDate')"
              /><small v-if="fieldErrors.closedDate" :id="'error-closedDate'" class="field-error">{{
                fieldErrors.closedDate
              }}</small></label
            ><label v-if="form.outcome === 'Won'"
              >Realisasi dana (rupiah)<MoneyInput
                v-model="form.realization"
                aria-label="Realisasi dana (rupiah)"
                required
                v-bind="fieldAttrs('realization')"
              /><small>{{ compactMoney(Number(form.realization) || 0) }}</small
              ><small
                v-if="fieldErrors.realization"
                :id="'error-realization'"
                class="field-error"
                >{{ fieldErrors.realization }}</small
              ></label
            ><label v-else class="full"
              >Alasan Lost<textarea
                v-model="form.lostReason"
                required
                rows="2"
                maxlength="1000"
                placeholder="Contoh: Nasabah menunda penempatan dana."
                v-bind="fieldAttrs('lostReason')"
              ></textarea
              ><small v-if="fieldErrors.lostReason" :id="'error-lostReason'" class="field-error">{{
                fieldErrors.lostReason
              }}</small></label
            ></template
          >
          <label class="full"
            >Catatan tindak lanjut<textarea
              v-model="form.notes"
              rows="4"
              maxlength="2000"
              placeholder="Tuliskan hasil komunikasi dan langkah berikutnya..."
              v-bind="fieldAttrs('notes')"
            ></textarea>
            <small v-if="fieldErrors.notes" :id="'error-notes'" class="field-error">{{
              fieldErrors.notes
            }}</small></label
          >
        </div>
      </fieldset>
      <p v-if="error" class="notice error" role="alert">
        {{ error }}
        <button v-if="conflict" type="button" class="text-button" @click="reloadConflict">
          Muat data terbaru
        </button>
      </p>
      <div class="form-actions">
        <button
          v-if="reviewing"
          type="button"
          class="button secondary"
          :disabled="saving || uncertain"
          @click="reviewing = false"
        >
          Kembali ke formulir</button
        ><button v-else type="button" class="button secondary" :disabled="saving" @click="cancel">
          Batal</button
        ><button class="button primary" :disabled="saving">
          <AppIcon name="check" :size="17" />{{
            saving
              ? 'Menyimpan...'
              : uncertain
                ? 'Coba lagi'
                : reviewing
                  ? `Konfirmasi closing ${form.outcome}`
                  : form.outcome === 'Active'
                    ? followupOnly
                      ? 'Simpan tindak lanjut'
                      : 'Simpan peluang'
                    : `Simpan closing ${form.outcome}`
          }}
        </button>
      </div>
    </form>
    <template v-else-if="current">
      <div class="detail-customer">
        <span class="product-icon"><AppIcon name="building" :size="25" /></span>
        <div>
          <h3>{{ current.customer }}</h3>
          <p>{{ current.product }} · {{ current.segment }}</p>
        </div>
        <StatusBadge :status="isClosed(current) ? current.outcome : current.status" />
      </div>
      <dl class="detail-grid">
        <div>
          <dt>Tanggal pencatatan</dt>
          <dd>{{ dateLabel(current.date) }}</dd>
        </div>
        <div>
          <dt>PIC {{ isClosed(current) ? 'saat closing' : 'saat ini' }}</dt>
          <dd>{{ current.pic }}</dd>
        </div>
        <div class="full">
          <dt>Nominal peluang</dt>
          <dd class="big-number" :title="money(current.nominal)">
            {{ compactMoney(current.nominal) }}
          </dd>
        </div>
        <div>
          <dt>Status ketertarikan terakhir</dt>
          <dd><StatusBadge :status="current.status" /></dd>
        </div>
        <div>
          <dt>Update terakhir</dt>
          <dd>{{ timeLabel(current.updatedAt) }}</dd>
        </div>
        <template v-if="isClosed(current)"
          ><div>
            <dt>Tanggal closing</dt>
            <dd>{{ dateLabel(current.closedDate) }}</dd>
          </div>
          <div>
            <dt>Realisasi dana</dt>
            <dd :title="money(current.realization)">{{ compactMoney(current.realization) }}</dd>
          </div>
          <div v-if="current.outcome === 'Lost'" class="full">
            <dt>Alasan Lost</dt>
            <dd class="notes">{{ current.lostReason }}</dd>
          </div></template
        >
        <template v-else
          ><div class="full">
            <dt>Tindak lanjut</dt>
            <dd>
              {{ dateLabel(current.followUpDate) }}
              <span v-if="current.completed" class="success-text">· Selesai</span>
            </dd>
          </div></template
        >
        <div class="full">
          <dt>Catatan tindak lanjut</dt>
          <dd class="notes">{{ current.notes || 'Belum ada catatan.' }}</dd>
        </div>
        <div v-if="current.handledBy.length > 1" class="full">
          <dt>PIC yang pernah menangani</dt>
          <dd>{{ current.handledBy.join(', ') }}</dd>
        </div>
      </dl>
      <OpportunityTimeline :id="current.id" :version="current.version" />
      <p v-if="success" class="notice success" role="status">{{ success }}</p>
      <p v-if="error" class="notice error" role="alert">{{ error }}</p>
      <p v-if="!canEdit" class="notice closing-note">
        Pilih divisi {{ current.division }} untuk mengubah peluang ini.
      </p>
      <template v-if="canEdit && !isClosed(current)"
        ><div class="drawer-actions">
          <button type="button" class="button secondary" @click="edit()">
            <AppIcon name="edit" :size="17" />Ubah peluang</button
          ><button
            type="button"
            class="button secondary"
            :disabled="saving"
            @click="edit(undefined, 'followup')"
          >
            Catat tindak lanjut</button
          ><button
            v-if="current.followUpDate && !current.completed"
            type="button"
            class="button primary"
            :disabled="saving"
            @click="finishFollowup"
          >
            <AppIcon name="done" :size="17" />{{
              saving ? 'Menyimpan...' : 'Tindak lanjut selesai'
            }}
          </button>
        </div>
        <div class="close-opportunity">
          <h3>Selesaikan peluang</h3>
          <p>Pilih hasil setelah proses dengan nasabah berakhir.</p>
          <div class="drawer-actions">
            <button type="button" class="button won-button" @click="edit('Won')">Closing Won</button
            ><button type="button" class="button lost-button" @click="edit('Lost')">
              Closing Lost
            </button>
          </div>
        </div></template
      >
      <p v-else-if="isClosed(current)" class="notice closing-note">
        Hasil closing tersimpan di Riwayat. Realisasi dikreditkan kepada PIC saat closing.
      </p>
    </template>
  </AppDrawer>
</template>
