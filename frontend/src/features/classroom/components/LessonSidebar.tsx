import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProgressBar } from './ProgressBar';
import type { CourseDetail } from '../types';

interface LessonSidebarProps {
  course: CourseDetail;
  activeLessonId: string;
}

export function LessonSidebar({ course, activeLessonId }: LessonSidebarProps): JSX.Element {
  const navigate = useNavigate();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const progress = course.progress;

  return (
    <>
      {/* Mobile toggle button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="fixed bottom-4 right-4 z-50 rounded-full bg-blue-600 p-3 text-white shadow-lg md:hidden"
        aria-label="Toggle sidebar"
      >
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 w-72 transform border-r bg-white transition-transform md:relative md:translate-x-0 ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        data-testid="lesson-sidebar"
      >
        <div className="flex h-full flex-col">
          {/* Course header */}
          <div className="border-b p-4">
            <button
              onClick={() => navigate(`/classroom/courses/${course.id}`)}
              className="mb-2 text-left hover:text-blue-600"
            >
              <h2 className="text-lg font-semibold text-gray-900">{course.title}</h2>
            </button>
            {progress?.started === true && (
              <ProgressBar
                percentage={progress.completion_percentage}
                size="sm"
                showLabel={false}
              />
            )}
          </div>

          {/* Module and lesson list */}
          <div className="flex-1 overflow-y-auto">
            {course.modules.map((module) => (
              <div key={module.id} className="border-b">
                <div className="bg-gray-50 px-4 py-3">
                  <h3 className="text-sm font-medium text-gray-900">{module.title}</h3>
                  {module.completion_percentage !== null && module.completion_percentage !== undefined && (
                    <div className="mt-2">
                      <ProgressBar
                        percentage={module.completion_percentage}
                        size="sm"
                        showLabel={false}
                      />
                    </div>
                  )}
                </div>
                <div>
                  {module.lessons.map((lesson) => {
                    const isActive = lesson.id === activeLessonId;
                    return (
                      <button
                        key={lesson.id}
                        onClick={() => navigate(`/classroom/courses/${course.id}/lessons/${lesson.id}`)}
                        className={`flex w-full items-center gap-3 px-4 py-3 text-left transition-colors ${
                          isActive
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-700 hover:bg-gray-50'
                        }`}
                        data-testid={`sidebar-lesson-${lesson.id}`}
                      >
                        {/* Completion icon */}
                        <div
                          className="h-4 w-4 flex-shrink-0 rounded-full border-2 flex items-center justify-center"
                          style={{
                            borderColor: lesson.is_complete === true ? '#10b981' : '#d1d5db',
                            backgroundColor: lesson.is_complete === true ? '#10b981' : 'transparent',
                          }}
                        >
                          {lesson.is_complete === true && (
                            <svg className="h-2.5 w-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>

                        <span className="flex-1 text-sm">{lesson.title}</span>

                        {/* Active indicator */}
                        {isActive && (
                          <div className="h-2 w-2 rounded-full bg-blue-600" />
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen(false)}
          className="fixed inset-0 z-30 bg-black bg-opacity-50 md:hidden"
        />
      )}
    </>
  );
}
