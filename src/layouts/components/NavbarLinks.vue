<script setup lang="ts">
import { RouterLink } from 'vue-router';

</script>

<template>
  <div class="join">
    <RouterLink to="/cosmos" @click.native="reloadPage" class="btn rounded-none cosmos-styles normal-case">
        _Dashboard
    </RouterLink>
    <RouterLink to="/cosmos/staking" @click.native="reloadPage" class="btn rounded-none cosmos-styles normal-case">
        _Stacking
    </RouterLink>
    <RouterLink to="/cosmos/gov" @click.native="reloadPage" class="btn rounded-none cosmos-styles normal-case">
        _Governance
    </RouterLink>
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