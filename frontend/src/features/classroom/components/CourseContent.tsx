import { useState } from 'react';
import type { CourseDetail, Module } from '../types';

interface CourseContentProps {
  course: CourseDetail;
}

function LessonItem({ lesson }: { lesson: { id: string; title: string; content_type: string; content?: string } }): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div data-testid={`lesson-${lesson.id}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center gap-3 rounded-md px-4 py-3 text-left hover:bg-gray-50"
      >
        <svg className="h-5 w-5 flex-shrink-0 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {lesson.content_type === 'video' ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          )}
        </svg>
        <span className="text-sm text-gray-700">{lesson.title}</span>
        <span className="ml-auto text-xs text-gray-400">{lesson.content_type}</span>
        <svg
          className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && lesson.content !== undefined && (
        <div className="px-12 pb-3 text-sm text-gray-600 whitespace-pre-wrap" data-testid={`lesson-content-${lesson.id}`}>
          {lesson.content}
        </div>
      )}
    </div>
  );
}

function ModuleSection({ module }: { module: Module }): JSX.Element {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="border rounded-lg" data-testid={`module-${module.id}`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between rounded-t-lg bg-gray-50 px-6 py-4"
      >
        <div>
          <h3 className="text-base font-semibold text-gray-900">{module.title}</h3>
          {module.description !== null && (
            <p className="mt-1 text-sm text-gray-500">{module.description}</p>
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
              <LessonItem key={lesson.id} lesson={lesson} />
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
          <ModuleSection key={module.id} module={module} />
        ))
      )}
    </div>
  );
}
