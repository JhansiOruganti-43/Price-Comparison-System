from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=True)
    results_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category,
            'results_count': self.results_count
        }

class ProductGroup(db.Model):
    __tablename__ = 'product_groups'
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search_history.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    min_price = db.Column(db.Float, default=0.0)
    max_price = db.Column(db.Float, default=0.0)

    deals = db.relationship('ProductDeal', backref='group', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'search_id': self.search_id,
            'name': self.name,
            'image_url': self.image_url,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'deals': [deal.to_dict() for deal in self.deals]
        }

class ProductDeal(db.Model):
    __tablename__ = 'product_deals'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('product_groups.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)
    discount = db.Column(db.Float, default=0.0) # Percentage
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    delivery_fee = db.Column(db.Float, default=0.0)
    delivery_time = db.Column(db.String(100), nullable=True) # e.g. "Tomorrow", "In 3 Days"
    platform = db.Column(db.String(50), nullable=False) # e.g. "Amazon", "Flipkart", etc.
    url = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    sentiment_score = db.Column(db.Float, default=0.0) # From -1.0 to 1.0
    recommendation_score = db.Column(db.Float, default=0.0) # From 0.0 to 100.0
    
    is_best_value = db.Column(db.Boolean, default=False)
    is_cheapest = db.Column(db.Boolean, default=False)
    is_highest_rated = db.Column(db.Boolean, default=False)
    
    ai_summary = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'title': self.title,
            'price': self.price,
            'original_price': self.original_price,
            'discount': self.discount,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'delivery_fee': self.delivery_fee,
            'delivery_time': self.delivery_time,
            'platform': self.platform,
            'url': self.url,
            'image_url': self.image_url,
            'sentiment_score': self.sentiment_score,
            'recommendation_score': self.recommendation_score,
            'is_best_value': self.is_best_value,
            'is_cheapest': self.is_cheapest,
            'is_highest_rated': self.is_highest_rated,
            'ai_summary': self.ai_summary
        }

class SavedDeal(db.Model):
    __tablename__ = 'saved_deals'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    target_price = db.Column(db.Float, nullable=True)
    date_saved = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'platform': self.platform,
            'image_url': self.image_url,
            'url': self.url,
            'target_price': self.target_price,
            'date_saved': self.date_saved.isoformat()
        }
