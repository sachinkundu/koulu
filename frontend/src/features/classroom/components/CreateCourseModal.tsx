import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { cn } from '@/lib/utils';
import { createCourse } from '../api';

const createCourseSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be 200 characters or less'),
  description: z.string().max(2000, 'Description must be 2000 characters or less').optional().or(z.literal('')),
});

type CreateCourseFormData = z.infer<typeof createCourseSchema>;

interface CreateCourseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (courseId: string) => void;
}

export function CreateCourseModal({ isOpen, onClose, onSuccess }: CreateCourseModalProps): JSX.Element | null {
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: CreateCourseFormData) =>
      createCourse({
        title: data.title,
        description: data.description !== '' ? data.description : null,
      }),
    onSuccess: (result) => {
      void queryClient.invalidateQueries({ queryKey: ['courses'] });
      onSuccess(result.id);
      onClose();
    },
    onError: () => {
      setError('Failed to create course. Please try again.');
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateCourseFormData>({
    resolver: zodResolver(createCourseSchema),
    defaultValues: { title: '', description: '' },
  });

  useEffect(() => {
    if (isOpen) {
      reset({ title: '', description: '' });
      setError(null);
    }
  }, [isOpen, reset]);

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

  const onSubmit = (data: CreateCourseFormData): void => {
    setError(null);
    mutation.mutate(data);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="create-course-modal">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className="relative z-10 w-full max-w-lg rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">Create Course</h2>
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

        <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="p-6 space-y-4">
          {error !== null && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">{error}</div>
          )}

          <div>
            <label htmlFor="course-title" className="block text-sm font-medium text-gray-700">Title</label>
            <input
              id="course-title"
              type="text"
              {...register('title')}
              className={cn(
                'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                errors.title !== undefined ? 'border-red-500' : 'border-gray-300'
              )}
              disabled={mutation.isPending}
              data-testid="course-title-input"
            />
            {errors.title !== undefined && <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>}
          </div>

          <div>
            <label htmlFor="course-description" className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              id="course-description"
              {...register('description')}
              rows={3}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={mutation.isPending}
              data-testid="course-description-input"
            />
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
              data-testid="create-course-submit"
            >
              {mutation.isPending ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
