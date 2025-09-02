<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { user } from '$lib/stores';
	import { getUserTokenSummary } from '$lib/apis/token-usage';

	import Spinner from '$lib/components/common/Spinner.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import ChartBar from '$lib/components/icons/ChartBar.svelte';

	const i18n = getContext('i18n');

	let loading = true;
	let tokenSummary: any = null;
	let error: string | null = null;

	const loadTokenSummary = async () => {
		try {
			loading = true;
			error = null;
			tokenSummary = await getUserTokenSummary(localStorage.token, $user.id);
		} catch (err) {
			error = err.message || 'Failed to load token usage';
		} finally {
			loading = false;
		}
	};

	const formatNumber = (num: number) => {
		if (num === undefined || num === null) return 'N/A';
		return num.toLocaleString();
	};

	const getUsageColor = (percentage: number | undefined) => {
		if (percentage === undefined || percentage === null) return 'gray';
		if (percentage >= 90) return 'red';
		if (percentage >= 75) return 'yellow';
		return 'green';
	};

	const getUsageStatus = (percentage: number | undefined) => {
		if (percentage === undefined || percentage === null) return 'No Limit';
		if (percentage >= 90) return 'Critical';
		if (percentage >= 75) return 'Warning';
		return 'Good';
	};

	onMount(() => {
		loadTokenSummary();
	});
</script>

