import { LeaderboardSidebarWidget } from '@/features/gamification/components/LeaderboardSidebarWidget';

/**
 * Right sidebar matching Skool's community info panel.
 * Shows a promo card, community stats, and leaderboard widget.
 */
export function CommunitySidebar(): JSX.Element {
  return (
    <aside className="hidden w-80 shrink-0 space-y-4 lg:block">
      {/* Promo Card */}
      <div className="overflow-hidden rounded-lg bg-gray-800 text-white">
        <div className="flex h-32 items-center justify-center bg-gradient-to-br from-gray-700 to-gray-900 px-6">
          <h3 className="text-center text-2xl font-bold italic leading-tight">
            Launch and{' '}
            <br />
            grow your{' '}
            <br />
            <span className="text-yellow-400">Business</span>
          </h3>
        </div>
        <div className="p-4">
          <h4 className="mb-1 text-base font-bold">Koulu Community</h4>
          <p className="mb-3 text-sm text-gray-300">
            The community platform for builders and entrepreneurs.
          </p>
          <p className="mb-4 text-xs text-gray-400">
            Start today, imagine where you&apos;ll be in 3 months.
          </p>
          <button className="w-full rounded-lg bg-yellow-400 py-2.5 text-sm font-semibold text-gray-900 transition-colors hover:bg-yellow-500">
            JOIN NOW
          </button>
        </div>
      </div>

      {/* Community Stats */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-3 text-base font-bold text-gray-900">Koulu Community</h3>

        <div className="mb-4 flex gap-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">692</p>
            <p className="text-xs text-gray-500">Members</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">4</p>
            <p className="text-xs text-gray-500">Online</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">12</p>
            <p className="text-xs text-gray-500">Admins</p>
          </div>
        </div>

        {/* Member avatars (placeholder) */}
        <div className="mb-4 flex -space-x-2">
          {['A', 'B', 'C', 'D', 'E', 'F'].map((letter) => (
            <div
              key={letter}
              className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-gray-300 text-xs font-medium text-gray-600"
            >
              {letter}
            </div>
          ))}
        </div>

        <button className="w-full rounded-lg bg-gray-900 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-gray-800">
          INVITE PEOPLE
        </button>
      </div>

      {/* Leaderboard Widget */}
      <LeaderboardSidebarWidget />
    </aside>
  );
}
