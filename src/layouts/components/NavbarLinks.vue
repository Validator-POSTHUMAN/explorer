<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { useBlockchain } from '@/stores';

const blockchain = useBlockchain();

</script>

<template>
  <div class="join">
    <img class="px-5 join-item" src="src/assets/logo.svg"/>
    <div class="border join-horizontal border-t-0 border-[#686868] overflow-hidden h-[6rem] rounded-b-[1.5625rem] rounded-t-none bg-black">
      <img :src="blockchain.logo" class="w-full h-full object-cover p-4"/>
    </div>
    <div class="join-item ml-[0.001rem] pl-5">
      <RouterLink to="/cosmos" @click.native="reloadPage" class="btn px-16 rounded-none cosmos-navbar-pgs normal-case -ml-5 z-20 relative border-l-0">
          _Dashboard
      </RouterLink>
      <RouterLink to="/cosmos/staking" @click.native="reloadPage" class="btn px-16 rounded-none cosmos-navbar-pgs normal-case -ml-5 z-10 relative border-l-0">
          _Stacking
      </RouterLink>
      <RouterLink to="/cosmos/gov" @click.native="reloadPage" class="btn px-16 rounded-none cosmos-navbar-pgs normal-case -ml-5 z-0 relative border-l-0">
          _Governance
      </RouterLink>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  methods: {
    reloadPage() {
      setTimeout(() => {
        window.location.reload();
      }, 100); 
    }
  }
};
</script>