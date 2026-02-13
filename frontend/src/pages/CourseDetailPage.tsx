import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useCourse, useStartCourse } from '@/features/classroom/hooks';
import { CourseContent } from '@/features/classroom/components';
import { deleteCourse, getContinueLesson } from '@/features/classroom/api';
import { useCurrentUser } from '@/features/identity/hooks';

export function CourseDetailPage(): JSX.Element {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { course, isLoading, error } = useCourse(courseId ?? '');
  const { user } = useCurrentUser();
  const { start, data: startData, isPending: isStarting } = useStartCourse(courseId ?? '');

  const deleteMutation = useMutation({
    mutationFn: () => deleteCourse(courseId ?? ''),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['courses'] });
      navigate('/classroom');
    },
  });

  const handleDelete = (): void => {
    if (!window.confirm('Are you sure you want to delete this course?')) return;
    deleteMutation.mutate();
  };

  const handleAction = async (): Promise<void> => {
    const progress = course?.progress;

    if (progress === null || progress === undefined || !progress.started) {
      // Start course
      start();
    } else if (progress.completion_percentage < 100) {
      // Continue course
      try {
        const { lesson_id } = await getContinueLesson(courseId ?? '');
        navigate(`/classroom/courses/${courseId}/lessons/${lesson_id}`);
      } catch {
        // Fallback to first lesson or stay
        return;
      }
    } else {
      // Review course - navigate to first lesson
      const firstModule = course?.modules[0];
      const firstLesson = firstModule?.lessons[0];
      if (firstLesson !== undefined) {
        navigate(`/classroom/courses/${courseId}/lessons/${firstLesson.id}`);
      }
    }
  };

  // Navigate to first lesson after start
  if (startData !== undefined && !isStarting) {
    navigate(`/classroom/courses/${courseId}/lessons/${startData.first_lesson_id}`);
  }

  const getButtonText = (): string => {
    const progress = course?.progress;
    if (progress === null || progress === undefined || !progress.started) {
      return 'Start Course';
    }
    if (progress.completion_percentage < 100) {
      return 'Continue Learning';
    }
    return 'Review Course';
  };

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 w-1/3 rounded bg-gray-200" />
        <div className="h-4 w-2/3 rounded bg-gray-200" />
        <div className="h-64 rounded bg-gray-200" />
      </div>
    );
  }

  if (error !== null || course === undefined) {
    return (
      <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
        Course not found or failed to load.
      </div>
    );
  }

  const isInstructor = user?.id === course.instructor_id;

  return (
    <div data-testid="course-detail">
      {/* Back link */}
      <button
        onClick={() => navigate('/classroom')}
        className="mb-4 flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        data-testid="back-to-courses"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Courses
      </button>

      {/* Course header */}
      <div className="mb-6 rounded-lg bg-white p-6 shadow">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900" data-testid="course-title">{course.title}</h1>
            {course.description !== null && (
              <p className="mt-2 text-gray-600">{course.description}</p>
            )}
            <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
              <span>{course.module_count} modules</span>
              <span>{course.lesson_count} lessons</span>
              {course.estimated_duration !== null && <span>{course.estimated_duration}</span>}
            </div>

            {/* Progress bar */}
            {course.progress?.started === true && (
              <div className="mt-4" data-testid="course-progress-bar">
                <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                  <span>Your Progress</span>
                  <span>{Math.round(course.progress.completion_percentage)}%</span>
                </div>
                <div className="h-2 w-full max-w-md rounded-full bg-gray-200">
                  <div
                    className="h-2 rounded-full bg-green-500 transition-all"
                    style={{ width: `${course.progress.completion_percentage}%` }}
                  />
                </div>
              </div>
            )}

            {/* Action button */}
            <button
              onClick={() => void handleAction()}
              disabled={isStarting}
              className="mt-4 rounded-md bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              data-testid="course-action-button"
            >
              {isStarting ? 'Loading...' : getButtonText()}
            </button>
          </div>

          {isInstructor && (
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              data-testid="delete-course-button"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </button>
          )}
        </div>
      </div>

      {/* Course content (modules + lessons) */}
      <CourseContent course={course} />
    </div>
  );
}
