from typing import Dict, List, Optional
from models.user_profile import UserProfile
from models.user_preferences import UserPreferences, ImportanceLevel
import json
import math
import logging

logger = logging.getLogger(__name__)

def calculate_compatibility_score(
    user1_profile: UserProfile,
    user1_preferences: UserPreferences,
    user2_profile: UserProfile,
    user2_preferences: UserPreferences
) -> Dict:
    """Calculate compatibility score between two users"""
    
    scores = {}
    weights = {}
    total_weight = 0
    compatibility_breakdown = {}
    
    # Age compatibility
    age_score = calculate_age_compatibility(user1_profile, user1_preferences, user2_profile, user2_preferences)
    age_weight = get_importance_weight(user1_preferences.age_importance) + get_importance_weight(user2_preferences.age_importance)
    scores['age'] = age_score
    weights['age'] = age_weight
    total_weight += age_weight
    compatibility_breakdown['age'] = {
        'score': age_score,
        'weight': age_weight,
        'details': f"User1 age: {user1_profile.age}, User2 age: {user2_profile.age}"
    }
    
    # Location compatibility
    location_score = calculate_location_compatibility(user1_profile, user1_preferences, user2_profile, user2_preferences)
    location_weight = get_importance_weight(user1_preferences.location_importance) + get_importance_weight(user2_preferences.location_importance)
    scores['location'] = location_score
    weights['location'] = location_weight
    total_weight += location_weight
    compatibility_breakdown['location'] = {
        'score': location_score,
        'weight': location_weight,
        'details': f"User1: {user1_profile.location_city}, {user1_profile.location_state}; User2: {user2_profile.location_city}, {user2_profile.location_state}"
    }
    
    # Family goals compatibility (most important)
    family_score = calculate_family_compatibility(user1_profile, user1_preferences, user2_profile, user2_preferences)
    family_weight = 10.0  # Highest weight for family compatibility
    scores['family'] = family_score
    weights['family'] = family_weight
    total_weight += family_weight
    compatibility_breakdown['family'] = {
        'score': family_score,
        'weight': family_weight,
        'details': "Children timeline, count, and parenting philosophy alignment"
    }
    
    # Religious/spiritual compatibility
    religious_score = calculate_religious_compatibility(user1_profile, user1_preferences, user2_profile, user2_preferences)
    religious_weight = get_importance_weight(user1_preferences.religious_importance) + get_importance_weight(user2_preferences.religious_importance)
    scores['religious'] = religious_score
    weights['religious'] = religious_weight
    total_weight += religious_weight
    compatibility_breakdown['religious'] = {
        'score': religious_score,
        'weight': religious_weight,
        'details': f"User1: {user1_profile.religious_views.value if user1_profile.religious_views else 'Unknown'}, User2: {user2_profile.religious_views.value if user2_profile.religious_views else 'Unknown'}"
    }
    
    # Education compatibility
    education_score = calculate_education_compatibility(user1_profile, user1_preferences, user2_profile, user2_preferences)
    education_weight = get_importance_weight(user1_preferences.education_importance) + get_importance_weight(user2_preferences.education_importance)
    scores['education'] = education_score
    weights['education'] = education_weight
    total_weight += education_weight
    compatibility_breakdown['education'] = {
        'score': education_score,
        'weight': education_weight,
        'details': f"User1: {user1_profile.education_level.value if user1_profile.education_level else 'Unknown'}, User2: {user2_profile.education_level.value if user2_profile.education_level else 'Unknown'}"
    }
    
    # Lifestyle compatibility
    lifestyle_score = calculate_lifestyle_compatibility(user1_profile, user1_preferences, user2_profile, user2_preferences)
    lifestyle_weight = 3.0  # Moderate weight
    scores['lifestyle'] = lifestyle_score
    weights['lifestyle'] = lifestyle_weight
    total_weight += lifestyle_weight
    compatibility_breakdown['lifestyle'] = {
        'score': lifestyle_score,
        'weight': lifestyle_weight,
        'details': "Smoking, drinking, and exercise preferences"
    }
    
    # Calculate weighted average
    if total_weight > 0:
        overall_score = sum(scores[key] * weights[key] for key in scores) / total_weight
    else:
        overall_score = 0.0
    
    # Apply penalties for deal breakers
    deal_breaker_penalty = check_deal_breakers(user1_profile, user1_preferences, user2_profile, user2_preferences)
    overall_score *= (1 - deal_breaker_penalty)
    
    compatibility_breakdown['overall'] = {
        'score': overall_score,
        'deal_breaker_penalty': deal_breaker_penalty,
        'total_weight': total_weight
    }
    
    return {
        'compatibility_score': round(overall_score, 3),
        'breakdown': compatibility_breakdown
    }

