"""Community category API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.community.application.commands import (
    CreateCategoryCommand,
    DeleteCategoryCommand,
    UpdateCategoryCommand,
)
from src.community.application.handlers import (
    CreateCategoryHandler,
    DeleteCategoryHandler,
    ListCategoriesHandler,
    UpdateCategoryHandler,
)
from src.community.application.queries import ListCategoriesQuery
from src.community.domain.exceptions import (
    CannotManageCategoriesError,
    CategoryHasPostsError,
    CategoryNameExistsError,
    CategoryNotFoundError,
    CommunityDomainError,
)
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    SessionDep,
    get_create_category_handler,
    get_delete_category_handler,
    get_list_categories_handler,
    get_update_category_handler,
)
from src.community.interface.api.schemas import (
    CategoryResponse,
    CreateCategoryRequest,
    CreateCategoryResponse,
    ErrorResponse,
    MessageResponse,
    UpdateCategoryRequest,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/community",
    tags=["Community - Categories"],
)


async def _get_default_community_id(session: SessionDep) -> UUID:
    """Get the default community ID."""
    result = await session.execute(
        select(CommunityModel.id).order_by(CommunityModel.created_at).limit(1)
    )
    community_id = result.scalar_one_or_none()
    if community_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No community found",
        )
    return community_id


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    session: SessionDep,
    handler: Annotated[ListCategoriesHandler, Depends(get_list_categories_handler)],
) -> list[CategoryResponse]:
    """
    List all categories for the default community.

    Returns a list of all available categories that can be used
    when creating posts.
    """
    result = await session.execute(
        select(CommunityModel.id).order_by(CommunityModel.created_at).limit(1)
    )
    community_id = result.scalar_one_or_none()

    if not community_id:
        return []

    query = ListCategoriesQuery(community_id=community_id)
    categories = await handler.handle(query)

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


@router.post(
    "/categories",
    response_model=CreateCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized"},
        409: {"model": ErrorResponse, "description": "Category name exists"},
    },
)
async def create_category(
    body: CreateCategoryRequest,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[CreateCategoryHandler, Depends(get_create_category_handler)],
) -> CreateCategoryResponse:
    """Create a new category (admin only)."""
    try:
        community_id = await _get_default_community_id(session)
        command = CreateCategoryCommand(
            community_id=community_id,
            creator_id=current_user_id,
            name=body.name,
            slug=body.slug,
            emoji=body.emoji,
            description=body.description,
        )
        category = await handler.handle(command)
        await session.commit()
        logger.info("create_category_api_success", category_id=str(category.id))
        return CreateCategoryResponse(id=category.id.value)
    except CannotManageCategoriesError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except CategoryNameExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except CommunityDomainError as e:
        logger.error("create_category_domain_error", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch(
    "/categories/{category_id}",
    response_model=MessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized"},
        404: {"model": ErrorResponse, "description": "Category not found"},
        409: {"model": ErrorResponse, "description": "Category name exists"},
    },
)
async def update_category(
    category_id: UUID,
    body: UpdateCategoryRequest,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UpdateCategoryHandler, Depends(get_update_category_handler)],
) -> MessageResponse:
    """Update a category (admin only)."""
    try:
        community_id = await _get_default_community_id(session)
        command = UpdateCategoryCommand(
            category_id=category_id,
            updater_id=current_user_id,
            community_id=community_id,
            name=body.name,
            emoji=body.emoji,
            description=body.description,
        )
        await handler.handle(command)
        await session.commit()
        logger.info("update_category_api_success", category_id=str(category_id))
        return MessageResponse(message="Category updated successfully")
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except CannotManageCategoriesError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except CategoryNameExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except CommunityDomainError as e:
        logger.error("update_category_domain_error", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"model": ErrorResponse, "description": "Category has posts"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized"},
        404: {"model": ErrorResponse, "description": "Category not found"},
    },
)
async def delete_category(
    category_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[DeleteCategoryHandler, Depends(get_delete_category_handler)],
) -> None:
    """Delete a category (admin only)."""
    try:
        community_id = await _get_default_community_id(session)
        command = DeleteCategoryCommand(
            category_id=category_id,
            deleter_id=current_user_id,
            community_id=community_id,
        )
        await handler.handle(command)
        await session.commit()
        logger.info("delete_category_api_success", category_id=str(category_id))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except CannotManageCategoriesError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except CategoryHasPostsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except CommunityDomainError as e:
        logger.error("delete_category_domain_error", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
