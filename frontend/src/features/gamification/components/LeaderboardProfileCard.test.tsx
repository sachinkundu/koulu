import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LeaderboardProfileCard } from './LeaderboardProfileCard';

describe('LeaderboardProfileCard', () => {
  it('renders avatar, name, and level label', () => {
    render(
      <LeaderboardProfileCard
        avatarUrl={null}
        displayName="Alice Admin"
        level={3}
        levelName="Rising Star"
        pointsToNextLevel={50}
        isMaxLevel={false}
      />,
    );
    expect(screen.getByText('Alice Admin')).toBeInTheDocument();
    expect(screen.getByText('Level 3 - Rising Star')).toBeInTheDocument();
  });

  it('shows points to level up when not max level', () => {
    render(
      <LeaderboardProfileCard
        avatarUrl={null}
        displayName="Alice"
        level={3}
        levelName="Star"
        pointsToNextLevel={50}
        isMaxLevel={false}
      />,
    );
    expect(screen.getByText('50 points to level up')).toBeInTheDocument();
  });

  it('hides points to level up when max level', () => {
    render(
      <LeaderboardProfileCard
        avatarUrl={null}
        displayName="Alice"
        level={9}
        levelName="Legend"
        pointsToNextLevel={null}
        isMaxLevel={true}
      />,
    );
    expect(screen.queryByText(/points to level up/)).not.toBeInTheDocument();
  });
});
