import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ProfileLevelSection } from './ProfileLevelSection';

describe('ProfileLevelSection', () => {
  it('renders level name and points', () => {
    render(
      <ProfileLevelSection
        level={3}
        levelName="Builder"
        totalPoints={450}
        pointsToNextLevel={50}
        isMaxLevel={false}
      />,
    );

    expect(screen.getByTestId('profile-level-name')).toHaveTextContent('Level 3 - Builder');
    expect(screen.getByTestId('profile-level-points')).toHaveTextContent('450 points');
  });

  it('shows progress when not max level', () => {
    render(
      <ProfileLevelSection
        level={5}
        levelName="Contributor"
        totalPoints={1200}
        pointsToNextLevel={300}
        isMaxLevel={false}
      />,
    );

    expect(screen.getByTestId('profile-level-progress')).toHaveTextContent(
      '300 points to level up',
    );
  });

  it('shows "Max Level" when is_max_level', () => {
    render(
      <ProfileLevelSection
        level={9}
        levelName="Legend"
        totalPoints={50000}
        pointsToNextLevel={null}
        isMaxLevel={true}
      />,
    );

    expect(screen.getByTestId('profile-level-progress')).toHaveTextContent('Max Level');
  });

  it('hides progress when pointsToNextLevel is null and not max level', () => {
    render(
      <ProfileLevelSection
        level={2}
        levelName="Member"
        totalPoints={100}
        pointsToNextLevel={null}
        isMaxLevel={false}
      />,
    );

    expect(screen.queryByTestId('profile-level-progress')).not.toBeInTheDocument();
  });

  it('renders the profile-level-section test id', () => {
    render(
      <ProfileLevelSection
        level={1}
        levelName="Newcomer"
        totalPoints={0}
        pointsToNextLevel={100}
        isMaxLevel={false}
      />,
    );

    expect(screen.getByTestId('profile-level-section')).toBeInTheDocument();
  });
});
