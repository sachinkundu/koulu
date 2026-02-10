import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCourses } from '@/features/classroom/hooks';
import { CourseCard, CreateCourseModal } from '@/features/classroom/components';

export function ClassroomPage(): JSX.Element {
  const { courses, isLoading, error } = useCourses();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div data-testid="classroom-page">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Courses</h2>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          data-testid="create-course-button"
        >
          Create Course
        </button>
      </div>

      {isLoading ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 animate-pulse rounded-lg bg-white shadow" />
          ))}
        </div>
      ) : error !== null ? (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
          Failed to load courses.
        </div>
      ) : courses === undefined || courses.length === 0 ? (
        <div className="rounded-lg bg-white p-12 text-center shadow">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h3 className="mt-2 text-lg font-medium text-gray-900">No courses yet</h3>
          <p className="mt-1 text-sm text-gray-500">Create your first course to get started.</p>
          <button
            onClick={() => setIsCreateOpen(true)}
            className="mt-4 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            Create Course
          </button>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3" data-testid="courses-grid">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}

      <CreateCourseModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSuccess={(courseId) => navigate(`/classroom/courses/${courseId}`)}
      />
    </div>
  );
}
