"""Main application entry point"""

import sys
from services import UserService, PostService, CommentService
from models import User, Post


def main():
    """Initialize the application and run demo"""
    print("Initializing Blog Application...")
    
    # Initialize services
    user_service = UserService()
    post_service = PostService(user_service)
    comment_service = CommentService(user_service, post_service)
    
    # Create some sample users
    alice = user_service.create_user("alice", "alice@example.com")
    bob = user_service.create_user("bob", "bob@example.com")
    charlie = user_service.create_user("charlie", "charlie@example.com")
    
    print(f"Created {len(user_service.users)} users")
    
    # Create some posts
    post1 = post_service.create_post(
        "alice@example.com",
        "Introduction to Python",
        "Python is a great programming language..."
    )
    
    post2 = post_service.create_post(
        "bob@example.com", 
        "Web Development with Django",
        "Django makes web development easy..."
    )
    
    post3 = post_service.create_post(
        "alice@example.com",
        "Advanced Python Techniques",
        "Let's explore some advanced Python features..."
    )
    
    print(f"Created {len(post_service.posts)} posts")
    
    # Add some comments
    comment1 = comment_service.add_comment(
        post1.id,
        "bob@example.com",
        "Great introduction! Very helpful."
    )
    
    comment2 = comment_service.add_comment(
        post1.id,
        "charlie@example.com",
        "Thanks for sharing this!"
    )
    
    comment3 = comment_service.add_comment(
        post2.id,
        "alice@example.com",
        "Django is indeed powerful."
    )
    
    print("Added comments to posts")
    
    # Display recent posts
    print("\n=== Recent Posts ===")
    for post in post_service.get_recent_posts(5):
        print(f"- {post.title} by {post.author.username}")
        print(f"  Comments: {post.get_comment_count()}")
    
    # Search functionality
    search_results = post_service.search_posts("Python")
    print(f"\n=== Search Results for 'Python' ===")
    for post in search_results:
        print(f"- {post.title}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())