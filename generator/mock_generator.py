"""
Mock Generator Module for Expeta 2.0

This module provides mock code generation functionality for testing purposes.
"""
import os
import json
from datetime import datetime

class MockGenerator:
    """Mock code generator for testing"""
    
    def __init__(self, memory_system=None):
        """Initialize the mock generator
        
        Args:
            memory_system: Optional memory system for storing generated code
        """
        self.memory_system = memory_system
        
    def generate_code(self, expectation_id, options=None):
        """Generate mock code based on the expectation ID
        
        Args:
            expectation_id: ID of the expectation to generate code for
            options: Optional generation options
            
        Returns:
            Generated code files
        """
        print(f"DEBUG: Mock generator generating code for expectation ID: {expectation_id}")
        
        if expectation_id == "test-creative-portfolio":
            mock_files = [
                {
                    "path": "app.py",
                    "content": """from flask import Flask, render_template, request, redirect, url_for
import markdown
import os
from datetime import datetime

app = Flask(__name__)

POSTS = [
    {
        'id': 1,
        'title': 'First Portfolio Project',
        'content': 'This is my first portfolio project showcasing my design skills.',
        'date': '2025-04-01',
        'category': 'design'
    },
    {
        'id': 2,
        'title': 'Web Development Tips',
        'content': 'Here are some tips for web development that I have learned.',
        'date': '2025-04-05',
        'category': 'development'
    }
]

@app.route('/')
def home():
    return render_template('index.html', posts=POSTS[:2])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=POSTS)

@app.route('/blog/<int:post_id>')
def post(post_id):
    post = next((p for p in POSTS if p['id'] == post_id), None)
    if post:
        return render_template('post.html', post=post)
    return redirect(url_for('blog'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return render_template('contact_success.html')
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
"""
                },
                {
                    "path": "templates/index.html",
                    "content": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creative Portfolio</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <nav>
            <div class="logo">Creative Portfolio</div>
            <ul>
                <li><a href="/" class="active">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/portfolio">Portfolio</a></li>
                <li><a href="/blog">Blog</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <div class="hero-content">
                <h1>Welcome to My Creative Portfolio</h1>
                <p>Showcasing my design work and sharing insights through my blog</p>
                <a href="/portfolio" class="btn">View Portfolio</a>
            </div>
        </section>
        
        <section class="featured-work">
            <h2>Featured Work</h2>
            <div class="work-grid">
                <div class="work-item">
                    <img src="{{ url_for('static', filename='images/placeholder1.jpg') }}" alt="Project 1">
                    <h3>Project 1</h3>
                    <p>A responsive website design for a local business</p>
                </div>
                <div class="work-item">
                    <img src="{{ url_for('static', filename='images/placeholder2.jpg') }}" alt="Project 2">
                    <h3>Project 2</h3>
                    <p>Brand identity design for a tech startup</p>
                </div>
                <div class="work-item">
                    <img src="{{ url_for('static', filename='images/placeholder3.jpg') }}" alt="Project 3">
                    <h3>Project 3</h3>
                    <p>Mobile app UI/UX design for a fitness application</p>
                </div>
            </div>
        </section>
        
        <section class="recent-posts">
            <h2>Recent Blog Posts</h2>
            <div class="post-grid">
                {% for post in posts %}
                <div class="post-item">
                    <h3>{{ post.title }}</h3>
                    <p class="post-meta">{{ post.date }} | {{ post.category }}</p>
                    <p>{{ post.content[:100] }}...</p>
                    <a href="{{ url_for('post', post_id=post.id) }}" class="read-more">Read More</a>
                </div>
                {% endfor %}
            </div>
        </section>
    </main>
    
    <footer>
        <div class="footer-content">
            <p>&copy; 2025 Creative Portfolio. All rights reserved.</p>
            <div class="social-links">
                <a href="#">Twitter</a>
                <a href="#">LinkedIn</a>
                <a href="#">Instagram</a>
            </div>
        </div>
    </footer>
    
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
"""
                },
                {
                    "path": "static/css/style.css",
                    "content": """/* Base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
}

a {
    text-decoration: none;
    color: #0066cc;
}

/* Header and Navigation */
header {
    background-color: #fff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 5%;
    max-width: 1200px;
    margin: 0 auto;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
}

nav ul {
    display: flex;
    list-style: none;
}

nav ul li {
    margin-left: 2rem;
}

nav ul li a {
    color: #333;
    font-weight: 500;
    transition: color 0.3s;
}

nav ul li a:hover, nav ul li a.active {
    color: #0066cc;
}

/* Hero Section */
.hero {
    background-color: #f5f7fa;
    padding: 5rem 5%;
    text-align: center;
}

.hero-content {
    max-width: 800px;
    margin: 0 auto;
}

.hero h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    color: #666;
}

.btn {
    display: inline-block;
    background-color: #0066cc;
    color: #fff;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    font-weight: 500;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: #0055aa;
}

/* Featured Work Section */
.featured-work, .recent-posts {
    padding: 4rem 5%;
    max-width: 1200px;
    margin: 0 auto;
}

h2 {
    font-size: 2rem;
    margin-bottom: 2rem;
    text-align: center;
}

.work-grid, .post-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
}

