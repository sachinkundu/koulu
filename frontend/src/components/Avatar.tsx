import { LevelBadge } from '@/features/gamification/components/LevelBadge';

interface AvatarProps {
  src: string | null | undefined;
  alt: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  fallback: string;
  level?: number;
}

const sizeClasses = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
};

export function Avatar({ src, alt, size = 'md', fallback, level }: AvatarProps): JSX.Element {
  const altText = level != null ? `${alt}, Level ${level}` : alt;

  const avatarElement = src != null && src !== '' ? (
    <img
      src={src}
      alt={altText}
      className={`${sizeClasses[size]} rounded-full object-cover`}
    />
  ) : (
    <div
      className={`${sizeClasses[size]} flex items-center justify-center rounded-full bg-primary-100 text-primary-700 font-medium`}
    >
      {fallback[0]?.toUpperCase() ?? 'U'}
    </div>
  );

  if (level == null) {
    return avatarElement;
  }

  return (
    <div className="relative inline-block">
      {avatarElement}
      <div className="absolute -bottom-0.5 -right-0.5">
        <LevelBadge level={level} size={size} />
      </div>
    </div>
  );
}
