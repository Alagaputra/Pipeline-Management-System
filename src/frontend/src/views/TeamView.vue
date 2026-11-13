<script setup>
import { computed, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import AppDrawer from '../components/AppDrawer.vue'
import YearFilter from '../components/YearFilter.vue'
import OpportunityDrawer from '../components/OpportunityDrawer.vue'
import StatusBadge from '../components/StatusBadge.vue'
import ProductDistribution from '../components/ProductDistribution.vue'
import { usePipeline } from '../composables/usePipeline'
import { compactMoney, isClosed, dateLabel } from '../utils/pipeline'
import { divisionProducts } from '../data/access'
const { rows, selectedYear, picRecords } = usePipeline()
const search = ref('')
const selected = ref('')
const opportunity = ref(null)
const chartMode = ref('active')
const sort = ref('active')
const people = computed(() =>
  // Ringkasan PIC: pipeline aktif seluruh periode, sedangkan Won/Lost mengikuti tahun pilihan.
  picRecords.value
    .filter((pic) => pic.name.toLowerCase().includes(search.value.toLowerCase()))
    .map((pic) => {
      const active = rows.value.filter((row) => row.pic === pic.name && !isClosed(row))
      const closed = rows.value.filter(
        (row) =>
          row.pic === pic.name &&
          isClosed(row) &&
          Number(row.closedDate.slice(0, 4)) === selectedYear.value,
      )
      return {
        name: pic.name,
        division: pic.division?.name || '',
        active: active.length,
        nominal: active.reduce((sum, row) => sum + row.nominal, 0),
        won: closed.filter((row) => row.outcome === 'Won').length,
        lost: closed.filter((row) => row.outcome === 'Lost').length,
        realized: closed
          .filter((row) => row.outcome === 'Won')
          .reduce((sum, row) => sum + row.realization, 0),
        distribution: divisionProducts(pic.division?.name).map((product) => ({
          product,
          value:
            chartMode.value === 'active'
              ? active
                  .filter((row) => row.product === product)
                  .reduce((sum, row) => sum + row.nominal, 0)
              : closed
                  .filter((row) => row.product === product && row.outcome === 'Won')
                  .reduce((sum, row) => sum + row.realization, 0),
        })),
      }
    })
    .sort((a, b) =>
      sort.value === 'name'
        ? a.name.localeCompare(b.name)
        : sort.value === 'realized'
          ? b.realized - a.realized || a.name.localeCompare(b.name)
          : b.nominal - a.nominal || a.name.localeCompare(b.name),
    ),
)
const selectedPerson = computed(() => people.value.find((person) => person.name === selected.value))
const handled = computed(() =>
  // Detail PIC juga menampilkan peluang yang pernah ditangani sebelum dialihkan.
  rows.value
    .filter((row) => row.pic === selected.value || row.handledBy.includes(selected.value))
    .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)),
)
function showOpportunity(id) {
  selected.value = ''
  opportunity.value = id
}
</script>
<template>
  <div class="page-heading">
    <div>
      <h1>Tim / PIC</h1>
    </div>
    <YearFilter label="Tahun hasil closing" />
  </div>
  <section class="panel team-summary" aria-label="Ringkasan tim">
    <div class="panel-heading">
      <div>
        <h2>
          Anggota tim <span class="count-badge">{{ people.length }}</span>
        </h2>
        <p>Peluang aktif seluruh periode · hasil Won/Lost tahun {{ selectedYear }}.</p>
      </div>
    </div>
    <div class="team-summary-toolbar">
      <div class="input-icon">
        <AppIcon name="search" :size="18" /><input
          v-model="search"
          placeholder="Cari PIC..."
          aria-label="Cari PIC"
        />
      </div>
      <label
        >Urutkan<select v-model="sort" aria-label="Urutkan PIC">
          <option value="active">Potensi aktif terbesar</option>
          <option value="realized">Realisasi terbesar</option>
          <option value="name">Nama PIC</option>
        </select></label
      >
    </div>
    <article
      v-for="person in people"
      :key="person.name"
      class="team-summary-row"
      :aria-label="'Ringkasan PIC ' + person.name"
    >
      <div class="team-summary-person">
        <span class="avatar" :class="person.name.toLowerCase()">{{
          person.name.slice(0, 2).toUpperCase()
        }}</span>
        <div>
          <h3>{{ person.name }}</h3>
          <p>{{ person.division || 'PIC Funding' }}</p>
        </div>
      </div>
      <dl class="team-summary-metrics">
        <div>
          <dt>Peluang aktif</dt>
          <dd>
            {{ person.active }} <small>{{ compactMoney(person.nominal) }}</small>
          </dd>
        </div>
        <div>
          <dt>Won {{ selectedYear }}</dt>
          <dd class="success-text">{{ person.won }}</dd>
        </div>
        <div>
          <dt>Lost {{ selectedYear }}</dt>
          <dd class="hot-text">{{ person.lost }}</dd>
        </div>
        <div>
          <dt>Realisasi {{ selectedYear }}</dt>
          <dd>{{ compactMoney(person.realized) }}</dd>
        </div>
      </dl>
      <button
        type="button"
        class="button secondary"
        :aria-label="'Detail PIC ' + person.name"
        @click="selected = person.name"
      >
        Detail <AppIcon name="right" :size="16" />
      </button>
    </article>
    <div v-if="!people.length" class="empty-state">
      <AppIcon name="search" :size="28" />
      <h3>PIC tidak ditemukan</h3>
      <p>Coba nama PIC lain dalam divisi ini.</p>
    </div>
  </section>
  <AppDrawer
    v-if="selected && selectedPerson"
    :title="'Detail PIC ' + selected"
    subtitle="RINGKASAN & PELUANG"
    @close="selected = ''"
  >
    <div class="team-detail-heading">
      <h3>Komposisi produk</h3>
      <div class="chart-mode">
        <button
          type="button"
          :class="{ selected: chartMode === 'active' }"
          :aria-pressed="chartMode === 'active'"
          @click="chartMode = 'active'"
        >
          Potensi aktif</button
        ><button
          type="button"
          :class="{ selected: chartMode === 'realized' }"
          :aria-pressed="chartMode === 'realized'"
          @click="chartMode = 'realized'"
        >
          Realisasi Won
        </button>
      </div>
    </div>
    <p class="drawer-intro">
      {{
        chartMode === 'active'
          ? 'Peluang aktif seluruh periode.'
          : 'Realisasi Won tahun ' + selectedYear + '.'
      }}
      Persentase menunjukkan komposisi produk.
    </p>
    <ProductDistribution
      v-if="selectedPerson.distribution.some((item) => item.value > 0)"
      :items="selectedPerson.distribution"
      :label="chartMode === 'active' ? 'Potensi aktif' : 'Realisasi ' + selectedYear"
    />
    <p v-else class="notice closing-note">
      Belum ada
      {{ chartMode === 'active' ? 'potensi aktif' : 'realisasi Won pada tahun ini' }} untuk
      ditampilkan.
    </p>
    <div class="team-handled-heading">
      <h3>Peluang pernah ditangani</h3>
      <p>Peluang aktif maupun selesai · seluruh periode.</p>
    </div>
    <div v-for="row in handled" :key="row.id" class="pic-opportunity">
      <div>
        <button class="customer-link" @click="showOpportunity(row.id)">{{ row.customer }}</button
        ><small>{{ row.product }} · {{ compactMoney(row.nominal) }}</small>
      </div>
      <StatusBadge :status="isClosed(row) ? row.outcome : row.status" />
      <p>
        PIC {{ isClosed(row) ? 'saat closing' : 'saat ini' }}: {{ row.pic
        }}<span v-if="isClosed(row)"> · {{ dateLabel(row.closedDate) }}</span>
      </p>
      <p v-if="row.notes">{{ row.notes }}</p>
    </div>
    <div v-if="!handled.length" class="empty-state">Belum ada peluang yang pernah ditangani.</div>
  </AppDrawer>
  <OpportunityDrawer v-if="opportunity !== null" :id="opportunity" @close="opportunity = null" />
