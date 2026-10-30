/**
 * HCM One Frontend API Client
 * Connects to the deterministic FastAPI backend.
 * Zero frontend calculations.
 */

const ENV_API_BASE = import.meta.env.VITE_API_BASE_URL;
const BASE_URL = ENV_API_BASE ? ENV_API_BASE.replace(/\/+$/, "") : "http://localhost:8000";
const API_BASE = BASE_URL.endsWith("/api") ? BASE_URL : `${BASE_URL}/api`;

let currentUserId = "HR01";

export function setCurrentUserId(userId: string) {
  currentUserId = userId;
}

export function getCurrentUserId(): string {
  return currentUserId;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    "X-User-Id": currentUserId,
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "API error";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail));
  }

  return response.json();
}

export const api = {
  // Auth
  getMe: () => request<any>("/me"),
  getUsers: () => request<any[]>("/users"),
  getEmployees: () => request<any[]>("/employees"),
  login: (userId: string) => {
    setCurrentUserId(userId);
    return request<any>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    });
  },

  // Scenarios
  listScenarios: () => request<any[]>("/scenarios"),
  getScenario: (scenarioId: string) => request<any>(`/scenarios/${scenarioId}`),

  // Proposals
  calculateBonusScope: (bonusType: string, period: string, selectedEmployeeIds: string[]) =>
    request<any>("/proposals/bonus/calculate-scope", {
      method: "POST",
      body: JSON.stringify({
        bonus_type: bonusType,
        period: period,
        selected_employee_ids: selectedEmployeeIds,
      }),
    }),

  approveProposal: (proposalId: string, version: number, selectedScope?: any) =>
    request<any>(`/proposals/${proposalId}/approve`, {
      method: "POST",
      body: JSON.stringify({
        version,
        selected_scope: selectedScope,
      }),
    }),

  editProposal: (proposalId: string, line: string, proposedValue: any, reason: string) =>
    request<any>(`/proposals/${proposalId}/edit`, {
      method: "POST",
      body: JSON.stringify({
        line,
        proposed_value: proposedValue,
        reason,
      }),
    }),

  rejectProposal: (proposalId: string, reason?: string) =>
    request<any>(`/proposals/${proposalId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  // Payslip comparison & TDS
  comparePayslips: (employeeId: string) =>
    request<any>(`/payslips/compare?employee_id=${employeeId}`),

  getTdsDetail: (employeeId: string) =>
    request<any>(`/tds/detail?employee_id=${employeeId}`),

  // Queries
  listQueries: () => request<any[]>("/queries"),
  getQuery: (queryId: string) => request<any>(`/queries/${queryId}`),

  draftQuery: (employeeId: string, category: string, months: string[], description: string, evidence: any[]) =>
    request<any>("/queries/draft", {
      method: "POST",
      body: JSON.stringify({
        employee_id: employeeId,
        category,
        months,
        description,
        evidence,
      }),
    }),

  confirmSendQuery: (draft: any, addOrNew: 'new' | 'add', targetQueryId?: string | null, confirmed: boolean = true) =>
    request<any>("/queries/confirm-send", {
      method: "POST",
      body: JSON.stringify({
        draft,
        add_or_new: addOrNew,
        target_query_id: targetQueryId,
        confirmed,
      }),
    }),

  takeIntoReview: (queryId: string) =>
    request<any>(`/queries/${queryId}/take-into-review`, {
      method: "POST",
    }),

  replyQuery: (queryId: string, replyText: string) =>
    request<any>(`/queries/${queryId}/reply`, {
      method: "POST",
      body: JSON.stringify({ reply_text: replyText }),
    }),

  resolveQuery: (queryId: string, replyText?: string) =>
    request<any>(`/queries/${queryId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ reply_text: replyText }),
    }),

  disputeQuery: (queryId: string, reason?: string) =>
    request<any>(`/queries/${queryId}/dispute`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  closeQuery: (queryId: string) =>
    request<any>(`/queries/${queryId}/close`, {
      method: "POST",
    }),

  // Demo reset
  resetDemo: () =>
    request<any>("/demo/reset", {
      method: "POST",
    }),

  getAiMessages: () => request<Record<string, string>>("/ai/messages"),

  // Chat-first endpoint per chat_contract.md
  chat: (
    userIdOrOptions: string | { userId: string; message?: string; action?: string | null; context?: any },
    message: string = "",
    action?: string | null,
    context?: any
  ) => {
    let uId = "";
    let msg = "";
    let act: string | null = null;
    let ctx = {};

    if (typeof userIdOrOptions === "object" && userIdOrOptions !== null) {
      uId = userIdOrOptions.userId;
      msg = userIdOrOptions.message || "";
      act = userIdOrOptions.action || null;
      ctx = userIdOrOptions.context || {};
    } else {
      uId = userIdOrOptions;
      msg = message;
      act = action || null;
      ctx = context || {};
    }

    return request<any>("/chat", {
      method: "POST",
      body: JSON.stringify({
        user_id: uId,
        message: msg,
        action: act,
        context: ctx,
      }),
    });
  },
};
