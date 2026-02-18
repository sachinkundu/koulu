import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import type { LeaderboardWidgetResponse } from '../types';
import { LeaderboardSidebarWidget } from './LeaderboardSidebarWidget';

const mockData: LeaderboardWidgetResponse = {
  entries: [
    { rank: 1, user_id: 'u1', display_name: 'Alice', avatar_url: null, level: 3, points: 60 },
    { rank: 2, user_id: 'u2', display_name: 'Bob', avatar_url: null, level: 2, points: 45 },
    { rank: 3, user_id: 'u3', display_name: 'Carol', avatar_url: null, level: 2, points: 30 },
    { rank: 4, user_id: 'u4', display_name: 'Dave', avatar_url: null, level: 1, points: 20 },
    { rank: 5, user_id: 'u5', display_name: 'Eve', avatar_url: null, level: 1, points: 10 },
  ],
  last_updated: '2026-02-18T00:00:00Z',
};

vi.mock('../hooks/useLeaderboardWidget', () => ({
  useLeaderboardWidget: vi.fn(),
}));

const { useLeaderboardWidget } = await import('../hooks/useLeaderboardWidget');
const mockUseLeaderboardWidget = vi.mocked(useLeaderboardWidget);

function renderWidget(): ReturnType<typeof render> {
  return render(
    <MemoryRouter>
      <LeaderboardSidebarWidget />
    </MemoryRouter>,
  );
}

describe('LeaderboardSidebarWidget', () => {
  it('renders header with 30-day label', () => {
    mockUseLeaderboardWidget.mockReturnValue({ data: mockData, isLoading: false, error: null });
    renderWidget();
    expect(screen.getByText('Leaderboard (30-day)')).toBeInTheDocument();
  });

  it('renders exactly 5 entries', () => {
    mockUseLeaderboardWidget.mockReturnValue({ data: mockData, isLoading: false, error: null });
    renderWidget();
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('Carol')).toBeInTheDocument();
    expect(screen.getByText('Dave')).toBeInTheDocument();
    expect(screen.getByText('Eve')).toBeInTheDocument();
  });

  it('shows points with plus prefix', () => {
    mockUseLeaderboardWidget.mockReturnValue({ data: mockData, isLoading: false, error: null });
    renderWidget();
    expect(screen.getByText('+60')).toBeInTheDocument();
    expect(screen.getByText('+10')).toBeInTheDocument();
  });

  it('shows "See all leaderboards" link', () => {
    mockUseLeaderboardWidget.mockReturnValue({ data: mockData, isLoading: false, error: null });
    renderWidget();
    const link = screen.getByText('See all leaderboards');
    expect(link).toBeInTheDocument();
    expect(link.closest('a')).toHaveAttribute('href', '/leaderboards');
  });

  it('returns null on error (fails silently)', () => {
    mockUseLeaderboardWidget.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('fail'),
    });
    const { container } = renderWidget();
    expect(container.innerHTML).toBe('');
  });

  it('shows loading skeleton', () => {
    mockUseLeaderboardWidget.mockReturnValue({ data: undefined, isLoading: true, error: null });
    const { container } = renderWidget();
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBe(5);
  });
});
