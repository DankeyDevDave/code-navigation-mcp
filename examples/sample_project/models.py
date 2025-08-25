"""Sample models for testing code navigation"""

from datetime import datetime
from typing import List, Optional


class BaseModel:
    """Base model with common functionality"""
    
    def __init__(self, id: Optional[int] = None):
        self.id = id
        self.created_at = datetime.now()
        
    def save(self):
        """Save the model to database"""
        print(f"Saving {self.__class__.__name__} with id {self.id}")
        
    def delete(self):
        """Delete the model from database"""
        print(f"Deleting {self.__class__.__name__} with id {self.id}")


class User(BaseModel):
    """User model representing a system user"""
    
    def __init__(self, username: str, email: str, id: Optional[int] = None):
        super().__init__(id)
        self.username = username
        self.email = email
        self.posts: List['Post'] = []
        
    def create_post(self, title: str, content: str) -> 'Post':
        """Create a new post for this user"""
        post = Post(title, content, author=self)
        self.posts.append(post)
        return post
        
    def get_recent_posts(self, limit: int = 5) -> List['Post']:
        """Get the most recent posts by this user"""
        return sorted(self.posts, key=lambda p: p.created_at, reverse=True)[:limit]


class Post(BaseModel):
    """Post model representing a blog post"""
    
    def __init__(self, title: str, content: str, author: User, id: Optional[int] = None):
        super().__init__(id)
        self.title = title
        self.content = content
        self.author = author
        self.comments: List['Comment'] = []
        
    def add_comment(self, text: str, commenter: User) -> 'Comment':
        """Add a comment to this post"""
        comment = Comment(text, commenter, self)
        self.comments.append(comment)
        return comment
        
    def get_comment_count(self) -> int:
        """Get the total number of comments"""
        return len(self.comments)


class Comment(BaseModel):
    """Comment model for post comments"""
    
    def __init__(self, text: str, author: User, post: Post, id: Optional[int] = None):
        super().__init__(id)
        self.text = text
        self.author = author
        self.post = post
        
    def __str__(self):
        return f"Comment by {self.author.username}: {self.text[:50]}..."