<div class="space-y-6">
	<div class="flex items-center space-x-2">
		<ChartBar className="w-5 h-5" />
		<h3 class="text-lg font-semibold">Token Usage</h3>
	</div>

	{#if loading}
		<div class="flex justify-center py-8">
			<Spinner />
		</div>
	{:else if error}
		<div class="text-center py-8 text-red-500">
			<p>{error}</p>
			<button
				class="mt-2 text-sm text-blue-500 hover:underline"
				on:click={loadTokenSummary}
			>
				Try Again
			</button>
		</div>
	{:else if tokenSummary}
		<div class="space-y-6">
			<!-- Usage Overview -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
					<div class="text-sm font-medium text-gray-600 dark:text-gray-400">
						Total Tokens Used
					</div>
					<div class="text-2xl font-bold">
						{formatNumber(tokenSummary.total_tokens)}
					</div>
					<div class="text-xs text-gray-500 mt-1">
						All time
					</div>
				</div>

				<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
					<div class="text-sm font-medium text-gray-600 dark:text-gray-400">
						Daily Usage
					</div>
					<div class="text-2xl font-bold">
						{formatNumber(tokenSummary.daily_tokens)}
					</div>
					{#if tokenSummary.daily_limit}
						<div class="text-xs text-gray-500 mt-1">
							Limit: {formatNumber(tokenSummary.daily_limit)}
						</div>
					{/if}
				</div>

				<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
					<div class="text-sm font-medium text-gray-600 dark:text-gray-400">
						Monthly Usage
					</div>
					<div class="text-2xl font-bold">
						{formatNumber(tokenSummary.monthly_tokens)}
					</div>
					{#if tokenSummary.monthly_limit}
						<div class="text-xs text-gray-500 mt-1">
							Limit: {formatNumber(tokenSummary.monthly_limit)}
						</div>
					{/if}
				</div>
			</div>

			<!-- Detailed Usage -->
			<div class="space-y-4">
				<h4 class="text-md font-medium">Usage Breakdown</h4>
				
				<!-- Daily Usage -->
				{#if tokenSummary.daily_limit}
					<div class="space-y-2">
						<div class="flex items-center justify-between">
							<span class="text-sm font-medium">Daily Usage</span>
							<span class="text-sm text-gray-600 dark:text-gray-400">
								{formatNumber(tokenSummary.daily_tokens)} / {formatNumber(tokenSummary.daily_limit)}
							</span>
						</div>
						<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
							<div
								class="h-3 rounded-full transition-all duration-300"
								class:bg-red-500={tokenSummary.daily_usage_percentage && tokenSummary.daily_usage_percentage >= 90}
								class:bg-yellow-500={tokenSummary.daily_usage_percentage && tokenSummary.daily_usage_percentage >= 75 && tokenSummary.daily_usage_percentage < 90}
								class:bg-green-500={!tokenSummary.daily_usage_percentage || tokenSummary.daily_usage_percentage < 75}
								style="width: {Math.min((tokenSummary.daily_usage_percentage || 0), 100)}%"
							></div>
						</div>
						<div class="flex items-center justify-between text-xs">
							<span class="text-gray-500">
								{Math.round(tokenSummary.daily_usage_percentage || 0)}% used
							</span>
							<Badge
								variant={getUsageColor(tokenSummary.daily_usage_percentage) === 'red' ? 'destructive' : 
										getUsageColor(tokenSummary.daily_usage_percentage) === 'yellow' ? 'secondary' : 'default'}
								size="sm"
							>
								{getUsageStatus(tokenSummary.daily_usage_percentage)}
							</Badge>
						</div>
					</div>
				{/if}

				<!-- Monthly Usage -->
				{#if tokenSummary.monthly_limit}
					<div class="space-y-2">
						<div class="flex items-center justify-between">
							<span class="text-sm font-medium">Monthly Usage</span>
							<span class="text-sm text-gray-600 dark:text-gray-400">
								{formatNumber(tokenSummary.monthly_tokens)} / {formatNumber(tokenSummary.monthly_limit)}
							</span>
						</div>
						<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
							<div
								class="h-3 rounded-full transition-all duration-300"
								class:bg-red-500={tokenSummary.monthly_usage_percentage && tokenSummary.monthly_usage_percentage >= 90}
								class:bg-yellow-500={tokenSummary.monthly_usage_percentage && tokenSummary.monthly_usage_percentage >= 75 && tokenSummary.monthly_usage_percentage < 90}
								class:bg-green-500={!tokenSummary.monthly_usage_percentage || tokenSummary.monthly_usage_percentage < 75}
								style="width: {Math.min((tokenSummary.monthly_usage_percentage || 0), 100)}%"
							></div>
						</div>
						<div class="flex items-center justify-between text-xs">
							<span class="text-gray-500">
								{Math.round(tokenSummary.monthly_usage_percentage || 0)}% used
							</span>
							<Badge
								variant={getUsageColor(tokenSummary.monthly_usage_percentage) === 'red' ? 'destructive' : 
										getUsageColor(tokenSummary.monthly_usage_percentage) === 'yellow' ? 'secondary' : 'default'}
								size="sm"
							>
								{getUsageStatus(tokenSummary.monthly_usage_percentage)}
							</Badge>
						</div>
					</div>
				{/if}

				<!-- Total Usage -->
				{#if tokenSummary.total_limit}
					<div class="space-y-2">
						<div class="flex items-center justify-between">
							<span class="text-sm font-medium">Total Usage</span>
							<span class="text-sm text-gray-600 dark:text-gray-400">
								{formatNumber(tokenSummary.total_tokens)} / {formatNumber(tokenSummary.total_limit)}
							</span>
						</div>
						<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
							<div
								class="h-3 rounded-full transition-all duration-300"
								class:bg-red-500={tokenSummary.total_usage_percentage && tokenSummary.total_usage_percentage >= 90}
								class:bg-yellow-500={tokenSummary.total_usage_percentage && tokenSummary.total_usage_percentage >= 75 && tokenSummary.total_usage_percentage < 90}
								class:bg-green-500={!tokenSummary.total_usage_percentage || tokenSummary.total_usage_percentage < 75}
								style="width: {Math.min((tokenSummary.total_usage_percentage || 0), 100)}%"
							></div>
						</div>
						<div class="flex items-center justify-between text-xs">
							<span class="text-gray-500">
								{Math.round(tokenSummary.total_usage_percentage || 0)}% used
							</span>
							<Badge
								variant={getUsageColor(tokenSummary.total_usage_percentage) === 'red' ? 'destructive' : 
										getUsageColor(tokenSummary.total_usage_percentage) === 'yellow' ? 'secondary' : 'default'}
								size="sm"
							>
								{getUsageStatus(tokenSummary.total_usage_percentage)}
							</Badge>
						</div>
					</div>
				{/if}
			</div>

			<!-- Token Types -->
			<div class="space-y-4">
				<h4 class="text-md font-medium">Token Types</h4>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
						<div class="text-sm font-medium text-gray-600 dark:text-gray-400">
							Prompt Tokens
						</div>
						<div class="text-xl font-bold">
							{formatNumber(tokenSummary.prompt_tokens)}
						</div>
						<div class="text-xs text-gray-500 mt-1">
							Input tokens this month
						</div>
					</div>

					<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
						<div class="text-sm font-medium text-gray-600 dark:text-gray-400">
							Completion Tokens
						</div>
						<div class="text-xl font-bold">
							{formatNumber(tokenSummary.completion_tokens)}
						</div>
						<div class="text-xs text-gray-500 mt-1">
							Output tokens this month
						</div>
					</div>
				</div>
			</div>

			<!-- No Limits Message -->
			{#if !tokenSummary.daily_limit && !tokenSummary.monthly_limit && !tokenSummary.total_limit}
				<div class="text-center py-6 text-gray-500">
					<p>No token limits have been set for your account.</p>
					<p class="text-sm mt-1">Contact your administrator to set usage limits.</p>
				</div>
			{/if}
		</div>
	{:else}
		<div class="text-center py-8 text-gray-500">
			<p>No token usage data available.</p>
		</div>
	{/if}

	<!-- Refresh Button -->
	<div class="flex justify-center">
		<button
			class="text-sm text-blue-500 hover:underline"
			on:click={loadTokenSummary}
		>
			Refresh Usage Data
		</button>
	</div>
</div> 