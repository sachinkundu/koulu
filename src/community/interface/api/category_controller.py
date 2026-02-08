"""Community category API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends

from src.community.application.handlers import ListCategoriesHandler
from src.community.application.queries import ListCategoriesQuery
from src.community.interface.api.dependencies import get_list_categories_handler
from src.community.interface.api.schemas import CategoryResponse

logger = structlog.get_logger()

router = APIRouter(
    prefix="/community",
    tags=["Community - Categories"],
)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    handler: Annotated[ListCategoriesHandler, Depends(get_list_categories_handler)],
) -> list[CategoryResponse]:
    """
    List all categories for the default community.

    Returns a list of all available categories that can be used when creating posts.
    """
    # TODO: Make community_id configurable when multi-community support is added
    # For now, hardcode the default community ID
    default_community_id = UUID("00000000-0000-0000-0000-000000000001")

    query = ListCategoriesQuery(community_id=default_community_id)
    categories = await handler.handle(query)

    # Convert domain entities to response DTOs
    return [
        CategoryResponse(
            id=cat.id.value,
            community_id=cat.community_id.value,
            name=cat.name,
            slug=cat.slug,
            emoji=cat.emoji,
            description=cat.description,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
        )
        for cat in categories
    ]
