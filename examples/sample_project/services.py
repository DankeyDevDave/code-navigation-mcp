"""Service layer for business logic"""

from typing import List, Optional
from models import User, Post, Comment


class UserService:
    """Service for user-related operations"""
    
    def __init__(self):
        self.users: List[User] = []
        
    def create_user(self, username: str, email: str) -> User:
        """Create a new user"""
        if self.find_user_by_email(email):
            raise ValueError(f"User with email {email} already exists")
            
        user = User(username, email, id=len(self.users) + 1)
        self.users.append(user)
        user.save()
        return user
        
    def find_user_by_email(self, email: str) -> Optional[User]:
        """Find a user by their email address"""
        for user in self.users:
            if user.email == email:
                return user
        return None
        
    def find_user_by_username(self, username: str) -> Optional[User]:
        """Find a user by their username"""
        for user in self.users:
            if user.username == username:
                return user
        return None
        
    def delete_user(self, user: User):
        """Delete a user and all their content"""
        if user in self.users:
            user.delete()
            self.users.remove(user)


class PostService:
    """Service for post-related operations"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.posts: List[Post] = []
        
    def create_post(self, author_email: str, title: str, content: str) -> Post:
        """Create a new post"""
        author = self.user_service.find_user_by_email(author_email)
        if not author:
            raise ValueError(f"User with email {author_email} not found")
            
        post = author.create_post(title, content)
        post.id = len(self.posts) + 1
        self.posts.append(post)
        post.save()
        return post
        
    def get_posts_by_user(self, user: User) -> List[Post]:
        """Get all posts by a specific user"""
        return [post for post in self.posts if post.author == user]
        
    def get_recent_posts(self, limit: int = 10) -> List[Post]:
        """Get the most recent posts across all users"""
        return sorted(self.posts, key=lambda p: p.created_at, reverse=True)[:limit]
        
    def search_posts(self, query: str) -> List[Post]:
        """Search posts by title or content"""
        query_lower = query.lower()
        results = []
        for post in self.posts:
            if query_lower in post.title.lower() or query_lower in post.content.lower():
                results.append(post)
        return results


class CommentService:
    """Service for comment operations"""
    
    def __init__(self, user_service: UserService, post_service: PostService):
        self.user_service = user_service
        self.post_service = post_service
        
    def add_comment(self, post_id: int, commenter_email: str, text: str) -> Comment:
        """Add a comment to a post"""
        commenter = self.user_service.find_user_by_email(commenter_email)
        if not commenter:
            raise ValueError(f"User with email {commenter_email} not found")
            
        post = None
        for p in self.post_service.posts:
            if p.id == post_id:
                post = p
                break
                
        if not post:
            raise ValueError(f"Post with id {post_id} not found")
            
        comment = post.add_comment(text, commenter)
        return comment