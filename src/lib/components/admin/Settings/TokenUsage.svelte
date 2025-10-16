<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { user } from '$lib/stores';

	import {
		getAllUserTokenLimits,
		getAllUsersTokenSummary,
		createUserTokenLimits,
		updateUserTokenLimits,
		deleteUserTokenLimits,
		type UserTokenLimitsCreate,
		type UserTokenLimitsUpdate,
		type TokenUsageSummary
	} from '$lib/apis/token-usage';
	import { getUsers } from '$lib/apis/users';

	import Button from '$lib/components/common/Button.svelte';
	import Input from '$lib/components/common/Input.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import Edit from '$lib/components/icons/Edit.svelte';
	import Trash from '$lib/components/icons/Trash.svelte';
	import ChartBar from '$lib/components/icons/ChartBar.svelte';

	const i18n = getContext('i18n');

	let loading = true;
	let users: any[] = [];
	let userLimits: any[] = [];
	let userSummaries: TokenUsageSummary[] = [];
	let showCreateModal = false;
	let showEditModal = false;
	let selectedUser = null;
	let selectedLimits = null;

	// Form data
	let createForm: UserTokenLimitsCreate = {
		user_id: '',
		daily_token_limit: undefined,
		monthly_token_limit: undefined,
		total_token_limit: undefined,
		notify_at_percentage: 80
	};

	let editForm: UserTokenLimitsUpdate = {
		daily_token_limit: undefined,
		monthly_token_limit: undefined,
		total_token_limit: undefined,
		is_active: true,
		notify_at_percentage: 80
	};

	const loadData = async () => {
		try {
			loading = true;
			const [usersRes, limitsRes, summariesRes] = await Promise.all([
				getUsers(localStorage.token),
				getAllUserTokenLimits(localStorage.token),
				getAllUsersTokenSummary(localStorage.token)
			]);

			users = usersRes.users || [];
			userLimits = limitsRes.limits || [];
			userSummaries = summariesRes.summaries || [];
		} catch (error) {
			toast.error(`Failed to load data: ${error}`);
		} finally {
			loading = false;
		}
	};

	const getUserLimits = (userId: string) => {
		return userLimits.find(limit => limit.user_id === userId);
	};

	const getUserSummary = (userId: string) => {
		return userSummaries.find(summary => summary.user_id === userId);
	};

	const openCreateModal = (user: any) => {
		selectedUser = user;
		createForm = {
			user_id: user.id,
			daily_token_limit: undefined,
			monthly_token_limit: undefined,
			total_token_limit: undefined,
			notify_at_percentage: 80
		};
		showCreateModal = true;
	};

	const openEditModal = (user: any) => {
		selectedUser = user;
		const limits = getUserLimits(user.id);
		if (limits) {
			selectedLimits = limits;
			editForm = {
				daily_token_limit: limits.daily_token_limit,
				monthly_token_limit: limits.monthly_token_limit,
				total_token_limit: limits.total_token_limit,
				is_active: limits.is_active,
				notify_at_percentage: limits.notify_at_percentage
			};
			showEditModal = true;
		}
	};

	const handleCreate = async () => {
		try {
			await createUserTokenLimits(localStorage.token, createForm);
			toast.success('Token limits created successfully');
			showCreateModal = false;
			await loadData();
		} catch (error) {
			toast.error(`Failed to create token limits: ${error}`);
		}
	};

	const handleUpdate = async () => {
		try {
			await updateUserTokenLimits(localStorage.token, selectedUser.id, editForm);
			toast.success('Token limits updated successfully');
			showEditModal = false;
			await loadData();
		} catch (error) {
			toast.error(`Failed to update token limits: ${error}`);
		}
	};

	const handleDelete = async (userId: string) => {
		if (confirm('Are you sure you want to delete token limits for this user?')) {
			try {
				await deleteUserTokenLimits(localStorage.token, userId);
				toast.success('Token limits deleted successfully');
				await loadData();
			} catch (error) {
				toast.error(`Failed to delete token limits: ${error}`);
			}
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

	onMount(() => {
		loadData();
	});
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h2 class="text-lg font-semibold">Token Usage Management</h2>
			<p class="text-sm text-gray-600 dark:text-gray-400">
				Monitor and manage token usage limits for all users
			</p>
		</div>
		<Button on:click={() => loadData()} variant="outline" size="sm">
			<ChartBar className="w-4 h-4 mr-2" />
			Refresh
		</Button>
	</div>

	{#if loading}
		<div class="flex justify-center py-8">
			<Spinner />
		</div>
	{:else}
		<div class="space-y-4">
			{#each users as user}
				{@const limits = getUserLimits(user.id)}
				{@const summary = getUserSummary(user.id)}
				<div class="border rounded-lg p-4 space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<div class="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
								<span class="text-sm font-medium">
									{user.name?.charAt(0)?.toUpperCase() || user.email?.charAt(0)?.toUpperCase()}
								</span>
							</div>
							<div>
								<div class="font-medium">{user.name || 'N/A'}</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">{user.email}</div>
								<div class="text-xs text-gray-500">
									Role: <Badge variant="outline" size="sm">{user.role}</Badge>
								</div>
							</div>
						</div>
						<div class="flex items-center space-x-2">
							{#if limits}
								<Button on:click={() => openEditModal(user)} variant="outline" size="sm">
									<Edit className="w-4 h-4 mr-2" />
									Edit Limits
								</Button>
								<Button on:click={() => handleDelete(user.id)} variant="outline" size="sm" color="red">
									<Trash className="w-4 h-4 mr-2" />
									Delete
								</Button>
							{:else}
								<Button on:click={() => openCreateModal(user)} variant="outline" size="sm">
									<Plus className="w-4 h-4 mr-2" />
									Set Limits
								</Button>
							{/if}
						</div>
					</div>

					{#if limits}
						<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
							<div class="space-y-2">
								<div class="text-sm font-medium">Daily Usage</div>
								<div class="text-2xl font-bold">
									{formatNumber(summary?.daily_tokens || 0)}
								</div>
								{#if limits.daily_token_limit}
									<div class="text-sm text-gray-600 dark:text-gray-400">
										Limit: {formatNumber(limits.daily_token_limit)}
									</div>
									<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
										<div
											class="h-2 rounded-full transition-all duration-300"
											class:bg-red-500={summary?.daily_usage_percentage && summary.daily_usage_percentage >= 90}
											class:bg-yellow-500={summary?.daily_usage_percentage && summary.daily_usage_percentage >= 75 && summary.daily_usage_percentage < 90}
											class:bg-green-500={!summary?.daily_usage_percentage || summary.daily_usage_percentage < 75}
											style="width: {Math.min((summary?.daily_usage_percentage || 0), 100)}%"
										></div>
									</div>
									<div class="text-xs text-gray-500">
										{Math.round(summary?.daily_usage_percentage || 0)}% used
									</div>
								{/if}
							</div>

							<div class="space-y-2">
								<div class="text-sm font-medium">Monthly Usage</div>
								<div class="text-2xl font-bold">
									{formatNumber(summary?.monthly_tokens || 0)}
								</div>
								{#if limits.monthly_token_limit}
									<div class="text-sm text-gray-600 dark:text-gray-400">
										Limit: {formatNumber(limits.monthly_token_limit)}
									</div>
									<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
										<div
											class="h-2 rounded-full transition-all duration-300"
											class:bg-red-500={summary?.monthly_usage_percentage && summary.monthly_usage_percentage >= 90}
											class:bg-yellow-500={summary?.monthly_usage_percentage && summary.monthly_usage_percentage >= 75 && summary.monthly_usage_percentage < 90}
											class:bg-green-500={!summary?.monthly_usage_percentage || summary.monthly_usage_percentage < 75}
											style="width: {Math.min((summary?.monthly_usage_percentage || 0), 100)}%"
										></div>
									</div>
									<div class="text-xs text-gray-500">
										{Math.round(summary?.monthly_usage_percentage || 0)}% used
									</div>
								{/if}
							</div>

							<div class="space-y-2">
								<div class="text-sm font-medium">Total Usage</div>
								<div class="text-2xl font-bold">
									{formatNumber(summary?.total_tokens || 0)}
								</div>
								{#if limits.total_token_limit}
									<div class="text-sm text-gray-600 dark:text-gray-400">
										Limit: {formatNumber(limits.total_token_limit)}
									</div>
									<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
										<div
											class="h-2 rounded-full transition-all duration-300"
											class:bg-red-500={summary?.total_usage_percentage && summary.total_usage_percentage >= 90}
											class:bg-yellow-500={summary?.total_usage_percentage && summary.total_usage_percentage >= 75 && summary.total_usage_percentage < 90}
											class:bg-green-500={!summary?.total_usage_percentage || summary.total_usage_percentage < 75}
											style="width: {Math.min((summary?.total_usage_percentage || 0), 100)}%"
										></div>
									</div>
									<div class="text-xs text-gray-500">
										{Math.round(summary?.total_usage_percentage || 0)}% used
									</div>
								{/if}
							</div>
						</div>

						<div class="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
							<div>
								Notify at: {limits.notify_at_percentage}%
							</div>
							<div>
								Status: 
								<Badge variant={limits.is_active ? 'default' : 'secondary'} size="sm">
									{limits.is_active ? 'Active' : 'Inactive'}
								</Badge>
							</div>
						</div>
					{:else}
						<div class="text-center py-4 text-gray-500">
							No token limits set for this user
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Create Modal -->
{#if showCreateModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
			<h3 class="text-lg font-semibold mb-4">Set Token Limits for {selectedUser?.name || selectedUser?.email}</h3>
			
			<div class="space-y-4">
                                {@const createDailyId = 'create-daily-token-limit'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={createDailyId}>Daily Token Limit</label>
                                        <Input
                                                type="number"
                                                bind:value={createForm.daily_token_limit}
                                                placeholder="Enter daily limit (optional)"
                                                id={createDailyId}
                                        />
                                </div>

                                {@const createMonthlyId = 'create-monthly-token-limit'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={createMonthlyId}
                                                >Monthly Token Limit</label
                                        >
                                        <Input
                                                type="number"
                                                bind:value={createForm.monthly_token_limit}
                                                placeholder="Enter monthly limit (optional)"
                                                id={createMonthlyId}
                                        />
                                </div>

                                {@const createTotalId = 'create-total-token-limit'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={createTotalId}
                                                >Total Token Limit</label
                                        >
                                        <Input
                                                type="number"
                                                bind:value={createForm.total_token_limit}
                                                placeholder="Enter total limit (optional)"
                                                id={createTotalId}
                                        />
                                </div>

                                {@const createNotifyId = 'create-notify-percentage'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={createNotifyId}
                                                >Notify at Percentage</label
                                        >
                                        <Input
                                                type="number"
                                                bind:value={createForm.notify_at_percentage}
                                                min="1"
                                                max="100"
                                                placeholder="80"
                                                id={createNotifyId}
                                        />
                                </div>
			</div>
			
			<div class="flex justify-end space-x-2 mt-6">
				<Button variant="outline" on:click={() => showCreateModal = false}>
					Cancel
				</Button>
				<Button on:click={handleCreate}>
					Create Limits
				</Button>
			</div>
		</div>
	</div>
{/if}

<!-- Edit Modal -->
{#if showEditModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
			<h3 class="text-lg font-semibold mb-4">Edit Token Limits for {selectedUser?.name || selectedUser?.email}</h3>
			
			<div class="space-y-4">
                                {@const editDailyId = 'edit-daily-token-limit'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={editDailyId}>Daily Token Limit</label>
                                        <Input
                                                type="number"
                                                bind:value={editForm.daily_token_limit}
                                                placeholder="Enter daily limit (optional)"
                                                id={editDailyId}
                                        />
                                </div>

                                {@const editMonthlyId = 'edit-monthly-token-limit'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={editMonthlyId}
                                                >Monthly Token Limit</label
                                        >
                                        <Input
                                                type="number"
                                                bind:value={editForm.monthly_token_limit}
                                                placeholder="Enter monthly limit (optional)"
                                                id={editMonthlyId}
                                        />
                                </div>

                                {@const editTotalId = 'edit-total-token-limit'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={editTotalId}>Total Token Limit</label>
                                        <Input
                                                type="number"
                                                bind:value={editForm.total_token_limit}
                                                placeholder="Enter total limit (optional)"
                                                id={editTotalId}
                                        />
                                </div>

                                {@const editNotifyId = 'edit-notify-percentage'}
                                <div>
                                        <label class="block text-sm font-medium mb-2" for={editNotifyId}
                                                >Notify at Percentage</label
                                        >
                                        <Input
                                                type="number"
                                                bind:value={editForm.notify_at_percentage}
                                                min="1"
                                                max="100"
                                                placeholder="80"
                                                id={editNotifyId}
                                        />
                                </div>

                                {@const editActiveId = 'edit-token-active'}
                                <div class="flex items-center space-x-2">
                                        <Switch bind:state={editForm.is_active} id={editActiveId} />
                                        <label class="text-sm font-medium" for={editActiveId}>Active</label>
                                </div>
			</div>
			
			<div class="flex justify-end space-x-2 mt-6">
				<Button variant="outline" on:click={() => showEditModal = false}>
					Cancel
				</Button>
				<Button on:click={handleUpdate}>
					Update Limits
				</Button>
			</div>
		</div>
	</div>
{/if} 