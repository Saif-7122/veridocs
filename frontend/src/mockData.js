export const MOCK_SESSION = ["contract_a.pdf", "research_paper.pdf"];

export const MOCK_CHAT = [
  {
    query: "What is the liability limit?",
    answer: "The liability is capped at $50,000 for any single incident, excluding gross negligence.",
    citations: [{ source: "contract_a.pdf", page: 4 }]
  },
  {
    query: "Does the paper discuss neural networks?",
    answer: "Yes, the entire methodology relies on convolutional neural networks trained on diverse datasets.",
    citations: [{ source: "research_paper.pdf", page: 2 }, { source: "research_paper.pdf", page: 3 }]
  }
];

export const MOCK_COMPARE = {
  agreements: ["Both documents emphasize data protection.", "Both highlight regular reporting requirements."],
  contradictions: ["Contract A states 30-day notice, while the procedural paper assumes 15 days."],
  unique_to: {
    "contract_a.pdf": ["Contains explicit non-compete clauses.", "Includes indemnification structure."],
    "research_paper.pdf": ["Proposes a new architectural framework.", "Provides statistical evidence of 90% accuracy."]
  },
  summary: "While the contract dictates strict boundaries and liabilities, the research paper outlines a methodology spanning broader timelines. They intersect primarily on data integrity."
};

export const MOCK_INSIGHTS = {
  "contract_a.pdf": ["Liability Constraints", "Confidentiality", "Payment Terms", "Termination Rights", "Governing Law"],
  "research_paper.pdf": ["Machine Learning Models", "Data Preprocessing", "Performance Metrics", "Scalability", "Future Work"]
};

export const MOCK_REPORT = `# VeriDocs Session Report

## Context
Analysis of contract_a.pdf and research_paper.pdf across 2 distinct queries.

## Key Themes
### contract_a.pdf
- Liability Constraints
- Confidentiality
- Payment Terms
- Termination Rights
- Governing Law

### research_paper.pdf
- Machine Learning Models
- Data Preprocessing
- Performance Metrics
- Scalability
- Future Work

## Cross-Document Analysis
**Summary:** While the contract dictates strict boundaries and liabilities, the research paper outlines a methodology spanning broader timelines. They intersect primarily on data integrity.

## Session QA History
**Q1: What is the liability limit?**
A: The liability is capped at $50,000 for any single incident, excluding gross negligence.
*Sources: contract_a.pdf (p.4)*

**Q2: Does the paper discuss neural networks?**
A: Yes, the entire methodology relies on convolutional neural networks trained on diverse datasets.
*Sources: research_paper.pdf (p.2), research_paper.pdf (p.3)*
`;
