# VeriDocs API Specification
> Contract between Python backend (Saif) and React frontend (frontend dev)

## Base URL
`http://localhost:8000/api/v1` (development)
`https://veridocs-api.onrender.com/api/v1` (production)

## Endpoints

### POST /upload
Upload 1–3 documents. Returns a session_id used in all subsequent calls.

**Request:** `multipart/form-data`
- `files`: list of PDF or DOCX files (max 20MB each)

**Response:**
```json
{
  "session_id": "uuid-string",
  "files": ["contract_a.pdf", "contract_b.pdf"],
  "outlines": {
    "contract_a.pdf": ["1. Introduction", "2. Terms", "3. Payment"],
    "contract_b.pdf": ["Overview", "Scope", "Deliverables"]
  },
  "status": "ready"
}
```

### POST /chat
Ask a question across all uploaded documents.

**Request:**
```json
{ "session_id": "uuid-string", "query": "What are the payment terms?" }
```

**Response:**
```json
{
  "answer": "According to contract_a.pdf, payment is due within 30 days...",
  "citations": [
    {"source": "contract_a.pdf", "page": 4},
    {"source": "contract_b.pdf", "page": 2}
  ],
  "session_id": "uuid-string"
}
```

### POST /compare
Compare all documents in the session.

**Request:**
```json
{ "session_id": "uuid-string" }
```

**Response:**
```json
{
  "agreements": ["Both docs agree on a 30-day notice period"],
  "contradictions": ["Doc A says liability cap is $10k; Doc B says $50k"],
  "unique_to": {
    "contract_a.pdf": ["Includes NDA clause"],
    "contract_b.pdf": ["Includes IP transfer clause"]
  },
  "summary": "These documents are largely aligned but differ on liability..."
}
```

### GET /insights/{session_id}
Get key themes per document.

**Response:**
```json
{
  "themes": {
    "contract_a.pdf": ["Payment terms", "Liability", "Termination", "IP rights", "Governing law"],
    "contract_b.pdf": ["Scope of work", "Deliverables", "Payment schedule", "Amendments", "Dispute resolution"]
  }
}
```

### GET /report/{session_id}
Download a Markdown analysis report.

**Response:** Plain text Markdown file download.

### DELETE /session/{session_id}
Clean up session. Call this when user closes the app.

**Response:**
```json
{ "status": "session deleted", "session_id": "uuid-string" }
```

## Error Codes
- `404` — Session not found or expired (older than 60 minutes)
- `422` — Validation error (bad request body)
- `415` — Unsupported file type
- `413` — File too large
