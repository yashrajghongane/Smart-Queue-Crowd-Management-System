const USE_MOCKS = false;

const MOCK_DATA = {
  departments: {
    departments: [
      { id: "dep_g", name: "General Medicine", code: "G", room: "2" },
      { id: "dep_d", name: "Dental", code: "D", room: "4" },
      { id: "dep_e", name: "Eye", code: "E", room: "5" }
    ]
  },
  registrationSuccess: {
    visit_id: "visit-demo-001",
    token_id: "token-demo-001",
    status_access_id: "status-demo-random-id",
    display_token: "G125",
    department: "General Medicine",
    room: "2",
    status: "WAITING",
    status_url: "/status.html?id=status-demo-random-id"
  }
};

async function apiFetch(endpoint, options = {}) {
  if (USE_MOCKS) {
    console.log(`[MOCK API] ${options.method || 'GET'} ${endpoint}`);
    await new Promise(r => setTimeout(r, 500)); // Simulate delay

    if (endpoint === '/api/departments') return MOCK_DATA.departments;
    if (endpoint === '/api/register') {
        if (options.body && JSON.parse(options.body).name === "Duplicate") {
             throw new Error(JSON.stringify({ error: "ACTIVE_VISIT_EXISTS", message: "Patient already has an active visit for this department.", ...MOCK_DATA.registrationSuccess }));
        }
        return MOCK_DATA.registrationSuccess;
    }

    throw new Error(`Mock endpoint not found: ${endpoint}`);
  }

  // Real fetch implementation
  const response = await fetch(endpoint, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(JSON.stringify(errorBody) || 'Network error');
  }

  return response.json();
}
