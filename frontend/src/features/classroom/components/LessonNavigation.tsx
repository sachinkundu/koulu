import { useNavigate } from 'react-router-dom';

interface LessonNavigationProps {
  courseId: string;
  prevLessonId: string | null;
  nextLessonId: string | null;
}

export function LessonNavigation({
  courseId,
  prevLessonId,
  nextLessonId,
}: LessonNavigationProps): JSX.Element {
  const navigate = useNavigate();

  return (
    <div className="mt-8 flex items-center justify-between border-t pt-6">
      <button
        onClick={() => prevLessonId !== null && navigate(`/classroom/courses/${courseId}/lessons/${prevLessonId}`)}
        disabled={prevLessonId === null}
        className="flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
        data-testid="prev-lesson-button"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Previous Lesson
      </button>

      <button
        onClick={() => nextLessonId !== null && navigate(`/classroom/courses/${courseId}/lessons/${nextLessonId}`)}
        disabled={nextLessonId === null}
        className="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        data-testid="next-lesson-button"
      >
        Next Lesson
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
}
