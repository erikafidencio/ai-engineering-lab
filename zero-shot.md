# Zero-shot Prompting

## 🎯 Goal

Understand how an LLM behaves when it receives only the task, without examples or additional context.

---

## Scenario

A product manager requests a new feature:

> Implement recurring payments.

The objective is to generate a Jira story.

---

## Prompt

```text
Generate a Jira story for the following feature:

Implement recurring payments.

Include:
- User Story
- Acceptance Criteria
- Technical Tasks
```

---

## Response

> _(Paste the model response here)_

---

## Evaluation

| Criteria | Rating |
|----------|--------|
| Correctness | ⭐⭐⭐⭐☆ |
| Completeness | ⭐⭐⭐☆☆ |
| Structure | ⭐⭐⭐☆☆ |
| Hallucinations | ⭐☆☆☆☆ |

---

## What worked

- Fast response
- Understands the task

---

## What could improve

- Missing business rules
- Acceptance criteria are generic
- No edge cases

---

## Next Experiment

Compare against Few-shot Prompting.
