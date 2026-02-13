import { VideoPlayer } from './VideoPlayer';
import type { LessonContext } from '../types';

interface LessonContentProps {
  lesson: LessonContext;
}

export function LessonContent({ lesson }: LessonContentProps): JSX.Element {
  if (lesson.content_type === 'video') {
    return (
      <div className="mb-6">
        <VideoPlayer url={lesson.content} />
      </div>
    );
  }

  // Text content
  return (
    <div className="prose max-w-none">
      <div className="whitespace-pre-wrap rounded-lg bg-gray-50 p-6 text-gray-800">
        {lesson.content}
      </div>
    </div>
  );
}
