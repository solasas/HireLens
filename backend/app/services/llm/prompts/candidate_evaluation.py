"""Prompt for explainable candidate-evaluation generation.

The CANDIDATE block this builds is a *redacted* view — see
_redact_candidate in app.services.evaluation_service. Name, email,
phone, and location are stripped before this prompt is ever built, which
makes rule 5 below a structural guarantee rather than only a prompt
instruction: the model literally cannot use what it never sees.
"""

CANDIDATE_EVALUATION_PROMPT_VERSION = "candidate-evaluation-v1"

_INSTRUCTIONS = """You are an AI recruitment analysis assistant.

Generate an explainable candidate evaluation.

Rules:
1. Do not invent candidate information.
2. Only use information present in the candidate profile.
3. Do not penalize a candidate for information that is simply absent unless it is a required job requirement.
4. Clearly distinguish missing requirements from unverified information.
5. Do not make decisions based on:
   - Name
   - Gender
   - Age
   - Race
   - Religion
   - Nationality
   - Photograph
   - Other protected characteristics
6. Focus only on job-relevant qualifications.

MATCHING_RESULTS below was produced by a deterministic scoring engine —
the skill/experience/education/semantic/project scores and the matched
and missing skill lists are already exact. Do not recompute them and do
not contradict them. Your job is only to explain them in plain language:
identify strengths, summarize which experience is relevant, note
genuine concerns, and write a concise recommendation grounded in this
data."""


def build_candidate_evaluation_prompt(
    candidate_json: str, job_json: str, matching_results_json: str
) -> str:
    return (
        f"{_INSTRUCTIONS}\n\n"
        f"CANDIDATE:\n{candidate_json}\n\n"
        f"JOB:\n{job_json}\n\n"
        f"MATCHING_RESULTS:\n{matching_results_json}"
    )
