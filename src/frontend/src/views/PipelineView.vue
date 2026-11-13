<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import OpportunityList from '../components/OpportunityList.vue'
import OpportunityDrawer from '../components/OpportunityDrawer.vue'
import { usePipeline } from '../composables/usePipeline'
const { activeRows, canEdit, loading } = usePipeline()
const route = useRoute()
// selected null menutup drawer, string kosong membuat peluang, ID membuka detail.
const selected = ref(null),
  message = ref('')
function saved(row) {
  // usePipeline memperbarui state; peluang Won/Lost otomatis keluar dari activeRows.
  message.value =
    row.outcome === 'Active'
      ? 'Peluang berhasil disimpan.'
      : `Closing ${row.outcome} tersimpan. Peluang tersedia di Riwayat.`
}
</script>
<template>
  <div class="page-heading">
    <div>
      <h1>Pipeline aktif</h1>
    </div>
    <button v-if="canEdit" class="button primary" @click="selected = ''">
      <AppIcon name="plus" :size="18" />Catat peluang
    </button>
  </div>
  <p v-if="!canEdit && !loading" class="notice closing-note">
    Pilih satu divisi untuk mencatat atau mengubah peluang.
  </p>
  <p v-if="message" class="notice success" role="status">
    {{ message
    }}<button class="icon-button" aria-label="Tutup notifikasi" @click="message = ''">
      <AppIcon name="close" :size="16" />
    </button>
  </p>
  <section class="panel pipeline-panel">
    <div class="panel-heading">
      <div>
        <h2>
          Daftar peluang <span class="count-badge">{{ activeRows.length }}</span>
        </h2>
      </div>
      <RouterLink to="/history" class="text-button"
        >Lihat Riwayat <AppIcon name="arrow" :size="17"
      /></RouterLink>
    </div>
    <OpportunityList
      :rows="activeRows"
      :due-only="route.query.followup === '1'"
      @select="selected = $event"
    />
  </section>
  <OpportunityDrawer
    v-if="selected !== null"
    :id="selected"
    @close="selected = null"
    @saved="saved"
  />
</template>
