<script setup lang="ts">
import { useIndexModule } from '@/modules/[chain]/indexStore';
import { useBlockchain, useBaseStore, type Endpoint } from '@/stores';
import { computed } from 'vue';
import { useRouter } from 'vue-router';
const chainStore = useBlockchain();
const store = useIndexModule();
const coinInfo = computed(() => {
  return store.coinInfo;
});
const baseStore = useBaseStore();
chainStore.initial();
const router = useRouter();
function changeEndpoint(item: Endpoint) {
  chainStore.setRestEndpoint(item);
  if (chainStore.current) router.push(`/${chainStore.current.chainName}`);
}
</script>

<template>
<div class="dropdown relative z-10 min-h-[72px] mx-7 body-text-14 text-addition
  before:content-['You_explore:'] before:absolute before:bottom-0 before:md:right-24 before:-mb-1 before:truncate before:hidden before:md:block">
  <label tabindex="0">
    <div class="relative flex items-center justify-center w-[72px] min-h-[72px] bg-black regular-red-hat-14">
      <p 
        :key="chainStore.chainName"
        class="absolute bottom-0 left-[90px] -mb-1 z-20 capitalize truncate hidden md:block">
        {{ coinInfo.name || '' }}
      </p>
      <img v-lazy="chainStore.logo" alt="icon" class="absolute z-10 cursor-pointer w-[60px] h-[72px] pb-2.5 pt-0.5 mx-1.5" />

      <!-- network indicator -->
      <div
        class="w-2 h-2 rounded-full absolute right-2 bottom-2 shadow z-10"
        :class="{
          'bg-success': baseStore.connected,
          'bg-error': !baseStore.connected,
        }"
      ></div>

      <!-- trapezoid -->
      <div class="absolute inset-0
        before:absolute before:inset-0 before:skew-x-[33deg] before:border-l-2 before:border-b before:border-addition before:bg-black before:-translate-x-6
        after:absolute after:inset-0 after:-skew-x-[33deg] after:border-r-2 after:border-b after:border-addition after:bg-black after:translate-x-6">
      </div>
      
    </div>
  </label>
  <div
      tabindex="0"
      class="dropdown-content -translate-x-1/2 md:translate-x-0 w-[100vw] left-6 md:w-80 menu shadow bg-base-200 rounded-box overflow-auto"
     >
      <!-- rest -->
      <div
        class="px-4 py-2 text-sm text-[#686868]"
        v-if="chainStore.current?.endpoints?.rest"
      >
        Rest Endpoint
      </div>
      <div
        v-for="(item, index) in chainStore.current?.endpoints?.rest"
        class="px-4 py-2 w-full hover:bg-gray-100 dark:hover:bg-[#384059] cursor-pointer"
        :key="index"
        @click="changeEndpoint(item)"
      >
        <div class="flex flex-col">
          <div class="flex items-center justify-between w-full">
            <div class="text-gray-500 dark:text-gray-200 capitalize">
              {{ item.provider }}
            </div>
            <span
              v-if="item.address === chainStore.endpoint?.address"
              class="bg-yes inline-block h-2 w-2 rounded-full"
            />
          </div>
          <div class="text-gray-400 text-xs whitespace-nowrap">
            {{ item.address }}
          </div>
        </div>
      </div>

      <!-- rest -->
      <div class="px-4 py-2 text-sm text-gray-400">Information</div>
      <div class="w-full">
        <div class="py-2 px-4">
          Chain Id:
          {{
            baseStore.latest.block?.header.chain_id && baseStore.connected
              ? baseStore.latest.block.header.chain_id
              : 'N/A'
          }}
        </div>
        <div class="py-2 px-4">
          Height:
          {{
            baseStore.latest.block?.header.height && baseStore.connected
              ? baseStore.latest.block.header.height
              : '0'
          }}
        </div>
      </div>
      <!-- bottom-->
      <div class="px-4 py-2">&nbsp;</div>
  </div>
</div>

                
</template>
