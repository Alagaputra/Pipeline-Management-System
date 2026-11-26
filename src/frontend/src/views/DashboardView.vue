<script setup>
import { computed, ref } from 'vue'
import { productColor } from '../utils/productColors'
import YearFilter from '../components/YearFilter.vue'
import StatusBadge from '../components/StatusBadge.vue'
import ReportChart from '../components/ReportChart.vue'
import FollowUpQueue from '../components/FollowUpQueue.vue'
import OpportunityDrawer from '../components/OpportunityDrawer.vue'
import { usePipeline } from '../composables/usePipeline'
import { moneyInMillions, percent, STATUSES } from '../utils/pipeline'
import { UNIT_PRODUCTS } from '../data/access'
import { formatInteger, sumAmounts } from '../utils/amounts'
const { dashboard, selectedYear, division, canEdit, isHead, annualTargets, getUnitTarget } =
  usePipeline()
// Angka laporan dihitung backend; halaman ini mengubah hasilnya menjadi kartu/grafik.
const summary = computed(() => dashboard.value?.summary || [])
const targetPeriod = ref('year')
const selectedMonth = ref(new Date().getMonth() + 1)
const serviceTargets = computed(() =>
  UNIT_PRODUCTS.filter((product) => division.value !== 'Komersil' || product === 'CMS').map(
    (product) => {
      const target = getUnitTarget(product, selectedYear.value)
      return {
        ...target,
        product,
        realization: sumAmounts([
          ...Object.values(target.monthly).map((item) => item.realization),
          ...Object.values(dashboard.value?.service_realizations?.[product] || {}),
        ]),
        currentMonth: {
          target: target.monthly[selectedMonth.value]?.target || 0,
          realization: sumAmounts([
            target.monthly[selectedMonth.value]?.realization || 0,
            dashboard.value?.service_realizations?.[product]?.[selectedMonth.value] || 0,
          ]),
        },
      }
    },
  ),
)
const progressRows = computed(() => {
  const monthly = targetPeriod.value === 'month'
  const month = selectedMonth.value
  const allocations = annualTargets.value[selectedYear.value]?.monthly?.[month] || {}
  const funds = summary.value.map((item) => ({
    product: item.product,
    target: monthly ? allocations[item.product] || 0 : item.target,
    realization: monthly ? item.monthly_realizations?.[month] || 0 : item.realization,
  }))
  const services = serviceTargets.value.map((item) => ({
    product: item.product,
    unit: true,
    target: monthly ? item.currentMonth.target : item.target,
    realization: monthly ? item.currentMonth.realization : item.realization,
  }))
  return [...funds, ...services].map((row) => ({
    ...row,
    percentage: row.target > 0 ? (row.realization / row.target) * 100 : null,
  }))
})
const formatValue = (value, unit) =>
  unit ? formatInteger(value) + ' unit' : moneyInMillions(value)
