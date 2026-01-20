"""Pydantic models for structured output."""

from pydantic import BaseModel, Field


class SearchResultPost(BaseModel):
    """A post result from a search query."""

    id: int = Field(description="Unique post ID")
    topic_id: int = Field(description="ID of the topic this post belongs to")
    username: str = Field(description="Author's username")
    created_at: str = Field(description="When the post was created (ISO 8601)")
    blurb: str = Field(description="Snippet of the post content")
    topic_title: str = Field(default="", description="Title of the topic")
    url: str = Field(description="URL to the post")
    like_count: int = Field(default=0, description="Number of likes")


class SearchResults(BaseModel):
    """Results from a search query."""

    query: str = Field(description="The search query that was executed")
    total_posts: int = Field(description="Number of posts found")
    posts: list[SearchResultPost] = Field(description="List of matching posts")


class TopicPost(BaseModel):
    """A post within a topic."""

    id: int = Field(description="Unique post ID")
    post_number: int = Field(description="Position in the topic (1 = original post)")
    username: str = Field(description="Author's username")
    created_at: str = Field(description="When the post was created")
    content: str = Field(description="Post content (HTML stripped)")
    like_count: int = Field(default=0, description="Number of likes")
    is_accepted_answer: bool = Field(
        default=False, description="Whether this is the accepted answer"
    )


class TopicDetails(BaseModel):
    """Detailed information about a topic."""

    id: int = Field(description="Unique topic ID")
    title: str = Field(description="Topic title")
    slug: str = Field(description="URL-friendly slug")
    url: str = Field(description="Full URL to the topic")
    created_at: str = Field(description="When the topic was created")
    posts_count: int = Field(description="Total number of posts in the topic")
    views: int = Field(default=0, description="Number of views")
    like_count: int = Field(default=0, description="Total likes on the topic")
    has_accepted_answer: bool = Field(
        default=False, description="Whether the topic has an accepted answer"
    )
    category_name: str = Field(default="", description="Category name")
    tags: list[str] = Field(default_factory=list, description="Topic tags")
    posts: list[TopicPost] = Field(description="Posts in the topic")


class Category(BaseModel):
    """A forum category."""

    id: int = Field(description="Unique category ID")
    name: str = Field(description="Category name")
    slug: str = Field(description="URL-friendly slug")
    description: str = Field(default="", description="Category description")
    topic_count: int = Field(default=0, description="Number of topics in category")
    url: str = Field(description="URL to the category")
    subcategories: list[str] = Field(
        default_factory=list, description="Subcategory names"
    )


class CategoryList(BaseModel):
    """List of all forum categories."""

    categories: list[Category] = Field(description="All available categories")


class LatestTopic(BaseModel):
    """A topic from the latest topics list."""

    id: int = Field(description="Unique topic ID")
    title: str = Field(description="Topic title")
    url: str = Field(description="Full URL to the topic")
    created_at: str = Field(description="When the topic was created")
    last_posted_at: str = Field(default="", description="When the last post was made")
    posts_count: int = Field(default=1, description="Number of posts")
    views: int = Field(default=0, description="Number of views")
    like_count: int = Field(default=0, description="Total likes")
    has_accepted_answer: bool = Field(default=False, description="Has accepted answer")
    category_name: str = Field(default="", description="Category name")
    excerpt: str = Field(default="", description="Short excerpt of the topic")


class LatestTopics(BaseModel):
    """List of latest topics."""

    topics: list[LatestTopic] = Field(description="Latest topics from the forum")
