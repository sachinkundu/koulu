"""Classroom domain value objects."""

from src.classroom.domain.value_objects.course_description import CourseDescription
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.course_title import CourseTitle
from src.classroom.domain.value_objects.cover_image_url import CoverImageUrl
from src.classroom.domain.value_objects.estimated_duration import EstimatedDuration

__all__ = [
    "CourseDescription",
    "CourseId",
    "CourseTitle",
    "CoverImageUrl",
    "EstimatedDuration",
]
