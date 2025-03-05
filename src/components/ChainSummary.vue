<script lang="ts" setup>
import { useDashboard } from '@/stores/useDashboard';
import { computed } from 'vue';
import { Icon } from '@iconify/vue';

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
});

const dashboardStore = useDashboard();
const conf = computed(() => dashboardStore.chains[props.name] || {});

const addFavor = (e: Event) => {
  e.stopPropagation();
  e.preventDefault();
  dashboardStore.favoriteMap[props.name] =
    !dashboardStore?.favoriteMap?.[props.name];
  window.localStorage.setItem(
    'favoriteMap',
    JSON.stringify(dashboardStore.favoriteMap)
  );
};
</script>
<template>
  <RouterLink
    :to="`/${name}`"
    class="bg-[#171718] bg-opacity-50 hover:bg-[#242424] border border-[#686868] rounded shadow flex flex-col items-center py-3 px-3 cursor-pointer"
  >
  <div class="flex flex-row-reverse">
    <div
      @click="addFavor"
      class="pl-4 text-xl ml-6"
      :class="{
        'text-warning': dashboardStore?.favoriteMap?.[props.name],
        'text-gray-500': !dashboardStore?.favoriteMap?.[props.name],
      }"
    >
      <Icon icon="mdi-star" />
    </div>
    <div class="w-12 h-12 ml-16 rounded-full overflow-hidden">
      <img :src="conf.logo" />
    </div>
  </div>
    <div class="font-semibold text-[#FFFFFF] truncate capitalize">
      {{ conf?.prettyName || props.name }}
    </div>
  </RouterLink>
</template>