const selectedOpportunity = ref(null)
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
const interestColors = { Cold: '#80a6d8', Warm: '#e3b862', Hot: '#d7758b' }
const interestSummary = computed(() => {
  const total = STATUSES.reduce(
    (sum, status) => sum + Number(dashboard.value?.interest[status] || 0),
    0,
  )
  return STATUSES.map((status) => {
    const count = Number(dashboard.value?.interest[status] || 0)
    return {
      status,
      count,
      percentage: total ? (count / total) * 100 : 0,
      color: interestColors[status],
    }
  })
})
const interestGradient = computed(() => {
  const [cold, warm] = interestSummary.value
  if (!dashboard.value?.active_opportunities) return '#eeeaf3'
  return `conic-gradient(${interestColors.Cold} 0% ${cold.percentage}%, ${interestColors.Warm} ${cold.percentage}% ${cold.percentage + warm.percentage}%, ${interestColors.Hot} ${cold.percentage + warm.percentage}% 100%)`
})
const trendChart = computed(() => ({
  // Pertahankan null dari backend untuk bulan mendatang agar grafik menyisakan celah.
  labels: months,
  datasets: [
    {
      label: 'Nominal peluang dicatat',
      data: (dashboard.value?.trend || []).map((item) =>
        item.recorded_nominal === null ? null : item.recorded_nominal / 1e6,
      ),
      borderColor: '#7451ca',
      backgroundColor: '#7451ca',
      tension: 0.2,
    },
    {
      label: 'Realisasi Won',
      data: (dashboard.value?.trend || []).map((item) =>
        item.realization === null ? null : item.realization / 1e6,
      ),
      borderColor: '#389585',
      backgroundColor: '#389585',
      tension: 0.2,
    },
  ],
}))
</script>
<template>
  <div class="page-heading">
    <div>
      <h1>Dashboard</h1>
    </div>
    <YearFilter />
  </div>
  <template v-if="dashboard">
    <dl class="dashboard-metrics">
      <div class="panel dashboard-metric dashboard-realization">
        <dt>Realisasi dana Won {{ selectedYear }}</dt>
        <dd>{{ moneyInMillions(dashboard.realization) }}</dd>
        <dd class="metric-note">
          {{
            dashboard.total_target
              ? percent(dashboard.percentage) + ' dari target tahunan'
              : 'Target tahunan belum ditetapkan'
          }}
        </dd>
        <dd
          v-if="dashboard.total_target"
          class="achievement-track"
          role="progressbar"
          aria-label="Pencapaian target tahunan"
          aria-valuemin="0"
          :aria-valuemax="Math.max(100, Math.ceil(dashboard.percentage || 0))"
          :aria-valuenow="Math.round(dashboard.percentage || 0)"
          :aria-valuetext="percent(dashboard.percentage)"
        >
          <span :style="{ width: Math.min(100, dashboard.percentage || 0) + '%' }"></span>
        </dd>
        <dd class="metric-note">
          Target {{ moneyInMillions(dashboard.total_target) }} · {{ dashboard.won }} Won ·
          {{ dashboard.lost }} Lost
        </dd>
      </div>
      <div class="panel dashboard-metric">
        <dt>Realisasi unit Won {{ selectedYear }}</dt>
        <dd>{{ formatInteger(dashboard.realized_units) }} unit</dd>
        <dd class="metric-note">{{ serviceTargets.map((item) => item.product).join(' · ') }}</dd>
      </div>
      <div class="panel dashboard-metric">
        <dt>Potensi dana aktif</dt>
        <dd>{{ moneyInMillions(dashboard.active_nominal) }}</dd>
        <dd class="metric-note">{{ dashboard.active_opportunities }} peluang dari semua tahun</dd>
      </div>
    </dl>
    <div class="dashboard-content">
      <div class="dashboard-main">
        <section class="panel dashboard-section trend-panel">
          <header class="section-header">
            <div>
              <h2>Perkembangan pipeline</h2>
            </div>
          </header>
          <ReportChart
            type="line"
            integer-axis
            :data="trendChart"
            label="Nilai peluang yang dicatat dan realisasi Won setiap bulan"
          />
        </section>
        <section class="panel dashboard-section">
          <header class="section-header">
            <div>
              <h2>Ketertarikan nasabah</h2>
              <p>Peluang aktif dari semua tahun</p>
            </div>
          </header>
          <div class="interest-content">
            <div
              class="interest-donut"
              :style="{ background: interestGradient }"
              role="img"
              :aria-label="
                'Total ' +
                dashboard.active_opportunities +
                ' peluang aktif. ' +
                interestSummary
                  .map((item) => item.status + ' ' + item.count + ' peluang')
                  .join(', ')
              "
            >
              <div class="donut-center">
                <strong>{{ dashboard.active_opportunities }}</strong>
                <span>peluang aktif</span>
              </div>
            </div>
            <div class="interest-list">
              <div v-for="item in interestSummary" :key="item.status">
                <StatusBadge :status="item.status" />
                <strong>{{ item.count }} peluang</strong>
                <span>{{ percent(item.percentage) }}</span>
              </div>
            </div>
          </div>
          <p v-if="!dashboard.active_opportunities" class="empty-note">Belum ada peluang aktif.</p>
        </section>
      </div>
      <aside class="dashboard-aside">
        <FollowUpQueue
          :rows="dashboard.follow_ups.slice(0, 3)"
          :count="dashboard.follow_up_count"
          @open="selectedOpportunity = $event"
        />
      </aside>
    </div>
    <section class="panel dashboard-section product-section">
      <header class="section-header">
        <div>
          <h2>Progres target {{ selectedYear }}</h2>
        </div>
        <div class="service-filter">
          <div class="period-switch" role="group" aria-label="Periode target">
            <button
              type="button"
              :aria-pressed="targetPeriod === 'year'"
              @click="targetPeriod = 'year'"
            >
              Tahunan
            </button>
            <button
              type="button"
              :aria-pressed="targetPeriod === 'month'"
              @click="targetPeriod = 'month'"
            >
              Bulanan
            </button>
          </div>
          <label v-if="targetPeriod === 'month'"
            >Bulan
            <select v-model.number="selectedMonth" aria-label="Bulan target unit">
              <option v-for="(month, index) in months" :key="month" :value="index + 1">
                {{ month }}
              </option>
            </select>
          </label>
          <RouterLink to="/target" class="text-button">Kelola target</RouterLink>
        </div>
      </header>
      <div v-if="progressRows.length" class="progress-list">
        <div class="progress-head" aria-hidden="true">
          <span>Produk</span><span>Realisasi / target</span><span>Pencapaian</span>
        </div>
        <article
          v-for="item in progressRows"
          :key="item.product"
          class="product-progress"
          :data-measure="item.unit ? 'unit' : 'idr'"
          :aria-label="(item.unit ? 'Target unit ' : 'Target ') + item.product"
        >
          <div class="progress-label">
            <h3>{{ item.product }}</h3>
            <small v-if="item.product === 'CMS'">Bersama</small>
          </div>
          <div class="progress-numbers">
            <span class="mobile-caption">Realisasi </span>
            <strong data-metric="realization">{{
              formatValue(item.realization, item.unit)
            }}</strong>
            / <span data-metric="target">{{ formatValue(item.target, item.unit) }}</span>
          </div>
          <div class="progress-value">
            <progress
              v-if="item.target > 0"
              :aria-label="'Pencapaian ' + targetPeriod + ' ' + item.product"
              :aria-valuetext="percent(item.percentage)"
              :value="Math.min(100, item.percentage)"
              max="100"
              :style="{ '--fill': productColor(item.product) }"
            ></progress>
            <strong v-if="item.target > 0">{{ percent(item.percentage) }}</strong>
            <RouterLink
              v-else-if="canEdit || (item.product === 'CMS' && isHead)"
              class="text-button unset-target"
              :aria-label="'Tetapkan target ' + item.product"
              :to="{
                path: '/target',
                query: {
                  ...(item.unit
                    ? { editUnit: item.product }
                    : { edit: '1', product: item.product }),
                  year: String(selectedYear),
                  ...(targetPeriod === 'month' ? { month: String(selectedMonth) } : {}),
                },
              }"
            >
              Tetapkan target
            </RouterLink>
            <span v-else class="unset-target">Belum ada target</span>
          </div>
        </article>
      </div>
      <p v-else class="empty-note">Belum ada produk untuk ditampilkan.</p>
    </section>
    <OpportunityDrawer
      v-if="selectedOpportunity !== null"
      :id="selectedOpportunity"
      initial-action="followup"
      @close="selectedOpportunity = null"
    />
  </template>
