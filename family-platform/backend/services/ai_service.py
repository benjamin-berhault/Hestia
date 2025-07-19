import cv2
import numpy as np
from PIL import Image
import io
import face_recognition
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from typing import Dict, List, Optional, Tuple
import logging
import json
from config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI-powered services for content moderation, personality analysis, and compatibility"""
    
    def __init__(self):
        self.inappropriate_content_model = None
        self.personality_analyzer = None
        self.compatibility_model = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained AI models"""
        try:
            # In production, load actual trained models
            # For now, we'll use placeholder logic
            self.inappropriate_content_model = LogisticRegression()
            logger.info("AI models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
    
    async def moderate_image(self, image_data: bytes) -> Dict:
        """Analyze image for inappropriate content using AI"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image analysis
            width, height = image.size
            
            # Face detection
            faces_data = self._detect_faces(image_data)
            
            # Content moderation
            moderation_result = self._analyze_image_content(image)
            
            # Image quality assessment
            quality_score = self._assess_image_quality(image)
            
            return {
                "dimensions": {"width": width, "height": height},
                "faces": faces_data,
                "moderation": moderation_result,
                "quality_score": quality_score,
                "dominant_colors": self._extract_dominant_colors(image)
            }
            
        except Exception as e:
            logger.error(f"Image moderation failed: {e}")
            return {
                "error": str(e),
                "moderation": {"is_appropriate": False, "confidence": 0.0}
            }
    
    def _detect_faces(self, image_data: bytes) -> Dict:
        """Detect faces in image"""
        try:
            # Convert to format face_recognition can use
            image = face_recognition.load_image_from_file(io.BytesIO(image_data))
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return {"count": 0, "confidence": 0.0}
            
            # Basic face analysis
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            return {
                "count": len(face_locations),
                "confidence": 0.9,  # Placeholder
                "locations": face_locations,
                "estimated_age": None,  # Would use age estimation model
                "estimated_gender": None  # Would use gender classification model
            }
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return {"count": 0, "confidence": 0.0, "error": str(e)}
    
    def _analyze_image_content(self, image: Image.Image) -> Dict:
        """Analyze image for inappropriate content"""
        try:
            # Convert to OpenCV format for analysis
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Placeholder for actual content moderation
            # In production, use trained models for:
            # - Nudity detection
            # - Violence detection
            # - Inappropriate content
            
            # Simple brightness and contrast checks
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Basic heuristics (replace with actual AI models)
            is_appropriate = True
            confidence = 0.95
            flags = []
            
            # Very basic checks
            if brightness < 30:  # Too dark
                flags.append("image_too_dark")
                confidence -= 0.1
            
            return {
                "is_appropriate": is_appropriate,
                "confidence": confidence,
                "flags": flags,
                "nudity_confidence": 0.1,  # Placeholder
                "violence_confidence": 0.05,  # Placeholder
                "brightness_score": float(brightness / 255)
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {
                "is_appropriate": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _assess_image_quality(self, image: Image.Image) -> float:
        """Assess image quality score"""
        try:
            # Convert to OpenCV for quality analysis
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (sharpness)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 scale (rough approximation)
            quality_score = min(laplacian_var / 1000, 1.0)
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return 0.5  # Default medium quality
    
    def _extract_dominant_colors(self, image: Image.Image) -> List[List[int]]:
        """Extract dominant colors from image"""
        try:
            # Resize image for faster processing
            image = image.resize((150, 150))
            
            # Convert to numpy array
            data = np.array(image)
            data = data.reshape((-1, 3))
            
            # Use k-means clustering to find dominant colors
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=5, random_state=42)
            kmeans.fit(data)
            
            # Get the RGB values of the cluster centers
            colors = kmeans.cluster_centers_.astype(int).tolist()
            
            return colors
            
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
            return []
    
    async def moderate_text(self, text: str) -> Dict:
        """Analyze text for inappropriate content"""
        try:
            # Basic text moderation
            inappropriate_words = [
                # Add your inappropriate words list
                'spam', 'scam', 'inappropriate'
            ]
            
            text_lower = text.lower()
            flags = []
            
            for word in inappropriate_words:
                if word in text_lower:
                    flags.append(f"inappropriate_word_{word}")
            
            # Sentiment analysis (placeholder)
            sentiment_score = 0.7  # Positive sentiment
            
            # Spam detection (placeholder)
            spam_score = 0.1  # Low spam probability
            
            is_appropriate = len(flags) == 0 and spam_score < 0.5
            
            return {
                "is_appropriate": is_appropriate,
                "confidence": 0.9,
                "flags": flags,
                "sentiment_score": sentiment_score,
                "spam_score": spam_score,
                "toxicity_score": 0.05  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Text moderation failed: {e}")
            return {
                "is_appropriate": True,
                "confidence": 0.5,
                "error": str(e)
            }
    
    async def analyze_personality(self, text_data: List[str]) -> Dict:
        """Analyze personality traits from text data (bio, messages, etc.)"""
        try:
            # Combine all text
            combined_text = " ".join(text_data)
            
            # Placeholder for Big 5 personality analysis
            # In production, use trained models for personality detection
            
            personality_scores = {
                "openness": 0.7,  # Openness to experience
                "conscientiousness": 0.8,  # Conscientiousness
                "extraversion": 0.6,  # Extraversion
                "agreeableness": 0.75,  # Agreeableness
                "neuroticism": 0.3  # Neuroticism (lower is better)
            }
            
            # Communication style analysis
            communication_style = self._analyze_communication_style(combined_text)
            
            return {
                "big_five": personality_scores,
                "communication_style": communication_style,
                "confidence": 0.8,
                "word_count": len(combined_text.split())
            }
            
        except Exception as e:
            logger.error(f"Personality analysis failed: {e}")
            return {
                "big_five": {},
                "communication_style": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _analyze_communication_style(self, text: str) -> str:
        """Analyze communication style from text"""
        text_lower = text.lower()
        
        # Simple heuristics (replace with ML models)
        if any(word in text_lower for word in ['excited', 'amazing', 'fantastic', '!']):
            return "enthusiastic"
        elif any(word in text_lower for word in ['think', 'analyze', 'consider']):
            return "analytical"
        elif any(word in text_lower for word in ['feel', 'emotion', 'heart']):
            return "emotional"
        else:
            return "balanced"
    
    async def calculate_advanced_compatibility(self, user1_data: Dict, user2_data: Dict) -> Dict:
        """Calculate advanced compatibility using AI/ML"""
        try:
            # Extract features for ML model
            features1 = self._extract_compatibility_features(user1_data)
            features2 = self._extract_compatibility_features(user2_data)
            
            # Calculate similarity scores for different dimensions
            personality_match = self._calculate_personality_compatibility(
                user1_data.get('personality', {}),
                user2_data.get('personality', {})
            )
            
            communication_match = self._calculate_communication_compatibility(
                user1_data.get('communication_style'),
                user2_data.get('communication_style')
            )
            
            values_match = self._calculate_values_compatibility(
                user1_data.get('values', {}),
                user2_data.get('values', {})
            )
            
            # ML-based prediction (placeholder)
            ml_score = 0.75  # Would use trained model
            
            return {
                "overall_score": (personality_match + communication_match + values_match) / 3,
                "personality_compatibility": personality_match,
                "communication_compatibility": communication_match,
                "values_compatibility": values_match,
                "ml_prediction": ml_score,
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Advanced compatibility calculation failed: {e}")
            return {
                "overall_score": 0.5,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _extract_compatibility_features(self, user_data: Dict) -> List[float]:
        """Extract numerical features for ML compatibility model"""
        features = []
        
        # Age feature
        features.append(user_data.get('age', 30) / 100)
        
        # Education level (encoded)
        education_map = {
            'high_school': 0.2,
            'some_college': 0.4,
            'bachelors': 0.6,
            'masters': 0.8,
            'doctorate': 1.0
        }
        features.append(education_map.get(user_data.get('education'), 0.5))
        
        # Add more features as needed
        return features
    
    def _calculate_personality_compatibility(self, p1: Dict, p2: Dict) -> float:
        """Calculate personality compatibility using Big 5 traits"""
        if not p1 or not p2:
            return 0.5
        
        # Complementary traits (some differences are good)
        score = 0.0
        traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            if trait in p1 and trait in p2:
                diff = abs(p1[trait] - p2[trait])
                # Some traits benefit from similarity, others from complementarity
                if trait in ['conscientiousness', 'agreeableness']:
                    score += 1 - diff  # Similarity is good
                else:
                    score += 1 - min(diff, 0.5)  # Some difference is okay
        
        return score / len(traits) if traits else 0.5
    
    def _calculate_communication_compatibility(self, style1: str, style2: str) -> float:
        """Calculate communication style compatibility"""
        if not style1 or not style2:
            return 0.5
        
        # Compatible communication styles
        compatible_pairs = {
            ('analytical', 'analytical'): 0.9,
            ('emotional', 'emotional'): 0.8,
            ('enthusiastic', 'balanced'): 0.85,
            ('analytical', 'balanced'): 0.8
        }
        
        pair = tuple(sorted([style1, style2]))
        return compatible_pairs.get(pair, 0.6)
    
    def _calculate_values_compatibility(self, values1: Dict, values2: Dict) -> float:
        """Calculate values compatibility"""
        if not values1 or not values2:
            return 0.5
        
        score = 0.0
        count = 0
        
        # Compare important values
        important_values = ['family_timeline', 'children_count', 'religious_views', 'parenting_philosophy']
        
        for value in important_values:
            if value in values1 and value in values2:
                if values1[value] == values2[value]:
                    score += 1.0
                else:
                    score += 0.3  # Some mismatch penalty
                count += 1
        
        return score / count if count > 0 else 0.5