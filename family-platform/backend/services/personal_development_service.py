from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import logging
from models.personal_development import (
    PersonalDevelopmentGoal, SkillChallenge, ChallengeParticipation,
    MentorshipPair, AchievementBadge, UserBadge, PeerSupportGroup,
    GroupMembership, FeedbackRequest, FeedbackResponse,
    DevelopmentCategory, GoalDifficulty, AchievementStatus, MentorshipStatus
)
from models.user import User
from services.notification_service import NotificationService
from services.ai_service import AIService
import random

logger = logging.getLogger(__name__)

class PersonalDevelopmentService:
    """Service for managing personal development features"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.ai_service = AIService()
    
    # Goal Management
    async def create_development_goal(
        self, 
        db: Session, 
        user: User, 
        category: DevelopmentCategory,
        difficulty: GoalDifficulty,
        title: str,
        description: str,
        target_description: str,
        target_date: datetime,
        target_value: Optional[float] = None,
        unit: Optional[str] = None
    ) -> PersonalDevelopmentGoal:
        """Create a new personal development goal"""
        
        goal = PersonalDevelopmentGoal(
            user_id=user.id,
            category=category,
            difficulty=difficulty,
            title=title,
            description=description,
            target_description=target_description,
            target_date=target_date,
            target_value=target_value,
            unit=unit,
            status=AchievementStatus.NOT_STARTED
        )
        
        db.add(goal)
        db.commit()
        db.refresh(goal)
        
        # Create suggested challenges based on goal
        await self._suggest_related_challenges(db, goal)
        
        logger.info(f"Created development goal for user {user.id}: {title}")
        return goal
    
    async def update_goal_progress(
        self,
        db: Session,
        goal: PersonalDevelopmentGoal,
        progress_description: str,
        current_value: Optional[float] = None,
        photos: List[str] = None
    ) -> PersonalDevelopmentGoal:
        """Update progress on a development goal"""
        
        goal.add_progress_update(progress_description, photos, current_value)
        
        if goal.status == AchievementStatus.NOT_STARTED:
            goal.status = AchievementStatus.IN_PROGRESS
        
        # Check if goal is completed
        if goal.progress_percentage >= 100:
            goal.status = AchievementStatus.COMPLETED
            goal.completed_date = datetime.utcnow()
            await self._award_goal_completion(db, goal)
        
        db.commit()
        db.refresh(goal)
        
        # Notify mentors and peer groups
        await self._notify_progress_update(db, goal, progress_description)
        
        return goal
    
    async def get_recommended_goals(
        self, 
        db: Session, 
        user: User, 
        category: Optional[DevelopmentCategory] = None
    ) -> List[Dict]:
        """Get AI-recommended goals based on user profile and progress"""
        
        user_expertise = user.get_category_expertise()
        current_goals = [goal.category for goal in user.development_goals 
                        if goal.status in [AchievementStatus.NOT_STARTED, AchievementStatus.IN_PROGRESS]]
        
        recommendations = []
        
        # Beginner recommendations
        beginner_goals = {
            DevelopmentCategory.FITNESS: [
                {
                    "title": "Daily 20-Minute Walks",
                    "description": "Build a consistent walking habit",
                    "target": "Walk 20 minutes daily for 30 days",
                    "points": 100
                },
                {
                    "title": "Basic Push-up Progression", 
                    "description": "Build upper body strength",
                    "target": "Complete 10 proper push-ups",
                    "points": 150
                }
            ],
            DevelopmentCategory.PRACTICAL_SKILLS: [
                {
                    "title": "Learn Basic Cooking",
                    "description": "Master 5 healthy meals",
                    "target": "Cook 5 different healthy meals from scratch",
                    "points": 200
                },
                {
                    "title": "Home Organization System",
                    "description": "Create an organized living space",
                    "target": "Organize and maintain tidy home for 2 weeks",
                    "points": 150
                }
            ],
            DevelopmentCategory.SOCIAL: [
                {
                    "title": "Conversation Skills Practice",
                    "description": "Improve social confidence",
                    "target": "Have meaningful conversations with 10 new people",
                    "points": 200
                },
                {
                    "title": "Active Listening Development",
                    "description": "Become a better listener",
                    "target": "Practice active listening techniques daily for 2 weeks",
                    "points": 150
                }
            ],
            DevelopmentCategory.FINANCIAL: [
                {
                    "title": "Budget Creation and Tracking",
                    "description": "Take control of finances",
                    "target": "Create and stick to budget for 2 months",
                    "points": 250
                },
                {
                    "title": "Emergency Fund Start",
                    "description": "Build financial security",
                    "target": "Save $500 emergency fund",
                    "points": 300
                }
            ]
        }
        
        # Get recommendations based on expertise level
        for cat, level in user_expertise.items():
            category_enum = DevelopmentCategory(cat)
            
            if category and category != category_enum:
                continue
                
            if category_enum not in current_goals:
                if level == "beginner" and category_enum in beginner_goals:
                    recommendations.extend(beginner_goals[category_enum])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    # Challenge System
    async def create_skill_challenge(
        self,
        db: Session,
        category: DevelopmentCategory,
        difficulty: GoalDifficulty,
        title: str,
        description: str,
        instructions: str,
        success_criteria: Dict,
        required_evidence: List[str],
        start_date: datetime,
        end_date: datetime,
        base_points: int,
        max_participants: Optional[int] = None
    ) -> SkillChallenge:
        """Create a new skill challenge"""
        
        challenge = SkillChallenge(
            category=category,
            difficulty=difficulty,
            title=title,
            description=description,
            instructions=instructions,
            success_criteria=success_criteria,
            required_evidence=required_evidence,
            start_date=start_date,
            end_date=end_date,
            base_points=base_points,
            max_participants=max_participants
        )
        
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        
        # Notify relevant users about new challenge
        await self._notify_new_challenge(db, challenge)
        
        return challenge
    
    async def join_challenge(
        self,
        db: Session,
        user: User,
        challenge: SkillChallenge
    ) -> ChallengeParticipation:
        """Have user join a skill challenge"""
        
        if not challenge.can_participate(user):
            raise ValueError("User cannot participate in this challenge")
        
        participation = ChallengeParticipation(
            user_id=user.id,
            challenge_id=challenge.id,
            status=AchievementStatus.IN_PROGRESS
        )
        
        db.add(participation)
        challenge.current_participants += 1
        
        db.commit()
        db.refresh(participation)
        
        logger.info(f"User {user.id} joined challenge {challenge.id}")
        return participation
    
    async def submit_challenge_completion(
        self,
        db: Session,
        participation: ChallengeParticipation,
        submission_text: str,
        photos: List[str] = None,
        videos: List[str] = None
    ) -> ChallengeParticipation:
        """Submit challenge completion for review"""
        
        participation.submission_text = submission_text
        participation.submission_photos = photos or []
        participation.submission_videos = videos or []
        participation.status = AchievementStatus.COMPLETED
        participation.completed_date = datetime.utcnow()
        
        # Auto-award points for effort (subject to review)
        participation.points_earned = participation.challenge.base_points
        
        db.commit()
        db.refresh(participation)
        
        # Queue for admin review
        await self._queue_challenge_review(db, participation)
        
        return participation
    
    async def get_active_challenges(
        self, 
        db: Session,
        category: Optional[DevelopmentCategory] = None,
        difficulty: Optional[GoalDifficulty] = None,
        user: Optional[User] = None
    ) -> List[SkillChallenge]:
        """Get currently active challenges"""
        
        query = db.query(SkillChallenge).filter(
            SkillChallenge.is_active == True,
            SkillChallenge.start_date <= datetime.utcnow(),
            SkillChallenge.end_date >= datetime.utcnow()
        )
        
        if category:
            query = query.filter(SkillChallenge.category == category)
        
        if difficulty:
            query = query.filter(SkillChallenge.difficulty == difficulty)
        
        challenges = query.order_by(SkillChallenge.start_date.desc()).all()
        
        # Filter out challenges user is already participating in
        if user:
            user_challenge_ids = [p.challenge_id for p in user.challenge_participations]
            challenges = [c for c in challenges if c.id not in user_challenge_ids]
        
        return challenges
    
    # Mentorship System
    async def request_mentor(
        self,
        db: Session,
        mentee: User,
        focus_areas: List[str],
        goals: str,
        preferred_communication: str = "video"
    ) -> MentorshipPair:
        """Request mentorship matching"""
        
        # Find suitable mentors
        potential_mentors = await self._find_suitable_mentors(db, mentee, focus_areas)
        
        if not potential_mentors:
            raise ValueError("No suitable mentors available")
        
        # For now, pick the best match (in production, would use more sophisticated matching)
        mentor = potential_mentors[0]
        
        mentorship = MentorshipPair(
            mentor_id=mentor.id,
            mentee_id=mentee.id,
            focus_areas=focus_areas,
            goals=goals,
            preferred_communication=preferred_communication,
            status=MentorshipStatus.PENDING
        )
        
        db.add(mentorship)
        db.commit()
        db.refresh(mentorship)
        
        # Notify mentor of request
        await self.notification_service.send_notification(
            mentor.id,
            "mentorship_request",
            f"New mentorship request from {mentee.profile.first_name}",
            f"Someone wants you as a mentor for: {', '.join(focus_areas)}"
        )
        
        return mentorship
    
    async def accept_mentorship(
        self,
        db: Session,
        mentorship: MentorshipPair
    ) -> MentorshipPair:
        """Accept a mentorship request"""
        
        mentorship.status = MentorshipStatus.ACTIVE
        mentorship.started_date = datetime.utcnow()
        
        db.commit()
        db.refresh(mentorship)
        
        # Notify mentee
        await self.notification_service.send_notification(
            mentorship.mentee_id,
            "mentorship_accepted",
            "Mentorship request accepted!",
            f"Your mentor is ready to start working with you"
        )
        
        return mentorship
    
    # Gamification System
    async def check_and_award_badges(
        self,
        db: Session,
        user: User
    ) -> List[AchievementBadge]:
        """Check and award any badges user has earned"""
        
        earned_badges = []
        user_badge_ids = [ub.badge_id for ub in user.badges]
        
        # Get all available badges user hasn't earned
        available_badges = db.query(AchievementBadge).filter(
            AchievementBadge.is_active == True,
            ~AchievementBadge.id.in_(user_badge_ids)
        ).all()
        
        for badge in available_badges:
            if await self._check_badge_requirements(db, user, badge):
                user_badge = UserBadge(
                    user_id=user.id,
                    badge_id=badge.id,
                    points_earned=badge.points_reward
                )
                
                db.add(user_badge)
                badge.total_earned += 1
                earned_badges.append(badge)
        
        if earned_badges:
            db.commit()
            
            # Notify user of new badges
            for badge in earned_badges:
                await self.notification_service.send_notification(
                    user.id,
                    "badge_earned",
                    f"New badge earned: {badge.name}!",
                    badge.description
                )
        
        return earned_badges
    
    # Peer Support Groups
    async def create_support_group(
        self,
        db: Session,
        creator: User,
        name: str,
        description: str,
        focus_category: Optional[DevelopmentCategory] = None,
        group_type: str = "mixed",
        max_members: int = 8
    ) -> PeerSupportGroup:
        """Create a new peer support group"""
        
        group = PeerSupportGroup(
            name=name,
            description=description,
            focus_category=focus_category,
            group_type=group_type,
            max_members=max_members,
            created_by_id=creator.id,
            current_members=1
        )
        
        db.add(group)
        db.flush()  # Get the ID
        
        # Add creator as first member
        membership = GroupMembership(
            user_id=creator.id,
            group_id=group.id,
            role="leader"
        )
        
        db.add(membership)
        db.commit()
        db.refresh(group)
        
        return group
    
    async def join_support_group(
        self,
        db: Session,
        user: User,
        group: PeerSupportGroup
    ) -> GroupMembership:
        """Join a peer support group"""
        
        if group.current_members >= group.max_members:
            raise ValueError("Group is full")
        
        # Check if user is already a member
        existing = db.query(GroupMembership).filter(
            GroupMembership.user_id == user.id,
            GroupMembership.group_id == group.id,
            GroupMembership.status == "active"
        ).first()
        
        if existing:
            raise ValueError("User is already a member")
        
        membership = GroupMembership(
            user_id=user.id,
            group_id=group.id,
            status="pending" if group.requires_approval else "active"
        )
        
        db.add(membership)
        
        if not group.requires_approval:
            group.current_members += 1
        
        db.commit()
        db.refresh(membership)
        
        return membership
    
    # Feedback System
    async def request_feedback(
        self,
        db: Session,
        user: User,
        feedback_type: str,
        description: str,
        specific_area: Optional[str] = None,
        feedback_from_women: bool = True,
        feedback_from_men: bool = True
    ) -> FeedbackRequest:
        """Request anonymous feedback from community"""
        
        # Create snapshot of current profile
        profile_data = {
            "bio": user.profile.bio if user.profile else None,
            "family_vision": user.profile.family_vision if user.profile else None,
            "interests": user.profile.interests if user.profile else None,
            "photos_count": len([p for p in user.photos if p.is_approved()])
        }
        
        request = FeedbackRequest(
            requesting_user_id=user.id,
            feedback_type=feedback_type,
            specific_area=specific_area,
            description=description,
            profile_snapshot=profile_data,
            feedback_from_women=feedback_from_women,
            feedback_from_men=feedback_from_men,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.add(request)
        db.commit()
        db.refresh(request)
        
        # Notify eligible users about feedback opportunity
        await self._notify_feedback_opportunity(db, request)
        
        return request
    
    async def provide_feedback(
        self,
        db: Session,
        responder: User,
        request: FeedbackRequest,
        overall_rating: int,
        specific_feedback: str,
        suggestions: str = None,
        positive_aspects: List[str] = None,
        improvement_areas: List[str] = None
    ) -> FeedbackResponse:
        """Provide feedback response"""
        
        if request.responses_received >= request.max_responses:
            raise ValueError("Feedback request is full")
        
        if not request.is_active or request.expires_at < datetime.utcnow():
            raise ValueError("Feedback request is no longer active")
        
        response = FeedbackResponse(
            request_id=request.id,
            responding_user_id=responder.id,
            overall_rating=overall_rating,
            specific_feedback=specific_feedback,
            suggestions=suggestions,
            positive_aspects=positive_aspects or [],
            improvement_areas=improvement_areas or []
        )
        
        db.add(response)
        request.responses_received += 1
        
        db.commit()
        db.refresh(response)
        
        # Notify requester (anonymously)
        await self.notification_service.send_notification(
            request.requesting_user_id,
            "feedback_received",
            "New feedback received!",
            "Someone has provided feedback on your profile"
        )
        
        return response
    
    # Private Helper Methods
    async def _suggest_related_challenges(self, db: Session, goal: PersonalDevelopmentGoal):
        """Suggest challenges related to a goal"""
        # Find challenges in the same category
        related_challenges = db.query(SkillChallenge).filter(
            SkillChallenge.category == goal.category,
            SkillChallenge.is_active == True,
            SkillChallenge.end_date > datetime.utcnow()
        ).limit(3).all()
        
        if related_challenges:
            await self.notification_service.send_notification(
                goal.user_id,
                "challenges_suggested",
                "Challenges available for your goal!",
                f"We found {len(related_challenges)} challenges that can help with '{goal.title}'"
            )
    
    async def _award_goal_completion(self, db: Session, goal: PersonalDevelopmentGoal):
        """Award points and badges for goal completion"""
        
        # Award points based on difficulty
        points_map = {
            GoalDifficulty.BEGINNER: 100,
            GoalDifficulty.INTERMEDIATE: 250,
            GoalDifficulty.ADVANCED: 500,
            GoalDifficulty.EXPERT: 1000
        }
        
        goal.points_earned = points_map.get(goal.difficulty, 100)
        
        # Check for badge eligibility
        await self.check_and_award_badges(db, goal.user)
        
        # Notify user
        await self.notification_service.send_notification(
            goal.user_id,
            "goal_completed",
            f"Goal completed: {goal.title}!",
            f"Congratulations! You earned {goal.points_earned} points."
        )
    
    async def _find_suitable_mentors(
        self, 
        db: Session, 
        mentee: User, 
        focus_areas: List[str]
    ) -> List[User]:
        """Find suitable mentors for a mentee"""
        
        # Get users who can be mentors
        potential_mentors = db.query(User).filter(
            User.status == "active",
            User.warning_count == 0
        ).all()
        
        suitable_mentors = []
        for user in potential_mentors:
            if (user.can_be_mentor() and 
                user.get_mentorship_capacity() > 0 and
                user.id != mentee.id):
                
                # Check expertise in focus areas
                expertise = user.get_category_expertise()
                has_expertise = any(
                    expertise.get(area, "beginner") in ["advanced", "expert"]
                    for area in focus_areas
                )
                
                if has_expertise:
                    suitable_mentors.append(user)
        
        return suitable_mentors[:5]  # Return top 5 matches
    
    async def _check_badge_requirements(
        self, 
        db: Session, 
        user: User, 
        badge: AchievementBadge
    ) -> bool:
        """Check if user meets badge requirements"""
        
        requirements = badge.requirements
        
        # Check basic requirements
        if "completed_goals" in requirements:
            if user.get_completed_goals_count() < requirements["completed_goals"]:
                return False
        
        if "total_points" in requirements:
            if user.get_development_score() < requirements["total_points"]:
                return False
        
        if "challenges_completed" in requirements:
            completed_challenges = len([p for p in user.challenge_participations 
                                      if p.status == AchievementStatus.COMPLETED])
            if completed_challenges < requirements["challenges_completed"]:
                return False
        
        if "mentoring_sessions" in requirements:
            total_sessions = sum(m.total_sessions for m in user.mentoring_relationships)
            if total_sessions < requirements["mentoring_sessions"]:
                return False
        
        return True
    
    async def _notify_new_challenge(self, db: Session, challenge: SkillChallenge):
        """Notify relevant users about new challenge"""
        
        # Find users interested in this category
        interested_users = db.query(User).join(PersonalDevelopmentGoal).filter(
            PersonalDevelopmentGoal.category == challenge.category,
            PersonalDevelopmentGoal.status.in_([AchievementStatus.NOT_STARTED, AchievementStatus.IN_PROGRESS]),
            User.status == "active"
        ).distinct().limit(50).all()
        
        for user in interested_users:
            await self.notification_service.send_notification(
                user.id,
                "new_challenge",
                f"New {challenge.category.value} challenge available!",
                f"'{challenge.title}' - {challenge.description[:100]}..."
            )
    
    async def _queue_challenge_review(self, db: Session, participation: ChallengeParticipation):
        """Queue challenge submission for admin review"""
        # In a real system, this would add to an admin queue
        logger.info(f"Challenge submission queued for review: {participation.id}")
    
    async def _notify_progress_update(
        self, 
        db: Session, 
        goal: PersonalDevelopmentGoal, 
        description: str
    ):
        """Notify mentors and peer groups about progress"""
        
        # Notify mentors
        for mentorship in goal.user.mentee_relationships:
            if mentorship.status == MentorshipStatus.ACTIVE:
                await self.notification_service.send_notification(
                    mentorship.mentor_id,
                    "mentee_progress",
                    f"Progress update from {goal.user.profile.first_name}",
                    f"Goal: {goal.title} - {description}"
                )
    
    async def _notify_feedback_opportunity(self, db: Session, request: FeedbackRequest):
        """Notify eligible users about feedback opportunity"""
        
        # Find eligible users (verified, active, different gender if requested)
        query = db.query(User).filter(
            User.status == "active",
            User.is_email_verified == True,
            User.id != request.requesting_user_id
        )
        
        # Filter by gender preferences
        if request.feedback_from_women and not request.feedback_from_men:
            query = query.join(UserProfile).filter(UserProfile.gender == "female")
        elif request.feedback_from_men and not request.feedback_from_women:
            query = query.join(UserProfile).filter(UserProfile.gender == "male")
        
        eligible_users = query.limit(20).all()
        
        for user in eligible_users:
            await self.notification_service.send_notification(
                user.id,
                "feedback_opportunity",
                "Help a community member improve!",
                f"Someone needs feedback on their {request.feedback_type}"
            )