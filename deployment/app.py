from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Data storage
BLOG_DATA_FILE = 'data/blog_posts.json'
PORTFOLIO_DATA_FILE = 'data/portfolio_items.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Load data functions
def load_blog_posts():
    if os.path.exists(BLOG_DATA_FILE):
        with open(BLOG_DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def load_portfolio_items():
    if os.path.exists(PORTFOLIO_DATA_FILE):
        with open(PORTFOLIO_DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save data functions
def save_blog_posts(posts):
    with open(BLOG_DATA_FILE, 'w') as f:
        json.dump(posts, f, indent=2)

def save_portfolio_items(items):
    with open(PORTFOLIO_DATA_FILE, 'w') as f:
        json.dump(items, f, indent=2)

# Initialize with sample data if files don't exist
if not os.path.exists(BLOG_DATA_FILE):
    sample_posts = [
        {
            "id": "post1",
            "title": "Getting Started with Web Design",
            "content": "<p>This is a sample blog post about web design.</p>",
            "excerpt": "Learn the basics of web design and how to create your first website.",
            "author": "Jane Doe",
            "date": "2023-01-15",
            "categories": ["Design", "Web Development"],
            "featured_image": "/static/images/blog1.jpg",
            "comments": []
        },
        {
            "id": "post2",
            "title": "Portfolio Photography Tips",
            "content": "<p>This is a sample blog post about photography for portfolios.</p>",
            "excerpt": "How to take professional photos for your design portfolio.",
            "author": "John Smith",
            "date": "2023-02-20",
            "categories": ["Photography", "Portfolio"],
            "featured_image": "/static/images/blog2.jpg",
            "comments": []
        }
    ]
    save_blog_posts(sample_posts)

if not os.path.exists(PORTFOLIO_DATA_FILE):
    sample_items = [
        {
            "id": "item1",
            "title": "Website Redesign",
            "description": "Complete redesign of an e-commerce website.",
            "image": "/static/images/portfolio1.jpg",
            "category": "Web Design",
            "date": "2023-01-10"
        },
        {
            "id": "item2",
            "title": "Brand Identity",
            "description": "Brand identity design for a local coffee shop.",
            "image": "/static/images/portfolio2.jpg",
            "category": "Branding",
            "date": "2023-02-15"
        }
    ]
    save_portfolio_items(sample_items)

# Routes
@app.route('/')
def home():
    posts = load_blog_posts()
    items = load_portfolio_items()
    return render_template('index.html', recent_posts=posts[:3], featured_items=items[:4])

@app.route('/blog')
def blog():
    posts = load_blog_posts()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<post_id>')
def blog_post(post_id):
    posts = load_blog_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return redirect(url_for('blog'))
    return render_template('blog_post.html', post=post)

@app.route('/blog/category/<category>')
def blog_category(category):
    posts = load_blog_posts()
    filtered_posts = [p for p in posts if category in p.get('categories', [])]
    return render_template('blog.html', posts=filtered_posts, category=category)

@app.route('/portfolio')
def portfolio():
    items = load_portfolio_items()
    return render_template('portfolio.html', items=items)

@app.route('/portfolio/<item_id>')
def portfolio_item(item_id):
    items = load_portfolio_items()
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return redirect(url_for('portfolio'))
    return render_template('portfolio_item.html', item=item)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog/<post_id>/comment', methods=['POST'])
def add_comment(post_id):
    posts = load_blog_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return redirect(url_for('blog'))
    
    if 'comments' not in post:
        post['comments'] = []
    
    comment = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'content': request.form.get('content'),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    post['comments'].append(comment)
    save_blog_posts(posts)
    
    return redirect(url_for('blog_post', post_id=post_id))

if __name__ == '__main__':
    app.run(debug=True)