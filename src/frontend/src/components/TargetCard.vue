<script setup>
import { productColor } from '../utils/productColors'
import { computed } from 'vue'
import { compactMoney, money, percent } from '../utils/pipeline'
const props = defineProps({
  item: { type: Object, required: true },
  unit: Boolean,
  badge: String,
  label: String,
})
const percentage = computed(() =>
  props.item.target > 0 ? (props.item.realization / props.item.target) * 100 : null,
)
const remaining = computed(() => Math.max(0, props.item.target - props.item.realization))
const format = (value) =>
  props.unit ? new Intl.NumberFormat('id-ID').format(value) + ' unit' : compactMoney(value)
const full = (value) => (props.unit ? format(value) : money(value))
</script>
<template>
  <article
    class="goal-card"
    :class="{ 'is-unset': !item.target }"
    :aria-label="label || 'Target ' + item.product"
  >
    <header class="goal-heading">
      <h3>
        <span class="goal-dot" :style="{ backgroundColor: productColor(item.product) }"></span
        >{{ item.product }}
      </h3>
      <span v-if="badge" class="goal-scope">{{ badge }}</span>
    </header>
    <div class="goal-achievement">
      <span>Pencapaian tahunan</span>
      <strong :class="{ achieved: percentage !== null && percentage >= 100 }">{{
        percent(percentage)
      }}</strong>
    </div>
    <dl class="goal-values">
      <div>
        <dt>Target tahunan</dt>
        <dd data-metric="target" :title="full(item.target)">{{ format(item.target) }}</dd>
      </div>
      <div>
        <dt>{{ unit ? 'Realisasi tahunan' : 'Realisasi Won' }}</dt>
        <dd data-metric="realization" :title="full(item.realization)">
          {{ format(item.realization) }}
        </dd>
      </div>
    </dl>
    <div
      class="goal-track"
      role="progressbar"
      :aria-label="'Pencapaian ' + item.product"
      aria-valuemin="0"
      :aria-valuemax="Math.max(100, Math.ceil(percentage || 0))"
      :aria-valuenow="percentage === null ? undefined : Math.round(percentage)"
      :aria-valuetext="percent(percentage)"
    >
      <span :style="{ width: Math.min(100, percentage || 0) + '%' }"></span>
    </div>
    <p class="goal-remaining">
      {{
        item.target
          ? remaining
            ? 'Sisa target ' + format(remaining)
            : 'Target tahunan tercapai'
          : 'Target belum ditetapkan'
      }}
    </p>
    <div v-if="$slots.default" class="goal-details"><slot /></div>
    <footer v-if="$slots.actions" class="goal-actions"><slot name="actions" /></footer>
  </article>
</template>
<style scoped>
.goal-card {
  min-width: 0;
  padding: 20px;
  border: 1px solid #e8e2f0;
  border-radius: 14px;
  background: #fdfcfe;
}
.goal-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.goal-heading h3 {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 16px;
  margin: 0;
}
.goal-dot {
  flex: 0 0 8px;
  height: 8px;
  border-radius: 50%;
  background: #8260cd;
}
.goal-dot.tabungan {
  background: #389585;
}
.goal-dot.giro {
  background: #80a6d8;
}
.goal-scope {
  padding: 5px 9px;
  border-radius: 6px;
  background: #f0ebfa;
  font-size: 11px;
  color: #6e4da6;
}
.goal-achievement {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
}
.goal-achievement > span,
.goal-values dt,
.goal-remaining {
  color: #716b80;
  font-size: 12px;
  line-height: 1.6;
}
.goal-achievement strong {
  color: #7051ac;
  font-size: 14px;
}
.goal-achievement strong.achieved {
  color: #278063;
}
.goal-values {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0 14px;
}
.goal-values > div {
  min-width: 0;
}
.goal-values > div:last-child {
  text-align: right;
}
.goal-values dd {
  margin: 5px 0 0;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.5;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}
.goal-track {
  height: 7px;
  border-radius: 7px;
  background: #ebe5f4;
  overflow: hidden;
}
.goal-track > span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #8260cd;
}
.goal-remaining {
  margin: 10px 0 0;
}
.goal-details {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #e8e2f0;
}
.goal-actions {
  margin-top: 18px;
}
@media (max-width: 420px) {
  .goal-card {
    padding: 16px;
  }
  .goal-values dd {
    font-size: 16px;
  }
}
</style>
