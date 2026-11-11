<script setup>
import { computed, ref } from 'vue'
import TargetCard from '../components/TargetCard.vue'
import AppIcon from '../components/AppIcon.vue'
import YearFilter from '../components/YearFilter.vue'
import StatusBadge from '../components/StatusBadge.vue'
import ReportChart from '../components/ReportChart.vue'
import FollowUpQueue from '../components/FollowUpQueue.vue'
import OpportunityDrawer from '../components/OpportunityDrawer.vue'
import UnitTargets from '../components/UnitTargets.vue'
import { usePipeline } from '../composables/usePipeline'
import { useSession } from '../composables/useSession'
import { compactMoney, percent, STATUSES } from '../utils/pipeline'
const { dashboard, selectedYear } = usePipeline()
const { user } = useSession()
const summary = computed(() => dashboard.value?.summary || [])
const comparisonOpen = ref(false)
const selectedOpportunity = ref(null)
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
const targetChart = computed(() => ({
  labels: summary.value.map((item) => item.product),
  datasets: [
    {
      label: 'Target tahunan',
      data: summary.value.map((item) => item.target / 1e9),
      backgroundColor: '#d9cff7',
      borderRadius: 5,
    },
    {
      label: 'Realisasi Won',
      data: summary.value.map((item) => item.realization / 1e9),
      backgroundColor: '#7451ca',
      borderRadius: 5,
    },
  ],
}))
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
      total,
      percentage: total ? (count / total) * 100 : 0,
      color: interestColors[status],
    }
  })
})
const interestChart = computed(() => ({
  labels: interestSummary.value.map((item) => item.status),
  datasets: [
    {
      data: interestSummary.value.map((item) => item.count),
      backgroundColor: interestSummary.value.map((item) => item.color),
      borderWidth: 0,
    },
  ],
}))
const trendChart = computed(() => ({
  labels: months,
  datasets: [
    {
      label: 'Nominal peluang dicatat',
      data: (dashboard.value?.trend || []).map((item) =>
        item.recorded_nominal === null ? null : item.recorded_nominal / 1e9,
      ),
      borderColor: '#7451ca',
      backgroundColor: '#7451ca',
      tension: 0.2,
    },
    {
      label: 'Realisasi Won',
      data: (dashboard.value?.trend || []).map((item) =>
        item.realization === null ? null : item.realization / 1e9,
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
      <h1>Selamat bekerja, {{ user?.name || 'PIC' }}</h1>
    </div>
    <YearFilter />
  </div>
  <template v-if="dashboard">
    <div class="monitor-cards">
      <article class="panel">
        <span class="metric-icon"><AppIcon name="pipeline" /></span
        ><span>Peluang aktif · semua periode</span
        ><strong>{{ dashboard.active_opportunities }}</strong>
      </article>
      <article class="panel">
        <span class="metric-icon"><AppIcon name="wallet" /></span><span>Nominal potensi aktif</span
        ><strong>{{ compactMoney(dashboard.active_nominal) }}</strong>
      </article>
      <article class="panel">
        <span class="metric-icon warm-text"><AppIcon name="trend" /></span><span>Peluang Hot</span
        ><strong>{{ dashboard.hot_opportunities }}</strong
        ><small>{{ compactMoney(dashboard.hot_nominal) }} potensi aktif</small>
      </article>
      <article class="panel realization-card">
        <span class="metric-icon"><AppIcon name="success" /></span
        ><span>Realisasi Won {{ selectedYear }}</span
        ><strong>{{ compactMoney(dashboard.realization) }}</strong
        ><small>{{
          dashboard.total_target
            ? percent(dashboard.percentage) + ' dari target tim'
            : 'Target tahunan belum ditetapkan'
        }}</small>
      </article>
    </div>
    <FollowUpQueue
      :rows="dashboard.follow_ups"
      :count="dashboard.follow_up_count"
      @open="selectedOpportunity = $event"
    />
    <div class="dashboard-grid">
      <section class="panel annual-panel">
        <div class="panel-heading">
          <div>
            <h2>Target dan realisasi tahunan</h2>
          </div>
          <RouterLink to="/target" class="text-button">Kelola target dana</RouterLink>
        </div>
        <div class="dashboard-targets">
          <TargetCard
            v-for="item in summary"
            :key="item.product"
            :item="item"
            class="dashboard-target-card"
            :label="'Target ' + item.product"
          >
            <template v-if="!item.target" #actions>
              <RouterLink
                class="text-button"
                :aria-label="'Tetapkan target ' + item.product"
                :to="{
                  path: '/target',
                  query: { edit: '1', product: item.product, year: String(selectedYear) },
                }"
                >Tetapkan target <AppIcon name="arrow" :size="14"
              /></RouterLink>
            </template>
          </TargetCard>
        </div>
        <details class="target-comparison" @toggle="comparisonOpen = $event.target.open">
          <summary>Lihat perbandingan grafik</summary>
          <ReportChart
            v-if="comparisonOpen"
            type="bar"
            :data="targetChart"
            label="Perbandingan target tahunan dan realisasi Won per produk"
          />
        </details>
      </section>
      <section class="panel status-panel">
        <div class="panel-heading">
          <div>
            <h2>Ketertarikan nasabah</h2>
          </div>
        </div>
        <ReportChart
          v-if="dashboard.active_opportunities"
          type="doughnut"
          :data="interestChart"
          label="Distribusi peluang aktif Cold, Warm, dan Hot"
        />
        <p v-else class="empty-state">Belum ada peluang aktif.</p>
        <div v-for="item in interestSummary" :key="item.status" class="status-distribution">
          <div>
            <StatusBadge :status="item.status" />
            <div class="interest-counts">
              <strong>{{ item.count }} peluang</strong><span>{{ percent(item.percentage) }}</span>
            </div>
          </div>
          <div
            class="interest-track"
            role="progressbar"
            :aria-label="'Proporsi peluang ' + item.status"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-valuenow="Math.round(item.percentage * 10) / 10"
            :aria-valuetext="`${item.count} dari ${item.total} peluang aktif (${percent(item.percentage)})`"
          >
            <span :style="{ width: item.percentage + '%', backgroundColor: item.color }"></span>
          </div>
        </div>
      </section>
    </div>
    <section class="panel trend-panel">
      <div class="panel-heading">
        <div>
          <h2>Perkembangan nilai pipeline {{ selectedYear }}</h2>
        </div>
      </div>
      <ReportChart
        type="line"
        integer-axis
        :data="trendChart"
        label="Nilai peluang yang dicatat dan realisasi Won setiap bulan"
      />
      <details class="monthly-details">
        <summary><span>Lihat rincian bulanan</span><AppIcon name="right" :size="16" /></summary>
        <div class="report-table-wrap">
          <table class="report-table">
            <thead>
              <tr>
                <th scope="col">Bulan</th>
                <th scope="col" class="monthly-number">Nominal peluang dicatat</th>
                <th scope="col" class="monthly-number">Realisasi Won</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in dashboard.trend" :key="item.month">
                <th scope="row">{{ months[item.month - 1] }}</th>
                <td
                  class="monthly-number"
                  :class="{ 'monthly-future': item.recorded_nominal === null }"
                >
                  {{
                    item.recorded_nominal === null
                      ? 'Belum berlangsung'
                      : compactMoney(item.recorded_nominal)
                  }}
                </td>
                <td class="monthly-number" :class="{ 'monthly-future': item.realization === null }">
                  {{
                    item.realization === null ? 'Belum berlangsung' : compactMoney(item.realization)
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>
    </section>
    <UnitTargets read-only />
    <OpportunityDrawer
      v-if="selectedOpportunity !== null"
      :id="selectedOpportunity"
      initial-action="followup"
      @close="selectedOpportunity = null"
    />
  </template>
</template>
<style scoped>
.interest-counts {
  display: flex;
  align-items: baseline;
  gap: 12px;
  font-variant-numeric: tabular-nums;
}
.interest-counts strong {
  font-size: 13px;
}
.interest-counts > span {
  font-size: 12px;
  color: #716b80;
  min-width: 42px;
  text-align: right;
}
.interest-track {
  height: 8px;
  margin-top: 12px;
  background: #eeeaf3;
  border-radius: 8px;
  overflow: hidden;
}
.interest-track > span {
  display: block;
  height: 100%;
  border-radius: inherit;
}
.monthly-details {
  margin: 22px 26px 26px;
  border: 1px solid #e9e3f1;
  border-radius: 12px;
  overflow: hidden;
}
.monthly-details > summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0;
  padding: 14px 16px;
  list-style: none;
  background: #f8f6fc;
  color: #645a76;
  font-size: 13px;
  font-weight: 600;
}
.monthly-details > summary::-webkit-details-marker {
  display: none;
}
.monthly-details[open] > summary :deep(.app-icon) {
  transform: rotate(90deg);
}
.monthly-details .report-table-wrap {
  border-top: 1px solid #e9e3f1;
}
.monthly-details .report-table {
  margin: 0;
  table-layout: fixed;
}
.monthly-details .report-table th,
.monthly-details .report-table td {
  padding: 13px 16px;
  font-size: 13px;
  color: #51485f;
}
.monthly-details .report-table thead th {
  background: #fcfbfe;
  font-size: 12px;
  font-weight: 600;
  border-top: 0;
}
.monthly-details .report-table thead th:first-child {
  width: 18%;
}
.monthly-details .report-table tbody th {
  background: transparent;
  border-top: 0;
  font-weight: 500;
}
.monthly-details .report-table .monthly-number {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.monthly-details .report-table td.monthly-number {
  white-space: nowrap;
}
.monthly-details .report-table td.monthly-future {
  color: #7b7289;
  font-size: 12px;
  white-space: normal;
}
.monthly-details .report-table tbody tr:last-child th,
.monthly-details .report-table tbody tr:last-child td {
  border-bottom: 0;
}
@media (max-width: 760px) {
  .monthly-details {
    margin: 18px;
  }
  .monthly-details .report-table th,
  .monthly-details .report-table td {
    padding: 12px 9px;
    font-size: 12px;
  }
  .monthly-details .report-table thead th {
    font-size: 11px;
  }
  .monthly-details .report-table td.monthly-future {
    font-size: 11px;
  }
}
.dashboard-targets {
  display: grid;
  gap: 12px;
  margin: 0 26px;
}
.target-comparison {
  margin: 0 26px 12px;
}
.target-comparison > summary {
  padding: 12px 0 5px;
  color: #826b9d;
  font-size: 11px;
}
.target-comparison .report-chart {
  margin: 14px 0 0;
  width: 100%;
}
@media (max-width: 760px) {
  .dashboard-targets {
    margin: 0 18px;
  }
  .target-comparison {
    margin-left: 18px;
    margin-right: 18px;
  }
}
.dashboard-grid > section {
  min-width: 0;
}
.report-chart {
  margin: 0 18px;
  width: calc(100% - 36px);
}
.trend-panel {
  margin: 22px 0;
}
.report-table-wrap {
  overflow-x: auto;
}
.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-top: 16px;
  white-space: normal;
}
.report-table th,
.report-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #eee9f5;
}
.report-table caption {
  text-align: left;
  color: #747083;
  margin-top: 14px;
}
summary {
  cursor: pointer;
  margin-top: 16px;
}
</style>