def get_importance_weight(importance: ImportanceLevel) -> float:
    """Convert importance level to numeric weight"""
    weights = {
        ImportanceLevel.NOT_IMPORTANT: 1.0,
        ImportanceLevel.SOMEWHAT_IMPORTANT: 2.0,
        ImportanceLevel.IMPORTANT: 3.0,
        ImportanceLevel.VERY_IMPORTANT: 4.0,
        ImportanceLevel.DEAL_BREAKER: 5.0
    }
    return weights.get(importance, 1.0)

def calculate_age_compatibility(user1_profile, user1_prefs, user2_profile, user2_prefs) -> float:
    """Calculate age compatibility score"""
    user1_age = user1_profile.age
    user2_age = user2_profile.age
    
    # Check if each user falls within the other's age preference
    user1_wants_user2 = user1_prefs.min_age <= user2_age <= user1_prefs.max_age
    user2_wants_user1 = user2_prefs.min_age <= user1_age <= user2_prefs.max_age
    
    if user1_wants_user2 and user2_wants_user1:
        return 1.0
    elif user1_wants_user2 or user2_wants_user1:
        return 0.5
    else:
        return 0.0

def calculate_location_compatibility(user1_profile, user1_prefs, user2_profile, user2_prefs) -> float:
    """Calculate location compatibility score"""
    # Simplified distance calculation (would use actual geolocation in production)
    if user1_profile.location_city == user2_profile.location_city and user1_profile.location_state == user2_profile.location_state:
        return 1.0
    elif user1_profile.location_state == user2_profile.location_state:
        return 0.7
    else:
        # Check if either user is willing to relocate
        if user1_prefs.willing_to_relocate or user2_prefs.willing_to_relocate:
            return 0.5
        else:
            return 0.2

def calculate_family_compatibility(user1_profile, user1_prefs, user2_profile, user2_prefs) -> float:
    """Calculate family goals compatibility score"""
    score = 0.0
    factors = 0
    
    # Children timeline compatibility
    if user1_profile.children_timeline and user2_profile.children_timeline:
        timeline_score = 1.0 if user1_profile.children_timeline == user2_profile.children_timeline else 0.3
        score += timeline_score
        factors += 1
    
    # Desired children count compatibility
    if user1_profile.desired_children_count and user2_profile.desired_children_count:
        count_score = 1.0 if user1_profile.desired_children_count == user2_profile.desired_children_count else 0.5
        score += count_score
        factors += 1
    
    # Parenting philosophy compatibility
    if user1_profile.parenting_philosophy and user2_profile.parenting_philosophy:
        parenting_score = 1.0 if user1_profile.parenting_philosophy == user2_profile.parenting_philosophy else 0.4
        score += parenting_score
        factors += 1
    
    # Relationship timeline compatibility
    if user1_profile.relationship_timeline and user2_profile.relationship_timeline:
        relationship_score = 1.0 if user1_profile.relationship_timeline == user2_profile.relationship_timeline else 0.6
        score += relationship_score
        factors += 1
    
    return score / factors if factors > 0 else 0.5

