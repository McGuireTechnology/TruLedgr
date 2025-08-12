"""
HTML templates for API endpoints
"""

def get_api_landing_page() -> str:
    """Beautiful landing page for the TruLedgr API"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TruLedgr API</title>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                width: 100%;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .logo {
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .logo i {
                color: white;
                font-size: 2rem;
            }
            
            h1 {
                color: #2d3748;
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            .subtitle {
                color: #718096;
                font-size: 1.2rem;
                margin-bottom: 30px;
            }
            
            .status-badge {
                display: inline-flex;
                align-items: center;
                background: #48bb78;
                color: white;
                padding: 8px 16px;
                border-radius: 25px;
                font-weight: 600;
                margin-bottom: 30px;
            }
            
            .status-badge i {
                margin-right: 8px;
            }
            
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .feature {
                padding: 20px;
                background: #f7fafc;
                border-radius: 12px;
                border-left: 4px solid #667eea;
                transition: transform 0.2s ease;
            }
            
            .feature:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            
            .feature i {
                color: #667eea;
                font-size: 1.5rem;
                margin-bottom: 10px;
            }
            
            .feature h3 {
                color: #2d3748;
                font-size: 1.1rem;
                margin-bottom: 8px;
            }
            
            .feature p {
                color: #718096;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .actions {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }
            
            .btn {
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-secondary {
                background: #e2e8f0;
                color: #4a5568;
            }
            
            .btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .endpoints {
                background: #1a202c;
                color: #e2e8f0;
                padding: 20px;
                border-radius: 12px;
                font-family: 'Monaco', 'Menlo', monospace;
                margin-bottom: 30px;
            }
            
            .endpoints h3 {
                color: #63b3ed;
                margin-bottom: 15px;
                font-size: 1.1rem;
            }
            
            .endpoint {
                margin-bottom: 10px;
                padding: 8px 0;
                border-bottom: 1px solid #2d3748;
            }
            
            .endpoint:last-child {
                border-bottom: none;
            }
            
            .method {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 700;
                margin-right: 10px;
                min-width: 50px;
                text-align: center;
            }
            
            .get { background: #48bb78; }
            .post { background: #ed8936; }
            
            .path {
                color: #90cdf4;
            }
            
            .footer {
                text-align: center;
                color: #718096;
                font-size: 0.9rem;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
            }
            
            .footer a {
                color: #667eea;
                text-decoration: none;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 30px 20px;
                }
                
                h1 {
                    font-size: 2rem;
                }
                
                .features {
                    grid-template-columns: 1fr;
                }
                
                .actions {
                    flex-direction: column;
                    align-items: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h1>TruLedgr API</h1>
                <p class="subtitle">Powerful backend services for modern applications</p>
                <div class="status-badge">
                    <i class="fas fa-check-circle"></i>
                    API Online & Ready
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <i class="fas fa-shield-alt"></i>
                    <h3>Secure Authentication</h3>
                    <p>JWT-based authentication with biometric support for mobile applications</p>
                </div>
                <div class="feature">
                    <i class="fas fa-mobile-alt"></i>
                    <h3>Mobile Ready</h3>
                    <p>Optimized endpoints for iOS and Android with offline-first capabilities</p>
                </div>
                <div class="feature">
                    <i class="fas fa-rocket"></i>
                    <h3>High Performance</h3>
                    <p>Built with FastAPI for maximum speed and automatic API documentation</p>
                </div>
                <div class="feature">
                    <i class="fas fa-cloud"></i>
                    <h3>Cloud Native</h3>
                    <p>Deployed on Digital Ocean App Platform with auto-scaling and monitoring</p>
                </div>
            </div>
            
            <div class="actions">
                <a href="/docs" class="btn btn-primary">
                    <i class="fas fa-book"></i>
                    API Documentation
                </a>
                <a href="/health" class="btn btn-secondary">
                    <i class="fas fa-heart"></i>
                    Health Check
                </a>
                <a href="https://dash.truledgr.app" class="btn btn-secondary">
                    <i class="fas fa-external-link-alt"></i>
                    Dashboard
                </a>
            </div>
            
            <div class="endpoints">
                <h3><i class="fas fa-code"></i> Quick API Reference</h3>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/health</span> - System health status
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/auth/register</span> - User registration
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/auth/login</span> - User authentication
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/users/me</span> - Current user profile
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/mobile/config</span> - Mobile app configuration
                </div>
            </div>
            
            <div class="try-api" style="background: #f0fff4; padding: 20px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #9ae6b4;">
                <h3 style="color: #22543d; margin-bottom: 15px;"><i class="fas fa-play-circle"></i> Try the API</h3>
                <p style="color: #2f855a; margin-bottom: 15px;">Test endpoints directly from your browser:</p>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <a href="/health" target="_blank" style="background: #48bb78; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9rem;">
                        <i class="fas fa-heartbeat"></i> /health
                    </a>
                    <a href="/mobile/config" target="_blank" style="background: #4299e1; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9rem;">
                        <i class="fas fa-mobile-alt"></i> /mobile/config
                    </a>
                    <a href="/status" target="_blank" style="background: #805ad5; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9rem;">
                        <i class="fas fa-code"></i> /status
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>
                    <strong>TruLedgr API v1.0.0</strong> | 
                    Built with <i class="fas fa-heart" style="color: #e53e3e;"></i> using FastAPI | 
                    <a href="/docs">View Full Documentation</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
