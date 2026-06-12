import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ProductMatcher:
    def __init__(self, threshold=0.55):
        self.threshold = threshold

    def _clean_text(self, text):
        """
        Cleans and tokenizes text for vectorization.
        """
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Remove punctuation except numbers/specs
        text = re.sub(r'[^a-z0-9\s-]', ' ', text)
        # Normalize spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_specs(self, text):
        """
        Extracts key specs to prevent false positive matching (e.g. 128GB matching with 256GB).
        """
        text = text.lower()
        specs = {}
        
        # 1. Storage / RAM (e.g. 128gb, 256 gb, 16gb ram)
        # Search for RAM specifically
        ram_match = re.search(r'\b(\d+)\s*gb\s*ram\b', text)
        if ram_match:
            specs['ram'] = ram_match.group(1) + 'gb'
            
        # Search for generic GB/TB (might be storage or RAM)
        storage_matches = re.findall(r'\b(\d+)\s*(gb|tb)\b', text)
        for val, unit in storage_matches:
            if 'ram' in text and f"{val}{unit} ram" in text:
                continue
            # If not labeled as RAM, assume storage
            if 'storage' not in specs:
                specs['storage'] = f"{val}{unit}"
                
        # 2. Clothing/Shoe Size (e.g., Size M, Size 8)
        size_match = re.search(r'\bsize\s*([xsml]|xl|xxl|\d+)\b', text)
        if size_match:
            specs['size'] = size_match.group(1)
            
        return specs

    def _are_specs_compatible(self, specs1, specs2):
        """
        Returns False if there are conflicting specifications (e.g., different storage sizes).
        """
        for key in ['storage', 'ram', 'size']:
            if key in specs1 and key in specs2:
                if specs1[key] != specs2[key]:
                    return False
        return True

    def cluster_deals(self, deals):
        """
        Clusters similar deals into groups based on text similarity and compatible specs.
        """
        if not deals:
            return []

        cleaned_titles = [self._clean_text(d['title']) for d in deals]
        specs_list = [self._extract_specs(d['title']) for d in deals]

        # Vectorize titles
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(cleaned_titles)
        
        # Calculate cosine similarity matrix
        sim_matrix = cosine_similarity(tfidf_matrix)
        
        n_deals = len(deals)
        visited = [False] * n_deals
        groups = []

        for i in range(n_deals):
            if visited[i]:
                continue
                
            # Create a new cluster
            cluster_indices = [i]
            visited[i] = True
            
            # Find similar items
            for j in range(i + 1, n_deals):
                if visited[j]:
                    continue
                
                # Check similarity threshold
                similarity = sim_matrix[i][j]
                
                # Check if specs are compatible (e.g., not matching 128GB vs 256GB)
                specs_compatible = self._are_specs_compatible(specs_list[i], specs_list[j])
                
                if similarity >= self.threshold and specs_compatible:
                    cluster_indices.append(j)
                    visited[j] = True
            
            # Form the ProductGroup
            cluster_deals = [deals[idx] for idx in cluster_indices]
            
            # Determine representing name (usually the shortest or cleanest title)
            # Sorting by length is a simple, effective heuristic for clean titles
            representative_deal = min(cluster_deals, key=lambda x: len(x['title']))
            group_name = representative_deal['title']
            
            # Clean up the group name if it has trailing specs
            # e.g., strip platform-specific info if needed
            group_name = re.sub(r'\s*[\(\[-]\s*(amazon|flipkart|myntra|ajio|meesho).*', '', group_name, flags=re.IGNORECASE)
            
            group_img = representative_deal['image_url']
            
            prices = [d['price'] for d in cluster_deals]
            min_price = min(prices)
            max_price = max(prices)
            
            groups.append({
                "name": group_name,
                "image_url": group_img,
                "min_price": min_price,
                "max_price": max_price,
                "deals": cluster_deals
            })
            
        # Sort groups by number of deals (popular products first)
        groups = sorted(groups, key=lambda g: len(g['deals']), reverse=True)
        return groups