def calculate_religious_compatibility(user1_profile, user1_prefs, user2_profile, user2_prefs) -> float:
    """Calculate religious/spiritual compatibility score"""
    if not user1_profile.religious_views or not user2_profile.religious_views:
        return 0.5
    
    if user1_profile.religious_views == user2_profile.religious_views:
        return 1.0
    
    # Some religious views are more compatible than others
    compatible_pairs = [
        ("christian", "catholic"),
        ("spiritual", "buddhist"),
        ("agnostic", "atheist")
    ]
    
    user1_view = user1_profile.religious_views.value
    user2_view = user2_profile.religious_views.value
    
    for pair in compatible_pairs:
        if (user1_view in pair and user2_view in pair):
            return 0.7
    
    return 0.3

def calculate_education_compatibility(user1_profile, user1_prefs, user2_profile, user2_prefs) -> float:
    """Calculate education compatibility score"""
    if not user1_profile.education_level or not user2_profile.education_level:
        return 0.5
    
    education_hierarchy = {
        "high_school": 1,
        "some_college": 2,
        "trade_school": 2,
        "bachelors": 3,
        "masters": 4,
        "doctorate": 5,
        "other": 2
    }
    
    user1_level = education_hierarchy.get(user1_profile.education_level.value, 2)
    user2_level = education_hierarchy.get(user2_profile.education_level.value, 2)
    
    difference = abs(user1_level - user2_level)
    
    if difference == 0:
        return 1.0
    elif difference == 1:
        return 0.8
    elif difference == 2:
        return 0.6
    else:
        return 0.3

def calculate_lifestyle_compatibility(user1_profile, user1_prefs, user2_profile, user2_prefs) -> float:
    """Calculate lifestyle compatibility score"""
    score = 0.0
    factors = 0
    
    # Smoking compatibility
    if user1_profile.smoking and user2_profile.smoking:
        if user1_profile.smoking == user2_profile.smoking:
            score += 1.0
        elif "never" in [user1_profile.smoking, user2_profile.smoking]:
            score += 0.3
        else:
            score += 0.7
        factors += 1
    
    # Drinking compatibility
    if user1_profile.drinking and user2_profile.drinking:
        if user1_profile.drinking == user2_profile.drinking:
            score += 1.0
        elif "never" in [user1_profile.drinking, user2_profile.drinking] and "regularly" in [user1_profile.drinking, user2_profile.drinking]:
            score += 0.2
        else:
            score += 0.6
        factors += 1
    
    # Exercise compatibility
    if user1_profile.exercise_frequency and user2_profile.exercise_frequency:
        if user1_profile.exercise_frequency == user2_profile.exercise_frequency:
            score += 1.0
        else:
            score += 0.5
        factors += 1
    
    return score / factors if factors > 0 else 0.5

def check_deal_breakers(user1_profile, user1_prefs, user2_profile, user2_prefs) -> float:
    """Check for deal breakers and return penalty (0.0 to 1.0)"""
    penalty = 0.0
    
    # Age deal breakers
    if user1_prefs.age_importance == ImportanceLevel.DEAL_BREAKER:
        if not (user1_prefs.min_age <= user2_profile.age <= user1_prefs.max_age):
            penalty = 1.0  # Complete incompatibility
    
    if user2_prefs.age_importance == ImportanceLevel.DEAL_BREAKER:
        if not (user2_prefs.min_age <= user1_profile.age <= user2_prefs.max_age):
            penalty = 1.0
    
    # Children timeline deal breakers
    if (user1_prefs.children_timeline_importance == ImportanceLevel.DEAL_BREAKER and 
        user1_profile.children_timeline != user2_profile.children_timeline):
        penalty = max(penalty, 0.8)
    
    if (user2_prefs.children_timeline_importance == ImportanceLevel.DEAL_BREAKER and 
        user1_profile.children_timeline != user2_profile.children_timeline):
        penalty = max(penalty, 0.8)
    
    return penalty