<template>
	<div class="flex h-screen w-screen">
		<div class="h-full border-e bg-surface-sidebar">
			<AppSidebar />
		</div>
		<!-- Page content panel: cream (#fbf8f0 / cream-100) so the page reads as
		     brand while cards/modals/header stay white (those use bg-white /
		     --surface-elevation-* / --surface-base, left untouched). -->
		<div class="flex-1 flex flex-col h-full overflow-auto bg-[#fbf8f0]">
			<slot />
		</div>
	</div>
</template>
<script setup>
import AppSidebar from '@/components/Sidebar/AppSidebar.vue'
</script>
