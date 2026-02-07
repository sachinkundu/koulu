"""Classroom domain value objects."""

from src.classroom.domain.value_objects.content_type import ContentType
from src.classroom.domain.value_objects.course_description import CourseDescription
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.course_title import CourseTitle
from src.classroom.domain.value_objects.cover_image_url import CoverImageUrl
from src.classroom.domain.value_objects.estimated_duration import EstimatedDuration
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.classroom.domain.value_objects.lesson_title import LessonTitle
from src.classroom.domain.value_objects.module_description import ModuleDescription
from src.classroom.domain.value_objects.module_id import ModuleId
from src.classroom.domain.value_objects.module_title import ModuleTitle
from src.classroom.domain.value_objects.text_content import TextContent
from src.classroom.domain.value_objects.video_url import VideoUrl

__all__ = [
    "ContentType",
    "CourseDescription",
    "CourseId",
    "CourseTitle",
    "CoverImageUrl",
    "EstimatedDuration",
    "LessonId",
    "LessonTitle",
    "ModuleDescription",
    "ModuleId",
    "ModuleTitle",
    "TextContent",
    "VideoUrl",
]
