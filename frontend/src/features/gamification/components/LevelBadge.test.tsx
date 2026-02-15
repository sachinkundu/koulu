import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LevelBadge } from './LevelBadge';

describe('LevelBadge', () => {
  it('renders the level number', () => {
    render(<LevelBadge level={3} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders level 1', () => {
    render(<LevelBadge level={1} />);
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('renders level 9', () => {
    render(<LevelBadge level={9} />);
    expect(screen.getByText('9')).toBeInTheDocument();
  });

  it('applies correct size classes for md', () => {
    const { container } = render(<LevelBadge level={2} size="md" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('h-5');
    expect(badge.className).toContain('w-5');
  });

  it('has aria-hidden for accessibility', () => {
    const { container } = render(<LevelBadge level={2} />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.getAttribute('aria-hidden')).toBe('true');
  });
});
