<script setup>
import { computed } from 'vue'
import account from '../../Icon/ic--baseline-account-circle.svg'
import home from '../../Icon/akar-icons--home-alt1.svg'
import target from '../../Icon/boxicons--target.svg'
import analytics from '../../Icon/carbon--chart-column-target.svg'
import team from '../../Icon/mdi--account-group.svg'
import logout from '../../Icon/mdi-light--logout.svg'
import back from '../../Icon/mdi-light--arrow-left.svg'
import close from '../../Icon/lineicons--xmark.svg'
import upload from '../../Icon/ant-design--cloud-upload-outlined.svg'
import filter from '../../Icon/ant-design--filter-outlined.svg'
import savings from '../../Icon/streamline-freehand--saving-bag-increase.svg'
import giro from '../../Icon/griddy-icons--term-deposit.svg'
import deposit from '../../Icon/hugeicons--reverse-withdrawal-01.svg'
import {
  LayoutDashboard,
  History,
  ListTodo,
  Target,
  ChartNoAxesCombined,
  Users,
  CircleHelp,
  LogOut,
  ChevronRight,
  ChevronLeft,
  ArrowLeft,
  Plus,
  Search,
  ArrowUpRight,
  ArrowDownToLine,
  Wallet,
  Landmark,
  CalendarDays,
  Clock3,
  Check,
  X,
  Eye,
  EyeOff,
  UploadCloud,
  FileSpreadsheet,
  SlidersHorizontal,
  Bell,
  ArrowRight,
  Pencil,
  CheckCheck,
  Menu,
  TrendingUp,
  CircleAlert,
  CircleCheck,
  Building2,
} from 'lucide-vue-next'
const props = defineProps({ name: String, size: { type: Number, default: 20 } })
const icons = {
  history: History,
  pipeline: ListTodo,
  dashboard: LayoutDashboard,
  target: Target,
  analytics: ChartNoAxesCombined,
  team: Users,
  help: CircleHelp,
  logout: LogOut,
  right: ChevronRight,
  left: ChevronLeft,
  back: ArrowLeft,
  plus: Plus,
  search: Search,
  trend: ArrowUpRight,
  download: ArrowDownToLine,
  wallet: Wallet,
  bank: Landmark,
  calendar: CalendarDays,
  clock: Clock3,
  check: Check,
  close: X,
  eye: Eye,
  eyeOff: EyeOff,
  upload: UploadCloud,
  file: FileSpreadsheet,
  filter: SlidersHorizontal,
  bell: Bell,
  arrow: ArrowRight,
  edit: Pencil,
  done: CheckCheck,
  menu: Menu,
  growth: TrendingUp,
  alert: CircleAlert,
  success: CircleCheck,
  building: Building2,
}
const originalIcons = {
  account,
  dashboard: home,
  target,
  analytics,
  team,
  logout,
  back,
  close,
  upload,
  filter,
  savings,
  giro,
  deposit,
}
const iconStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  maskImage: `url("${originalIcons[props.name]}")`,
  WebkitMaskImage: `url("${originalIcons[props.name]}")`,
}))
</script>
<template>
  <span
    v-if="originalIcons[name]"
    class="app-icon original-icon"
    :style="iconStyle"
    aria-hidden="true"
  ></span>
  <component
    v-else
    :is="icons[name] || icons.dashboard"
    class="app-icon"
    :size="size"
    :stroke-width="1.8"
    aria-hidden="true"
  />
</template>
