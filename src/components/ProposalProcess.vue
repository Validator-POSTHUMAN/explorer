<script lang="ts" setup>
import { useFormatter } from '@/stores';
import type { Tally } from '@/types';
import { computed } from '@vue/reactivity';
import type { PropType } from 'vue';

const props = defineProps({
  tally: { type: Object as PropType<Tally> },
  pool: {
    type: Object as PropType<{
      not_bonded_tokens: string;
      bonded_tokens: string;
    }>,
  },
  status: {}
});
const total = computed(() => props.pool?.bonded_tokens);
const format = useFormatter();
const yes = computed(() =>
  format.calculatePercent(props.tally?.yes, total.value)
);
const no = computed(() =>
  format.calculatePercent(props.tally?.no, total.value)
);
const abstain = computed(() =>
  format.calculatePercent(props.tally?.abstain, total.value)
);
const veto = computed(() =>
  format.calculatePercent(props.tally?.no_with_veto, total.value)
);
console.log('tally', props.tally);
console.log('pool', props.pool);
console.log('status', props.status);
</script>

<template>
  <div class="progress rounded-full h-6 text-xs flex items-center">
    <div v-if="status === 'PASSED'"
      class="h-6 bg-proposal-status-approved rounded-r-full flex items-center pl-2 text-white overflow-hidden"
      :style="`width: ${yes}`">
      <!-- {{ yes }} -->
    </div>
    <div v-if="status === 'REJECTED'"
      class="h-6 bg-proposal-status-rejected rounded-r-full flex items-center text-white overflow-hidden"
      :style="`width: ${no}`" :title="no">
      <!-- {{ no }} -->
    </div>
    <div v-if="status === 'VETO'"
      class="h-6 bg-proposal-status-veto rounded-r-full flex items-center text-white overflow-hidden"
      :style="`width: ${veto};`" :title="veto">
      <!-- {{ veto }} -->
    </div>
    <div v-if="status === 'VOTING'"
      class="h-6 bg-proposal-status-voting rounded-r-full flex items-center text-white overflow-hidden"
      :style="`width: ${abstain}`" :title="abstain">
      <!-- {{ abstain }} -->
    </div>
    <div class="header-16-medium ml-3">
      <span v-if="status === 'PASSED'" class="text-status-text-approved">{{ yes }}</span>
      <span v-if="status === 'REJECTED'" class="text-status-text-rejected">{{ no }}</span>
      <span v-if="status === 'VETO'" class="text-status-text-veto">{{ veto }}</span>
      <span v-if="status === 'VOTING'" class="text-status-text-voting">{{ abstain }}</span>
    </div>
  </div>
</template>
<style scoped>
.progress {
  overflow: hidden;
  background-color: rgba(128, 128, 128, 0.178);
}
</style>
