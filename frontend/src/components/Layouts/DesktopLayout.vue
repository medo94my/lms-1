<template>
	<div class="flex h-screen w-screen">
		<div class="h-full border-e bg-surface-sidebar">
			<AppSidebar />
		</div>
		<!-- Page content panel: theme-aware via --lms-page-bg (basiret-theme.css):
		     cream (#fbf8f0) in light, dark neutral (#171717) in dark. Cards/modals/
		     header stay white. Using a CSS var (not a dark: variant) keeps this
		     deterministic and independent of JIT variant emission. -->
		<div
			class="flex-1 flex flex-col h-full overflow-auto bg-[var(--lms-page-bg)]"
		>
			<slot />
		</div>
	</div>
</template>
<script setup>
import AppSidebar from '@/components/Sidebar/AppSidebar.vue'
</script>
