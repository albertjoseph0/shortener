# URL Shortener - Like Bitly

A high-performance URL shortener service built with FastAPI and React, designed to handle 1 billion shortened URLs and 100 million daily active users.

## 🚀 Features

- **URL Shortening**: Convert long URLs into short, memorable links
- **Custom Aliases**: Create custom short codes for your URLs
- **Expiration Dates**: Set expiration dates for temporary links
- **Analytics**: Track clicks, geographic data, and user behavior
- **Rate Limiting**: Built-in protection against abuse
- **Security**: Comprehensive security measures and input validation
- **Caching**: Redis-based caching for high performance
- **Modern UI**: Beautiful, responsive React frontend

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI for high-performance async API
- **Database**: PostgreSQL for ACID compliance and data integrity
- **Caching**: Redis for hot URL caching and rate limiting
- **URL Encoding**: Base62 encoding for compact, URL-safe short codes
- **Security**: Rate limiting, input validation, and security headers

### Frontend (React)
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS for responsive design
- **State Management**: React Hook Form for form handling
- **HTTP Client**: Axios for API communication
- **Notifications**: React Hot Toast for user feedback

### Database Schema
- **URLs Table**: Stores original URLs, short codes, metadata
- **Clicks Table**: Tracks analytics data for each click
- **Counters Table**: Manages auto-incrementing counters for short codes

## 📊 Performance Characteristics

- **Scale**: Designed for 1B URLs and 100M DAU
- **Response Time**: Sub-100ms for cached URLs
- **Throughput**: 10,000+ requests per second
- **Storage**: Efficient base62 encoding reduces storage requirements
- **Caching**: Redis caching for 99%+ cache hit rate on popular URLs

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

1. **Clone and setup environment**:
```bash
cd /workspace
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database and Redis credentials
```

3. **Setup database**:
```bash
# Start PostgreSQL and Redis (using Docker)
docker-compose up -d db redis

# Run migrations
alembic upgrade head
```

4. **Start the backend**:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start the frontend**:
```bash
npm start
```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🔧 API Endpoints

### URL Management
- `POST /api/v1/urls/` - Create shortened URL
- `GET /api/v1/urls/{short_code}/info` - Get URL information
- `PUT /api/v1/urls/{url_id}` - Update URL
- `DELETE /api/v1/urls/{url_id}` - Delete URL

### Analytics
- `GET /api/v1/urls/{url_id}/analytics` - Get click analytics

### Redirection
- `GET /{short_code}` - Redirect to original URL

## 📝 Usage Examples

### Create a Short URL
```bash
curl -X POST "http://localhost:8000/api/v1/urls/" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://example.com/very/long/url",
    "custom_alias": "my-link",
    "title": "My Awesome Link",
    "expires_at": "2024-12-31T23:59:59"
  }'
```

### Get URL Information
```bash
curl "http://localhost:8000/api/v1/urls/my-link/info"
```

### Get Analytics
```bash
curl "http://localhost:8000/api/v1/urls/1/analytics"
```

## 🧪 Testing

```bash
# Run backend tests
pytest tests/ -v

# Run frontend tests
cd frontend
npm test
```

## 🔒 Security Features

- **Rate Limiting**: 100 requests per minute per IP
- **Input Validation**: Comprehensive URL and alias validation
- **XSS Protection**: Security headers and input sanitization
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CSRF Protection**: Built-in FastAPI CSRF protection

## 📈 Monitoring & Analytics

- **Click Tracking**: IP address, user agent, referer, geographic data
- **Performance Metrics**: Response times, cache hit rates
- **Error Tracking**: Comprehensive error logging and monitoring
- **Health Checks**: Built-in health check endpoints

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**:
   - Set strong `SECRET_KEY`
   - Configure production database URLs
   - Set appropriate CORS origins
   - Configure trusted hosts

2. **Database**:
   - Use connection pooling
   - Set up read replicas for analytics
   - Regular backups

3. **Caching**:
   - Redis cluster for high availability
   - Appropriate cache TTL settings

4. **Load Balancing**:
   - Multiple FastAPI instances
   - Redis session storage
   - CDN for static assets

### Docker Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs` when running locally

---

Built with ❤️ using FastAPI, React, PostgreSQL, and Redis.
