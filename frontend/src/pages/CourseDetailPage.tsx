import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useCourse } from '@/features/classroom/hooks';
import { CourseContent } from '@/features/classroom/components';
import { deleteCourse } from '@/features/classroom/api';
import { useCurrentUser } from '@/features/identity/hooks';

export function CourseDetailPage(): JSX.Element {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { course, isLoading, error } = useCourse(courseId ?? '');
  const { user } = useCurrentUser();

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
          <div>
            <h1 className="text-2xl font-bold text-gray-900" data-testid="course-title">{course.title}</h1>
            {course.description !== null && (
              <p className="mt-2 text-gray-600">{course.description}</p>
            )}
            <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
              <span>{course.module_count} modules</span>
              <span>{course.lesson_count} lessons</span>
              {course.estimated_duration !== null && <span>{course.estimated_duration}</span>}
            </div>
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
