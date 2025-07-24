from functools import wraps
from flask import request, jsonify, g
import time
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Any

from src.config import config
from src.utils.logger import get_logger

logger = get_logger("middleware")

# Rate limiting storage (in production, use Redis)
rate_limit_storage = defaultdict(lambda: deque())
failed_attempts = defaultdict(int)


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth for health checks in development
        if config.DEBUG and request.endpoint == 'health_check':
            return f(*args, **kwargs)
        
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            logger.warning(f"Missing API key from {request.remote_addr}")
            return jsonify({'error': 'API key required'}), 401
        
        # Simple API key validation (in production, use proper key management)
        expected_key = config.get_metadata('API_KEY', 'dev-key-12345')
        if api_key != expected_key:
            logger.warning(f"Invalid API key from {request.remote_addr}: {api_key[:8]}...")
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.authenticated = True
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit(max_requests: int = 100, window_minutes: int = 1):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = get_client_id()
            current_time = datetime.now()
            window_start = current_time - timedelta(minutes=window_minutes)
            
            # Get client's request history
            requests = rate_limit_storage[client_id]
            
            # Remove old requests outside the window
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # Check rate limit
            if len(requests) >= max_requests:
                logger.warning(f"Rate limit exceeded for {client_id}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': window_minutes * 60
                }), 429
            
            # Add current request
            requests.append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def log_requests(app):
    """Request/response logging middleware"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = generate_request_id()
        
        logger.info(
            f"[{g.request_id}] {request.method} {request.path} "
            f"from {request.remote_addr} "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
        )
        
        # Log request data for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            logger.debug(f"[{g.request_id}] Request data: {request.get_json()}")
    
    @app.after_request
    def after_request(response):
        duration = time.time() - getattr(g, 'start_time', time.time())
        request_id = getattr(g, 'request_id', 'unknown')
        
        logger.info(
            f"[{request_id}] Response: {response.status_code} "
            f"Duration: {duration:.3f}s "
            f"Size: {response.content_length or 0} bytes"
        )
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        return response


def error_handler(app):
    """Global error handling middleware"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request: {error}")
        return jsonify({
            'error': 'Bad request',
            'message': 'Invalid request data'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized access: {error}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden access: {error}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"Not found: {request.path}")
        return jsonify({
            'error': 'Not found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        client_id = get_client_id()
        logger.warning(f"Rate limit exceeded for {client_id}")
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong'
        }), 500


def security_headers(app):
    """Add security headers to responses"""
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        if not config.DEBUG:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


def cors_handler(app):
    """Custom CORS handling"""
    
    @app.after_request
    def after_request(response):
        # Allow specific origins in production
        if config.DEBUG:
            response.headers.add('Access-Control-Allow-Origin', '*')
        else:
            # In production, specify allowed origins
            allowed_origins = config.get_metadata('CORS_ORIGINS', ['http://localhost:3000'])
            origin = request.headers.get('Origin')
            if origin in allowed_origins:
                response.headers.add('Access-Control-Allow-Origin', origin)
        
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-API-Key')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response


def validate_json(f):
    """Decorator to validate JSON requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            try:
                request.get_json(force=True)
            except Exception as e:
                logger.warning(f"Invalid JSON in request: {e}")
                return jsonify({'error': 'Invalid JSON format'}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_client_id() -> str:
    """Generate a client identifier for rate limiting"""
    # Use IP + User-Agent for identification
    ip = request.remote_addr or 'unknown'
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    # Hash for privacy
    client_string = f"{ip}:{user_agent}"
    return hashlib.md5(client_string.encode()).hexdigest()[:16]


def generate_request_id() -> str:
    """Generate unique request ID"""
    import uuid
    return str(uuid.uuid4())[:8]


def setup_middleware(app):
    """Setup all middleware for the Flask app"""
    logger.info("Setting up middleware...")
    
    # Order matters - setup in correct sequence
    log_requests(app)
    security_headers(app)
    cors_handler(app)
    error_handler(app)
    
    logger.info("Middleware setup complete")


# Context processor for templates (if using)
def inject_globals(app):
    """Inject global variables into templates"""
    
    @app.context_processor
    def inject_app_info():
        return {
            'app_name': config.APP_NAME,
            'app_version': config.APP_VERSION,
            'debug': config.DEBUG,
            'current_time': datetime.now()
        }