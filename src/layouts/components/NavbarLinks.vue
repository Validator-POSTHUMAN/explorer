<script lang="ts" setup>
import { RouterLink } from 'vue-router';
import type {
  NavGroup,
  NavLink,
  NavSectionTitle,
  VerticalNavItems,
} from '../types';
import { useBlockchain } from '@/stores';

const bch = useBlockchain();

function isNavLink(nav: VerticalNavItems | any): nav is NavLink {
  return (<NavLink>nav).to !== undefined;
}

</script>

<template>
  <div class="join">
    <RouterLink class="btn rounded-none cosmos-styles skew-x-[-35deg] transform normal-case"
    to="/cosmos"
    >
      <span class="skew-x-[35deg] transform ">
        _Dashboard
      </span>
    </RouterLink>
    <RouterLink class="btn rounded-none cosmos-styles skew-x-[-35deg] transform normal-case"
    
    >
      <span class="skew-x-[35deg] transform ">
        _Stacking
      </span>
    </RouterLink>
    <RouterLink class="btn rounded-none cosmos-styles skew-x-[-35deg] transform normal-case"
    
    >
      <span class="skew-x-[35deg] transform ">
        _Governance
      </span>
    </RouterLink>
  </div>
</template>

