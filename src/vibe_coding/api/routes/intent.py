"""
Intent parsing routes
"""

from fastapi import APIRouter, HTTPException, status

from vibe_coding.models.schema import APIResponse, ParsedIntent
from pydantic import BaseModel

router = APIRouter()


class IntentParseRequest(BaseModel):
    """Request for intent parsing"""

    input: str
    project_id: str


@router.post("/intent/parse", response_model=APIResponse)
async def parse_intent(request: IntentParseRequest):
    """
    Parse natural language into structured intent

    Args:
        request: Parse request with input text and project ID

    Returns:
        Parsed intent and updated schema
    """
    # TODO: Implement actual intent parsing
    # For now, return a mock response

    input_lower = request.input.lower()

    # Simple intent detection
    if "create" in input_lower or "add" in input_lower:
        intent_type = "create_entity"
    elif "update" in input_lower or "modify" in input_lower:
        intent_type = "update_entity"
    elif "delete" in input_lower or "remove" in input_lower:
        intent_type = "delete_entity"
    elif "permission" in input_lower:
        intent_type = "set_permission"
    else:
        intent_type = "create_entity"

    return APIResponse(
        success=True,
        data={
            "intent": ParsedIntent(
                type=intent_type,
                confidence=0.8,
                entities={"input": request.input},
                operations=[],
            ),
            "message": "Intent parsing not fully implemented",
        },
    )
