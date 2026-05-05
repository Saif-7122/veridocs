/**
 * VeriDocs API Client
 * Centralized module for all backend communication.
 * Base URL points to the FastAPI server via Vite's proxy.
 */

const API_BASE = "/api/v1";

/**
 * Upload files to the backend. Returns session metadata.
 * @param {File[]} files - Array of File objects from the file input
 */
export async function uploadFiles(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Upload failed (${res.status}): ${errText}`);
  }

  return res.json();
}

/**
 * Send a chat query against the session's indexed documents.
 * @param {string} sessionId
 * @param {string} query
 */
export async function chatQuery(sessionId, query) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, query }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Chat failed (${res.status}): ${errText}`);
  }

  return res.json();
}

/**
 * Get key themes per document for this session.
 * @param {string} sessionId
 */
export async function getInsights(sessionId) {
  const res = await fetch(`${API_BASE}/insights/${sessionId}`);

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Insights failed (${res.status}): ${errText}`);
  }

  return res.json();
}

/**
 * Compare all documents in the session.
 * @param {string} sessionId
 */
export async function compareDocs(sessionId) {
  const res = await fetch(`${API_BASE}/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Compare failed (${res.status}): ${errText}`);
  }

  return res.json();
}

/**
 * Download the session report as Markdown text.
 * @param {string} sessionId
 */
export async function getReport(sessionId) {
  const res = await fetch(`${API_BASE}/report/${sessionId}`);

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Report failed (${res.status}): ${errText}`);
  }

  return res.text();
}

/**
 * Delete the session and clean up server-side resources.
 * @param {string} sessionId
 */
export async function deleteSession(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Delete failed (${res.status}): ${errText}`);
  }

  return res.json();
}
