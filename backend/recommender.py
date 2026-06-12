import random
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Fallback keyword-based sentiment analyzer in case NLTK VADER lexicon download fails
class SimpleSentimentAnalyzer:
    def __init__(self):
        self.pos_words = {
            "good", "great", "awesome", "excellent", "love", "amazing", "best", 
            "perfect", "worth", "satisfied", "fast", "easy", "happy", "nice", 
            "premium", "genuine", "original", "superb", "beautiful"
        }
        self.neg_words = {
            "bad", "worst", "poor", "broken", "cheap", "fake", "hate", "useless", 
            "return", "defect", "slow", "disappointed", "damaged", "scam", 
            "waste", "horrible", "stitching", "low-quality"
        }

    def polarity_scores(self, text):
        text_lower = text.lower()
        words = text_lower.split()
        pos_count = sum(1 for w in words if w in self.pos_words)
        neg_count = sum(1 for w in words if w in self.neg_words)
        
        total = pos_count + neg_count
        if total == 0:
            return {"compound": 0.0}
        
        score = (pos_count - neg_count) / total
        return {"compound": score}

# Attempt to download VADER lexicon
try:
    # Set a timeout or catch exception to fail fast if offline
    nltk.download('vader_lexicon', quiet=True)
    analyzer = SentimentIntensityAnalyzer()
    vader_working = True
except Exception:
    analyzer = SimpleSentimentAnalyzer()
    vader_working = False

def get_sentiment_score(reviews):
    """
    Computes an average compound sentiment score for a list of reviews.
    Returns a score between -1.0 and 1.0.
    """
    if not reviews:
        return 0.0
    
    scores = []
    for r in reviews:
        score = analyzer.polarity_scores(r)
        scores.append(score.get('compound', 0.0))
        
    return sum(scores) / len(scores)

def generate_mock_reviews_for_deal(platform, rating):
    """
    Generates realistic, platform-specific mock reviews based on the rating.
    """
    positive_reviews = [
        "Highly recommended! The quality is premium and worth the price.",
        "Fits perfectly and looks exactly like the image.",
        "Super fast delivery and nice packaging. Very happy with the purchase.",
        "Best in this budget. Original product, verified it.",
        "Amazing experience. The details are very neat and clean.",
        "Excellent quality, ordering another one for my family!"
    ]
    
    neutral_reviews = [
        "Product is okay, but delivery was a bit delayed.",
        "Decent quality for the price. Not bad, not great.",
        "It performs well, but the material could be slightly better.",
        "Satisfactory purchase, but packaging was slightly damaged.",
        "Normal product, does the job. Nothing fancy."
    ]
    
    negative_reviews = [
        "Very poor quality. Do not buy this product, total waste of money.",
        "Stitching is coming off and sizes run extremely small.",
        "Item is damaged and looks fake. Initiating return immediately.",
        "Horrible service. Slower delivery and wrong color received.",
        "Not worth the price. Better options are available elsewhere."
    ]

    reviews = []
    
    # Adjust review pool based on rating
    if rating >= 4.4:
        reviews.extend(random.sample(positive_reviews, 3))
        reviews.extend(random.sample(neutral_reviews, 1))
    elif rating >= 3.8:
        reviews.extend(random.sample(positive_reviews, 2))
        reviews.extend(random.sample(neutral_reviews, 2))
    else:
        reviews.extend(random.sample(neutral_reviews, 2))
        reviews.extend(random.sample(negative_reviews, 2))
        
    # Inject platform specifics
    if platform == "Meesho":
        reviews.append("Cheap price, but shipping took a long time.")
    elif platform == "Amazon":
        reviews.append("Delivered in less than 24 hours. Amazon service is amazing!")
    elif platform == "Flipkart":
        reviews.append("Good discount on Flipkart, packing was secure.")
        
    return reviews

