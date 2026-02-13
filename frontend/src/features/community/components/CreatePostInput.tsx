import { Avatar } from '@/components';
import { useCurrentUser } from '@/features/identity/hooks';

interface CreatePostInputProps {
  onClick: () => void;
}

export function CreatePostInput({ onClick }: CreatePostInputProps): JSX.Element {
  const { user } = useCurrentUser();

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center gap-3">
        <Avatar
          src={user?.profile?.avatar_url}
          alt={user?.profile?.display_name ?? 'You'}
          fallback={user?.profile?.display_name ?? 'You'}
          size="md"
        />
        <button
          onClick={onClick}
          className="flex-1 rounded-full bg-gray-100 px-4 py-2.5 text-left text-sm text-gray-500 transition-colors hover:bg-gray-200"
          data-testid="create-post-input"
        >
          Write something...
        </button>
      </div>
    </div>
  );
}
