"""Community category API endpoints."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import select

from src.community.application.handlers import ListCategoriesHandler
from src.community.application.queries import ListCategoriesQuery
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import SessionDep, get_list_categories_handler
from src.community.interface.api.schemas import CategoryResponse

logger = structlog.get_logger()

router = APIRouter(
    prefix="/community",
    tags=["Community - Categories"],
)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    session: SessionDep,
    handler: Annotated[ListCategoriesHandler, Depends(get_list_categories_handler)],
) -> list[CategoryResponse]:
    """
    List all categories for the default community.

    Returns a list of all available categories that can be used when creating posts.
    """
    # Get the first available community (same logic as feed endpoint)
    result = await session.execute(
        select(CommunityModel.id).order_by(CommunityModel.created_at).limit(1)
    )
    community_id = result.scalar_one_or_none()

    if not community_id:
        return []

    query = ListCategoriesQuery(community_id=community_id)
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
