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
    class="btn cosmos-styles rounded h-full flex flex-col justify-center cursor-pointer relative"
  >
      <div class="grid grid-cols-3 mt-3">
        <div>

        </div>
        <div class="w-12 h-12 rounded-full overflow-hidden">
          <img :src="conf.logo" />
        </div>
        <div
          @click="addFavor"
          class="text-xl ml-7 -mt-1"
          :class="{
            'text-warning': dashboardStore?.favoriteMap?.[props.name],
            'text-gray-500': !dashboardStore?.favoriteMap?.[props.name],
          }"
        >
          <Icon icon="mdi-star" />
        </div>
      </div>
    <div class="font-semibold truncate capitalize justify-center mb-3">
      {{ conf?.prettyName || props.name }}
    </div>
  </RouterLink>
</template>
