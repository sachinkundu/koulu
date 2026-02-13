import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { CourseDetail, Module, Lesson } from '../types';

interface CourseContentProps {
  course: CourseDetail;
}

function LessonItem({ lesson, courseId }: { lesson: Lesson; courseId: string }): JSX.Element {
  const navigate = useNavigate();

  const handleClick = (): void => {
    navigate(`/classroom/courses/${courseId}/lessons/${lesson.id}`);
  };

  return (
    <button
      onClick={handleClick}
      className="flex w-full items-center gap-3 rounded-md px-4 py-3 text-left hover:bg-gray-50"
      data-testid={`lesson-${lesson.id}`}
    >
      {/* Completion icon */}
      <div
        className="h-5 w-5 flex-shrink-0 rounded-full border-2 flex items-center justify-center"
        data-testid={`lesson-complete-icon-${lesson.id}`}
        style={{
          borderColor: lesson.is_complete === true ? '#10b981' : '#d1d5db',
          backgroundColor: lesson.is_complete === true ? '#10b981' : 'transparent',
        }}
      >
        {lesson.is_complete === true && (
          <svg className="h-3 w-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>

      {/* Content type icon */}
      <svg className="h-5 w-5 flex-shrink-0 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        {lesson.content_type === 'video' ? (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        ) : (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        )}
      </svg>

      <span className="text-sm text-gray-700 flex-1">{lesson.title}</span>
      <span className="text-xs text-gray-400">{lesson.content_type}</span>
    </button>
  );
}

function ModuleSection({ module, courseId }: { module: Module; courseId: string }): JSX.Element {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="border rounded-lg" data-testid={`module-${module.id}`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between rounded-t-lg bg-gray-50 px-6 py-4"
      >
        <div className="flex-1">
          <h3 className="text-base font-semibold text-gray-900">{module.title}</h3>
          {module.description !== null && (
            <p className="mt-1 text-sm text-gray-500">{module.description}</p>
          )}
          {/* Module progress bar */}
          {module.completion_percentage !== null && module.completion_percentage !== undefined && (
            <div className="mt-2" data-testid={`module-progress-${module.id}`}>
              <div className="h-1.5 w-32 rounded-full bg-gray-200">
                <div
                  className="h-1.5 rounded-full bg-green-500 transition-all"
                  style={{ width: `${module.completion_percentage}%` }}
                />
              </div>
            </div>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">{module.lessons.length} lessons</span>
          <svg
            className={`h-5 w-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      {isExpanded && (
        <div className="divide-y">
          {module.lessons.length === 0 ? (
            <p className="px-6 py-4 text-sm text-gray-500">No lessons yet.</p>
          ) : (
            module.lessons.map((lesson) => (
              <LessonItem key={lesson.id} lesson={lesson} courseId={courseId} />
            ))
          )}
        </div>
      )}
    </div>
  );
}

export function CourseContent({ course }: CourseContentProps): JSX.Element {
  return (
    <div className="space-y-4" data-testid="course-content">
      <h2 className="text-lg font-semibold text-gray-900">
        Course Content ({course.module_count} modules, {course.lesson_count} lessons)
      </h2>
      {course.modules.length === 0 ? (
        <p className="text-sm text-gray-500">No modules yet.</p>
      ) : (
        course.modules.map((module) => (
          <ModuleSection key={module.id} module={module} courseId={course.id} />
        ))
      )}
    </div>
  );
}
