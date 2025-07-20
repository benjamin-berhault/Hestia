from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.personal_development import (
    PersonalDevelopmentGoal, SkillChallenge, ChallengeParticipation,
    MentorshipPair, AchievementBadge, UserBadge, PeerSupportGroup,
    GroupMembership, FeedbackRequest, FeedbackResponse,
    DevelopmentCategory, GoalDifficulty, AchievementStatus, MentorshipStatus
)
from services.personal_development_service import PersonalDevelopmentService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
dev_service = PersonalDevelopmentService()

# Pydantic Models
class CreateGoalRequest(BaseModel):
    category: DevelopmentCategory
    difficulty: GoalDifficulty
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    target_description: str = Field(..., min_length=10, max_length=500)
    target_date: datetime
    target_value: Optional[float] = None
    unit: Optional[str] = None

class UpdateGoalProgressRequest(BaseModel):
    progress_description: str = Field(..., min_length=5, max_length=500)
    current_value: Optional[float] = None
    photos: Optional[List[str]] = []

class CreateChallengeRequest(BaseModel):
    category: DevelopmentCategory
    difficulty: GoalDifficulty
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    instructions: str = Field(..., min_length=10, max_length=2000)
    success_criteria: Dict[str, Any]
    required_evidence: List[str]
    start_date: datetime
    end_date: datetime
    base_points: int = Field(..., ge=10, le=1000)
    max_participants: Optional[int] = None

class SubmitChallengeRequest(BaseModel):
    submission_text: str = Field(..., min_length=10, max_length=2000)
    photos: Optional[List[str]] = []
    videos: Optional[List[str]] = []

class RequestMentorshipRequest(BaseModel):
    focus_areas: List[str] = Field(..., min_items=1, max_items=5)
    goals: str = Field(..., min_length=20, max_length=1000)
    preferred_communication: str = Field(default="video")

class CreateSupportGroupRequest(BaseModel):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    focus_category: Optional[DevelopmentCategory] = None
    group_type: str = Field(default="mixed")
    max_members: int = Field(default=8, ge=3, le=20)

class RequestFeedbackRequest(BaseModel):
    feedback_type: str = Field(..., regex="^(profile|photos|messaging|general)$")
    description: str = Field(..., min_length=10, max_length=500)
    specific_area: Optional[str] = None
    feedback_from_women: bool = True
    feedback_from_men: bool = True

class ProvideFeedbackRequest(BaseModel):
    overall_rating: int = Field(..., ge=1, le=5)
    specific_feedback: str = Field(..., min_length=20, max_length=1000)
    suggestions: Optional[str] = None
    positive_aspects: Optional[List[str]] = []
    improvement_areas: Optional[List[str]] = []

