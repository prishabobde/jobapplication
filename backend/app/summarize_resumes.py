import json
import re
from typing import Any

from openai import AsyncOpenAI


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1, flags=re.IGNORECASE)
        if "```" in text:
            text = text.rsplit("```", 1)[0]
    return text.strip()


def _parse_summaries_json(raw: str) -> dict[str, Any]:
    cleaned = _strip_code_fence(raw)
    return json.loads(cleaned)


async def summarize_top_applicants(
    *,
    api_key: str,
    model: str,
    job_title: str,
    job_description: str,
    blocks: list[tuple[int, str, str]],
) -> dict[str, Any]:
    """
    blocks: (application_id, username, resume_text)
    Returns {"summaries": [...], "top_pick": {...} | None}
    """
    if not blocks:
        return {"summaries": [], "top_pick": None}

    valid_ids = {b[0] for b in blocks}
    sections = []
    for app_id, username, text in blocks:
        sections.append(
            f"### application_id: {app_id}\n### username: {username}\n{text}\n"
        )
    bundle = "\n---\n".join(sections)
    job_ctx = f"Job title: {job_title}\n\nJob description:\n{job_description[:4000]}"

    system = (
        "You assist HR recruiters. You are given one open role and up to five applicant resume excerpts.\n"
        "1) For each applicant, write a concise neutral summary: 3–5 bullet points (skills, experience level, "
        "strengths, gaps/risks).\n"
        "2) Choose exactly ONE applicant who is the best fit for THIS specific job title and description. "
        "Base the choice only on the resumes and the job context. If none are suitable, still pick the "
        "relatively strongest match and say so briefly.\n"
        "Respond with JSON only (no markdown fences). Shape:\n"
        '{"summaries": [{"application_id": <int>, "username": "<string>", "summary": "<string>"}], '
        '"top_pick": {"application_id": <int>, "username": "<string>", "reason": "<string>"}}\n'
        "Include every applicant exactly once in summaries. top_pick.application_id must match one of the "
        "provided application_id values."
    )

    client = AsyncOpenAI(api_key=api_key)
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"{job_ctx}\n\n---\n\nApplicants:\n\n{bundle}"},
        ],
        temperature=0.25,
    )
    content = completion.choices[0].message.content or "{}"
    data = _parse_summaries_json(content)
    summaries = data.get("summaries")
    if not isinstance(summaries, list):
        raise ValueError("OpenAI response missing summaries array")

    out: list[dict[str, Any]] = []
    for item in summaries:
        if not isinstance(item, dict):
            continue
        try:
            aid = int(item["application_id"])
            uname = str(item["username"])
            summ = str(item["summary"])
        except (KeyError, TypeError, ValueError):
            continue
        out.append({"application_id": aid, "username": uname, "summary": summ})

    top_pick: dict[str, Any] | None = None
    raw_tp = data.get("top_pick")
    if isinstance(raw_tp, dict):
        try:
            tid = int(raw_tp["application_id"])
            if tid in valid_ids:
                top_pick = {
                    "application_id": tid,
                    "username": str(raw_tp.get("username", "")),
                    "reason": str(raw_tp.get("reason", "")),
                }
        except (KeyError, TypeError, ValueError):
            top_pick = None

    return {"summaries": out, "top_pick": top_pick}
