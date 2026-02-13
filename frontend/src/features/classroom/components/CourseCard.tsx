import { useNavigate } from 'react-router-dom';
import { useStartCourse } from '../hooks';
import { getContinueLesson } from '../api';
import type { Course } from '../types';

interface CourseCardProps {
  course: Course;
}

export function CourseCard({ course }: CourseCardProps): JSX.Element {
  const navigate = useNavigate();
  const { start, data: startData, isPending } = useStartCourse(course.id);
  const progress = course.progress;

  const handleAction = async (e: React.MouseEvent): Promise<void> => {
    e.stopPropagation();

    if (progress === null || progress === undefined || !progress.started) {
      // Start course
      start();
    } else if (progress.completion_percentage < 100) {
      // Continue course
      try {
        const { lesson_id } = await getContinueLesson(course.id);
        navigate(`/classroom/courses/${course.id}/lessons/${lesson_id}`);
      } catch {
        // Fallback to course detail
        navigate(`/classroom/courses/${course.id}`);
      }
    } else {
      // Review course (go to first lesson)
      navigate(`/classroom/courses/${course.id}`);
    }
  };

  // Navigate to first lesson after start
  if (startData !== undefined && !isPending) {
    navigate(`/classroom/courses/${course.id}/lessons/${startData.first_lesson_id}`);
  }

  const getButtonText = (): string => {
    if (progress === null || progress === undefined || !progress.started) {
      return 'Start Course';
    }
    if (progress.completion_percentage < 100) {
      return 'Continue';
    }
    return 'Review';
  };

  return (
    <div
      onClick={() => navigate(`/classroom/courses/${course.id}`)}
      className="cursor-pointer rounded-lg bg-white p-6 shadow hover:shadow-md transition-shadow"
      data-testid={`course-card-${course.id}`}
    >
      {course.cover_image_url !== null && (
        <img
          src={course.cover_image_url}
          alt=""
          className="mb-4 h-40 w-full rounded-lg object-cover"
        />
      )}

      <h3 className="text-lg font-semibold text-gray-900">{course.title}</h3>

      {course.description !== null && (
        <p className="mt-2 text-sm text-gray-600 line-clamp-2">{course.description}</p>
      )}

      <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
        <span>{course.module_count} modules</span>
        <span>{course.lesson_count} lessons</span>
        {course.estimated_duration !== null && (
          <span>{course.estimated_duration}</span>
        )}
      </div>

      {/* Progress bar */}
      {progress?.started === true && (
        <div
          className="mt-4"
          data-testid={`course-progress-${course.id}`}
        >
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span>{Math.round(progress.completion_percentage)}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-gray-200">
            <div
              className="h-2 rounded-full bg-green-500 transition-all"
              style={{ width: `${progress.completion_percentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Action button */}
      <button
        onClick={(e) => void handleAction(e)}
        disabled={isPending}
        className="mt-4 w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        data-testid={`course-action-btn-${course.id}`}
      >
        {isPending ? 'Loading...' : getButtonText()}
      </button>
    </div>
  );
}