</template>
<style scoped>
.team-summary-toolbar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 26px 22px;
}
.team-summary-toolbar .input-icon {
  flex: 1;
}
.team-summary-toolbar label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #716b80;
  font-size: 12px;
}
.team-summary-toolbar select {
  width: 205px;
  font-size: 13px;
}
.team-summary-row {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 22px 26px;
  border-top: 1px solid #eeeaf4;
}
.team-summary-person {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 160px;
}
.team-summary-person h3 {
  font-size: 15px;
}
.team-summary-person p {
  color: #716b80;
  font-size: 12px;
  margin-top: 4px;
}
.team-summary-metrics {
  display: grid;
  grid-template-columns: 1.4fr 0.7fr 0.7fr 1.4fr;
  gap: 20px;
  margin: 0;
  flex: 1;
  min-width: 0;
}
.team-summary-metrics dt {
  color: #716b80;
  font-size: 12px;
  margin-bottom: 7px;
}
.team-summary-metrics dd {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  overflow-wrap: anywhere;
}
.team-summary-metrics small {
  display: block;
  color: #716b80;
  font-size: 12px;
  font-weight: 400;
  margin-top: 4px;
}
.team-summary-row > button {
  font-size: 12px;
  padding: 10px 12px;
}
.team-detail-heading h3 {
  margin-bottom: 14px;
}
.team-detail-heading .chart-mode {
  margin-bottom: 16px;
}
.team-handled-heading {
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid #eeeaf4;
}
.team-handled-heading p {
  color: #716b80;
  font-size: 12px;
  margin-top: 6px;
}
:deep(.product-distribution) {
  grid-template-columns: 1fr;
  gap: 20px;
}
:deep(.distribution-donut) {
  margin: 0 auto;
}
@media (max-width: 1000px) {
  .team-summary-row {
    flex-wrap: wrap;
    gap: 20px;
  }
  .team-summary-metrics {
    flex-basis: calc(100% - 210px);
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .team-summary-row > button {
    margin-left: auto;
  }
}
@media (max-width: 760px) {
  .team-summary-toolbar {
    flex-wrap: wrap;
    padding: 0 18px 18px;
    gap: 12px;
  }
  .team-summary-toolbar .input-icon {
    flex-basis: 100%;
  }
  .team-summary-toolbar label {
    width: 100%;
    justify-content: space-between;
  }
  .team-summary-toolbar select {
    width: 205px;
  }
  .team-summary-row {
    padding: 18px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
  }
  .team-summary-person {
    min-width: 0;
  }
  .team-summary-metrics {
    grid-column: 1 / -1;
    grid-row: 2;
    gap: 18px;
  }
  .team-summary-row > button {
    grid-column: 2;
    grid-row: 1;
  }
}
</style>
