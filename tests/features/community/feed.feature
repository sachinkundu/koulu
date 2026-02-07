Feature: Community Feed
  As a community member
  I want to create posts, comment, and engage with content
  So that I can participate in discussions and build connections

  Background:
    Given a community exists with name "Koulu Community"
    And the following categories exist:
      | name          | slug          | emoji |
      | General       | general       | 🗣️    |
      | Q&A           | qa            | ❓    |
      | Wins          | wins          | 🎉    |
      | Introductions | introductions | 👋    |

  # ============================================
  # POST CREATION
  # ============================================

  @happy_path @post
  Scenario: Member creates a post with title and content
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When I create a post with:
      | title    | How to get started with Python? |
      | content  | I'm new to programming and want to learn Python. Any tips? |
      | category | Q&A |
    Then the post should be created successfully
    And the post should have title "How to get started with Python?"
    And the post should be in category "Q&A"
    And the post author should be "alice@example.com"
    And a "PostCreated" event should be published

  @happy_path @post
  Scenario: Member creates a post with an image
    Given a user exists with email "bob@example.com" and role "MEMBER"
    And I am authenticated as "bob@example.com"
    When I create a post with:
      | title     | My first project! |
      | content   | Check out what I built |
      | category  | Wins |
      | image_url | https://example.com/image.jpg |
    Then the post should be created successfully
    And the post should have an image at "https://example.com/image.jpg"

  @error @post
  Scenario: Post creation fails without title
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When I attempt to create a post with:
      | content  | This post has no title |
      | category | General |
    Then the post creation should fail with error "Title is required"

  @error @post
  Scenario: Post creation fails with title too long
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When I attempt to create a post with a title of 201 characters
    Then the post creation should fail with error "Title must be 200 characters or less"

  @error @post
  Scenario: Post creation fails with content too long
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When I attempt to create a post with content of 5001 characters
    Then the post creation should fail with error "Content must be 5000 characters or less"

  @error @post
  Scenario: Post creation fails with invalid category
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When I attempt to create a post with:
      | title    | Test post |
      | content  | Test content |
      | category | NonExistent |
    Then the post creation should fail with error "Category not found"

  @error @post
  Scenario: Post creation fails with invalid image URL
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When I attempt to create a post with:
      | title     | Test |
      | content   | Test |
      | category  | General |
      | image_url | http://insecure.com/image.jpg |
    Then the post creation should fail with error "Image URL must use HTTPS"

  @security @post
  Scenario: Unauthenticated user cannot create post
    When I attempt to create a post without authentication
    Then the post creation should fail with error "Authentication required"

  @edge_case @post
  Scenario: Rate limit prevents excessive posting
    Given a user exists with email "spammer@example.com" and role "MEMBER"
    And I am authenticated as "spammer@example.com"
    And I have created 10 posts in the last hour
    When I attempt to create another post
    Then the post creation should fail with error "Rate limit exceeded. Try again later."

  # ============================================
  # POST EDITING
  # ============================================

  @happy_path @post
  Scenario: Author edits their own post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    And I created a post with title "Original Title"
    When I edit the post with:
      | title   | Updated Title |
      | content | Updated content with more details |
    Then the post should be updated successfully
    And the post should have title "Updated Title"
    And the post should show as "edited"
    And a "PostEdited" event should be published

  @error @post
  Scenario: User cannot edit another user's post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And user "alice@example.com" created a post
    And I am authenticated as "bob@example.com"
    When I attempt to edit Alice's post
    Then the edit should fail with error "You don't have permission to edit this post"

  # ============================================
  # POST DELETION
  # ============================================

  @happy_path @post
  Scenario: Author deletes their own post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    And I created a post with title "To be deleted"
    When I delete my post
    Then the post should be deleted successfully
    And the post should not appear in the feed
    And a "PostDeleted" event should be published

  @happy_path @post
  Scenario: Admin deletes another user's post
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a user exists with email "member@example.com" and role "MEMBER"
    And user "member@example.com" created a post with title "Inappropriate content"
    And I am authenticated as "admin@example.com"
    When I delete the member's post
    Then the post should be deleted successfully
    And a "PostDeleted" event should be published with admin user_id

  @happy_path @post
  Scenario: Moderator deletes a post
    Given a user exists with email "mod@example.com" and role "MODERATOR"
    And a user exists with email "member@example.com" and role "MEMBER"
    And user "member@example.com" created a post
    And I am authenticated as "mod@example.com"
    When I delete the member's post
    Then the post should be deleted successfully

  @error @post
  Scenario: Regular member cannot delete another member's post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And user "alice@example.com" created a post
    And I am authenticated as "bob@example.com"
    When I attempt to delete Alice's post
    Then the deletion should fail with error "You don't have permission to delete this post"

  @edge_case @post
  Scenario: Deleting a post cascades to comments and reactions
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And user "alice@example.com" created a post
    And the post has 5 comments
    And the post has 3 likes
    And I am authenticated as "alice@example.com"
    When I delete my post
    Then the post should be deleted
    And all comments on the post should be deleted
    And all reactions on the post should be deleted

  # ============================================
  # POST PINNING
  # ============================================

  @happy_path @post
  Scenario: Admin pins an important post
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a user exists with email "member@example.com" and role "MEMBER"
    And user "member@example.com" created a post with title "Important announcement"
    And I am authenticated as "admin@example.com"
    When I pin the post
    Then the post should be pinned successfully
    And the post should appear at the top of the feed
    And a "PostPinned" event should be published

  @happy_path @post
  Scenario: Moderator pins a post
    Given a user exists with email "mod@example.com" and role "MODERATOR"
    And a post exists with title "Community guidelines"
    And I am authenticated as "mod@example.com"
    When I pin the post
    Then the post should be pinned successfully

  @happy_path @post
  Scenario: Admin unpins a post
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a post exists and is pinned
    And I am authenticated as "admin@example.com"
    When I unpin the post
    Then the post should no longer be pinned
    And the post should appear in normal feed order

  @error @post
  Scenario: Regular member cannot pin posts
    Given a user exists with email "member@example.com" and role "MEMBER"
    And a post exists
    And I am authenticated as "member@example.com"
    When I attempt to pin the post
    Then the pin should fail with error "You don't have permission to pin posts"

  # ============================================
  # POST LOCKING
  # ============================================

  @happy_path @post
  Scenario: Admin locks comments on a post
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a post exists with title "Locked thread"
    And I am authenticated as "admin@example.com"
    When I lock the post
    Then the post should be locked successfully
    And new comments should not be allowed
    And a "PostLocked" event should be published

  @happy_path @post
  Scenario: Admin unlocks a locked post
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a post exists and is locked
    And I am authenticated as "admin@example.com"
    When I unlock the post
    Then the post should be unlocked
    And new comments should be allowed again

  @error @post
  Scenario: Cannot comment on locked post
    Given a user exists with email "member@example.com" and role "MEMBER"
    And a post exists and is locked
    And I am authenticated as "member@example.com"
    When I attempt to add a comment to the locked post
    Then the comment should fail with error "Post is locked. Comments are disabled."

  @error @post
  Scenario: Regular member cannot lock posts
    Given a user exists with email "member@example.com" and role "MEMBER"
    And a post exists
    And I am authenticated as "member@example.com"
    When I attempt to lock the post
    Then the lock should fail with error "You don't have permission to lock posts"

  # ============================================
  # COMMENTS
  # ============================================

  @happy_path @comment
  Scenario: Member adds a comment to a post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with title "Python tips"
    And I am authenticated as "alice@example.com"
    When I add a comment with content "Great post! Very helpful."
    Then the comment should be added successfully
    And the comment should appear on the post
    And the post comment count should increase by 1
    And a "CommentAdded" event should be published

  @happy_path @comment
  Scenario: Member replies to a comment
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And a post exists with a comment by "bob@example.com"
    And I am authenticated as "alice@example.com"
    When I reply to Bob's comment with "I agree with this point"
    Then the reply should be added successfully
    And the reply should be nested under Bob's comment
    And a "CommentAdded" event should be published with parent_comment_id

  @error @comment
  Scenario: Cannot reply to a reply (max depth exceeded)
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with a comment and a reply to that comment
    And I am authenticated as "alice@example.com"
    When I attempt to reply to the reply
    Then the reply should fail with error "Maximum reply depth exceeded"

  @error @comment
  Scenario: Comment content too long
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists
    And I am authenticated as "alice@example.com"
    When I attempt to add a comment with 2001 characters
    Then the comment should fail with error "Comment must be 2000 characters or less"

  @error @comment
  Scenario: Comment content required
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists
    And I am authenticated as "alice@example.com"
    When I attempt to add an empty comment
    Then the comment should fail with error "Comment content is required"

  @edge_case @comment
  Scenario: Rate limit prevents comment spam
    Given a user exists with email "spammer@example.com" and role "MEMBER"
    And a post exists
    And I am authenticated as "spammer@example.com"
    And I have created 50 comments in the last hour
    When I attempt to add another comment
    Then the comment should fail with error "Rate limit exceeded. Try again later."

  # ============================================
  # COMMENT EDITING & DELETION
  # ============================================

  @happy_path @comment
  Scenario: Author edits their own comment
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with a comment by "alice@example.com"
    And I am authenticated as "alice@example.com"
    When I edit my comment to "Updated comment text"
    Then the comment should be updated successfully
    And the comment should show as "edited"
    And a "CommentEdited" event should be published

  @happy_path @comment
  Scenario: Author deletes their own comment with no replies
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with a comment by "alice@example.com"
    And the comment has no replies
    And I am authenticated as "alice@example.com"
    When I delete my comment
    Then the comment should be removed completely
    And a "CommentDeleted" event should be published

  @happy_path @comment
  Scenario: Author deletes comment that has replies
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with a comment by "alice@example.com"
    And the comment has 2 replies
    And I am authenticated as "alice@example.com"
    When I delete my comment
    Then the comment content should show "[deleted]"
    And the replies should remain visible
    And a "CommentDeleted" event should be published

  @happy_path @comment
  Scenario: Admin deletes any comment
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a user exists with email "member@example.com" and role "MEMBER"
    And a post exists with a comment by "member@example.com"
    And I am authenticated as "admin@example.com"
    When I delete the member's comment
    Then the comment should be deleted successfully

  @error @comment
  Scenario: Member cannot edit another member's comment
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And a post exists with a comment by "alice@example.com"
    And I am authenticated as "bob@example.com"
    When I attempt to edit Alice's comment
    Then the edit should fail with error "You don't have permission to edit this comment"

  @error @comment
  Scenario: Member cannot delete another member's comment
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And a post exists with a comment by "alice@example.com"
    And I am authenticated as "bob@example.com"
    When I attempt to delete Alice's comment
    Then the deletion should fail with error "You don't have permission to delete this comment"

  # ============================================
  # REACTIONS (LIKES)
  # ============================================

  @happy_path @reaction
  Scenario: Member likes a post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with title "Great content"
    And I am authenticated as "alice@example.com"
    When I like the post
    Then the like should be recorded successfully
    And the post like count should increase by 1
    And I should appear in the list of likers
    And a "PostLiked" event should be published

  @happy_path @reaction
  Scenario: Member unlikes a post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists
    And I have already liked the post
    And I am authenticated as "alice@example.com"
    When I unlike the post
    Then the like should be removed successfully
    And the post like count should decrease by 1
    And I should not appear in the list of likers
    And a "PostUnliked" event should be published

  @happy_path @reaction
  Scenario: Member likes a comment
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with a comment
    And I am authenticated as "alice@example.com"
    When I like the comment
    Then the like should be recorded successfully
    And the comment like count should increase by 1
    And a "CommentLiked" event should be published

  @happy_path @reaction
  Scenario: Member unlikes a comment
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with a comment
    And I have already liked the comment
    And I am authenticated as "alice@example.com"
    When I unlike the comment
    Then the like should be removed
    And the comment like count should decrease by 1
    And a "CommentUnliked" event should be published

  @edge_case @reaction
  Scenario: Liking a post twice is idempotent
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists
    And I have already liked the post
    And I am authenticated as "alice@example.com"
    When I like the post again
    Then the like count should not change
    And no additional event should be published

  @edge_case @reaction
  Scenario: Member can like their own post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    And I created a post
    When I like my own post
    Then the like should be recorded successfully
    And the post like count should be 1

  @edge_case @reaction
  Scenario: Rate limit prevents excessive liking
    Given a user exists with email "liker@example.com" and role "MEMBER"
    And I am authenticated as "liker@example.com"
    And I have liked 200 posts in the last hour
    When I attempt to like another post
    Then the like should fail with error "Rate limit exceeded. Try again later."

  @security @reaction
  Scenario: Unauthenticated user cannot like posts
    Given a post exists
    When I attempt to like the post without authentication
    Then the like should fail with error "Authentication required"

  # ============================================
  # CATEGORIES
  # ============================================

  @happy_path @category
  Scenario: Admin creates a new category
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When I create a category with:
      | name        | Resources |
      | slug        | resources |
      | emoji       | 📚        |
      | description | Helpful resources and links |
    Then the category should be created successfully
    And the category should appear in the category list
    And a "CategoryCreated" event should be published

  @happy_path @category
  Scenario: Admin updates a category
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a category exists with name "Resources"
    And I am authenticated as "admin@example.com"
    When I update the category with:
      | name        | Tools & Resources |
      | emoji       | 🛠️                |
      | description | Updated description |
    Then the category should be updated successfully
    And a "CategoryUpdated" event should be published

  @happy_path @category
  Scenario: Admin deletes empty category
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a category exists with name "Temporary"
    And the category has no posts
    And I am authenticated as "admin@example.com"
    When I delete the category
    Then the category should be deleted successfully
    And a "CategoryDeleted" event should be published

  @error @category
  Scenario: Cannot delete category with posts
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a category exists with name "General"
    And the category has 5 posts
    And I am authenticated as "admin@example.com"
    When I attempt to delete the category
    Then the deletion should fail with error "Cannot delete category with posts. Reassign posts first."

  @error @category
  Scenario: Category name must be unique
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a category exists with name "Q&A"
    And I am authenticated as "admin@example.com"
    When I attempt to create a category with name "Q&A"
    Then the creation should fail with error "Category name already exists"

  @error @category
  Scenario: Member cannot create categories
    Given a user exists with email "member@example.com" and role "MEMBER"
    And I am authenticated as "member@example.com"
    When I attempt to create a category
    Then the creation should fail with error "You don't have permission to create categories"

  @error @category
  Scenario: Moderator cannot create categories
    Given a user exists with email "mod@example.com" and role "MODERATOR"
    And I am authenticated as "mod@example.com"
    When I attempt to create a category
    Then the creation should fail with error "You don't have permission to create categories"

  @happy_path @category
  Scenario: Admin moves post to different category
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a post exists in category "General"
    And I am authenticated as "admin@example.com"
    When I move the post to category "Q&A"
    Then the post should be in category "Q&A"

  # ============================================
  # FEED DISPLAY
  # ============================================

  @happy_path @feed
  Scenario: View feed with Hot sorting (default)
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And the following posts exist:
      | title       | created_hours_ago | like_count | comment_count |
      | Recent hot  | 2                 | 5          | 3             |
      | Old cold    | 48                | 0          | 0             |
      | Recent warm | 5                 | 2          | 1             |
    And I am authenticated as "alice@example.com"
    When I view the feed with "Hot" sorting
    Then posts should be ordered: "Recent hot", "Recent warm", "Old cold"

  @happy_path @feed
  Scenario: View feed with New sorting
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And the following posts exist:
      | title   | created_hours_ago |
      | Newest  | 1                 |
      | Middle  | 5                 |
      | Oldest  | 10                |
    And I am authenticated as "alice@example.com"
    When I view the feed with "New" sorting
    Then posts should be ordered: "Newest", "Middle", "Oldest"

  @happy_path @feed
  Scenario: View feed with Top sorting
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And the following posts exist:
      | title         | like_count |
      | Most liked    | 10         |
      | Medium liked  | 5          |
      | Least liked   | 1          |
    And I am authenticated as "alice@example.com"
    When I view the feed with "Top" sorting
    Then posts should be ordered: "Most liked", "Medium liked", "Least liked"

  @happy_path @feed
  Scenario: Pinned posts always appear first
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And the following posts exist:
      | title           | is_pinned | created_hours_ago |
      | Regular post 1  | false     | 1                 |
      | Pinned post 1   | true      | 10                |
      | Regular post 2  | false     | 2                 |
      | Pinned post 2   | true      | 5                 |
    And I am authenticated as "alice@example.com"
    When I view the feed with "New" sorting
    Then pinned posts should appear first: "Pinned post 2", "Pinned post 1"
    And then regular posts: "Regular post 1", "Regular post 2"

  @happy_path @feed
  Scenario: Filter feed by category
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And the following posts exist:
      | title       | category |
      | Question 1  | Q&A      |
      | General 1   | General  |
      | Question 2  | Q&A      |
    And I am authenticated as "alice@example.com"
    When I filter the feed by category "Q&A"
    Then I should see only posts: "Question 1", "Question 2"

  @happy_path @feed
  Scenario: Paginate feed with cursor
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And 30 posts exist in the community
    And I am authenticated as "alice@example.com"
    When I view the feed with limit 20
    Then I should see 20 posts
    And I should receive a cursor for the next page
    When I request the next page with the cursor
    Then I should see the remaining 10 posts

  @edge_case @feed
  Scenario: Empty feed shows appropriate message
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And no posts exist in the community
    And I am authenticated as "alice@example.com"
    When I view the feed
    Then I should see an empty state message
    And the message should say "No posts yet. Be the first to start a conversation!"

  @security @feed
  Scenario: Unauthenticated user cannot view feed
    When I attempt to view the feed without authentication
    Then the request should fail with error "Authentication required"

  @security @feed
  Scenario: Non-member cannot view community feed
    Given a user exists with email "outsider@example.com" and is not a community member
    And I am authenticated as "outsider@example.com"
    When I attempt to view the community feed
    Then the request should fail with error "You are not a member of this community"

  # ============================================
  # POST DETAIL VIEW
  # ============================================

  @happy_path @feed
  Scenario: View post with comments
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists with title "Python Tips"
    And the post has 3 comments
    And I am authenticated as "alice@example.com"
    When I view the post details
    Then I should see the full post content
    And I should see all 3 comments
    And I should see like counts for post and comments
    And I should see the list of users who liked

  @happy_path @feed
  Scenario: View post with threaded comments
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post exists
    And the post has a comment with 2 replies
    And I am authenticated as "alice@example.com"
    When I view the post details
    Then I should see the parent comment
    And I should see the 2 replies nested under the parent

  # ============================================
  # PERMISSIONS
  # ============================================

  @security @permissions
  Scenario: Admin role has full permissions
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    Then I should be able to create posts
    And I should be able to delete any post
    And I should be able to pin posts
    And I should be able to lock posts
    And I should be able to create categories
    And I should be able to delete categories

  @security @permissions
  Scenario: Moderator has moderation permissions
    Given a user exists with email "mod@example.com" and role "MODERATOR"
    And I am authenticated as "mod@example.com"
    Then I should be able to create posts
    And I should be able to delete any post
    And I should be able to pin posts
    And I should be able to lock posts
    And I should NOT be able to create categories
    And I should NOT be able to delete categories

  @security @permissions
  Scenario: Member has basic permissions
    Given a user exists with email "member@example.com" and role "MEMBER"
    And I am authenticated as "member@example.com"
    Then I should be able to create posts
    And I should be able to edit my own posts
    And I should be able to delete my own posts
    And I should NOT be able to delete other posts
    And I should NOT be able to pin posts
    And I should NOT be able to lock posts
    And I should NOT be able to create categories

  # ============================================
  # EDGE CASES
  # ============================================

  @edge_case
  Scenario: Concurrent edits - last write wins
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    And I created a post with title "Original"
    When two users edit the post simultaneously
    Then the last edit should be saved
    And the post should show as "edited"

  @edge_case
  Scenario: Viewing deleted post returns 404
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a post existed but was deleted
    And I am authenticated as "alice@example.com"
    When I attempt to view the deleted post
    Then I should see a 404 error
    And the error message should say "Post not found"

  @edge_case
  Scenario: Deleted user's content shows placeholder
    Given a post exists authored by a user who deleted their account
    And I am a community member
    When I view the post
    Then the author should show as "[deleted user]"
    And the post content should still be visible

  @edge_case
  Scenario: Maximum 5 pinned posts displayed
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And 7 posts are pinned
    And I am authenticated as "admin@example.com"
    When I view the feed
    Then I should see only the 5 most recently pinned posts at the top
