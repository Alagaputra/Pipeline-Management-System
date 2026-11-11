<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  Chart,
  BarController,
  BarElement,
  DoughnutController,
  ArcElement,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

Chart.register(
  BarController,
  BarElement,
  DoughnutController,
  ArcElement,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
)
const props = defineProps({
  type: { type: String, required: true },
  data: { type: Object, required: true },
  label: { type: String, required: true },
  integerAxis: { type: Boolean, default: false },
})
const canvas = ref(null)
let chart
function draw() {
  if (!canvas.value) return
  chart?.destroy()
  chart = new Chart(canvas.value, {
    type: props.type,
    data: JSON.parse(JSON.stringify(props.data)),
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        ? false
        : { duration: 250 },
      plugins: { legend: { position: 'bottom' } },
      ...(props.type === 'doughnut'
        ? { cutout: '65%' }
        : {
            scales: {
              y: {
                beginAtZero: true,
                title: { display: true, text: 'Miliar rupiah' },
                ...(props.integerAxis
                  ? {
                      suggestedMax: 3,
                      ticks: {
                        precision: 0,
                        stepSize: 1,
                        maxTicksLimit: 8,
                        callback: (value) =>
                          value > 0 && Number.isInteger(Number(value))
                            ? new Intl.NumberFormat('id-ID', { maximumFractionDigits: 0 }).format(
                                value,
                              )
                            : '',
                      },
                    }
                  : {}),
              },
            },
          }),
    },
  })
}
onMounted(draw)
watch(() => [props.data, props.type, props.integerAxis], draw, { deep: true })
onBeforeUnmount(() => chart?.destroy())
</script>
<template>
  <div class="report-chart">
    <canvas ref="canvas" role="img" :aria-label="label">{{ label }}</canvas>
  </div>
</template>
<style scoped>
.report-chart {
  position: relative;
  height: 280px;
  width: 100%;
  min-width: 0;
}
</style>
