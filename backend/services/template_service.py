# -*- coding: utf-8 -*-
"""
Template Service for Catalyst
Provides message template management and rendering functionality
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
from pydantic import ValidationError

# Import schema models
from schemas.template_schema import (
    TemplateCategory,
    TemplateContext,
    TemplateUsageStatus,
    TemplateVariable,
    Template,
    TemplateUsage,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateSearchRequest,
    TemplateSearchResponse,
    TemplateRenderRequest,
    TemplateRenderResponse
)

logger = logging.getLogger(__name__)


class TemplateService:
    """
    Main template service that provides message template management,
    rendering, and usage tracking.
    """

    def __init__(self):
        """Initialize the template service with a library of default templates."""
        self._templates = self._initialize_template_library()
        # Dictionary to store template usage records by ID
        self._template_usages = {}

    def _initialize_template_library(self) -> Dict[str, Template]:
        """
        Initialize a library of default templates.

        Returns:
            Dict[str, Template]: Dictionary of templates keyed by ID
        """
        templates = {}

        # Add greeting templates
        templates.update(self._create_greeting_templates())

        # Add follow-up templates
        templates.update(self._create_follow_up_templates())

        # Add closing templates
        templates.update(self._create_closing_templates())

        # Add question templates
        templates.update(self._create_question_templates())

        # Add clarification templates
        templates.update(self._create_clarification_templates())

        # Add feedback templates
        templates.update(self._create_feedback_templates())

        # Add status update templates
        templates.update(self._create_status_update_templates())

        # Add introduction templates
        templates.update(self._create_introduction_templates())

        # Add thank you templates
        templates.update(self._create_thank_you_templates())

        # Add apology templates
        templates.update(self._create_apology_templates())

        # Add request templates
        templates.update(self._create_request_templates())

        # Add reminder templates
        templates.update(self._create_reminder_templates())

        return templates

    def _create_greeting_templates(self) -> Dict[str, Template]:
        """Create greeting templates."""
        templates = {}

        # Professional greeting
        greeting_id = str(uuid.uuid4())
        templates[greeting_id] = Template(
            id=greeting_id,
            title="Professional Greeting",
            description="A formal greeting for professional communication",
            content="Dear {recipient_name},\n\nI hope this message finds you well.",
            category=TemplateCategory.GREETING,
            contexts=[TemplateContext.PROFESSIONAL, TemplateContext.GENERAL],
            variables=[
                TemplateVariable(
                    name="recipient_name",
                    description="Name of the recipient",
                    default_value="Valued Client",
                    required=True,
                    example="Mr. Smith"
                )
            ],
            tags=["formal", "professional", "greeting"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_default=True,
            usage_count=0,
            status=TemplateUsageStatus.ACTIVE
        )

        # Casual greeting
        casual_greeting_id = str(uuid.uuid4())
        templates[casual_greeting_id] = Template(
            id=casual_greeting_id,
            title="Casual Greeting",
            description="A friendly greeting for casual communication",
            content="Hi {recipient_name}!\n\nHope you're doing great today.",
            category=TemplateCategory.GREETING,
            contexts=[TemplateContext.CASUAL, TemplateContext.GENERAL],
            variables=[
                TemplateVariable(
                    name="recipient_name",
                    description="Name of the recipient",
                    default_value="there",
                    required=True,
                    example="John"
                )
            ],
            tags=["casual", "friendly", "greeting"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_default=True,
            usage_count=0,
            status=TemplateUsageStatus.ACTIVE
        )

        return templates

    def _create_follow_up_templates(self) -> Dict[str, Template]:
        """Create follow-up templates."""
        templates = {}

        # Professional follow-up
        follow_up_id = str(uuid.uuid4())
        templates[follow_up_id] = Template(
            id=follow_up_id,
            title="Professional Follow-up",
            description="A formal follow-up for professional communication",
            content="Dear {recipient_name},\n\nI'm writing to follow up on our {previous_topic} from {previous_date}. {specific_question}\n\nLooking forward to your response.\n\nBest regards,\n{sender_name}",
            category=TemplateCategory.FOLLOW_UP,
            contexts=[TemplateContext.PROFESSIONAL, TemplateContext.GENERAL],
            variables=[
                TemplateVariable(
                    name="recipient_name",
                    description="Name of the recipient",
                    default_value="Valued Client",
                    required=True,
                    example="Mr. Smith"
                ),
                TemplateVariable(
                    name="previous_topic",
                    description="Topic of the previous communication",
                    default_value="discussion",
                    required=True,
                    example="project proposal"
                ),
                TemplateVariable(
                    name="previous_date",
                    description="Date of the previous communication",
                    default_value="our last correspondence",
                    required=True,
                    example="May 15th"
                ),
                TemplateVariable(
                    name="specific_question",
                    description="Specific question or request",
                    default_value="I was wondering if you've had a chance to review the information I sent.",
                    required=True,
                    example="Have you had a chance to review the proposal I sent?"
                ),
                TemplateVariable(
                    name="sender_name",
                    description="Name of the sender",
                    default_value="",
                    required=True,
                    example="Jane Doe"
                )
            ],
            tags=["follow-up", "professional", "reminder"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_default=True,
            usage_count=0,
            status=TemplateUsageStatus.ACTIVE
        )

        return templates

    def _create_closing_templates(self) -> Dict[str, Template]:
        """Create closing templates."""
        return {}

    def _create_question_templates(self) -> Dict[str, Template]:
        """Create question templates."""
        return {}

    def _create_clarification_templates(self) -> Dict[str, Template]:
        """Create clarification templates."""
        return {}

    def _create_feedback_templates(self) -> Dict[str, Template]:
        """Create feedback templates."""
        return {}

    def _create_status_update_templates(self) -> Dict[str, Template]:
        """Create status update templates."""
        return {}

    def _create_introduction_templates(self) -> Dict[str, Template]:
        """Create introduction templates."""
        return {}

    def _create_thank_you_templates(self) -> Dict[str, Template]:
        """Create thank you templates."""
        return {}

    def _create_apology_templates(self) -> Dict[str, Template]:
        """Create apology templates."""
        return {}

    def _create_request_templates(self) -> Dict[str, Template]:
        """Create request templates."""
        return {}

    def _create_reminder_templates(self) -> Dict[str, Template]:
        """Create reminder templates."""
        return {}

    def get_template_by_id(self, template_id: str) -> Optional[Template]:
        """Get a specific template by ID."""
        return self._templates.get(template_id)

    def get_templates_by_category(self, category: Union[TemplateCategory, str]) -> List[Template]:
        """Get templates filtered by category."""
        # Convert category string to enum if needed
        if isinstance(category, str):
            try:
                category_enum = TemplateCategory(category)
            except ValueError:
                category_enum = None
                logger.warning(f"Invalid category: {category}")
        else:
            category_enum = category

        if not category_enum:
            return []

        return [
            template for template in self._templates.values()
            if template.category == category_enum
        ]

    def get_templates_by_context(self, context: Union[TemplateContext, str]) -> List[Template]:
        """Get templates filtered by context."""
        # Convert context string to enum if needed
        if isinstance(context, str):
            try:
                context_enum = TemplateContext(context)
            except ValueError:
                context_enum = None
                logger.warning(f"Invalid context: {context}")
        else:
            context_enum = context

        if not context_enum:
            return []

        return [
            template for template in self._templates.values()
            if context_enum in template.contexts
        ]

    def search_templates(self, request: TemplateSearchRequest) -> TemplateSearchResponse:
        """Search templates based on various criteria."""
        try:
            # Start with all templates
            matching_templates = list(self._templates.values())

            # Filter by query if provided
            if request.query:
                query_lower = request.query.lower()
                matching_templates = [
                    template for template in matching_templates
                    if query_lower in template.title.lower() or
                    query_lower in template.description.lower() or
                    query_lower in template.content.lower()
                ]

            # Filter by categories if provided
            if request.categories:
                matching_templates = [
                    template for template in matching_templates
                    if template.category in request.categories
                ]

            # Filter by contexts if provided
            if request.contexts:
                matching_templates = [
                    template for template in matching_templates
                    if any(context in template.contexts for context in request.contexts)
                ]

            # Filter by tags if provided
            if request.tags:
                matching_templates = [
                    template for template in matching_templates
                    if any(tag in template.tags for tag in request.tags)
                ]

            # Filter by creator if provided
            if request.created_by:
                matching_templates = [
                    template for template in matching_templates
                    if template.created_by == request.created_by
                ]

            # Filter by status if provided
            if request.status:
                matching_templates = [
                    template for template in matching_templates
                    if template.status == request.status
                ]

            # Filter by default status if provided
            if request.is_default is not None:
                matching_templates = [
                    template for template in matching_templates
                    if template.is_default == request.is_default
                ]

            # Filter by minimum rating if provided
            if request.min_rating is not None:
                matching_templates = [
                    template for template in matching_templates
                    if template.rating is not None and template.rating >= request.min_rating
                ]

            # Calculate total count
            total_count = len(matching_templates)

            # Apply pagination
            page = getattr(request, 'page', 1)
            page_size = getattr(request, 'page_size', 20)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_templates = matching_templates[start_idx:end_idx]

            # Prepare search metadata
            search_metadata = {
                "query": request.query,
                "filters_applied": {
                    "categories": [cat.value for cat in request.categories] if request.categories else None,
                    "contexts": [ctx.value for ctx in request.contexts] if request.contexts else None,
                    "tags": request.tags,
                    "created_by": request.created_by,
                    "status": request.status.value if request.status else None,
                    "is_default": request.is_default,
                    "min_rating": request.min_rating
                }
            }

            return TemplateSearchResponse(
                templates=paginated_templates,
                total_count=total_count,
                page=page,
                page_size=page_size,
                search_metadata=search_metadata
            )

        except Exception as e:
            logger.error(f"Error searching templates: {str(e)}")
            return TemplateSearchResponse(
                templates=[],
                total_count=0,
                page=1,
                page_size=20,
                search_metadata={"error": f"Failed to search templates: {str(e)}"}
            )

    def create_template(self, request: TemplateCreateRequest, user_id: Optional[str] = None) -> Template:
        """Create a new template."""
        try:
            template_id = str(uuid.uuid4())
            now = datetime.now()

            template = Template(
                id=template_id,
                title=request.title,
                content=request.content,
                description=request.description,
                category=request.category,
                contexts=request.contexts,
                variables=request.variables,
                tags=request.tags,
                created_at=now,
                updated_at=now,
                created_by=user_id,
                is_default=request.is_default,
                usage_count=0,
                status=TemplateUsageStatus.ACTIVE
            )

            # Add to templates dictionary
            self._templates[template_id] = template

            return template

        except ValidationError as e:
            logger.error(f"Validation error creating template: {str(e)}")
            raise ValueError(f"Invalid template data: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            raise ValueError(f"Failed to create template: {str(e)}")

    def update_template(self, template_id: str, request: TemplateUpdateRequest) -> Optional[Template]:
        """Update an existing template."""
        try:
            template = self._templates.get(template_id)
            if not template:
                logger.warning(f"Template not found: {template_id}")
                return None

            # Update fields if provided
            if request.title is not None:
                template.title = request.title
            if request.content is not None:
                template.content = request.content
            if request.description is not None:
                template.description = request.description
            if request.category is not None:
                template.category = request.category
            if request.contexts is not None:
                template.contexts = request.contexts
            if request.variables is not None:
                template.variables = request.variables
            if request.tags is not None:
                template.tags = request.tags
            if request.status is not None:
                template.status = request.status

            # Update the updated_at timestamp
            template.updated_at = datetime.now()

            return template

        except ValidationError as e:
            logger.error(f"Validation error updating template: {str(e)}")
            raise ValueError(f"Invalid template data: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating template: {str(e)}")
            raise ValueError(f"Failed to update template: {str(e)}")

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        try:
            if template_id in self._templates:
                del self._templates[template_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting template: {str(e)}")
            return False

    def render_template(self, request: TemplateRenderRequest) -> TemplateRenderResponse:
        """Render a template with provided variables."""
        try:
            template = self._templates.get(request.template_id)
            if not template:
                raise ValueError(f"Template not found: {request.template_id}")

            # Get the template content
            content = template.content

            # Track missing variables
            missing_variables = []

            # Replace variables in the content
            for variable in template.variables:
                placeholder = f"{{{variable.name}}}"
                if variable.name in request.variables:
                    value = request.variables[variable.name]
                    content = content.replace(placeholder, value)
                elif variable.default_value is not None:
                    content = content.replace(placeholder, variable.default_value)
                    if variable.required:
                        missing_variables.append(variable.name)
                else:
                    # Leave placeholder if no value or default
                    if variable.required:
                        missing_variables.append(variable.name)

            # Create usage record
            usage_id = str(uuid.uuid4())
            usage = TemplateUsage(
                id=usage_id,
                template_id=request.template_id,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                used_at=datetime.now(),
                variables_used=request.variables,
                context_data={}
            )

            # Store usage record
            self._template_usages[usage_id] = usage

            # Increment usage count for the template
            template.usage_count += 1

            # Prepare template metadata
            template_metadata = {
                "title": template.title,
                "category": template.category.value,
                "contexts": [ctx.value for ctx in template.contexts],
                "is_default": template.is_default
            }

            return TemplateRenderResponse(
                rendered_content=content,
                template_id=request.template_id,
                usage_id=usage_id,
                missing_variables=missing_variables,
                template_metadata=template_metadata
            )

        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            raise ValueError(f"Failed to render template: {str(e)}")

    def update_template_usage(self, usage_id: str, message_id: Optional[str] = None,
                             modified_content: Optional[str] = None,
                             effectiveness_rating: Optional[int] = None) -> bool:
        """Update a template usage record with additional information."""
        try:
            usage = self._template_usages.get(usage_id)
            if not usage:
                logger.warning(f"Template usage not found: {usage_id}")
                return False

            # Update fields if provided
            if message_id is not None:
                usage.message_id = message_id
            if modified_content is not None:
                usage.modified_content = modified_content
            if effectiveness_rating is not None:
                usage.effectiveness_rating = effectiveness_rating

            return True

        except Exception as e:
            logger.error(f"Error updating template usage: {str(e)}")
            return False

    def get_template_usage_stats(self, template_id: Optional[str] = None,
                               user_id: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get usage statistics for templates."""
        try:
            # Filter usages based on criteria
            filtered_usages = self._template_usages.values()

            if template_id:
                filtered_usages = [u for u in filtered_usages if u.template_id == template_id]
            if user_id:
                filtered_usages = [u for u in filtered_usages if u.user_id == user_id]
            if start_date:
                filtered_usages = [u for u in filtered_usages if u.used_at >= start_date]
            if end_date:
                filtered_usages = [u for u in filtered_usages if u.used_at <= end_date]

            # Calculate statistics
            total_usages = len(filtered_usages)
            templates_used = set(u.template_id for u in filtered_usages)
            users = set(u.user_id for u in filtered_usages)

            # Calculate average effectiveness rating
            ratings = [u.effectiveness_rating for u in filtered_usages if u.effectiveness_rating is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else None

            # Calculate modification rate
            modified_count = sum(1 for u in filtered_usages if u.modified_content is not None)
            modification_rate = modified_count / total_usages if total_usages > 0 else 0

            # Get most used templates
            template_usage_counts = {}
            for usage in filtered_usages:
                template_usage_counts[usage.template_id] = template_usage_counts.get(usage.template_id, 0) + 1

            most_used_templates = sorted(
                template_usage_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            return {
                "total_usages": total_usages,
                "unique_templates_used": len(templates_used),
                "unique_users": len(users),
                "average_effectiveness_rating": avg_rating,
                "modification_rate": modification_rate,
                "most_used_templates": [
                    {
                        "template_id": t_id,
                        "template_title": self._templates.get(t_id).title if self._templates.get(t_id) else "Unknown",
                        "usage_count": count
                    }
                    for t_id, count in most_used_templates
                ]
            }

        except Exception as e:
            logger.error(f"Error getting template usage stats: {str(e)}")
            return {"error": f"Failed to get template usage stats: {str(e)}"}


# Create a singleton instance
template_service = TemplateService()


def get_available_categories() -> List[Dict[str, str]]:
    """Get a list of all available template categories."""
    return [
        {"id": category.value, "name": category.name.replace('_', ' ').title()}
        for category in TemplateCategory
    ]


def get_available_contexts() -> List[Dict[str, str]]:
    """Get a list of all available template contexts."""
    return [
        {"id": context.value, "name": context.name.replace('_', ' ').title()}
        for context in TemplateContext
    ]


def get_template_recommendations(user_id: str, context: Optional[str] = None,
                               category: Optional[str] = None) -> List[Template]:
    """Get personalized template recommendations for a user."""
    try:
        # Start with all active templates
        templates = [t for t in template_service._templates.values()
                    if t.status == TemplateUsageStatus.ACTIVE]

        # Filter by context if provided
        if context:
            try:
                context_enum = TemplateContext(context)
                templates = [t for t in templates if context_enum in t.contexts]
            except ValueError:
                pass

        # Filter by category if provided
        if category:
            try:
                category_enum = TemplateCategory(category)
                templates = [t for t in templates if t.category == category_enum]
            except ValueError:
                pass

        # Get user's previous template usages
        user_usages = [u for u in template_service._template_usages.values()
                      if u.user_id == user_id]

        # Calculate template scores based on usage and ratings
        template_scores = {}
        for template in templates:
            # Base score - higher for default templates
            score = 5 if template.is_default else 3

            # Add points for usage count (max 5 points)
            score += min(template.usage_count / 10, 5)

            # Add points for rating (max 5 points)
            if template.rating is not None:
                score += template.rating

            # Add points for user's previous usage of this template
            user_template_usages = [u for u in user_usages if u.template_id == template.id]
            if user_template_usages:
                score += 3

                # Add points for good ratings from this user
                user_ratings = [u.effectiveness_rating for u in user_template_usages
                              if u.effectiveness_rating is not None]
                if user_ratings:
                    avg_user_rating = sum(user_ratings) / len(user_ratings)
                    score += avg_user_rating

            template_scores[template.id] = score

        # Sort templates by score and return top 10
        sorted_templates = sorted(
            templates,
            key=lambda t: template_scores.get(t.id, 0),
            reverse=True
        )[:10]

        return sorted_templates

    except Exception as e:
        logger.error(f"Error getting template recommendations: {str(e)}")
        return []