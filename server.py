"""
B&R Community MCP Server

An MCP server for searching and retrieving information from the B&R Automation
community forum (https://community.br-automation.com).
"""

import re
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Base URL for the B&R Community Discourse forum
BASE_URL = "https://community.br-automation.com"

# Initialize the MCP server
mcp = FastMCP(
    "B&R Community",
    instructions="""
    This server provides tools to search and retrieve information from the 
    B&R Automation community forum (https://community.br-automation.com).
    
    Use these tools to:
    - Search for topics, posts, and solutions
    - Get details about specific topics
    - List categories and their topics
    - Find answers to B&R Automation related questions
    """,
)


# --- Pydantic Models for Structured Output ---


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


# --- Helper Functions ---


def strip_html(html: str) -> str:
    """Remove HTML tags and clean up text."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Decode common HTML entities
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("&nbsp;", " ")
    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def make_request(endpoint: str, params: Optional[dict] = None) -> dict:
    """Make an HTTP request to the Discourse API."""
    url = f"{BASE_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


# --- MCP Tools ---


@mcp.tool()
async def search_community(
    query: str,
    category: Optional[str] = None,
    solved_only: bool = False,
) -> SearchResults:
    """
    Search the B&R Community forum for topics and posts.

    Args:
        query: Search terms to look for (e.g., "mappView widget", "ACOPOS error")
        category: Optional category slug to filter results (e.g., "ask-questions")
        solved_only: If True, only return topics with accepted answers

    Returns:
        SearchResults containing matching posts with links and excerpts
    """
    # Build the search query
    search_query = query
    if category:
        search_query += f" ##{category}"
    if solved_only:
        search_query += " status:solved"

    data = await make_request("/search.json", {"q": search_query})

    posts = []
    topics_map = {}

    # Build a map of topic IDs to titles from the topics array
    for topic in data.get("topics", []):
        topics_map[topic["id"]] = topic.get("title", "")

    for post in data.get("posts", []):
        topic_title = topics_map.get(post.get("topic_id", 0), "")
        posts.append(
            SearchResultPost(
                id=post["id"],
                topic_id=post.get("topic_id", 0),
                username=post.get("username", "unknown"),
                created_at=post.get("created_at", ""),
                blurb=post.get("blurb", ""),
                topic_title=topic_title,
                url=f"{BASE_URL}/t/{post.get('topic_id', 0)}/{post.get('post_number', 1)}",
                like_count=post.get("like_count", 0),
            )
        )

    return SearchResults(
        query=query,
        total_posts=len(posts),
        posts=posts,
    )


@mcp.tool()
async def get_topic(topic_id: int, max_posts: int = 10) -> TopicDetails:
    """
    Get detailed information about a specific topic including its posts.

    Args:
        topic_id: The numeric ID of the topic (found in URLs like /t/topic-name/1234)
        max_posts: Maximum number of posts to retrieve (default 10)

    Returns:
        TopicDetails with full topic information and posts
    """
    data = await make_request(f"/t/{topic_id}.json")

    # Extract posts from the post_stream
    posts = []
    post_stream = data.get("post_stream", {})
    for post in post_stream.get("posts", [])[:max_posts]:
        content = strip_html(post.get("cooked", ""))
        posts.append(
            TopicPost(
                id=post["id"],
                post_number=post.get("post_number", 1),
                username=post.get("username", "unknown"),
                created_at=post.get("created_at", ""),
                content=content,
                like_count=post.get("like_count", 0),
                is_accepted_answer=post.get("accepted_answer", False),
            )
        )

    # Get category name
    category_id = data.get("category_id")
    category_name = ""
    if category_id:
        try:
            cat_data = await make_request("/categories.json")
            for cat in cat_data.get("category_list", {}).get("categories", []):
                if cat["id"] == category_id:
                    category_name = cat["name"]
                    break
        except Exception:
            pass  # Category lookup is optional

    return TopicDetails(
        id=data["id"],
        title=data.get("title", ""),
        slug=data.get("slug", ""),
        url=f"{BASE_URL}/t/{data.get('slug', '')}/{data['id']}",
        created_at=data.get("created_at", ""),
        posts_count=data.get("posts_count", 0),
        views=data.get("views", 0),
        like_count=data.get("like_count", 0),
        has_accepted_answer=data.get("has_accepted_answer", False),
        category_name=category_name,
        tags=data.get("tags", []),
        posts=posts,
    )


@mcp.tool()
async def list_categories() -> CategoryList:
    """
    List all available categories in the B&R Community forum.

    Returns:
        CategoryList with all categories and their descriptions
    """
    data = await make_request("/categories.json")

    categories = []
    category_list = data.get("category_list", {}).get("categories", [])

    # Build subcategory mapping
    subcategory_map: dict[int, list[str]] = {}
    for cat in category_list:
        parent_id = cat.get("parent_category_id")
        if parent_id:
            if parent_id not in subcategory_map:
                subcategory_map[parent_id] = []
            subcategory_map[parent_id].append(cat["name"])

    # Process top-level categories
    for cat in category_list:
        if not cat.get("parent_category_id"):  # Top-level only
            categories.append(
                Category(
                    id=cat["id"],
                    name=cat["name"],
                    slug=cat.get("slug", ""),
                    description=strip_html(cat.get("description", "") or ""),
                    topic_count=cat.get("topic_count", 0),
                    url=f"{BASE_URL}/c/{cat.get('slug', '')}/{cat['id']}",
                    subcategories=subcategory_map.get(cat["id"], []),
                )
            )

    return CategoryList(categories=categories)


@mcp.tool()
async def get_latest_topics(
    category: Optional[str] = None,
    page: int = 0,
) -> LatestTopics:
    """
    Get the latest topics from the B&R Community forum.

    Args:
        category: Optional category slug to filter (e.g., "ask-questions", "share-knowledge")
        page: Page number for pagination (starts at 0)

    Returns:
        LatestTopics containing the most recent discussions
    """
    if category:
        endpoint = f"/c/{category}.json"
    else:
        endpoint = "/latest.json"

    params = {"page": page} if page > 0 else None
    data = await make_request(endpoint, params)

    # Build category ID to name mapping
    cat_map: dict[int, str] = {}
    for cat in data.get("categories", []):
        cat_map[cat["id"]] = cat["name"]

    topics = []
    topic_list = data.get("topic_list", {}).get("topics", [])

    for topic in topic_list[:30]:  # Limit to 30 topics
        category_name = cat_map.get(topic.get("category_id", 0), "")
        topics.append(
            LatestTopic(
                id=topic["id"],
                title=topic.get("title", ""),
                url=f"{BASE_URL}/t/{topic.get('slug', '')}/{topic['id']}",
                created_at=topic.get("created_at", ""),
                last_posted_at=topic.get("last_posted_at", ""),
                posts_count=topic.get("posts_count", 1),
                views=topic.get("views", 0),
                like_count=topic.get("like_count", 0),
                has_accepted_answer=topic.get("has_accepted_answer", False),
                category_name=category_name,
                excerpt=topic.get("excerpt", ""),
            )
        )

    return LatestTopics(topics=topics)


@mcp.tool()
async def get_top_topics(
    period: str = "monthly",
) -> LatestTopics:
    """
    Get the top/most popular topics from the B&R Community forum.

    Args:
        period: Time period for top topics - one of "daily", "weekly", "monthly", 
                "quarterly", "yearly", or "all"

    Returns:
        LatestTopics containing the most popular discussions for the period
    """
    valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly", "all"]
    if period not in valid_periods:
        period = "monthly"

    endpoint = f"/top/{period}.json"
    data = await make_request(endpoint)

    # Build category ID to name mapping
    cat_map: dict[int, str] = {}
    for cat in data.get("categories", []):
        cat_map[cat["id"]] = cat["name"]

    topics = []
    topic_list = data.get("topic_list", {}).get("topics", [])

    for topic in topic_list[:30]:
        category_name = cat_map.get(topic.get("category_id", 0), "")
        topics.append(
            LatestTopic(
                id=topic["id"],
                title=topic.get("title", ""),
                url=f"{BASE_URL}/t/{topic.get('slug', '')}/{topic['id']}",
                created_at=topic.get("created_at", ""),
                last_posted_at=topic.get("last_posted_at", ""),
                posts_count=topic.get("posts_count", 1),
                views=topic.get("views", 0),
                like_count=topic.get("like_count", 0),
                has_accepted_answer=topic.get("has_accepted_answer", False),
                category_name=category_name,
                excerpt=topic.get("excerpt", ""),
            )
        )

    return LatestTopics(topics=topics)


# --- Entry Point ---

if __name__ == "__main__":
    mcp.run()
