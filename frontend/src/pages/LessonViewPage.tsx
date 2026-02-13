import { useParams } from 'react-router-dom';
import { useAuth } from '@/features/identity/hooks';
import { useLesson, useCourse, useLessonComplete } from '@/features/classroom/hooks';
import {
  LessonHeader,
  LessonContent,
  LessonNavigation,
  LessonSidebar,
} from '@/features/classroom/components';
import { TabBar, UserDropdown } from '@/components';
import type { User } from '@/features/identity/types';

const APP_TABS = [
  { label: 'Community', path: '/' },
  { label: 'Classroom', path: '/classroom' },
];

function AppHeader({ user, onLogout }: { user: User | null; onLogout: () => void }): JSX.Element {
  const projectName = import.meta.env.VITE_PROJECT_NAME ?? 'koulu';

  return (
    <header className="bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-gray-900">Koulu</h1>
          <span className="rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
            {projectName}
          </span>
        </div>
        {user !== null && (
          <div className="flex items-center space-x-4">
            <UserDropdown user={user} onLogout={onLogout} />
          </div>
        )}
      </div>
    </header>
  );
}

function FullPageSpinner(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
    </div>
  );
}

export function LessonViewPage(): JSX.Element {
  const { courseId, lessonId } = useParams<{ courseId: string; lessonId: string }>();
  const { user, logout, isLoading: authLoading } = useAuth();
  const { lesson, isLoading: lessonLoading, error: lessonError } = useLesson(lessonId ?? '');
  const { course, isLoading: courseLoading, error: courseError } = useCourse(courseId ?? '');
  const {
    markComplete,
    unmarkComplete,
    isMarkPending,
    isUnmarkPending,
  } = useLessonComplete(lessonId ?? '', courseId ?? '');

  const isLoading = authLoading || lessonLoading || courseLoading;
  const error = lessonError ?? courseError;

  if (isLoading) {
    return <FullPageSpinner />;
  }

  if (error !== null || lesson === undefined || course === undefined) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AppHeader user={user} onLogout={() => void logout()} />
        <TabBar tabs={APP_TABS} />
        <div className="mx-auto max-w-4xl px-4 py-8">
          <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
            Lesson not found or failed to load.
          </div>
        </div>
      </div>
    );
  }

  const handleToggleComplete = (): void => {
    if (lesson.is_complete) {
      unmarkComplete();
    } else {
      markComplete();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader user={user} onLogout={() => void logout()} />
      <TabBar tabs={APP_TABS} />

      {/* Two-column layout */}
      <div className="flex">
        {/* Sidebar */}
        <LessonSidebar course={course} activeLessonId={lessonId ?? ''} />

        {/* Main content */}
        <main className="flex-1 px-6 py-8">
          <div className="mx-auto max-w-4xl">
            <LessonHeader
              lesson={lesson}
              isComplete={lesson.is_complete}
              onToggleComplete={handleToggleComplete}
              isPending={isMarkPending || isUnmarkPending}
            />

            <LessonContent lesson={lesson} />

            <LessonNavigation
              courseId={courseId ?? ''}
              prevLessonId={lesson.prev_lesson_id}
              nextLessonId={lesson.next_lesson_id}
            />
          </div>
        </main>
      </div>
    </div>
  );
}
