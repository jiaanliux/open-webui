import { WEBUI_BASE_URL } from '$lib/constants';

// Types
export interface TokenUsageCreate {
	user_id: string;
	model_id?: string;
	session_id?: string;
	chat_id?: string;
	prompt_tokens: number;
	completion_tokens: number;
	total_tokens: number;
	request_type?: string;
	cost?: string;
}

export interface UserTokenLimitsCreate {
	user_id: string;
	daily_token_limit?: number;
	monthly_token_limit?: number;
	total_token_limit?: number;
	notify_at_percentage?: number;
}

export interface UserTokenLimitsUpdate {
	daily_token_limit?: number;
	monthly_token_limit?: number;
	total_token_limit?: number;
	is_active?: boolean;
	notify_at_percentage?: number;
}

export interface TokenUsageSummary {
	user_id: string;
	total_tokens: number;
	prompt_tokens: number;
	completion_tokens: number;
	daily_tokens: number;
	monthly_tokens: number;
	daily_limit?: number;
	monthly_limit?: number;
	total_limit?: number;
	daily_usage_percentage?: number;
	monthly_usage_percentage?: number;
	total_usage_percentage?: number;
}

// Token Usage Tracking
export const trackTokenUsage = async (token: string, usageData: TokenUsageCreate) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/track`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(usageData)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to track token usage');
	}

	return res.json();
};

export const getUserTokenUsage = async (
	token: string,
	userId: string,
	startTime?: number,
	endTime?: number
) => {
	const params = new URLSearchParams();
	if (startTime) params.append('start_time', startTime.toString());
	if (endTime) params.append('end_time', endTime.toString());

	const res = await fetch(
		`${WEBUI_BASE_URL}/api/v1/token-usage/user/${userId}?${params}`,
		{
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${token}`
			}
		}
	);

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to get user token usage');
	}

	return res.json();
};

export const getUserTokenSummary = async (token: string, userId: string) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/user/${userId}/summary`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to get user token summary');
	}

	return res.json() as Promise<TokenUsageSummary>;
};

// Admin Token Limits Management
export const createUserTokenLimits = async (token: string, limitsData: UserTokenLimitsCreate) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/admin/limits`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(limitsData)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to create user token limits');
	}

	return res.json();
};

export const getUserTokenLimits = async (token: string, userId: string) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/admin/limits/${userId}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to get user token limits');
	}

	return res.json();
};

export const updateUserTokenLimits = async (
	token: string,
	userId: string,
	updateData: UserTokenLimitsUpdate
) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/admin/limits/${userId}`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(updateData)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to update user token limits');
	}

	return res.json();
};

export const deleteUserTokenLimits = async (token: string, userId: string) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/admin/limits/${userId}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to delete user token limits');
	}

	return res.json();
};

export const getAllUserTokenLimits = async (token: string) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/admin/limits`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to get all user token limits');
	}

	return res.json();
};

export const getAllUsersTokenSummary = async (token: string) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/admin/usage/summary`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to get all users token summary');
	}

	return res.json();
};

// Utility Functions
export const convertOllamaUsage = async (token: string, ollamaUsage: any) => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/v1/token-usage/convert-ollama-usage`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(ollamaUsage)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to convert Ollama usage');
	}

	return res.json();
}; 