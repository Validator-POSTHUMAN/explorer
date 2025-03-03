<script setup lang="ts">
defineProps<{
  text: string;
  href: string;
}>();
</script>

<template>
  <a
    class="h-16 flex items-center px-8 text-white hover:underline"
    :href="href"
    >{{ text }}</a
  >
  <div class="h-full w-[1px] bg-[#686868] -skew-x-[35deg]"></div>
</template>
