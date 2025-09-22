import React from 'react';
import { Link } from 'react-router-dom';
import { Link as LinkIcon, BarChart3 } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <LinkIcon className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold text-gray-900">Short.ly</span>
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link 
              to="/" 
              className="text-gray-600 hover:text-primary-600 transition-colors duration-200"
            >
              Home
            </Link>
            <Link 
              to="/analytics" 
              className="flex items-center space-x-1 text-gray-600 hover:text-primary-600 transition-colors duration-200"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Analytics</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;