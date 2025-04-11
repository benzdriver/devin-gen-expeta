def get_mock_requirement_result(requirement):
    """Get mock result for requirement processing"""
    return {
        "requirement": requirement,
        "expectation": {
            "name": "Data Processing System",
            "description": "A system that processes data according to specific rules",
            "components": [
                {"name": "Input Validation", "description": "Validates input data format"},
                {"name": "Data Transformation", "description": "Transforms data according to rules"},
                {"name": "Output Formatting", "description": "Formats output data for consumption"}
            ],
            "constraints": [
                {"name": "Performance", "description": "Must process 1000 records per second"},
                {"name": "Security", "description": "Must encrypt sensitive data"}
            ]
        },
        "clarification": {
            "questions": [
                {"question": "What format is the input data?", "answer": "JSON"},
                {"question": "What transformations are needed?", "answer": "Aggregation and filtering"}
            ]
        }
    }

def get_mock_expectation_result(expectation):
    """Get mock result for expectation processing"""
    function_name = expectation.get("name", "process_data").lower().replace(" ", "_")
    expectation_id = expectation.get("expectation_id", expectation.get("id", ""))
    
    is_blog_website = False
    if expectation_id and (expectation_id == "test-creative-portfolio" or 
                          "blog" in str(expectation).lower() or 
                          "website" in str(expectation).lower()):
        is_blog_website = True
        print(f"DEBUG: Detected blog website request for expectation ID: {expectation_id}")
    
    if is_blog_website:
        return {
            "expectation": expectation,
            "generation": {
                "generated_code": {
                    "language": "python",
                    "files": [
                        {
                            "path": "app.py",
                            "content": "from flask import Flask, render_template, request, redirect, url_for\nimport json\nimport os\nfrom datetime import datetime\n\napp = Flask(__name__)\n\n# Data storage\nBLOG_DATA_FILE = 'data/blog_posts.json'\nPORTFOLIO_DATA_FILE = 'data/portfolio_items.json'\n\n# Ensure data directory exists\nos.makedirs('data', exist_ok=True)\n\n# Load data functions\ndef load_blog_posts():\n    if os.path.exists(BLOG_DATA_FILE):\n        with open(BLOG_DATA_FILE, 'r') as f:\n            return json.load(f)\n    return []\n\ndef load_portfolio_items():\n    if os.path.exists(PORTFOLIO_DATA_FILE):\n        with open(PORTFOLIO_DATA_FILE, 'r') as f:\n            return json.load(f)\n    return []\n\n# Save data functions\ndef save_blog_posts(posts):\n    with open(BLOG_DATA_FILE, 'w') as f:\n        json.dump(posts, f, indent=2)\n\ndef save_portfolio_items(items):\n    with open(PORTFOLIO_DATA_FILE, 'w') as f:\n        json.dump(items, f, indent=2)\n\n# Initialize with sample data if files don't exist\nif not os.path.exists(BLOG_DATA_FILE):\n    sample_posts = [\n        {\n            \"id\": \"post1\",\n            \"title\": \"Getting Started with Web Design\",\n            \"content\": \"<p>This is a sample blog post about web design.</p>\",\n            \"excerpt\": \"Learn the basics of web design and how to create your first website.\",\n            \"author\": \"Jane Doe\",\n            \"date\": \"2023-01-15\",\n            \"categories\": [\"Design\", \"Web Development\"],\n            \"featured_image\": \"/static/images/blog1.jpg\",\n            \"comments\": []\n        },\n        {\n            \"id\": \"post2\",\n            \"title\": \"Portfolio Photography Tips\",\n            \"content\": \"<p>This is a sample blog post about photography for portfolios.</p>\",\n            \"excerpt\": \"How to take professional photos for your design portfolio.\",\n            \"author\": \"John Smith\",\n            \"date\": \"2023-02-20\",\n            \"categories\": [\"Photography\", \"Portfolio\"],\n            \"featured_image\": \"/static/images/blog2.jpg\",\n            \"comments\": []\n        }\n    ]\n    save_blog_posts(sample_posts)\n\nif not os.path.exists(PORTFOLIO_DATA_FILE):\n    sample_items = [\n        {\n            \"id\": \"item1\",\n            \"title\": \"Website Redesign\",\n            \"description\": \"Complete redesign of an e-commerce website.\",\n            \"image\": \"/static/images/portfolio1.jpg\",\n            \"category\": \"Web Design\",\n            \"date\": \"2023-01-10\"\n        },\n        {\n            \"id\": \"item2\",\n            \"title\": \"Brand Identity\",\n            \"description\": \"Brand identity design for a local coffee shop.\",\n            \"image\": \"/static/images/portfolio2.jpg\",\n            \"category\": \"Branding\",\n            \"date\": \"2023-02-15\"\n        }\n    ]\n    save_portfolio_items(sample_items)\n\n# Routes\n@app.route('/')\ndef home():\n    posts = load_blog_posts()\n    items = load_portfolio_items()\n    return render_template('index.html', recent_posts=posts[:3], featured_items=items[:4])\n\n@app.route('/blog')\ndef blog():\n    posts = load_blog_posts()\n    return render_template('blog.html', posts=posts)\n\n@app.route('/blog/<post_id>')\ndef blog_post(post_id):\n    posts = load_blog_posts()\n    post = next((p for p in posts if p['id'] == post_id), None)\n    if not post:\n        return redirect(url_for('blog'))\n    return render_template('blog_post.html', post=post)\n\n@app.route('/blog/category/<category>')\ndef blog_category(category):\n    posts = load_blog_posts()\n    filtered_posts = [p for p in posts if category in p.get('categories', [])]\n    return render_template('blog.html', posts=filtered_posts, category=category)\n\n@app.route('/portfolio')\ndef portfolio():\n    items = load_portfolio_items()\n    return render_template('portfolio.html', items=items)\n\n@app.route('/portfolio/<item_id>')\ndef portfolio_item(item_id):\n    items = load_portfolio_items()\n    item = next((i for i in items if i['id'] == item_id), None)\n    if not item:\n        return redirect(url_for('portfolio'))\n    return render_template('portfolio_item.html', item=item)\n\n@app.route('/about')\ndef about():\n    return render_template('about.html')\n\n@app.route('/contact')\ndef contact():\n    return render_template('contact.html')\n\n@app.route('/blog/<post_id>/comment', methods=['POST'])\ndef add_comment(post_id):\n    posts = load_blog_posts()\n    post = next((p for p in posts if p['id'] == post_id), None)\n    if not post:\n        return redirect(url_for('blog'))\n    \n    if 'comments' not in post:\n        post['comments'] = []\n    \n    comment = {\n        'name': request.form.get('name'),\n        'email': request.form.get('email'),\n        'content': request.form.get('content'),\n        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')\n    }\n    \n    post['comments'].append(comment)\n    save_blog_posts(posts)\n    \n    return redirect(url_for('blog_post', post_id=post_id))\n\nif __name__ == '__main__':\n    app.run(debug=True)"
                        },
                        {
                            "path": "templates/index.html",
                            "content": "<!DOCTYPE html>\n<html>\n<head>\n    <title>My Personal Website with Blog</title>\n    <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/style.css') }}\">\n</head>\n<body>\n    <header>\n        <nav>\n            <ul>\n                <li><a href=\"{{ url_for('home') }}\" class=\"active\">Home</a></li>\n                <li><a href=\"{{ url_for('about') }}\">About</a></li>\n                <li><a href=\"{{ url_for('portfolio') }}\">Portfolio</a></li>\n                <li><a href=\"{{ url_for('blog') }}\">Blog</a></li>\n                <li><a href=\"{{ url_for('contact') }}\">Contact</a></li>\n            </ul>\n        </nav>\n    </header>\n    \n    <section class=\"hero\">\n        <div class=\"container\">\n            <h1>Welcome to My Creative Space</h1>\n            <p>I'm a designer showcasing my work and thoughts</p>\n        </div>\n    </section>\n    \n    <section class=\"featured-works\">\n        <div class=\"container\">\n            <h2>Featured Works</h2>\n            <div class=\"works-grid\">\n                {% for item in featured_items %}\n                <div class=\"work-item\">\n                    <img src=\"{{ item.image }}\" alt=\"{{ item.title }}\">\n                    <h3>{{ item.title }}</h3>\n                    <p>{{ item.category }}</p>\n                    <a href=\"{{ url_for('portfolio_item', item_id=item.id) }}\">View Details</a>\n                </div>\n                {% endfor %}\n            </div>\n        </div>\n    </section>\n    \n    <section class=\"recent-posts\">\n        <div class=\"container\">\n            <h2>Recent Blog Posts</h2>\n            <div class=\"posts-grid\">\n                {% for post in recent_posts %}\n                <div class=\"post-card\">\n                    <img src=\"{{ post.featured_image }}\" alt=\"{{ post.title }}\">\n                    <h3>{{ post.title }}</h3>\n                    <p>{{ post.excerpt }}</p>\n                    <a href=\"{{ url_for('blog_post', post_id=post.id) }}\">Read More</a>\n                </div>\n                {% endfor %}\n            </div>\n        </div>\n    </section>\n    \n    <footer>\n        <div class=\"container\">\n            <p>&copy; 2023 My Creative Portfolio</p>\n        </div>\n    </footer>\n</body>\n</html>"
                        },
                        {
                            "path": "templates/blog.html",
                            "content": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Blog - My Personal Website</title>\n    <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/style.css') }}\">\n</head>\n<body>\n    <header>\n        <nav>\n            <ul>\n                <li><a href=\"{{ url_for('home') }}\">Home</a></li>\n                <li><a href=\"{{ url_for('about') }}\">About</a></li>\n                <li><a href=\"{{ url_for('portfolio') }}\">Portfolio</a></li>\n                <li><a href=\"{{ url_for('blog') }}\" class=\"active\">Blog</a></li>\n                <li><a href=\"{{ url_for('contact') }}\">Contact</a></li>\n            </ul>\n        </nav>\n    </header>\n    \n    <section class=\"page-header\">\n        <div class=\"container\">\n            <h1>Blog</h1>\n            <p>Thoughts, insights, and updates on design and creativity</p>\n        </div>\n    </section>\n    \n    <section class=\"blog-content\">\n        <div class=\"container\">\n            <div class=\"blog-grid\">\n                {% for post in posts %}\n                <article class=\"blog-post\">\n                    <div class=\"post-image\">\n                        <img src=\"{{ post.featured_image }}\" alt=\"{{ post.title }}\">\n                    </div>\n                    <div class=\"post-content\">\n                        <div class=\"post-meta\">\n                            <span class=\"date\">{{ post.date }}</span>\n                            <span class=\"categories\">\n                                {% for category in post.categories %}\n                                <a href=\"{{ url_for('blog_category', category=category) }}\">{{ category }}</a>\n                                {% if not loop.last %}, {% endif %}\n                                {% endfor %}\n                            </span>\n                        </div>\n                        <h2><a href=\"{{ url_for('blog_post', post_id=post.id) }}\">{{ post.title }}</a></h2>\n                        <p>{{ post.excerpt }}</p>\n                        <a href=\"{{ url_for('blog_post', post_id=post.id) }}\" class=\"read-more\">Read More</a>\n                    </div>\n                </article>\n                {% endfor %}\n            </div>\n        </div>\n    </section>\n    \n    <footer>\n        <div class=\"container\">\n            <p>&copy; 2023 My Creative Portfolio</p>\n        </div>\n    </footer>\n</body>\n</html>"
                        },
                        {
                            "path": "static/css/style.css",
                            "content": "/* Base styles */\n* {\n    margin: 0;\n    padding: 0;\n    box-sizing: border-box;\n}\n\nbody {\n    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;\n    line-height: 1.6;\n    color: #333;\n    background-color: #f9f9f9;\n}\n\n.container {\n    max-width: 1200px;\n    margin: 0 auto;\n    padding: 0 20px;\n}\n\na {\n    text-decoration: none;\n    color: #3498db;\n}\n\nul {\n    list-style: none;\n}\n\nimg {\n    max-width: 100%;\n    height: auto;\n}\n\n/* Header */\nheader {\n    background-color: #fff;\n    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);\n    padding: 20px 0;\n}\n\nnav ul {\n    display: flex;\n    justify-content: center;\n    gap: 30px;\n}\n\nnav a {\n    color: #333;\n    font-weight: 500;\n    padding: 10px;\n    transition: all 0.3s ease;\n}\n\nnav a:hover {\n    color: #3498db;\n}\n\nnav a.active {\n    color: #3498db;\n    border-bottom: 2px solid #3498db;\n}\n\n/* Hero section */\n.hero {\n    text-align: center;\n    padding: 80px 0;\n    background-color: #f0f8ff;\n}\n\n.hero h1 {\n    font-size: 2.5rem;\n    margin-bottom: 20px;\n    color: #333;\n}\n\n.hero p {\n    font-size: 1.2rem;\n    color: #666;\n    max-width: 600px;\n    margin: 0 auto;\n}\n\n/* Featured works */\n.featured-works {\n    padding: 80px 0;\n}\n\n.section-header {\n    text-align: center;\n    margin-bottom: 40px;\n}\n\n.section-header h2 {\n    font-size: 2rem;\n    margin-bottom: 10px;\n}\n\n.works-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));\n    gap: 30px;\n}\n\n.work-item {\n    background-color: #fff;\n    border-radius: 8px;\n    overflow: hidden;\n    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);\n    transition: transform 0.3s ease;\n}\n\n.work-item:hover {\n    transform: translateY(-5px);\n}\n\n.work-item img {\n    width: 100%;\n    height: 200px;\n    object-fit: cover;\n}\n\n.work-info {\n    padding: 20px;\n}\n\n.work-info h3 {\n    margin-bottom: 10px;\n}\n\n.work-info p {\n    color: #666;\n    margin-bottom: 15px;\n}\n\n/* Blog posts */\n.recent-posts {\n    padding: 80px 0;\n    background-color: #f9f9f9;\n}\n\n.posts-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));\n    gap: 30px;\n}\n\n.post-card {\n    background-color: #fff;\n    border-radius: 8px;\n    overflow: hidden;\n    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);\n}\n\n.post-card img {\n    width: 100%;\n    height: 200px;\n    object-fit: cover;\n}\n\n.post-card h3 {\n    padding: 20px 20px 10px;\n}\n\n.post-card p {\n    padding: 0 20px 20px;\n    color: #666;\n}\n\n.read-more {\n    display: inline-block;\n    margin: 0 20px 20px;\n    color: #3498db;\n    font-weight: 500;\n}\n\n/* Blog page */\n.page-header {\n    text-align: center;\n    padding: 60px 0;\n    background-color: #f0f8ff;\n}\n\n.page-header h1 {\n    font-size: 2.5rem;\n    margin-bottom: 10px;\n}\n\n.blog-content {\n    padding: 60px 0;\n}\n\n.blog-grid {\n    display: grid;\n    gap: 40px;\n}\n\n.blog-post {\n    display: grid;\n    grid-template-columns: 1fr 2fr;\n    gap: 30px;\n    background-color: #fff;\n    border-radius: 8px;\n    overflow: hidden;\n    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);\n}\n\n.post-image img {\n    width: 100%;\n    height: 100%;\n    object-fit: cover;\n}\n\n.post-content {\n    padding: 30px;\n}\n\n.post-meta {\n    display: flex;\n    flex-wrap: wrap;\n    gap: 15px;\n    margin-bottom: 15px;\n    font-size: 0.9rem;\n    color: #666;\n}\n\n.post-content h2 {\n    margin-bottom: 15px;\n}\n\n.post-content h2 a {\n    color: #333;\n    transition: color 0.3s ease;\n}\n\n.post-content h2 a:hover {\n    color: #3498db;\n}\n\n.post-content p {\n    margin-bottom: 20px;\n    color: #666;\n}\n\n.read-more {\n    font-weight: 500;\n}\n\n/* Footer */\nfooter {\n    background-color: #333;\n    color: #fff;\n    padding: 40px 0;\n    text-align: center;\n}\n\n/* Responsive */\n@media (max-width: 768px) {\n    .blog-post {\n        grid-template-columns: 1fr;\n    }\n    \n    .post-image img {\n        height: 250px;\n    }\n    \n    .works-grid,\n    .posts-grid {\n        grid-template-columns: 1fr;\n    }\n}"
                        }
                    ]
                }
            },
            "validation": {
                "passed": True,
                "semantic_match": {"match_score": 0.98},
                "test_results": {"pass_rate": 1.0}
            },
            "success": True,
            "clarification": {
                "top_level_expectation": expectation,
                "sub_expectations": [
                    {"name": "Personal Website Implementation"}, 
                    {"name": "Blog Functionality"}, 
                    {"name": "Portfolio Display"}, 
                    {"name": "Responsive Design"}
                ]
            }
        }
    else:
        return {
            "expectation": expectation,
            "generation": {
                "generated_code": {
                    "language": "python",
                    "files": [
                        {
                            "path": f"{function_name}.py",
                            "content": f"def {function_name}(data):\n    \"\"\"Implementation of {function_name} function\"\"\"\n    # Process data according to expectation\n    result = data\n    return result"
                        }
                    ]
                }
            },
            "validation": {
                "passed": True,
                "semantic_match": {"match_score": 0.98},
                "test_results": {"pass_rate": 1.0}
            },
            "success": True,
            "clarification": {
                "top_level_expectation": expectation,
                "sub_expectations": [
                    {"name": "Input Validation"}, 
                    {"name": f"{function_name.title()} Implementation"}, 
                    {"name": "Error Handling"}
                ]
            }
        }
