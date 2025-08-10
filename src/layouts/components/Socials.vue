<script lang="ts" setup>
import { Icon } from '@iconify/vue';

const props = defineProps({
    list: Object,
    className: String
});

</script>
<template>
    <div class="absolute bottom-0 xl:flex flex-col gap-4 text-base text-white p-4" :class="className" >
        <p class="mb-3">{{ $t('module.links') }}</p>
        <a class="flex items-center hover:text-addition" v-for="social in list" :href="social.href" target="_blank"
          :key="social.name">
          <Icon :icon="social.icon" class="text-xl mr-2" width="20" height="20" />
          <span class="capitalize">{{ social.name }}</span>
        </a>

      </div>
</template>