.work-item, .post-item {
    background-color: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s;
}

.work-item:hover, .post-item:hover {
    transform: translateY(-5px);
}

.work-item img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.work-item h3, .post-item h3 {
    padding: 1rem 1rem 0.5rem;
    font-size: 1.2rem;
}

.work-item p, .post-item p {
    padding: 0 1rem 1rem;
    color: #666;
}

.post-meta {
    font-size: 0.9rem;
    color: #999;
    padding: 0 1rem;
}

.read-more {
    display: inline-block;
    margin: 0 1rem 1rem;
    font-weight: 500;
}

/* Footer */
footer {
    background-color: #333;
    color: #fff;
    padding: 2rem 5%;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
}

.social-links a {
    color: #fff;
    margin-left: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    nav {
        flex-direction: column;
        padding: 1rem;
    }
    
    nav ul {
        margin-top: 1rem;
    }
    
    nav ul li {
        margin-left: 1rem;
        margin-right: 1rem;
    }
    
    .hero h1 {
        font-size: 2rem;
    }
    
    .footer-content {
        flex-direction: column;
        text-align: center;
    }
    
    .social-links {
        margin-top: 1rem;
    }
    
    .social-links a {
        margin: 0 0.5rem;
    }
}
"""
                },
                {
                    "path": "README.md",
                    "content": """# Creative Portfolio Website

A personal website with portfolio and blog functionality built with Flask.


- Responsive design for mobile and desktop
- Accessible design for all users
- Portfolio showcase for design work
- Blog system with categories and comments
- Contact form for visitor communication


1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`


- `app.py`: Main application file
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and image files
- `tests/`: Test files


- Flask (Python web framework)
- HTML/CSS
- JavaScript
- SQLite (for blog data in production)


MIT License
"""
                },
                {
                    "path": "requirements.txt",
                    "content": """flask==2.0.1
markdown==3.3.4
pytest==6.2.5
"""
                },
                {
                    "path": "tests/test_app.py",
                    "content": """import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to My Creative Portfolio' in response.data

def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200

def test_portfolio_page(client):
    response = client.get('/portfolio')
    assert response.status_code == 200

def test_blog_page(client):
    response = client.get('/blog')
    assert response.status_code == 200
    assert b'Blog Posts' in response.data

def test_contact_page(client):
    response = client.get('/contact')
    assert response.status_code == 200
    assert b'Contact' in response.data

def test_contact_form_submission(client):
    response = client.post('/contact', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'This is a test message'
    })
    assert response.status_code == 200
    assert b'success' in response.data.lower()
"""
                }
            ]
            
            if self.memory_system:
                self.memory_system.store_generated_code(expectation_id, mock_files)
            
            return {"files": mock_files}
        else:
            return {"files": []}
            
    def download_code(self, expectation_id):
        """Generate a mock ZIP file for code download
        
        Args:
            expectation_id: ID of the expectation to download code for
            
        Returns:
            Path to the generated ZIP file
        """
        import tempfile
        import zipfile
        import os
        
        code_files = self.generate_code(expectation_id).get("files", [])
        
        if not code_files:
            return None
            
        temp_dir = tempfile.mkdtemp()
        
        zip_path = os.path.join(temp_dir, f"code_{expectation_id}.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_info in code_files:
                file_path = file_info.get("path")
                content = file_info.get("content", "")
                
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    os.makedirs(os.path.join(temp_dir, dir_path), exist_ok=True)
                
                full_path = os.path.join(temp_dir, file_path)
                with open(full_path, 'w') as f:
                    f.write(content)
                
                zipf.write(full_path, file_path)
        
        return zip_path
