import re
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from email_validator import validate_email as email_validate, EmailNotValidError

def validate_email(email: str) -> Dict[str, Any]:
    """Validate email address format"""
    try:
        valid = email_validate(email)
        return {
            "valid": True,
            "email": valid.email,
            "errors": []
        }
    except EmailNotValidError as e:
        return {
            "valid": False,
            "email": email,
            "errors": [str(e)]
        }

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "strength": calculate_password_strength(password)
    }

def calculate_password_strength(password: str) -> str:
    """Calculate password strength level"""
    score = 0
    
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    
    if score <= 2:
        return "weak"
    elif score <= 4:
        return "medium"
    else:
        return "strong"

def validate_age(date_of_birth: date) -> Dict[str, Any]:
    """Validate age requirements (18-65)"""
    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    errors = []
    
    if age < 18:
        errors.append("You must be at least 18 years old to join")
    elif age > 65:
        errors.append("Age must be 65 or younger")
    
    return {
        "valid": len(errors) == 0,
        "age": age,
        "errors": errors
    }

def validate_profile_data(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate complete profile data"""
    errors = []
    warnings = []
    
    # Required fields
    required_fields = [
        "first_name", "last_name", "date_of_birth", "gender",
        "location_city", "location_state", "education_level",
        "occupation", "religious_views", "wants_children",
        "children_timeline", "desired_children_count",
        "relationship_timeline", "living_arrangement_preference",
        "bio", "family_vision", "looking_for"
    ]
    
    for field in required_fields:
        if not profile_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # Name validation
    if profile_data.get("first_name"):
        if len(profile_data["first_name"]) < 2:
            errors.append("First name must be at least 2 characters")
        if not re.match(r"^[a-zA-Z\s-']+$", profile_data["first_name"]):
            errors.append("First name contains invalid characters")
    
    if profile_data.get("last_name"):
        if len(profile_data["last_name"]) < 2:
            errors.append("Last name must be at least 2 characters")
        if not re.match(r"^[a-zA-Z\s-']+$", profile_data["last_name"]):
            errors.append("Last name contains invalid characters")
    
    # Date of birth validation
    if profile_data.get("date_of_birth"):
        try:
            if isinstance(profile_data["date_of_birth"], str):
                dob = datetime.strptime(profile_data["date_of_birth"], "%Y-%m-%d").date()
            else:
                dob = profile_data["date_of_birth"]
            
            age_validation = validate_age(dob)
            if not age_validation["valid"]:
                errors.extend(age_validation["errors"])
        except ValueError:
            errors.append("Invalid date of birth format")
    
    # Bio validation
    if profile_data.get("bio"):
        if len(profile_data["bio"]) < 50:
            warnings.append("Bio should be at least 50 characters for better matches")
        if len(profile_data["bio"]) > 1000:
            errors.append("Bio must be less than 1000 characters")
    
    # Family vision validation
    if profile_data.get("family_vision"):
        if len(profile_data["family_vision"]) < 30:
            warnings.append("Family vision should be at least 30 characters")
        if len(profile_data["family_vision"]) > 500:
            errors.append("Family vision must be less than 500 characters")
    
    # Looking for validation
    if profile_data.get("looking_for"):
        if len(profile_data["looking_for"]) < 30:
            warnings.append("'Looking for' section should be at least 30 characters")
        if len(profile_data["looking_for"]) > 500:
            errors.append("'Looking for' section must be less than 500 characters")
    
    # Height validation
    if profile_data.get("height_inches"):
        height = profile_data["height_inches"]
        if height < 48 or height > 96:  # 4 feet to 8 feet
            errors.append("Height must be between 4 and 8 feet")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_preferences_data(preferences_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user preferences data"""
    errors = []
    warnings = []
    
    # Age range validation
    min_age = preferences_data.get("min_age")
    max_age = preferences_data.get("max_age")
    
    if min_age and max_age:
        if min_age >= max_age:
            errors.append("Minimum age must be less than maximum age")
        if min_age < 18:
            errors.append("Minimum age must be at least 18")
        if max_age > 65:
            errors.append("Maximum age must be 65 or less")
        if max_age - min_age > 20:
            warnings.append("Large age range may result in fewer quality matches")
    
    # Distance validation
    max_distance = preferences_data.get("max_distance_miles")
    if max_distance:
        if max_distance < 5:
            warnings.append("Very small distance range may limit matches")
        if max_distance > 500:
            warnings.append("Very large distance range may include incompatible locations")
    
    # Height preferences validation
    min_height = preferences_data.get("min_height_inches")
    max_height = preferences_data.get("max_height_inches")
    
    if min_height and max_height:
        if min_height >= max_height:
            errors.append("Minimum height must be less than maximum height")
        if min_height < 48 or max_height > 96:
            errors.append("Height preferences must be between 4 and 8 feet")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_photo_upload(file_data: bytes, content_type: str, filename: str) -> Dict[str, Any]:
    """Validate photo upload"""
    errors = []
    warnings = []
    
    # File size validation (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_data) > max_size:
        errors.append("File size must be less than 10MB")
    
    # Content type validation
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if content_type not in allowed_types:
        errors.append("File must be a JPEG, PNG, or WebP image")
    
    # Filename validation
    if not re.match(r"^[a-zA-Z0-9_.-]+\.(jpg|jpeg|png|webp)$", filename, re.IGNORECASE):
        errors.append("Invalid filename format")
    
    # File size warnings
    if len(file_data) < 50 * 1024:  # Less than 50KB
        warnings.append("Image quality may be too low")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def sanitize_text_input(text: str) -> str:
    """Sanitize text input to prevent XSS and other issues"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text