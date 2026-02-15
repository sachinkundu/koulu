import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Avatar } from './Avatar';

describe('Avatar with level badge', () => {
  it('renders without badge when level is undefined', () => {
    const { container } = render(
      <Avatar src={null} alt="Test" fallback="T" />
    );
    expect(container.querySelector('[aria-hidden="true"]')).toBeNull();
  });

  it('renders level badge when level is provided', () => {
    render(<Avatar src={null} alt="Test" fallback="T" level={3} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('wraps in relative container when level is provided', () => {
    const { container } = render(
      <Avatar src={null} alt="Test" fallback="T" level={2} />
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('relative');
  });

  it('includes level in alt text when provided', () => {
    render(<Avatar src="test.jpg" alt="John Doe" fallback="J" level={5} />);
    const img = screen.getByAltText('John Doe, Level 5');
    expect(img).toBeInTheDocument();
  });
});
