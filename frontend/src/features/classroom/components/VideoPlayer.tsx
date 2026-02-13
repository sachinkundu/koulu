interface VideoPlayerProps {
  url: string;
}

export function VideoPlayer({ url }: VideoPlayerProps): JSX.Element {
  // Extract video ID from common providers
  const getEmbedUrl = (videoUrl: string): string | null => {
    try {
      const urlObj = new URL(videoUrl);

      // YouTube
      if (urlObj.hostname.includes('youtube.com') || urlObj.hostname.includes('youtu.be')) {
        let videoId = '';
        if (urlObj.hostname.includes('youtu.be')) {
          videoId = urlObj.pathname.slice(1);
        } else {
          videoId = urlObj.searchParams.get('v') ?? '';
        }
        return videoId !== '' ? `https://www.youtube.com/embed/${videoId}` : null;
      }

      // Vimeo
      if (urlObj.hostname.includes('vimeo.com')) {
        const videoId = urlObj.pathname.split('/').pop();
        return videoId !== undefined && videoId !== '' ? `https://player.vimeo.com/video/${videoId}` : null;
      }

      // Loom
      if (urlObj.hostname.includes('loom.com')) {
        const videoId = urlObj.pathname.split('/').pop();
        return videoId !== undefined && videoId !== '' ? `https://www.loom.com/embed/${videoId}` : null;
      }

      return null;
    } catch {
      return null;
    }
  };

  const embedUrl = getEmbedUrl(url);

  if (embedUrl === null) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg bg-gray-100">
        <div className="text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-500">
            Unable to load video. Supported providers: YouTube, Vimeo, Loom.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
      <iframe
        src={embedUrl}
        className="absolute inset-0 h-full w-full rounded-lg"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        title="Video content"
      />
    </div>
  );
}
