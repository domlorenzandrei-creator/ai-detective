import os

from .models import fmt_time

SYSTEM_PROMPT = (
    "You are a suspect in a murder mystery, being questioned by a detective. "
    "Reply in 1-3 sentences, in character. You MUST keep every name, room and time "
    "exactly as given. Do not add new facts, names, or evidence."
)


def plain_statement(claim, sighting=None, seen_name=None):
    text = f"I was in the {claim.room} at {fmt_time(claim.minute)}. I never left."
    if sighting and seen_name:
        text += f" I saw {seen_name} in the {sighting.room} at {fmt_time(sighting.minute)}."
    return text


def render_statement(suspect, claim, use_ai=True, sighting=None, seen_name=None):
    base = plain_statement(claim, sighting, seen_name)
    if not use_ai or not os.getenv("ANTHROPIC_API_KEY"):
        return base
    try:
        import anthropic

        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"You are {suspect.name}, the {suspect.role}. "
                    f"Say this in your own voice: \"{base}\""
                ),
            }],
        )
        return message.content[0].text.strip()
    except Exception:
        return base