import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { Copy, ExternalLink, Calendar, Clock } from 'lucide-react';
import { urlService } from '../services/api';

const Home = () => {
  const [shortenedUrl, setShortenedUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      const result = await urlService.createUrl(data);
      setShortenedUrl(result);
      toast.success('URL shortened successfully!');
      reset();
    } catch (error) {
      toast.error(error.message || 'Failed to shorten URL');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy to clipboard');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Shorten Your URLs
        </h1>
        <p className="text-xl text-gray-600">
          Create short, memorable links that are easy to share
        </p>
      </div>

      <div className="card mb-8">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label htmlFor="original_url" className="block text-sm font-medium text-gray-700 mb-2">
              Long URL *
            </label>
            <input
              type="url"
              id="original_url"
              className="input-field"
              placeholder="https://example.com/very/long/url"
              {...register('original_url', {
                required: 'URL is required',
                pattern: {
                  value: /^https?:\/\/.+/,
                  message: 'Please enter a valid URL starting with http:// or https://'
                }
              })}
            />
            {errors.original_url && (
              <p className="mt-1 text-sm text-red-600">{errors.original_url.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="custom_alias" className="block text-sm font-medium text-gray-700 mb-2">
                Custom Alias (optional)
              </label>
              <input
                type="text"
                id="custom_alias"
                className="input-field"
                placeholder="my-custom-link"
                {...register('custom_alias', {
                  minLength: {
                    value: 3,
                    message: 'Custom alias must be at least 3 characters'
                  },
                  pattern: {
                    value: /^[a-zA-Z0-9-_]+$/,
                    message: 'Custom alias can only contain letters, numbers, hyphens, and underscores'
                  }
                })}
              />
              {errors.custom_alias && (
                <p className="mt-1 text-sm text-red-600">{errors.custom_alias.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="expires_at" className="block text-sm font-medium text-gray-700 mb-2">
                Expiration Date (optional)
              </label>
              <input
                type="datetime-local"
                id="expires_at"
                className="input-field"
                {...register('expires_at')}
              />
            </div>
          </div>

          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Title (optional)
            </label>
            <input
              type="text"
              id="title"
              className="input-field"
              placeholder="My awesome link"
              {...register('title')}
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description (optional)
            </label>
            <textarea
              id="description"
              rows={3}
              className="input-field"
              placeholder="Brief description of this link"
              {...register('description')}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Shortening...' : 'Shorten URL'}
          </button>
        </form>
      </div>

      {shortenedUrl && (
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Shortened URL</h2>
          
          <div className="space-y-4">
            <div className="flex items-center space-x-2 p-4 bg-gray-50 rounded-lg">
              <ExternalLink className="h-5 w-5 text-gray-500" />
              <span className="text-sm text-gray-600">Original URL:</span>
              <a 
                href={shortenedUrl.original_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 truncate"
              >
                {shortenedUrl.original_url}
              </a>
            </div>

            <div className="flex items-center space-x-2 p-4 bg-primary-50 rounded-lg">
              <Link className="h-5 w-5 text-primary-600" />
              <span className="text-sm text-gray-600">Short URL:</span>
              <a 
                href={shortenedUrl.short_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                {shortenedUrl.short_url}
              </a>
              <button
                onClick={() => copyToClipboard(shortenedUrl.short_url)}
                className="ml-auto p-1 text-gray-500 hover:text-primary-600"
              >
                <Copy className="h-4 w-4" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-gray-600">Created:</span>
                <span>{new Date(shortenedUrl.created_at).toLocaleDateString()}</span>
              </div>
              
              {shortenedUrl.expires_at && (
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-600">Expires:</span>
                  <span>{new Date(shortenedUrl.expires_at).toLocaleDateString()}</span>
                </div>
              )}
              
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">Clicks:</span>
                <span className="font-medium">{shortenedUrl.click_count}</span>
              </div>
            </div>

            {shortenedUrl.title && (
              <div>
                <span className="text-sm text-gray-600">Title:</span>
                <p className="font-medium">{shortenedUrl.title}</p>
              </div>
            )}

            {shortenedUrl.description && (
              <div>
                <span className="text-sm text-gray-600">Description:</span>
                <p className="text-gray-700">{shortenedUrl.description}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;