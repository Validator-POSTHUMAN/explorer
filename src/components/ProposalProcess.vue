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
</script>

<template>
  <div class="z-10 header-16-medium ml-3">
      <span v-if="status === 'PASSED'" class="text-status-text-approved">{{ yes }}</span>
      <span v-if="status === 'REJECTED'" class="text-status-text-rejected">{{ no }}</span>
      <span v-if="status === 'VETO'" class="text-status-text-veto">{{ veto }}</span>
      <span v-if="status === 'VOTING'" class="text-status-text-voting">{{ abstain }}</span>
    </div>
  <div class="progress rounded-full h-6 text-xs flex items-center">
    <div
      class="z-[4] h-6 bg-proposal-status-approved rounded-r-full flex items-center pl-2 text-white overflow-hidden"
      :class="{'bg-proposal-status-voting': status === 'VOTING'}"
      :style="`width: ${yes}`">
      <!-- {{ yes }} -->
    </div>
    <div
      class="z-[3] h-6 bg-proposal-status-rejected rounded-r-full flex items-center text-white overflow-hidden -ml-6"
      :style="`width: ${no}`" :title="no">
      <!-- {{ no }} -->
    </div>
    <div
      class="z-[2] h-6 bg-proposal-status-veto rounded-r-full flex items-center text-white overflow-hidden -ml-6"
      :style="`width: ${veto};`" :title="veto">
      <!-- {{ veto }} -->
    </div>
    <div
      class="z-[1] h-6 bg-proposal-status-voting rounded-r-full flex items-center text-white overflow-hidden -ml-6"
      :style="`width: ${abstain}`" :title="abstain">
      <!-- {{ abstain }} -->
    </div>
    
  </div>
  
</template>
<style scoped>
.progress {
  overflow: hidden;
  background-color: rgba(128, 128, 128, 0.178);
}
</style>
