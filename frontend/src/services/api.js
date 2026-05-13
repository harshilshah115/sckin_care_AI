/**
 * API Service Layer
 * Connects React frontend to Django backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// Token management
const getToken = () => localStorage.getItem('access_token');
const getRefreshToken = () => localStorage.getItem('refresh_token');
const setTokens = (access, refresh) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
};
const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// Base fetch wrapper with auth
async function fetchWithAuth(endpoint, options = {}) {
  const token = getToken();
  
  const config = {
    ...options,
    headers: {
      ...options.headers,
    },
  };

  // Add auth header if token exists
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // Add Content-Type for JSON (not for FormData)
  if (!(options.body instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json';
  }

  try {
    let response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // If 401, try to refresh token
    if (response.status === 401 && getRefreshToken()) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry with new token
        config.headers['Authorization'] = `Bearer ${getToken()}`;
        response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      }
    }

    return response;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Normalize list responses from DRF (pagination vs. plain lists)
function normalizeListResponse(data) {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
}

// Refresh access token
async function refreshAccessToken() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: getRefreshToken() }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access);
      return true;
    }
    
    // Refresh failed, clear tokens
    clearTokens();
    return false;
  } catch {
    clearTokens();
    return false;
  }
}

// ============================================
// AUTH API
// ============================================

export const authAPI = {
  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    
    const data = await response.json();
    
    if (response.ok && data.tokens) {
      setTokens(data.tokens.access, data.tokens.refresh);
    }
    
    return { ok: response.ok, data };
  },

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    const data = await response.json();
    
    if (response.ok && data.tokens) {
      setTokens(data.tokens.access, data.tokens.refresh);
    }
    
    return { ok: response.ok, data };
  },

  async logout() {
    try {
      await fetchWithAuth('/auth/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh: getRefreshToken() }),
      });
    } finally {
      clearTokens();
    }
  },

  async getProfile() {
    const response = await fetchWithAuth('/auth/profile/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async updateProfile(profileData) {
    const response = await fetchWithAuth('/auth/profile/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  isAuthenticated() {
    return !!getToken();
  },

  clearAuth() {
    clearTokens();
  }
};

// ============================================
// SKIN SCAN API
// ============================================

export const scanAPI = {
  async uploadScan(imageFile, scanType = 'full_face', context = {}) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('scan_type', scanType);

    if (context.age) formData.append('age', context.age);
    if (context.skinType) formData.append('skin_type', context.skinType);
    if (context.sleepHours) formData.append('sleep_hours', context.sleepHours);
    if (context.waterIntake) formData.append('water_intake', context.waterIntake);

    const response = await fetchWithAuth('/scan/', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getScanHistory() {
    const response = await fetchWithAuth('/scan/list/');
    const data = await response.json();
    return { ok: response.ok, data: normalizeListResponse(data) };
  },

  async getScanDetail(scanId) {
    const response = await fetchWithAuth(`/scan/${scanId}/`);
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async deleteScan(scanId) {
    const response = await fetchWithAuth(`/scan/${scanId}/`, {
      method: 'DELETE',
    });
    return { ok: response.ok };
  }
};

// ============================================
// QUESTION API
// ============================================

export const questionAPI = {
  async askQuestion(questionText, category = 'general') {
    const response = await fetchWithAuth('/scan/ask/', {
      method: 'POST',
      body: JSON.stringify({ 
        question_text: questionText,
        category: category 
      }),
    });
    
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getQuestionHistory() {
    const response = await fetchWithAuth('/scan/questions/');
    const data = await response.json();
    return { ok: response.ok, data: normalizeListResponse(data) };
  },

  async getQuestionDetail(questionId) {
    const response = await fetchWithAuth(`/scan/questions/${questionId}/`);
    const data = await response.json();
    return { ok: response.ok, data };
  }
};

// ============================================
// PRODUCTS API
// ============================================

export const productsAPI = {
  async getProducts(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.skin_type) params.append('skin_type', filters.skin_type);
    if (filters.concern) params.append('concern', filters.concern);
    if (filters.category) params.append('category', filters.category);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.search) params.append('search', filters.search);

    const queryString = params.toString();
    const endpoint = `/products/${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetchWithAuth(endpoint);
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getProductDetail(productId) {
    const response = await fetchWithAuth(`/products/${productId}/`);
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getCategories() {
    const response = await fetchWithAuth('/products/categories/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getFeaturedProducts() {
    const response = await fetchWithAuth('/products/featured/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getPersonalizedProducts() {
    const response = await fetchWithAuth('/products/personalized/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getNaturalRemedies(filters = {}) {
    const params = new URLSearchParams();
    if (filters.concern) params.append('concern', filters.concern);
    if (filters.skin_type) params.append('skin_type', filters.skin_type);
    
    const queryString = params.toString();
    const endpoint = `/products/remedies/${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetchWithAuth(endpoint);
    const data = await response.json();
    return { ok: response.ok, data };
  }
};

// ============================================
// RECOMMENDATIONS API (Saved Items)
// ============================================

export const savedAPI = {
  // Saved Products
  async getSavedProducts() {
    const response = await fetchWithAuth('/recommendations/saved/products/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async saveProduct(productId, notes = '') {
    const response = await fetchWithAuth('/recommendations/saved/products/', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, notes }),
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async removeSavedProduct(savedId) {
    const response = await fetchWithAuth(`/recommendations/saved/products/${savedId}/`, {
      method: 'DELETE',
    });
    return { ok: response.ok };
  },

  // Saved Remedies
  async getSavedRemedies() {
    const response = await fetchWithAuth('/recommendations/saved/remedies/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async saveRemedy(remedyId, notes = '') {
    const response = await fetchWithAuth('/recommendations/saved/remedies/', {
      method: 'POST',
      body: JSON.stringify({ remedy_id: remedyId, notes }),
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async removeSavedRemedy(savedId) {
    const response = await fetchWithAuth(`/recommendations/saved/remedies/${savedId}/`, {
      method: 'DELETE',
    });
    return { ok: response.ok };
  }
};

// ============================================
// ROUTINES API
// ============================================

export const routinesAPI = {
  async getRoutines() {
    const response = await fetchWithAuth('/recommendations/routines/');
    const data = await response.json();
    return { ok: response.ok, data: normalizeListResponse(data) };
  },

  async getTodayStatus() {
    const response = await fetchWithAuth('/recommendations/routines/today/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async generateRoutinePlan(payload) {
    const response = await fetchWithAuth('/recommendations/routines/generate/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async createRoutine(routineData) {
    const response = await fetchWithAuth('/recommendations/routines/', {
      method: 'POST',
      body: JSON.stringify(routineData),
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async updateRoutine(routineId, routineData) {
    const response = await fetchWithAuth(`/recommendations/routines/${routineId}/`, {
      method: 'PUT',
      body: JSON.stringify(routineData),
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async deleteRoutine(routineId) {
    const response = await fetchWithAuth(`/recommendations/routines/${routineId}/`, {
      method: 'DELETE',
    });
    return { ok: response.ok };
  },

  async logRoutineCompletion(routineId, routineType, completedSteps = [], notes = '') {
    const response = await fetchWithAuth('/recommendations/routines/logs/', {
      method: 'POST',
      body: JSON.stringify({
        routine: routineId,
        routine_type: routineType,
        completed_steps: completedSteps,
        notes
      }),
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getRoutineLogs(routineId = null) {
    const endpoint = routineId 
      ? `/recommendations/routines/logs/?routine_id=${routineId}`
      : '/recommendations/routines/logs/';
    const response = await fetchWithAuth(endpoint);
    const data = await response.json();
    return { ok: response.ok, data };
  }
};

// ============================================
// HISTORY API
// ============================================

export const historyAPI = {
  async getScanHistory() {
    const response = await fetchWithAuth('/history/scans/');
    const data = await response.json();
    return { ok: response.ok, data: normalizeListResponse(data) };
  },

  async getQuestionHistory() {
    const response = await fetchWithAuth('/history/questions/');
    const data = await response.json();
    return { ok: response.ok, data: normalizeListResponse(data) };
  },

  async getProgressSummary() {
    const response = await fetchWithAuth('/history/progress/');
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getProgressPhotos() {
    const response = await fetchWithAuth('/history/progress/photos/');
    const data = await response.json();
    return { ok: response.ok, data: normalizeListResponse(data) };
  },

  async addProgressPhoto(imageFile, notes = '') {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('notes', notes);

    const response = await fetchWithAuth('/history/progress/photos/', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    return { ok: response.ok, data };
  },

  async getMilestones() {
    const response = await fetchWithAuth('/history/milestones/');
    const data = await response.json();
    return { ok: response.ok, data: normalizeListResponse(data) };
  },

  async getActivityTimeline(limit = 20) {
    const response = await fetchWithAuth(`/history/timeline/?limit=${limit}`);
    const data = await response.json();
    return { ok: response.ok, data };
  }
};

// ============================================
// EXPORT ALL
// ============================================

export default {
  auth: authAPI,
  scan: scanAPI,
  question: questionAPI,
  products: productsAPI,
  saved: savedAPI,
  routines: routinesAPI,
  history: historyAPI,
};
