import { useNavigate } from 'react-router-dom';
import type { LessonContext } from '../types';

interface LessonHeaderProps {
  lesson: LessonContext;
  isComplete: boolean;
  onToggleComplete: () => void;
  isPending: boolean;
}

export function LessonHeader({
  lesson,
  isComplete,
  onToggleComplete,
  isPending,
}: LessonHeaderProps): JSX.Element {
  const navigate = useNavigate();

  return (
    <div className="mb-6 rounded-lg bg-white p-6 shadow" data-testid="lesson-header">
      {/* Breadcrumb */}
      <nav className="mb-4 flex items-center gap-2 text-sm text-gray-500" data-testid="breadcrumb">
        <button
          onClick={() => navigate(`/classroom/courses/${lesson.course_id}`)}
          className="hover:text-gray-700"
        >
          {lesson.course_title}
        </button>
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span>{lesson.module_title}</span>
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span className="text-gray-900">{lesson.title}</span>
      </nav>

      {/* Title and controls */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{lesson.title}</h1>
          <div className="mt-2 flex items-center gap-2">
            {/* Content type badge */}
            <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800">
              {lesson.content_type === 'video' ? (
                <>
                  <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                    />
                  </svg>
                  Video
                </>
              ) : (
                <>
                  <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Text
                </>
              )}
            </span>
          </div>
        </div>

        {/* Complete button */}
        <button
          onClick={onToggleComplete}
          disabled={isPending}
          className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 ${
            isComplete
              ? 'bg-green-600 text-white hover:bg-green-700'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          data-testid="mark-complete-button"
        >
          {isComplete ? (
            <>
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Completed
            </>
          ) : (
            <>
              <div className="h-4 w-4 rounded-full border-2 border-current" />
              Mark as Complete
            </>
          )}
        </button>
      </div>
    </div>
  );
}