</template>
<style scoped>
.dashboard-metrics {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin: 0 0 20px;
}
.dashboard-metric {
  min-width: 0;
  padding: 22px;
}
.dashboard-metric dt,
.metric-note,
.empty-note {
  color: #645a76;
  font-size: 12px;
  line-height: 1.5;
}
.dashboard-metric dd {
  margin: 10px 0 0;
  overflow-wrap: anywhere;
  font:
    800 clamp(21px, 2.3vw, 30px) Manrope,
    sans-serif;
  font-variant-numeric: tabular-nums;
}
.dashboard-metric .metric-note {
  margin-top: 6px;
  font: inherit;
  font-size: 12px;
}
.dashboard-realization {
  background: #f0faf5;
  border-color: #dceee3;
}
.dashboard-metric .achievement-track {
  margin: 12px 0 0;
  height: 6px;
  background: #dceee3;
  border-radius: 8px;
  overflow: hidden;
}
.achievement-track span {
  display: block;
  height: 100%;
  background: #33926c;
  border-radius: inherit;
}
.dashboard-content {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  align-items: start;
  gap: 20px;
}
.dashboard-main {
  display: grid;
  gap: 20px;
  min-width: 0;
}
.dashboard-aside {
  min-width: 0;
}
.dashboard-aside :deep(.work-queue) {
  margin: 0;
}
.dashboard-aside :deep(.panel-heading) {
  align-items: flex-start;
  flex-wrap: wrap;
}
.dashboard-aside :deep(.queue-row) {
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
}
.dashboard-aside :deep(.queue-row .button) {
  justify-self: end;
}
.dashboard-aside :deep(.queue-empty) {
  flex-wrap: wrap;
}
.dashboard-section {
  min-width: 0;
  padding: 24px;
}
.section-header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 22px;
}
.section-header h2 {
  font-size: 16px;
}
.section-header p {
  color: #716b80;
  font-size: 12px;
  margin-top: 5px;
}
.interest-content {
  display: flex;
  align-items: center;
  gap: 28px;
}
.interest-donut {
  width: 172px;
  aspect-ratio: 1;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
}
.donut-center {
  display: grid;
  place-content: center;
  text-align: center;
  width: 70%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #fff;
}
.donut-center strong {
  font:
    800 26px Manrope,
    sans-serif;
}
.donut-center span {
  color: #716b80;
  font-size: 12px;
}
.interest-list {
  display: grid;
  flex: 1;
  min-width: 0;
}
.interest-list > div {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: 12px 0;
  border-bottom: 1px solid #eee9f5;
}
.interest-list > div:last-child {
  border-bottom: 0;
}
.interest-list .status-badge {
  margin-right: auto;
}
.interest-list strong {
  font-size: 14px;
}
.interest-list > div > span:last-child {
  color: #716b80;
  font-size: 12px;
}
.empty-note {
  margin-top: 12px;
}
.product-section {
  margin-top: 16px;
  padding: 14px 18px;
}
.product-section .section-header {
  flex-wrap: wrap;
  gap: 4px 12px;
  margin-bottom: 4px;
}
.period-switch {
  display: inline-flex;
  padding: 3px;
  background: #eeeaf3;
  border-radius: 8px;
}
.period-switch button {
  border: 0;
  background: transparent;
  padding: 5px 10px;
  border-radius: 6px;
  font: inherit;
  font-size: 13px;
  cursor: pointer;
}
.period-switch button[aria-pressed='true'] {
  background: white;
  color: #7451ca;
  font-weight: 700;
}
.unset-target {
  grid-column: 1 / -1;
  justify-self: start;
}
.service-filter {
  min-width: 0;
  flex-wrap: wrap;
  display: flex;
  align-items: center;
  gap: 12px;
}
.service-filter label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #716b80;
  font-size: 12px;
}
.progress-head,
.product-progress {
  display: grid;
  grid-template-columns: minmax(95px, 0.8fr) minmax(120px, 1fr) minmax(120px, 1.2fr);
  align-items: center;
  gap: 18px;
}
.progress-head {
  padding: 8px 0;
  color: #716b80;
  font-size: 12px;
}
.product-progress {
  padding: 8px 0;
  border-top: 1px solid #eee9f5;
  font-variant-numeric: tabular-nums;
}
.progress-label h3 {
  margin: 0;
  font-size: 14px;
}
.progress-label small,
.month-detail {
  color: #716b80;
  font-size: 12px;
}
.month-detail {
  display: grid;
  gap: 1px;
  justify-items: start;
}
.progress-value {
  display: grid;
  grid-template-columns: minmax(24px, 1fr) auto;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.progress-numbers {
  font-size: 13px;
}
.mobile-caption {
  display: none;
}
.product-progress progress,
.empty-track {
  display: block;
  appearance: none;
  width: 100%;
  height: 8px;
  margin: 3px 0;
  border: 0;
  border-radius: 4px;
  overflow: hidden;
  background: #eeeaf3;
}
.product-progress progress::-webkit-progress-bar {
  background: #eeeaf3;
}
.product-progress progress::-webkit-progress-value {
  background: var(--fill);
  border-radius: 4px;
}
.product-progress progress::-moz-progress-bar {
  background: var(--fill);
  border-radius: 4px;
}
@media (max-width: 900px) {
  .progress-head {
    display: none;
  }
  .mobile-caption {
    display: inline;
  }
  .product-progress {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    grid-template-areas: 'product bar' 'annual annual';
    gap: 3px 12px;
  }
  .progress-label {
    grid-area: product;
  }
  .progress-label h3,
  .progress-label small {
    display: inline;
    margin-right: 4px;
  }
  .progress-value {
    grid-area: bar;
  }
  .progress-numbers {
    grid-area: annual;
  }
  .month-detail {
    grid-area: monthly;
    display: flex;
    flex-wrap: wrap;
    gap: 2px 10px;
  }
}
@media (min-width: 761px) and (max-width: 1100px) {
  .dashboard-content {
    grid-template-columns: minmax(0, 1fr);
  }
}
@media (max-width: 760px) {
  .dashboard-content {
    grid-template-columns: minmax(0, 1fr);
  }
  .dashboard-aside {
    order: -1;
  }
}
@media (max-width: 620px) {
  .dashboard-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .dashboard-realization {
    grid-column: 1 / -1;
  }
  .dashboard-metric,
  .dashboard-section {
    padding: 18px;
  }
  .interest-list {
    gap: 0;
  }
  .interest-list > div {
    padding: 10px 0;
  }
  .interest-list strong {
    font-size: 12px;
  }
}
@media (max-width: 420px) {
  .interest-content {
    flex-direction: column;
    gap: 14px;
  }
  .interest-list {
    width: 100%;
  }
}
</style>
