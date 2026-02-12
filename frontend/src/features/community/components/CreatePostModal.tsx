import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { cn } from '@/lib/utils';
import { useCreatePost, useCategories } from '../hooks';
import type { Post } from '../types';

const createPostSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be 200 characters or less'),
  content: z.string().min(1, 'Content is required').max(5000, 'Content must be 5000 characters or less'),
  category_id: z.string().min(1, 'Category is required'),
  image_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
});

type CreatePostFormData = z.infer<typeof createPostSchema>;

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (post: Post) => void;
}

export function CreatePostModal({ isOpen, onClose, onSuccess }: CreatePostModalProps): JSX.Element | null {
  const [error, setError] = useState<string | null>(null);
  const { categories, isLoading: categoriesLoading } = useCategories();
  const { mutateAsync, isPending } = useCreatePost();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    reset,
  } = useForm<CreatePostFormData>({
    resolver: zodResolver(createPostSchema),
    defaultValues: {
      title: '',
      content: '',
      category_id: '',
      image_url: '',
    },
  });

  const titleValue = watch('title');
  const contentValue = watch('content');

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const onSubmit = async (data: CreatePostFormData): Promise<void> => {
    setError(null);
    try {
      const postData = {
        title: data.title,
        content: data.content,
        category_id: data.category_id,
        image_url: data.image_url !== '' ? data.image_url : null,
      };
      const post = await mutateAsync(postData);
      reset();
      onSuccess(post);
      onClose();
    } catch (err) {
      const apiError = err as { response?: { status?: number; data?: { detail?: string; message?: string } } };
      if (apiError.response?.status === 429) {
        setError(apiError.response.data?.detail ?? 'Rate limit exceeded. Try again later.');
      } else {
        setError(apiError.response?.data?.detail ?? apiError.response?.data?.message ?? 'Failed to create post. Please try again.');
      }
    }
  };

  const handleClose = (): void => {
    if (!isPending) {
      reset();
      setError(null);
      onClose();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="create-post-modal">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-lg bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">Create Post</h2>
          <button
            onClick={handleClose}
            disabled={isPending}
            className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-50"
            data-testid="modal-close-button"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="p-6 space-y-6">
          {error !== null && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
              {error}
            </div>
          )}

          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Title
            </label>
            <input
              id="title"
              type="text"
              {...register('title')}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.title !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="Enter a descriptive title"
              disabled={isPending}
              data-testid="post-title-input"
            />
            <div className="mt-1 flex items-center justify-between">
              {errors.title !== undefined && (
                <p className="text-sm text-red-600">{errors.title.message}</p>
              )}
              <p className={cn(
                'text-sm ml-auto',
                titleValue.length > 200 ? 'text-red-600' : 'text-gray-500'
              )}>
                {titleValue.length}/200
              </p>
            </div>
          </div>

          {/* Category */}
          <div>
            <label htmlFor="category_id" className="block text-sm font-medium text-gray-700">
              Category
            </label>
            <select
              id="category_id"
              {...register('category_id')}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.category_id !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              disabled={isPending || categoriesLoading}
              data-testid="post-category-select"
            >
              <option value="">Select a category</option>
              {categories?.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.emoji} {category.name}
                </option>
              ))}
            </select>
            {errors.category_id !== undefined && (
              <p className="mt-1 text-sm text-red-600">{errors.category_id.message}</p>
            )}
          </div>

          {/* Content */}
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700">
              Content
            </label>
            <textarea
              id="content"
              {...register('content')}
              rows={10}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.content !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="What do you want to share?"
              disabled={isPending}
              data-testid="post-content-input"
            />
            <div className="mt-1 flex items-center justify-between">
              {errors.content !== undefined && (
                <p className="text-sm text-red-600">{errors.content.message}</p>
              )}
              <p className={cn(
                'text-sm ml-auto',
                contentValue.length > 5000 ? 'text-red-600' : 'text-gray-500'
              )}>
                {contentValue.length}/5000
              </p>
            </div>
          </div>

          {/* Image URL (optional) */}
          <div>
            <label htmlFor="image_url" className="block text-sm font-medium text-gray-700">
              Image URL (optional)
            </label>
            <input
              id="image_url"
              type="text"
              {...register('image_url')}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.image_url !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="https://example.com/image.jpg"
              disabled={isPending}
              data-testid="post-image-url-input"
            />
            {errors.image_url !== undefined && (
              <p className="mt-1 text-sm text-red-600">{errors.image_url.message}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end border-t pt-4">
            <button
              type="button"
              onClick={handleClose}
              disabled={isPending}
              className="rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300 disabled:opacity-50"
              data-testid="modal-cancel-button"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              data-testid="modal-submit-button"
            >
              {isPending ? 'Creating...' : 'Create Post'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