class AIRecommender:
    def __init__(self):
        pass

    def evaluate_group(self, group_deals):
        """
        Analyzes a list of deals in a product group, computes recommendation scores,
        and annotates the deals with metrics (is_cheapest, is_highest_rated, is_best_value).
        """
        if not group_deals:
            return []

        # Find min/max values for scaling
        prices = [d['price'] for d in group_deals]
        ratings = [d['rating'] for d in group_deals]
        delivery_fees = [d['delivery_fee'] for d in group_deals]
        
        min_price = min(prices)
        max_price = max(prices)
        
        max_rating = max(ratings)
        max_delivery_fee = max(delivery_fees) if max(delivery_fees) > 0 else 1.0

        for deal in group_deals:
            # 1. Generate sentiment score
            reviews = generate_mock_reviews_for_deal(deal['platform'], deal['rating'])
            deal['sentiment_score'] = get_sentiment_score(reviews)
            
            # 2. Normalize components to [0, 1] range
            # Price Score: lower is better
            if max_price == min_price:
                price_score = 1.0
            else:
                price_score = 1.0 - ((deal['price'] - min_price) / (max_price - min_price))
                
            # Rating Score: higher is better
            rating_score = deal['rating'] / 5.0
            
            # Discount Score: higher is better
            discount_score = deal['discount'] / 100.0
            
            # Delivery Fee Score: lower is better
            delivery_score = 1.0 - (deal['delivery_fee'] / max_delivery_fee)
            
            # Sentiment Score: map [-1, 1] to [0, 1]
            sentiment_score_norm = (deal['sentiment_score'] + 1.0) / 2.0
            
            # 3. Weighted scoring
            # Price: 40%, Rating: 25%, Discount: 15%, Delivery: 10%, Sentiment: 10%
            rec_score = (
                0.40 * price_score +
                0.25 * rating_score +
                0.15 * discount_score +
                0.10 * delivery_score +
                0.10 * sentiment_score_norm
            ) * 100.0 # Convert to percentage scale
            
            deal['recommendation_score'] = round(rec_score, 1)
            
            # Initialize flags
            deal['is_best_value'] = False
            deal['is_cheapest'] = False
            deal['is_highest_rated'] = False

        # Mark Cheapest Deal
        cheapest_deal = min(group_deals, key=lambda x: x['price'])
        cheapest_deal['is_cheapest'] = True

        # Mark Highest Rated Deal
        highest_rated_deal = max(group_deals, key=lambda x: x['rating'])
        highest_rated_deal['is_highest_rated'] = True

        # Mark Best Value (Highest Recommendation Score)
        best_value_deal = max(group_deals, key=lambda x: x['recommendation_score'])
        best_value_deal['is_best_value'] = True
        
        # 4. Generate AI Summaries explaining the recommendations
        for deal in group_deals:
            summary_points = []
            if deal['is_best_value']:
                summary_points.append("🏆 Ranked #1 Best Value Deal by our smart shopping AI.")
                
            # Compare price with average
            avg_price = sum(prices) / len(prices)
            savings = avg_price - deal['price']
            if savings > 0 and len(group_deals) > 1:
                summary_points.append(f"💰 Saves you ₹{round(savings):,} compared to the average price of this group.")
            
            if deal['is_cheapest']:
                summary_points.append("🏷️ Absolute lowest price option found.")
                
            if deal['rating'] >= 4.3:
                summary_points.append(f"⭐ Highly rated ({deal['rating']}/5) with positive customer feedback.")
                
            if deal['delivery_fee'] == 0:
                summary_points.append("🚚 Free Shipping included.")
            elif deal['delivery_fee'] < 40:
                summary_points.append(f"🚚 Low delivery fee of ₹{deal['delivery_fee']}.")
                
            if deal['sentiment_score'] > 0.4:
                summary_points.append("❤️ Customer sentiment is overwhelmingly positive.")
            elif deal['sentiment_score'] < 0.0:
                summary_points.append("⚠️ Reviews indicate mixed feedback, check product sizing/returns.")
                
            deal['ai_summary'] = " \n".join(summary_points)

        return group_deals