# Goal Management Endpoints
@router.post("/goals", response_model=Dict[str, Any])
async def create_development_goal(
    goal_data: CreateGoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new personal development goal"""
    try:
        goal = await dev_service.create_development_goal(
            db=db,
            user=current_user,
            category=goal_data.category,
            difficulty=goal_data.difficulty,
            title=goal_data.title,
            description=goal_data.description,
            target_description=goal_data.target_description,
            target_date=goal_data.target_date,
            target_value=goal_data.target_value,
            unit=goal_data.unit
        )
        
        return {
            "id": goal.id,
            "title": goal.title,
            "category": goal.category.value,
            "difficulty": goal.difficulty.value,
            "status": goal.status.value,
            "progress_percentage": goal.progress_percentage,
            "created_at": goal.created_at
        }
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        raise HTTPException(status_code=500, detail="Failed to create goal")

@router.get("/goals", response_model=List[Dict[str, Any]])
async def get_user_goals(
    category: Optional[DevelopmentCategory] = Query(None),
    status: Optional[AchievementStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's development goals"""
    query = db.query(PersonalDevelopmentGoal).filter(
        PersonalDevelopmentGoal.user_id == current_user.id
    )
    
    if category:
        query = query.filter(PersonalDevelopmentGoal.category == category)
    
    if status:
        query = query.filter(PersonalDevelopmentGoal.status == status)
    
    goals = query.order_by(PersonalDevelopmentGoal.created_at.desc()).all()
    
    return [
        {
            "id": goal.id,
            "title": goal.title,
            "category": goal.category.value,
            "difficulty": goal.difficulty.value,
            "description": goal.description,
            "target_description": goal.target_description,
            "status": goal.status.value,
            "progress_percentage": goal.progress_percentage,
            "current_value": goal.current_value,
            "target_value": goal.target_value,
            "unit": goal.unit,
            "points_earned": goal.points_earned,
            "target_date": goal.target_date,
            "completed_date": goal.completed_date,
            "progress_notes": goal.progress_notes[-5:] if goal.progress_notes else [],  # Last 5 updates
            "created_at": goal.created_at
        }
        for goal in goals
    ]

@router.put("/goals/{goal_id}/progress")
async def update_goal_progress(
    goal_id: int,
    progress_data: UpdateGoalProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress on a development goal"""
    goal = db.query(PersonalDevelopmentGoal).filter(
        PersonalDevelopmentGoal.id == goal_id,
        PersonalDevelopmentGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    try:
        updated_goal = await dev_service.update_goal_progress(
            db=db,
            goal=goal,
            progress_description=progress_data.progress_description,
            current_value=progress_data.current_value,
            photos=progress_data.photos
        )
        
        return {
            "id": updated_goal.id,
            "status": updated_goal.status.value,
            "progress_percentage": updated_goal.progress_percentage,
            "points_earned": updated_goal.points_earned,
            "message": "Progress updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating goal progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to update progress")

@router.get("/goals/recommendations")
async def get_recommended_goals(
    category: Optional[DevelopmentCategory] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-recommended goals for user"""
    try:
        recommendations = await dev_service.get_recommended_goals(
            db=db,
            user=current_user,
            category=category
        )
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting goal recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

# Challenge System Endpoints
@router.get("/challenges/active")
async def get_active_challenges(
    category: Optional[DevelopmentCategory] = Query(None),
    difficulty: Optional[GoalDifficulty] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get currently active challenges"""
    try:
        challenges = await dev_service.get_active_challenges(
            db=db,
            category=category,
            difficulty=difficulty,
            user=current_user
        )
        
        return [
            {
                "id": challenge.id,
                "title": challenge.title,
                "category": challenge.category.value,
                "difficulty": challenge.difficulty.value,
                "description": challenge.description,
                "instructions": challenge.instructions,
                "base_points": challenge.base_points,
                "current_participants": challenge.current_participants,
                "max_participants": challenge.max_participants,
                "start_date": challenge.start_date,
                "end_date": challenge.end_date,
                "success_criteria": challenge.success_criteria,
                "required_evidence": challenge.required_evidence
            }
            for challenge in challenges
        ]
    except Exception as e:
        logger.error(f"Error getting active challenges: {e}")
        raise HTTPException(status_code=500, detail="Failed to get challenges")

@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a skill challenge"""
    challenge = db.query(SkillChallenge).filter(SkillChallenge.id == challenge_id).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    try:
        participation = await dev_service.join_challenge(
            db=db,
            user=current_user,
            challenge=challenge
        )
        
        return {
            "id": participation.id,
            "challenge_id": challenge.id,
            "status": participation.status.value,
            "started_date": participation.started_date,
            "message": "Successfully joined challenge"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error joining challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to join challenge")

@router.get("/challenges/my-participations")
async def get_my_challenge_participations(
    status: Optional[AchievementStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's challenge participations"""
    query = db.query(ChallengeParticipation).filter(
        ChallengeParticipation.user_id == current_user.id
    )
    
    if status:
        query = query.filter(ChallengeParticipation.status == status)
    
    participations = query.order_by(ChallengeParticipation.started_date.desc()).all()
    
    return [
        {
            "id": participation.id,
            "challenge": {
                "id": participation.challenge.id,
                "title": participation.challenge.title,
                "category": participation.challenge.category.value,
                "difficulty": participation.challenge.difficulty.value,
                "base_points": participation.challenge.base_points
            },
            "status": participation.status.value,
            "started_date": participation.started_date,
            "completed_date": participation.completed_date,
            "points_earned": participation.points_earned,
            "progress_percentage": participation.progress_percentage,
            "effort_days_completed": participation.effort_days_completed,
            "daily_checkins": participation.daily_checkins[-5:] if participation.daily_checkins else []
        }
        for participation in participations
    ]

@router.post("/challenges/participations/{participation_id}/submit")
async def submit_challenge_completion(
    participation_id: int,
    submission_data: SubmitChallengeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit challenge completion for review"""
    participation = db.query(ChallengeParticipation).filter(
        ChallengeParticipation.id == participation_id,
        ChallengeParticipation.user_id == current_user.id
    ).first()
    
    if not participation:
        raise HTTPException(status_code=404, detail="Participation not found")
    
    try:
        updated_participation = await dev_service.submit_challenge_completion(
            db=db,
            participation=participation,
            submission_text=submission_data.submission_text,
            photos=submission_data.photos,
            videos=submission_data.videos
        )
        
        return {
            "id": updated_participation.id,
            "status": updated_participation.status.value,
            "points_earned": updated_participation.points_earned,
            "message": "Challenge submission successful"
        }
    except Exception as e:
        logger.error(f"Error submitting challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit challenge")

# Mentorship System Endpoints
@router.post("/mentorship/request")
async def request_mentorship(
    mentorship_data: RequestMentorshipRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request mentorship matching"""
    try:
        mentorship = await dev_service.request_mentor(
            db=db,
            mentee=current_user,
            focus_areas=mentorship_data.focus_areas,
            goals=mentorship_data.goals,
            preferred_communication=mentorship_data.preferred_communication
        )
        
        return {
            "id": mentorship.id,
            "mentor_id": mentorship.mentor_id,
            "status": mentorship.status.value,
            "focus_areas": mentorship.focus_areas,
            "message": "Mentorship request sent successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error requesting mentorship: {e}")
        raise HTTPException(status_code=500, detail="Failed to request mentorship")

@router.get("/mentorship/my-relationships")
async def get_my_mentorship_relationships(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's mentorship relationships (as mentor and mentee)"""
    
    # As mentee
    mentee_relationships = db.query(MentorshipPair).filter(
        MentorshipPair.mentee_id == current_user.id
    ).all()
    
    # As mentor
    mentor_relationships = db.query(MentorshipPair).filter(
        MentorshipPair.mentor_id == current_user.id
    ).all()
    
    return {
        "as_mentee": [
            {
                "id": rel.id,
                "mentor": {
                    "id": rel.mentor.id,
                    "name": rel.mentor.profile.first_name if rel.mentor.profile else "Unknown",
                    "expertise": rel.mentor.get_category_expertise()
                },
                "status": rel.status.value,
                "focus_areas": rel.focus_areas,
                "started_date": rel.started_date,
                "total_sessions": rel.total_sessions
            }
            for rel in mentee_relationships
        ],
        "as_mentor": [
            {
                "id": rel.id,
                "mentee": {
                    "id": rel.mentee.id,
                    "name": rel.mentee.profile.first_name if rel.mentee.profile else "Unknown"
                },
                "status": rel.status.value,
                "focus_areas": rel.focus_areas,
                "started_date": rel.started_date,
                "total_sessions": rel.total_sessions
            }
            for rel in mentor_relationships
        ]
    }

@router.post("/mentorship/{mentorship_id}/accept")
async def accept_mentorship(
    mentorship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a mentorship request (mentor only)"""
    mentorship = db.query(MentorshipPair).filter(
        MentorshipPair.id == mentorship_id,
        MentorshipPair.mentor_id == current_user.id,
        MentorshipPair.status == MentorshipStatus.PENDING
    ).first()
    
    if not mentorship:
        raise HTTPException(status_code=404, detail="Mentorship request not found")
    
    try:
        updated_mentorship = await dev_service.accept_mentorship(db=db, mentorship=mentorship)
        
        return {
            "id": updated_mentorship.id,
            "status": updated_mentorship.status.value,
            "started_date": updated_mentorship.started_date,
            "message": "Mentorship accepted successfully"
        }
    except Exception as e:
        logger.error(f"Error accepting mentorship: {e}")
        raise HTTPException(status_code=500, detail="Failed to accept mentorship")

# Gamification Endpoints
@router.get("/badges/available")
async def get_available_badges(
    category: Optional[DevelopmentCategory] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available badges"""
    query = db.query(AchievementBadge).filter(AchievementBadge.is_active == True)
    
    if category:
        query = query.filter(AchievementBadge.category == category)
    
    badges = query.all()
    user_badge_ids = [ub.badge_id for ub in current_user.badges]
    
    return [
        {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "category": badge.category.value,
            "difficulty": badge.difficulty.value,
            "points_reward": badge.points_reward,
            "requirements": badge.requirements,
            "earned": badge.id in user_badge_ids,
            "total_earned": badge.total_earned
        }
        for badge in badges
    ]

@router.get("/badges/my-badges")
async def get_my_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's earned badges"""
    user_badges = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).order_by(UserBadge.earned_date.desc()).all()
    
    return [
        {
            "id": ub.id,
            "badge": {
                "id": ub.badge.id,
                "name": ub.badge.name,
                "description": ub.badge.description,
                "category": ub.badge.category.value,
                "difficulty": ub.badge.difficulty.value,
                "icon_url": ub.badge.icon_url
            },
            "earned_date": ub.earned_date,
            "points_earned": ub.points_earned,
            "is_featured": ub.is_featured
        }
        for ub in user_badges
    ]

@router.get("/dashboard")
async def get_development_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personal development dashboard data"""
    
    # Get basic stats
    total_points = current_user.get_development_score()
    active_goals = current_user.get_active_goals_count()
    completed_goals = current_user.get_completed_goals_count()
    current_challenges = len(current_user.get_current_challenges())
    
    # Get category expertise
    expertise = current_user.get_category_expertise()
    
    # Get recent achievements
    recent_badges = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).order_by(UserBadge.earned_date.desc()).limit(3).all()
    
    # Get upcoming challenge deadlines
    upcoming_deadlines = db.query(ChallengeParticipation).join(SkillChallenge).filter(
        ChallengeParticipation.user_id == current_user.id,
        ChallengeParticipation.status == AchievementStatus.IN_PROGRESS,
        SkillChallenge.end_date > datetime.utcnow()
    ).order_by(SkillChallenge.end_date).limit(3).all()
    
    return {
        "stats": {
            "total_points": total_points,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "current_challenges": current_challenges,
            "badges_earned": len(current_user.badges),
            "development_streak": current_user.get_development_streak()
        },
        "expertise": expertise,
        "recent_badges": [
            {
                "name": ub.badge.name,
                "earned_date": ub.earned_date,
                "points_earned": ub.points_earned
            }
            for ub in recent_badges
        ],
        "upcoming_deadlines": [
            {
                "challenge_title": p.challenge.title,
                "end_date": p.challenge.end_date,
                "progress_percentage": p.progress_percentage
            }
            for p in upcoming_deadlines
        ]
    }

# Peer Support Groups
@router.post("/support-groups")
async def create_support_group(
    group_data: CreateSupportGroupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new peer support group"""
    try:
        group = await dev_service.create_support_group(
            db=db,
            creator=current_user,
            name=group_data.name,
            description=group_data.description,
            focus_category=group_data.focus_category,
            group_type=group_data.group_type,
            max_members=group_data.max_members
        )
        
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "focus_category": group.focus_category.value if group.focus_category else None,
            "current_members": group.current_members,
            "max_members": group.max_members,
            "message": "Support group created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating support group: {e}")
        raise HTTPException(status_code=500, detail="Failed to create support group")

@router.get("/support-groups")
async def get_support_groups(
    focus_category: Optional[DevelopmentCategory] = Query(None),
    group_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available support groups"""
    query = db.query(PeerSupportGroup).filter(
        PeerSupportGroup.current_members < PeerSupportGroup.max_members
    )
    
    if focus_category:
        query = query.filter(PeerSupportGroup.focus_category == focus_category)
    
    if group_type:
        query = query.filter(PeerSupportGroup.group_type == group_type)
    
    groups = query.order_by(PeerSupportGroup.created_at.desc()).all()
    
    # Filter out groups user is already in
    user_group_ids = [m.group_id for m in current_user.group_memberships if m.status == "active"]
    available_groups = [g for g in groups if g.id not in user_group_ids]
    
    return [
        {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "focus_category": group.focus_category.value if group.focus_category else None,
            "group_type": group.group_type,
            "current_members": group.current_members,
            "max_members": group.max_members,
            "requires_approval": group.requires_approval,
            "created_at": group.created_at
        }
        for group in available_groups
    ]

# Feedback System
@router.post("/feedback/request")
async def request_feedback(
    feedback_data: RequestFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request anonymous feedback from community"""
    try:
        request = await dev_service.request_feedback(
            db=db,
            user=current_user,
            feedback_type=feedback_data.feedback_type,
            description=feedback_data.description,
            specific_area=feedback_data.specific_area,
            feedback_from_women=feedback_data.feedback_from_women,
            feedback_from_men=feedback_data.feedback_from_men
        )
        
        return {
            "id": request.id,
            "feedback_type": request.feedback_type,
            "expires_at": request.expires_at,
            "max_responses": request.max_responses,
            "message": "Feedback request created successfully"
        }
    except Exception as e:
        logger.error(f"Error requesting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to request feedback")

@router.get("/feedback/my-requests")
async def get_my_feedback_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's feedback requests and responses"""
    requests = db.query(FeedbackRequest).filter(
        FeedbackRequest.requesting_user_id == current_user.id
    ).order_by(FeedbackRequest.created_at.desc()).all()
    
    return [
        {
            "id": request.id,
            "feedback_type": request.feedback_type,
            "description": request.description,
            "responses_received": request.responses_received,
            "max_responses": request.max_responses,
            "expires_at": request.expires_at,
            "is_active": request.is_active,
            "created_at": request.created_at,
            "responses": [
                {
                    "overall_rating": response.overall_rating,
                    "specific_feedback": response.specific_feedback,
                    "suggestions": response.suggestions,
                    "positive_aspects": response.positive_aspects,
                    "improvement_areas": response.improvement_areas,
                    "created_at": response.created_at
                }
                for response in request.feedback_responses
            ]
        }
        for request in requests
    ]

@router.get("/feedback/opportunities")
async def get_feedback_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback opportunities for user to help others"""
    
    # Get feedback requests user can respond to
    query = db.query(FeedbackRequest).filter(
        FeedbackRequest.requesting_user_id != current_user.id,
        FeedbackRequest.is_active == True,
        FeedbackRequest.expires_at > datetime.utcnow(),
        FeedbackRequest.responses_received < FeedbackRequest.max_responses
    )
    
    # Filter by gender preferences if specified
    user_gender = current_user.profile.gender.value if current_user.profile else None
    if user_gender:
        if user_gender == "female":
            query = query.filter(FeedbackRequest.feedback_from_women == True)
        elif user_gender == "male":
            query = query.filter(FeedbackRequest.feedback_from_men == True)
    
    opportunities = query.order_by(FeedbackRequest.created_at.desc()).limit(10).all()
    
    # Filter out requests user has already responded to
    user_response_request_ids = [r.request_id for r in current_user.feedback_responses]
    available_opportunities = [o for o in opportunities if o.id not in user_response_request_ids]
    
    return [
        {
            "id": opportunity.id,
            "feedback_type": opportunity.feedback_type,
            "description": opportunity.description,
            "specific_area": opportunity.specific_area,
            "responses_received": opportunity.responses_received,
            "max_responses": opportunity.max_responses,
            "expires_at": opportunity.expires_at
        }
        for opportunity in available_opportunities
    ]