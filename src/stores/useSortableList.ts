import { ref, computed } from 'vue';

export function useSortableList<T>(source: () => T[]) {
  const sortByField = ref<string>('');
  const sortDirection = ref<'asc' | 'desc'>('asc');

  const sortedList = computed(() => {
    if (!sortByField.value) return source();

    return [...source()].sort((a, b) => {
      const varA = (a as any)[sortByField.value] ?? 0;
      const varB = (b as any)[sortByField.value] ?? 0;

      return sortDirection.value === 'asc'
        ? varA - varB
        : varB - varA;
    });
  });

  const toggleSort = (field: string) => {
    if (sortByField.value === field) {
      sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
    } else {
      sortByField.value = field;
      sortDirection.value = 'asc';
    }
  };

  return {
    sortedList,
    sortByField,
    sortDirection,
    toggleSort,
  };
}
