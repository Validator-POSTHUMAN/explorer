<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useBlockchain } from '@/stores';
const vueRouters = useRouter();
const blockStore = useBlockchain();
let searchQuery = ref('');
let errorMessage = ref('');
onMounted(() => { });

function preventClick(event: any) {
  event.preventDefault();
  event.stopPropagation();
}
function confirm() {
  errorMessage.value = '';
  const key = searchQuery.value;
  if (!key) {
    errorMessage.value = 'Please enter a value!';
    return;
  }
  const height = /^\d+$/;
  const txhash = /^[A-Z\d]{64}$/;
  const addr = /^[a-z\d]+1[a-z\d]{38,58}$/;

  const current = blockStore?.current?.chainName || '';
  const routeParams = vueRouters?.currentRoute?.value;

  if (!Object.values(routeParams?.params).includes(key)) {
    if (height.test(key)) {
      vueRouters.push({ path: `/${current}/block/${key}` });
      setTimeout(() => {
        closeSearchModal();
      }, 1000);
    } else if (txhash.test(key)) {
      vueRouters.push({ path: `/${current}/tx/${key}` });
      setTimeout(() => {
        closeSearchModal();
      }, 1000);
      //     this.$router.push({ name: 'transaction', params: { chain: c.chain_name, hash: key } })
    } else if (addr.test(key)) {
      vueRouters.push({ path: `/${current}/account/${key}` });
      setTimeout(() => {
        closeSearchModal();
      }, 1000);
    } else {
      errorMessage.value = 'The input not recognized';
    }
  }
}
</script>
<!-- @click="openSearchModal" -->

<template>
    <div
        class="flex w-full md:w-1/2 items-center rounded-[26px] bg-transparent mt-10 border border-addition text-addition py-2 px-2">
        <input :placeholder="$t('pages.search_placeholder')"
        @keyup.enter="confirm"
          class="md:px-4 min-h-6 md:h-10 bg-transparent flex-1 outline-none text-xs md:text-xl placeholder:text-addition focus:text-white "
          v-model="searchQuery" />
        <div @click="confirm" class="md:px-4 pr-2 md:!block order-first md:order-last cursor-pointer">
          <Icon icon="icon-park-outline:search" width="20" height="20" class="ml-3" />
        </div>
      </div>
</template>
