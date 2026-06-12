import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, SearchHistory, ProductGroup, ProductDeal, SavedDeal
from scraper import ECommerceScraper
from matcher import ProductMatcher
from recommender import AIRecommender

app = Flask(__name__)
# Enable CORS for frontend requests (typically React dev server runs on localhost:5173)
CORS(app)

# Database path - setup inside backend directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'price_cmp.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize engines
scraper = ECommerceScraper()
matcher = ProductMatcher()
recommender = AIRecommender()

@app.before_request
def create_tables():
    # Automatically create SQLite database files and tables if they don't exist
    db.create_all()

@app.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "Search query cannot be empty"}), 400

    try:
        # Check if we have this search in database history within the last 1 hour
        # This makes subsequent loads instantaneous while preserving database caching
        existing_search = db.session.query(SearchHistory).filter_by(query=query).order_by(SearchHistory.timestamp.desc()).first()
        
        # If it exists, retrieve groups and deals from DB
        # To allow refreshing, the UI could send a force_refresh parameter if needed
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        if existing_search and not force_refresh:
            groups = db.session.query(ProductGroup).filter_by(search_id=existing_search.id).all()
            if groups:
                return jsonify({
                    "search_id": existing_search.id,
                    "query": query,
                    "from_cache": True,
                    "groups": [g.to_dict() for g in groups]
                })

        # Scraping live/simulated deals
        raw_deals = scraper.search_all_platforms(query)
        if not raw_deals:
            return jsonify({"search_id": None, "query": query, "groups": [], "message": "No products found"}), 200

        # Run NLP Matching and Grouping
        grouped_results = matcher.cluster_deals(raw_deals)

        # Create SearchHistory entry
        # Guess category based on query
        query_lower = query.lower()
        if any(x in query_lower for x in ["phone", "iphone", "samsung", "laptop", "watch", "earbuds", "headphones"]):
            category = "Electronics"
        elif any(x in query_lower for x in ["tshirt", "shirt", "jeans", "dress", "kurta", "saree"]):
            category = "Fashion"
        elif any(x in query_lower for x in ["shoes", "sneakers", "boots", "sandals"]):
            category = "Footwear"
        else:
            category = "General"

        new_search = SearchHistory(query=query, category=category, results_count=len(raw_deals))
        db.session.add(new_search)
        db.session.flush() # Populate new_search.id

        processed_groups = []
        for group in grouped_results:
            # Create ProductGroup DB object
            db_group = ProductGroup(
                search_id=new_search.id,
                name=group['name'],
                image_url=group['image_url'],
                min_price=group['min_price'],
                max_price=group['max_price']
            )
            db.session.add(db_group)
            db.session.flush() # Populate db_group.id

            # Evaluate deals inside the group using AI Recommender
            evaluated_deals = recommender.evaluate_group(group['deals'])

            for deal in evaluated_deals:
                db_deal = ProductDeal(
                    group_id=db_group.id,
                    title=deal['title'],
                    price=deal['price'],
                    original_price=deal.get('original_price'),
                    discount=deal['discount'],
                    rating=deal['rating'],
                    reviews_count=deal['reviews_count'],
                    delivery_fee=deal['delivery_fee'],
                    delivery_time=deal['delivery_time'],
                    platform=deal['platform'],
                    url=deal['url'],
                    image_url=deal['image_url'],
                    sentiment_score=deal['sentiment_score'],
                    recommendation_score=deal['recommendation_score'],
                    is_best_value=deal['is_best_value'],
                    is_cheapest=deal['is_cheapest'],
                    is_highest_rated=deal['is_highest_rated'],
                    ai_summary=deal.get('ai_summary')
                )
                db.session.add(db_deal)
            
            processed_groups.append(db_group)
            
        db.session.commit()

        return jsonify({
            "search_id": new_search.id,
            "query": query,
            "from_cache": False,
            "groups": [g.to_dict() for g in processed_groups]
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        history = db.session.query(SearchHistory).order_by(SearchHistory.timestamp.desc()).limit(15).all()
        return jsonify([h.to_dict() for h in history])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/saved', methods=['GET', 'POST'])
def handle_saved_deals():
    if request.method == 'GET':
        try:
            saved = db.session.query(SavedDeal).order_by(SavedDeal.date_saved.desc()).all()
            return jsonify([s.to_dict() for s in saved])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        data = request.json
        if not data or 'title' not in data or 'price' not in data or 'platform' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        try:
            # Check if already saved
            existing = db.session.query(SavedDeal).filter_by(title=data['title'], platform=data['platform']).first()
            if existing:
                return jsonify({"message": "Deal already saved", "deal": existing.to_dict()}), 200
                
            new_save = SavedDeal(
                title=data['title'],
                price=data['price'],
                platform=data['platform'],
                image_url=data.get('image_url'),
                url=data.get('url'),
                target_price=data.get('target_price')
            )
            db.session.add(new_save)
            db.session.commit()
            return jsonify({"message": "Deal saved successfully", "deal": new_save.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route('/api/saved/<int:deal_id>', methods=['DELETE'])
def unsave_deal(deal_id):
    try:
        deal = db.session.query(SavedDeal).get(deal_id)
        if not deal:
            return jsonify({"error": "Saved deal not found"}), 404
            
        db.session.delete(deal)
        db.session.commit()
        return jsonify({"message": "Deal removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        total_searches = db.session.query(SearchHistory).count()
        saved_deals = db.session.query(SavedDeal).all()
        
        # Calculate some fun stats
        deals_count = db.session.query(ProductDeal).count()
        avg_discount = 0.0
        if deals_count > 0:
            avg_discount = db.session.query(db.func.avg(ProductDeal.discount)).scalar() or 0.0
            
        # Estimated money saved
        # Sum of difference between average price and chosen price for all searches where best deal was analyzed
        total_savings = 0.0
        for s in db.session.query(SearchHistory).all():
            for g in db.session.query(ProductGroup).filter_by(search_id=s.id).all():
                prices = [d.price for d in g.deals]
                if prices:
                    avg_p = sum(prices) / len(prices)
                    min_p = min(prices)
                    total_savings += (avg_p - min_p)

        # Recent searches
        recent = [h.query for h in db.session.query(SearchHistory).order_by(SearchHistory.timestamp.desc()).limit(5).all()]
        
        # Category breakdown
        categories = db.session.query(SearchHistory.category, db.func.count(SearchHistory.id)).group_by(SearchHistory.category).all()
        category_stats = {cat: count for cat, count in categories if cat}

        return jsonify({
            "total_searches": total_searches,
            "total_saved_deals": len(saved_deals),
            "average_discount": round(avg_discount, 1),
            "estimated_savings": round(total_savings),
            "recent_searches": recent,
            "categories": category_stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start local Flask server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
