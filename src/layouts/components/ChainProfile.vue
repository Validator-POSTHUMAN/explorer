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
  <div
    class="dropdown relative z-20 min-h-[72px] mx-7 body-text-14 text-addition
  before:content-['You_explore:'] before:absolute before:bottom-0 before:md:right-24 before:-mb-1 before:truncate before:hidden before:md:block">
    <label tabindex="0">
      <div
        class="relative flex items-center justify-center w-[72px] min-h-[72px] bg-black regular-red-hat-14
        hover:before:bg-menu-button-hover hover:after:bg-menu-button-hover 
          before:cursor-pointer before:absolute before:inset-0 before:skew-x-[33deg] before:border-l-2 before:border-b before:border-addition before:bg-black before:-translate-x-6
          after:cursor-pointer after:absolute after:inset-0 after:-skew-x-[33deg] after:border-r-2 after:border-b after:border-addition after:bg-black after:translate-x-6">
        <p :key="chainStore.chainName"
          class="absolute bottom-0 left-[90px] -mb-1 z-20 capitalize truncate hidden md:block">
          {{ coinInfo.name || '' }}
        </p>
        <img v-lazy="chainStore.logo" alt="icon"
          class="absolute z-10 cursor-pointer w-[60px] h-[72px] pb-2.5 pt-0.5 mx-1.5" />

        <!-- network indicator -->
        <div class="w-2 h-2 rounded-full absolute right-2 bottom-2 shadow z-10" :class="{
          'bg-success': baseStore.connected,
          'bg-error': !baseStore.connected,
        }"></div>

        <!-- trapezoid -->
        <!-- <div
          class="absolute inset-0
        hover:before:bg-menu-button-hover hover:after:bg-menu-button-hover 
          before:cursor-pointer before:absolute before:inset-0 before:skew-x-[33deg] before:border-l-2 before:border-b before:border-addition before:bg-black before:-translate-x-6
          after:cursor-pointer after:absolute after:inset-0 after:-skew-x-[33deg] after:border-r-2 after:border-b after:border-addition after:bg-black after:translate-x-6">
        </div> -->

      </div>
    </label>
    <div tabindex="0"
      class="p-0 dropdown-content -translate-x-1/2 md:translate-x-0 w-[100vw] left-6 md:w-90 max-w-[436px] menu shadow bg-chart-stroke rounded-box overflow-auto">
      <!-- rest -->
      <div class="uppercase text-header-text header-14-medium-aa tracking-wide mb-5 px-6 pt-6" v-if="chainStore.current?.endpoints?.rest">
        Rest Endpoint
      </div>
      <div v-for="(item, index) in chainStore.current?.endpoints?.rest"
        class="px-6 py-1.5 w-full hover:bg-menu-button-hover dark:hover:bg-[#384059] cursor-pointer" :key="index"
        @click="changeEndpoint(item)"
        :class="{'bg-menu-button-active': item.address === chainStore.endpoint?.address}">
        <div class="flex flex-col">
          <div class="flex items-center justify-between w-full">
            <div class="header-16-medium text-button-text dark:text-gray-200 capitalize tracking-wide">
              {{ item.provider }}
            </div>
            <!-- <span v-if="item.address === chainStore.endpoint?.address"
              class="bg-yes inline-block h-2 w-2 rounded-full" /> -->
          </div>
          <div class="body-text-14 text-addition whitespace-nowrap">
            {{ item.address }}
          </div>
        </div>
      </div>

      <!-- rest -->
      <div class="mt-7 mb-4 px-6 uppercase text-header-text header-14-medium-aa tracking-wide">Information:</div>
      <div class="w-full">
        <div class="pb-1 px-6 header-16-medium text-button-text dark:text-gray-200 capitalize tracking-wide">
          Chain Id:
          {{
            baseStore.latest.block?.header.chain_id && baseStore.connected
              ? baseStore.latest.block.header.chain_id
              : 'N/A'
          }}
        </div>
        <div class="px-6 header-16-medium text-button-text dark:text-gray-200 capitalize tracking-wide">
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
