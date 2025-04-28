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
    class="w-full md:w-[153px] relative bg-[#171718] hover:bg-[#242424] border border-addition rounded shadow flex justify-center items-center p-2.5 cursor-pointer"
  >
    <div class="flex flex-col gap-2.5 justify-center items-center">
      <div class="w-[50px] h-[50px] rounded-full overflow-hidden">
        <img :src="conf.logo"  />
      </div>
      <div class="font-semibold text-[#FFFFFF] header-14-medium-aa flex-1 truncate uppercase">
        {{ conf?.prettyName || props.name }}
      </div>
    </div>

    <div
      @click="addFavor"
      class="absolute top-0 right-0 m-2.5 text-sm"
      :class="{
        'text-warning': dashboardStore?.favoriteMap?.[props.name],
        'text-gray-500': !dashboardStore?.favoriteMap?.[props.name],
        'shadow-[0_0_2px_1px_rgba(238,187,78,0.2)] rounded-full before:bg-[radial-gradient(circle,rgba(238,187,78,0.5)_30%,transparent_90%)] before:absolute before:w-full before:h-full before:rounded-full': dashboardStore?.favoriteMap?.[props.name],
      }"
    >
      <Icon icon="mingcute:star-fill" />
    </div>
  </RouterLink>
</template>
