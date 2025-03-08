<script setup lang="ts">
import { RouterLink } from 'vue-router';

</script>

<template>
  <div class="join">
    <RouterLink to="/cosmos" @click.native="reloadPage" class="btn rounded-none cosmos-styles skew-x-[-35deg] transform normal-case">
      <span class="skew-x-[35deg] transform ">
        _Dashboard
      </span>
    </RouterLink>
    <RouterLink to="/cosmos/stacking" @click.native="reloadPage" class="btn rounded-none cosmos-styles skew-x-[-35deg] transform normal-case">
      <span class="skew-x-[35deg] transform ">
        _Stacking
      </span>
    </RouterLink>
    <RouterLink to="/cosmos/gov" @click.native="reloadPage" class="btn rounded-none cosmos-styles skew-x-[-35deg] transform normal-case">
      <span class="skew-x-[35deg] transform ">
        _Governance
      </span>
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