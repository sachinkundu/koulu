interface AvatarProps {
  src: string | null | undefined;
  alt: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  fallback: string;
}

const sizeClasses = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
};

export function Avatar({ src, alt, size = 'md', fallback }: AvatarProps): JSX.Element {
  if (src != null && src !== '') {
    return (
      <img
        src={src}
        alt={alt}
        className={`${sizeClasses[size]} rounded-full object-cover`}
      />
    );
  }

  // Fallback to first letter
  const initial = fallback[0]?.toUpperCase() ?? 'U';

  return (
    <div
      className={`${sizeClasses[size]} flex items-center justify-center rounded-full bg-primary-100 text-primary-700 font-medium`}
    >
      {initial}
    </div>
  );
}
