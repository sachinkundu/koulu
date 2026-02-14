import { useNavigate } from 'react-router-dom';
import { CalendarIcon } from '@heroicons/react/24/outline';
import { Avatar } from '@/components/Avatar';
import type { MemberSearchItem } from '../types';

const ROLE_BADGE: Record<string, { label: string; className: string } | null> = {
  admin: { label: 'Admin', className: 'bg-yellow-100 text-yellow-800' },
  moderator: { label: 'Moderator', className: 'bg-blue-100 text-blue-800' },
  member: null,
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

interface MemberSearchCardProps {
  member: MemberSearchItem;
}

export function MemberSearchCard({ member }: MemberSearchCardProps): JSX.Element {
  const navigate = useNavigate();
  const displayName = member.display_name ?? 'Unknown';
  const badge = ROLE_BADGE[member.role];

  return (
    <button
      type="button"
      data-testid="member-search-card"
      onClick={() => navigate(`/profile/${member.user_id}`)}
      className="flex w-full items-start gap-4 rounded-lg border border-gray-200 bg-white p-4 text-left transition-shadow hover:shadow-sm"
    >
      <Avatar
        src={member.avatar_url}
        alt={displayName}
        size="lg"
        fallback={displayName}
      />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-semibold text-gray-900">
            {displayName}
          </span>
          {member.username != null && (
            <span className="truncate text-sm text-gray-500">
              @{member.username}
            </span>
          )}
          {badge != null && (
            <span
              className={`inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${badge.className}`}
            >
              {badge.label}
            </span>
          )}
        </div>
        <p className="mt-0.5 line-clamp-2 text-sm text-gray-500">
          {member.bio ?? 'No bio'}
        </p>
        <div className="mt-1 flex items-center gap-1 text-xs text-gray-400">
          <CalendarIcon className="h-3.5 w-3.5" />
          <span>Joined {formatDate(member.joined_at)}</span>
        </div>
      </div>
    </button>
  );
}
