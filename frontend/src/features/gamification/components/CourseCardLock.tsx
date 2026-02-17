interface CourseCardLockProps {
  minimumLevel: number;
  minimumLevelName: string;
  currentLevel: number;
}

export function CourseCardLock({
  minimumLevel,
  minimumLevelName,
  currentLevel,
}: CourseCardLockProps) {
  const isLocked = currentLevel < minimumLevel;

  if (!isLocked) {
    return null;
  }

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/60 rounded-lg" data-testid="course-card-lock">
      <div className="text-center text-white p-4">
        <svg
          className="mx-auto h-8 w-8 mb-2"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
          />
        </svg>
        <p className="text-sm font-medium">Unlock at Level {minimumLevel}</p>
        <p className="text-xs text-gray-300 mt-1">{minimumLevelName}</p>
      </div>
    </div>
  );
}
