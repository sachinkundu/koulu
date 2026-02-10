import { useNavigate } from 'react-router-dom';
import type { Course } from '../types';

interface CourseCardProps {
  course: Course;
}

export function CourseCard({ course }: CourseCardProps): JSX.Element {
  const navigate = useNavigate();

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
    </div>
  );
}
