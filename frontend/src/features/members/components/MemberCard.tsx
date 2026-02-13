import { useNavigate } from 'react-router-dom';
import { Avatar } from '@/components/Avatar';
import type { DirectoryMember } from '../types';

function relativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'today';
  if (diffDays === 1) return '1 day ago';
  if (diffDays < 30) return `${diffDays} days ago`;
  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths === 1) return '1 month ago';
  if (diffMonths < 12) return `${diffMonths} months ago`;
  const diffYears = Math.floor(diffDays / 365);
  if (diffYears === 1) return '1 year ago';
  return `${diffYears} years ago`;
}

const ROLE_BADGE: Record<string, { label: string; className: string } | null> = {
  admin: { label: 'Admin', className: 'bg-yellow-100 text-yellow-800' },
  moderator: { label: 'Moderator', className: 'bg-blue-100 text-blue-800' },
  member: null,
};

interface MemberCardProps {
  member: DirectoryMember;
}

export function MemberCard({ member }: MemberCardProps): JSX.Element {
  const navigate = useNavigate();
  const displayName = member.display_name ?? 'Unknown';
  const badge = ROLE_BADGE[member.role];

  return (
    <button
      type="button"
      data-testid="member-card"
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
          {badge != null && (
            <span className={`inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${badge.className}`}>
              {badge.label}
            </span>
          )}
        </div>
        <p className="mt-0.5 line-clamp-2 text-sm text-gray-500">
          {member.bio ?? 'No bio'}
        </p>
        <p className="mt-1 text-xs text-gray-400">
          Joined {relativeDate(member.joined_at)}
        </p>
      </div>
    </button>
  );
}
