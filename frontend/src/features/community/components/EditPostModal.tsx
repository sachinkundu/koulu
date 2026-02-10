import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { cn } from '@/lib/utils';
import { useCategories } from '../hooks';
import { updatePost } from '../api';
import type { Post } from '../types';

const editPostSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be 200 characters or less'),
  content: z.string().min(1, 'Content is required').max(5000, 'Content must be 5000 characters or less'),
  category_id: z.string().min(1, 'Category is required'),
  image_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
});

type EditPostFormData = z.infer<typeof editPostSchema>;

interface EditPostModalProps {
  post: Post;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditPostModal({ post, isOpen, onClose, onSuccess }: EditPostModalProps): JSX.Element | null {
  const [error, setError] = useState<string | null>(null);
  const { categories, isLoading: categoriesLoading } = useCategories();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: EditPostFormData) =>
      updatePost(post.id, {
        title: data.title,
        content: data.content,
        category_id: data.category_id,
        image_url: data.image_url !== '' ? data.image_url : null,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['posts'] });
      void queryClient.invalidateQueries({ queryKey: ['post', post.id] });
      onSuccess();
      onClose();
    },
    onError: () => {
      setError('Failed to update post. Please try again.');
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    reset,
  } = useForm<EditPostFormData>({
    resolver: zodResolver(editPostSchema),
    defaultValues: {
      title: post.title,
      content: post.content,
      category_id: post.category_id,
      image_url: post.image_url ?? '',
    },
  });

  const titleValue = watch('title');
  const contentValue = watch('content');

  useEffect(() => {
    if (isOpen) {
      reset({
        title: post.title,
        content: post.content,
        category_id: post.category_id,
        image_url: post.image_url ?? '',
      });
    }
  }, [isOpen, post, reset]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const onSubmit = (data: EditPostFormData): void => {
    setError(null);
    mutation.mutate(data);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="edit-post-modal">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className="relative z-10 w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">Edit Post</h2>
          <button
            onClick={onClose}
            disabled={mutation.isPending}
            className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-50"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="p-6 space-y-6">
          {error !== null && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">{error}</div>
          )}

          <div>
            <label htmlFor="edit-title" className="block text-sm font-medium text-gray-700">Title</label>
            <input
              id="edit-title"
              type="text"
              {...register('title')}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.title !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              disabled={mutation.isPending}
              data-testid="edit-post-title-input"
            />
            <div className="mt-1 flex items-center justify-between">
              {errors.title !== undefined && <p className="text-sm text-red-600">{errors.title.message}</p>}
              <p className={cn('text-sm ml-auto', titleValue.length > 200 ? 'text-red-600' : 'text-gray-500')}>
                {titleValue.length}/200
              </p>
            </div>
          </div>

          <div>
            <label htmlFor="edit-category" className="block text-sm font-medium text-gray-700">Category</label>
            <select
              id="edit-category"
              {...register('category_id')}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.category_id !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              disabled={mutation.isPending || categoriesLoading}
              data-testid="edit-post-category-select"
            >
              <option value="">Select a category</option>
              {categories?.map((category) => (
                <option key={category.id} value={category.id}>{category.emoji} {category.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="edit-content" className="block text-sm font-medium text-gray-700">Content</label>
            <textarea
              id="edit-content"
              {...register('content')}
              rows={10}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.content !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              disabled={mutation.isPending}
              data-testid="edit-post-content-input"
            />
            <div className="mt-1 flex items-center justify-between">
              {errors.content !== undefined && <p className="text-sm text-red-600">{errors.content.message}</p>}
              <p className={cn('text-sm ml-auto', contentValue.length > 5000 ? 'text-red-600' : 'text-gray-500')}>
                {contentValue.length}/5000
              </p>
            </div>
          </div>

          <div className="flex gap-3 justify-end border-t pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={mutation.isPending}
              className="rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              data-testid="edit-post-submit-button"
            >
              {mutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
