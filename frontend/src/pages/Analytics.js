import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { BarChart3, Eye, Users, Globe, Calendar, ExternalLink } from 'lucide-react';
import { urlService } from '../services/api';

const Analytics = () => {
  const { urlId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [urlInfo, setUrlInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsData, urlData] = await Promise.all([
          urlService.getAnalytics(urlId),
          urlService.getUrlInfo(urlData?.short_code || '')
        ]);
        setAnalytics(analyticsData);
        setUrlInfo(urlData);
      } catch (error) {
        toast.error('Failed to load analytics data');
      } finally {
        setIsLoading(false);
      }
    };

    if (urlId) {
      fetchData();
    }
  }, [urlId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!analytics || !urlInfo) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Analytics Not Found</h2>
        <p className="text-gray-600">The requested analytics data could not be found.</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
        <div className="flex items-center space-x-2 text-gray-600">
          <ExternalLink className="h-4 w-4" />
          <a 
            href={urlInfo.original_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="hover:text-primary-600 truncate"
          >
            {urlInfo.original_url}
          </a>
        </div>
        <div className="text-sm text-gray-500 mt-1">
          Short URL: {urlInfo.short_url}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Eye className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Clicks</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_clicks}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Users className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Unique Clicks</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.unique_clicks}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics.total_clicks > 0 
                  ? Math.round((analytics.unique_clicks / analytics.total_clicks) * 100)
                  : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Clicks by Day */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            Clicks by Day (Last 30 Days)
          </h3>
          {analytics.clicks_by_day && analytics.clicks_by_day.length > 0 ? (
            <div className="space-y-2">
              {analytics.clicks_by_day.slice(0, 10).map((day, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {new Date(day.date).toLocaleDateString()}
                  </span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full"
                        style={{
                          width: `${(day.count / Math.max(...analytics.clicks_by_day.map(d => d.count))) * 100}%`
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-8 text-right">
                      {day.count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No click data available</p>
          )}
        </div>

        {/* Clicks by Country */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Globe className="h-5 w-5 mr-2" />
            Clicks by Country
          </h3>
          {analytics.clicks_by_country && analytics.clicks_by_country.length > 0 ? (
            <div className="space-y-2">
              {analytics.clicks_by_country.slice(0, 10).map((country, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {country.country || 'Unknown'}
                  </span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full"
                        style={{
                          width: `${(country.count / Math.max(...analytics.clicks_by_country.map(c => c.count))) * 100}%`
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-8 text-right">
                      {country.count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No country data available</p>
          )}
        </div>
      </div>

      {/* Recent Clicks */}
      {analytics.recent_clicks && analytics.recent_clicks.length > 0 && (
        <div className="card mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Clicks</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    IP Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Country
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User Agent
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {analytics.recent_clicks.map((click, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(click.clicked_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {click.ip_address || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {click.country || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {click.user_agent || 'Unknown'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;