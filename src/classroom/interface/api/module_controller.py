"""Classroom module API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.classroom.application.commands import (
    AddModuleCommand,
    DeleteModuleCommand,
    ReorderModulesCommand,
    UpdateModuleCommand,
)
from src.classroom.application.handlers import (
    AddModuleHandler,
    DeleteModuleHandler,
    ReorderModulesHandler,
    UpdateModuleHandler,
)
from src.classroom.domain.exceptions import (
    ClassroomDomainError,
    CourseNotFoundError,
    InvalidPositionError,
    ModuleNotFoundError,
    ModuleTitleRequiredError,
    ModuleTitleTooLongError,
    ModuleTitleTooShortError,
)
from src.classroom.interface.api.dependencies import (
    AdminVerifiedDep,
    get_add_module_handler,
    get_delete_module_handler,
    get_reorder_modules_handler,
    get_update_module_handler,
)
from src.classroom.interface.api.schemas import (
    AddModuleRequest,
    CreateModuleResponse,
    ErrorResponse,
    MessageResponse,
    ReorderRequest,
    UpdateModuleRequest,
)

logger = structlog.get_logger()

router = APIRouter(tags=["Classroom Modules"])


@router.post(
    "/courses/{course_id}/modules",
    response_model=CreateModuleResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course not found"},
    },
)
async def add_module(
    course_id: UUID,
    body: AddModuleRequest,
    current_user_id: AdminVerifiedDep,  # noqa: ARG001
    handler: Annotated[AddModuleHandler, Depends(get_add_module_handler)],
) -> CreateModuleResponse:
    """Add a module to a course."""
    try:
        command = AddModuleCommand(
            course_id=course_id,
            title=body.title,
            description=body.description,
        )
        module_id = await handler.handle(command)

        logger.info("add_module_api_success", module_id=str(module_id))
        return CreateModuleResponse(id=module_id.value)

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (
        ModuleTitleRequiredError,
        ModuleTitleTooShortError,
        ModuleTitleTooLongError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("add_module_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.patch(
    "/modules/{module_id}",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Module not found"},
    },
)
async def update_module(
    module_id: UUID,
    body: UpdateModuleRequest,
    current_user_id: AdminVerifiedDep,  # noqa: ARG001
    handler: Annotated[UpdateModuleHandler, Depends(get_update_module_handler)],
) -> MessageResponse:
    """Update a module."""
    try:
        command = UpdateModuleCommand(
            module_id=module_id,
            title=body.title,
            description=body.description,
        )
        await handler.handle(command)

        logger.info("update_module_api_success", module_id=str(module_id))
        return MessageResponse(message="Module updated successfully")

    except ModuleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (
        ModuleTitleRequiredError,
        ModuleTitleTooShortError,
        ModuleTitleTooLongError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("update_module_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Module not found"},
    },
)
async def delete_module(
    module_id: UUID,
    current_user_id: AdminVerifiedDep,  # noqa: ARG001
    handler: Annotated[DeleteModuleHandler, Depends(get_delete_module_handler)],
) -> None:
    """Soft delete a module."""
    try:
        command = DeleteModuleCommand(module_id=module_id)
        await handler.handle(command)

        logger.info("delete_module_api_success", module_id=str(module_id))

    except ModuleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("delete_module_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put(
    "/courses/{course_id}/modules/reorder",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course not found"},
    },
)
async def reorder_modules(
    course_id: UUID,
    body: ReorderRequest,
    current_user_id: AdminVerifiedDep,  # noqa: ARG001
    handler: Annotated[ReorderModulesHandler, Depends(get_reorder_modules_handler)],
) -> MessageResponse:
    """Reorder modules in a course."""
    try:
        command = ReorderModulesCommand(
            course_id=course_id,
            module_ids=body.ordered_ids,
        )
        await handler.handle(command)

        logger.info("reorder_modules_api_success", course_id=str(course_id))
        return MessageResponse(message="Modules reordered successfully")

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except InvalidPositionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("reorder_modules_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
