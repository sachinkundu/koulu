Feature: Classroom
  As a community member
  I want to access structured learning content through courses
  So that I can learn at my own pace and track my progress

  Background:
    Given the system is initialized
    And a verified user "admin@example.com" with role "admin" exists
    And a verified user "member@example.com" with role "member" exists

  # =============================================================================
  # COURSE MANAGEMENT (ADMIN)
  # =============================================================================

  @happy_path
  Scenario: Admin creates a course with required fields only
    Given the user "admin@example.com" is authenticated
    When the admin creates a course with:
      | field | value                    |
      | title | Introduction to Python   |
    Then the course should be created successfully
    And a "CourseCreated" event should be published
    And the course should have no modules
    And the course should be visible in the course list

  @happy_path
  Scenario: Admin creates a course with all optional fields
    Given the user "admin@example.com" is authenticated
    When the admin creates a course with:
      | field              | value                                      |
      | title              | Advanced Web Development                   |
      | description        | Learn React, TypeScript, and backend APIs  |
      | cover_image_url    | https://example.com/course-cover.jpg       |
      | estimated_duration | 8 hours                                    |
    Then the course should be created successfully
    And the course should contain all provided information
    And the instructor should be "admin@example.com"

  @happy_path
  Scenario: Admin lists all courses
    Given the user "admin@example.com" is authenticated
    And the following courses exist:
      | title                  | instructor         |
      | Python Basics          | admin@example.com  |
      | Web Development        | admin@example.com  |
    When the admin requests the course list
    Then the response should contain 2 courses
    And each course should include title, module_count, lesson_count

  @happy_path
  Scenario: Admin views course details
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists created by "admin@example.com"
    And the course has 2 modules with 3 lessons each
    When the admin requests the course details
    Then the response should include the full module and lesson structure
    And each module should show its lesson count
    And each lesson should show its content type

  @happy_path
  Scenario: Admin edits course details
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists created by "admin@example.com"
    When the admin updates the course with:
      | field       | value                        |
      | title       | Python Fundamentals          |
      | description | Updated course description   |
    Then the course should be updated successfully
    And the course title should be "Python Fundamentals"

  @happy_path
  Scenario: Admin soft deletes a course
    Given the user "admin@example.com" is authenticated
    And a course "Old Course" exists created by "admin@example.com"
    And a member has started the course "Old Course"
    When the admin deletes the course "Old Course"
    Then the course should be soft deleted
    And a "CourseDeleted" event should be published
    And the course should not appear in the member course list
    And the member's progress should be retained

  # =============================================================================
  # COURSE CREATION VALIDATION ERRORS
  # =============================================================================

  @error
  Scenario: Course creation fails without title
    Given the user "admin@example.com" is authenticated
    When the admin attempts to create a course without a title
    Then course creation should fail with "title is required" error

  @error
  Scenario: Course creation fails with title too short
    Given the user "admin@example.com" is authenticated
    When the admin attempts to create a course with title "A"
    Then course creation should fail with "title too short" error

  @error
  Scenario: Course creation fails with title too long
    Given the user "admin@example.com" is authenticated
    When the admin attempts to create a course with a title of 201 characters
    Then course creation should fail with "title too long" error

  @error
  Scenario: Course creation fails with description too long
    Given the user "admin@example.com" is authenticated
    When the admin attempts to create a course with:
      | field       | value                  |
      | title       | Valid Title            |
      | description | <2001 character string> |
    Then course creation should fail with "description too long" error

  @error
  Scenario: Course creation fails with invalid cover image URL
    Given the user "admin@example.com" is authenticated
    When the admin attempts to create a course with:
      | field           | value       |
      | title           | Valid Title |
      | cover_image_url | not-a-url   |
    Then course creation should fail with "invalid URL format" error

  # =============================================================================
  # MODULE MANAGEMENT (ADMIN)
  # =============================================================================

  @happy_path
  Scenario: Admin adds a module to a course
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists created by "admin@example.com"
    When the admin adds a module to the course with:
      | field | value                |
      | title | Getting Started      |
    Then the module should be created successfully
    And the module position should be 1
    And the module should have no lessons

  @happy_path
  Scenario: Admin adds multiple modules in sequence
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists created by "admin@example.com"
    When the admin adds a module with title "Module 1"
    And the admin adds a module with title "Module 2"
    And the admin adds a module with title "Module 3"
    Then the course should have 3 modules
    And the modules should have positions 1, 2, 3 respectively

  @happy_path
  Scenario: Admin reorders modules
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists with modules:
      | title    | position |
      | Module A | 1        |
      | Module B | 2        |
      | Module C | 3        |
    When the admin reorders modules to:
      | module_id | new_position |
      | Module C  | 1            |
      | Module A  | 2            |
      | Module B  | 3            |
    Then the modules should have the new positions
    And the course module list should reflect the new order

  @happy_path
  Scenario: Admin edits module details
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin updates the module with:
      | field       | value                           |
      | title       | Introduction                    |
      | description | Learn the basics of Python      |
    Then the module should be updated successfully
    And the module title should be "Introduction"

  @happy_path
  Scenario: Admin soft deletes a module
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Old Module"
    And the module has 3 lessons
    When the admin deletes the module "Old Module"
    Then the module should be soft deleted
    And the module should not appear in course details
    And the lessons should also be soft deleted

  # =============================================================================
  # MODULE VALIDATION ERRORS
  # =============================================================================

  @error
  Scenario: Module creation fails without title
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists created by "admin@example.com"
    When the admin attempts to add a module without a title
    Then module creation should fail with "title is required" error

  @error
  Scenario: Module creation fails with title too short
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists created by "admin@example.com"
    When the admin attempts to add a module with title "A"
    Then module creation should fail with "title too short" error

  @error
  Scenario: Module creation fails with title too long
    Given the user "admin@example.com" is authenticated
    And a course "Python Basics" exists created by "admin@example.com"
    When the admin attempts to add a module with a title of 201 characters
    Then module creation should fail with "title too long" error

  @error
  Scenario: Reorder fails with duplicate positions
    Given the user "admin@example.com" is authenticated
    And a course exists with 3 modules
    When the admin attempts to reorder modules with duplicate position 1
    Then the reorder should fail with "duplicate position" error

  # =============================================================================
  # LESSON MANAGEMENT (ADMIN)
  # =============================================================================

  @happy_path
  Scenario: Admin creates a text lesson
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin adds a lesson to the module with:
      | field        | value                                    |
      | title        | What is Python?                          |
      | content_type | text                                     |
      | content      | Python is a high-level programming language. |
    Then the lesson should be created successfully
    And the lesson position should be 1
    And the lesson content_type should be "text"

  @happy_path
  Scenario: Admin creates a video lesson with YouTube embed
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin adds a lesson to the module with:
      | field        | value                                      |
      | title        | Introduction Video                         |
      | content_type | video                                      |
      | content      | https://www.youtube.com/watch?v=dQw4w9WgXcQ |
    Then the lesson should be created successfully
    And the lesson content_type should be "video"
    And the content should be a valid YouTube embed URL

  @happy_path
  Scenario: Admin creates a video lesson with Vimeo embed
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin adds a lesson to the module with:
      | field        | value                                |
      | title        | Introduction Video                   |
      | content_type | video                                |
      | content      | https://vimeo.com/123456789          |
    Then the lesson should be created successfully
    And the content should be a valid Vimeo embed URL

  @happy_path
  Scenario: Admin creates a video lesson with Loom embed
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin adds a lesson to the module with:
      | field        | value                                         |
      | title        | Introduction Video                            |
      | content_type | video                                         |
      | content      | https://www.loom.com/share/abc123def456       |
    Then the lesson should be created successfully
    And the content should be a valid Loom embed URL

  @happy_path
  Scenario: Admin adds multiple lessons in sequence
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin adds a lesson with title "Lesson 1"
    And the admin adds a lesson with title "Lesson 2"
    And the admin adds a lesson with title "Lesson 3"
    Then the module should have 3 lessons
    And the lessons should have positions 1, 2, 3 respectively

  @happy_path
  Scenario: Admin reorders lessons within a module
    Given the user "admin@example.com" is authenticated
    And a module exists with lessons:
      | title    | position |
      | Lesson A | 1        |
      | Lesson B | 2        |
      | Lesson C | 3        |
    When the admin reorders lessons to:
      | lesson_id | new_position |
      | Lesson C  | 1            |
      | Lesson A  | 2            |
      | Lesson B  | 3            |
    Then the lessons should have the new positions
    And the module lesson list should reflect the new order

  @happy_path
  Scenario: Admin edits a text lesson
    Given the user "admin@example.com" is authenticated
    And a module exists with a text lesson "Introduction"
    When the admin updates the lesson with:
      | field   | value                            |
      | title   | Introduction to Python           |
      | content | Updated content with more details |
    Then the lesson should be updated successfully
    And the lesson content should be updated

  @happy_path
  Scenario: Admin edits a video lesson URL
    Given the user "admin@example.com" is authenticated
    And a module exists with a video lesson "Intro Video"
    When the admin updates the lesson with:
      | field   | value                                      |
      | content | https://www.youtube.com/watch?v=newVideoID |
    Then the lesson should be updated successfully
    And the video embed URL should be updated

  @happy_path
  Scenario: Admin soft deletes a lesson
    Given the user "admin@example.com" is authenticated
    And a module exists with a lesson "Old Lesson"
    And a member has completed the lesson "Old Lesson"
    When the admin deletes the lesson "Old Lesson"
    Then the lesson should be soft deleted
    And the lesson should not appear in module details
    And the member's completion status should be retained

  # =============================================================================
  # LESSON VALIDATION ERRORS
  # =============================================================================

  @error
  Scenario: Lesson creation fails without title
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson without a title
    Then lesson creation should fail with "title is required" error

  @error
  Scenario: Lesson creation fails with title too short
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson with title "A"
    Then lesson creation should fail with "title too short" error

  @error
  Scenario: Lesson creation fails with title too long
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson with a title of 201 characters
    Then lesson creation should fail with "title too long" error

  @error
  Scenario: Lesson creation fails without content
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson with:
      | field        | value          |
      | title        | Valid Title    |
      | content_type | text           |
    Then lesson creation should fail with "content is required" error

  @error
  Scenario: Lesson creation fails with invalid content type
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson with:
      | field        | value          |
      | title        | Valid Title    |
      | content_type | pdf            |
      | content      | Some content   |
    Then lesson creation should fail with "invalid content type" error

  @error
  Scenario: Video lesson creation fails with invalid YouTube URL
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson with:
      | field        | value            |
      | title        | Video Lesson     |
      | content_type | video            |
      | content      | not-a-video-url  |
    Then lesson creation should fail with "invalid video URL" error

  @error
  Scenario: Video lesson creation fails with unsupported platform
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson with:
      | field        | value                                |
      | title        | Video Lesson                         |
      | content_type | video                                |
      | content      | https://www.dailymotion.com/video/x1 |
    Then lesson creation should fail with "invalid video URL" error

  @error
  Scenario: Text lesson creation fails with content too long
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to add a lesson with:
      | field        | value                   |
      | title        | Text Lesson             |
      | content_type | text                    |
      | content      | <50001 character string> |
    Then lesson creation should fail with "content too long" error

  # =============================================================================
  # COURSE DISCOVERY (MEMBER)
  # =============================================================================

  @happy_path
  Scenario: Member views course list
    Given the user "member@example.com" is authenticated
    And the following courses exist:
      | title           | instructor        |
      | Python Basics   | admin@example.com |
      | Web Development | admin@example.com |
    When the member requests the course list
    Then the response should contain 2 courses
    And each course should show module_count and lesson_count
    And the member's progress should be null for unstarted courses

  @happy_path
  Scenario: Member views course list with progress indicators
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 2 modules and 6 total lessons
    And the member has completed 3 lessons in "Python Basics"
    When the member requests the course list
    Then the course "Python Basics" should show 50% completion
    And the course should show "started: true"

  @happy_path
  Scenario: Member views course details
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with the following structure:
      | module_title    | lesson_title       | content_type |
      | Getting Started | What is Python?    | text         |
      | Getting Started | Installation       | video        |
      | Basic Syntax    | Variables          | text         |
    When the member requests the course details
    Then the response should include all modules and lessons
    And each lesson should show its content_type
    And each lesson should show is_complete: false

  @happy_path
  Scenario: Member views course details with progress
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 3 lessons
    And the member has completed lesson 1 and lesson 2
    When the member requests the course details
    Then lesson 1 should show is_complete: true
    And lesson 2 should show is_complete: true
    And lesson 3 should show is_complete: false
    And the progress should show 67% completion

  @happy_path
  Scenario: Soft-deleted courses are hidden from members
    Given the user "member@example.com" is authenticated
    And a course "Deleted Course" exists
    And the course "Deleted Course" is soft deleted
    When the member requests the course list
    Then the course "Deleted Course" should not appear in the list

  # =============================================================================
  # COURSE CONSUMPTION (MEMBER)
  # =============================================================================

  @happy_path
  Scenario: Member starts a course
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 1 module and 3 lessons
    When the member starts the course "Python Basics"
    Then a progress record should be created
    And a "ProgressStarted" event should be published
    And the member should be navigated to the first lesson

  @happy_path
  Scenario: Member views a text lesson
    Given the user "member@example.com" is authenticated
    And a course exists with a text lesson "Introduction" containing "Python is awesome"
    When the member views the lesson "Introduction"
    Then the lesson content should be displayed with rich text formatting
    And the "Mark as Complete" toggle should be unchecked
    And the navigation should show "Next Lesson" button

  @happy_path
  Scenario: Member views a video lesson
    Given the user "member@example.com" is authenticated
    And a course exists with a video lesson "Intro Video" with YouTube URL
    When the member views the lesson "Intro Video"
    Then the video should be displayed in an embedded player
    And the "Mark as Complete" toggle should be unchecked

  @happy_path
  Scenario: Member navigates to next lesson within module
    Given the user "member@example.com" is authenticated
    And a module exists with lessons "Lesson 1", "Lesson 2", "Lesson 3"
    And the member is viewing "Lesson 1"
    When the member clicks "Next Lesson"
    Then the member should be navigated to "Lesson 2"

  @happy_path
  Scenario: Member navigates to previous lesson within module
    Given the user "member@example.com" is authenticated
    And a module exists with lessons "Lesson 1", "Lesson 2", "Lesson 3"
    And the member is viewing "Lesson 2"
    When the member clicks "Previous Lesson"
    Then the member should be navigated to "Lesson 1"

  @happy_path
  Scenario: Member navigates to next lesson across modules
    Given the user "member@example.com" is authenticated
    And a course exists with:
      | module      | lessons               |
      | Module 1    | Lesson A, Lesson B    |
      | Module 2    | Lesson C, Lesson D    |
    And the member is viewing "Lesson B" (last lesson of Module 1)
    When the member clicks "Next Lesson"
    Then the member should be navigated to "Lesson C" (first lesson of Module 2)

  @happy_path
  Scenario: Member navigates to previous lesson across modules
    Given the user "member@example.com" is authenticated
    And a course exists with:
      | module      | lessons               |
      | Module 1    | Lesson A, Lesson B    |
      | Module 2    | Lesson C, Lesson D    |
    And the member is viewing "Lesson C" (first lesson of Module 2)
    When the member clicks "Previous Lesson"
    Then the member should be navigated to "Lesson B" (last lesson of Module 1)

  @happy_path
  Scenario: Member continues where they left off
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 5 lessons
    And the member has completed lessons 1 and 2
    When the member clicks "Continue" on the course
    Then the member should be navigated to lesson 3 (first incomplete)

  @happy_path
  Scenario: Member continues on fully completed course
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 3 lessons
    And the member has completed all lessons
    When the member clicks "Continue" on the course
    Then the member should be navigated to the last lesson
    And a "Course Complete" message should be displayed

  # =============================================================================
  # PROGRESS TRACKING (MEMBER)
  # =============================================================================

  @happy_path
  Scenario: Member marks a lesson as complete
    Given the user "member@example.com" is authenticated
    And the member is viewing a lesson "Introduction"
    And the lesson is not complete
    When the member marks the lesson as complete
    Then the lesson completion should be saved
    And a "LessonCompleted" event should be published
    And the lesson should show is_complete: true

  @happy_path
  Scenario: Member un-marks a lesson as complete
    Given the user "member@example.com" is authenticated
    And the member is viewing a lesson "Introduction"
    And the lesson is already marked complete
    When the member un-marks the lesson as complete
    Then the lesson completion should be removed
    And the lesson should show is_complete: false

  @happy_path
  Scenario: Member completes all lessons in a course
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 3 lessons
    And the member has completed 2 lessons
    When the member marks the third lesson as complete
    Then a "LessonCompleted" event should be published
    And a "CourseCompleted" event should be published
    And the course progress should show 100% completion

  @happy_path
  Scenario: Module completion percentage updates
    Given the user "member@example.com" is authenticated
    And a module exists with 4 lessons
    And the member has completed 2 lessons
    When the member requests the course details
    Then the module should show 50% completion

  @happy_path
  Scenario: Course completion percentage updates
    Given the user "member@example.com" is authenticated
    And a course exists with:
      | module   | lesson_count |
      | Module 1 | 3            |
      | Module 2 | 3            |
    And the member has completed 3 lessons
    When the member requests the course details
    Then the course should show 50% completion

  @happy_path
  Scenario: Progress is retained after course soft delete
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 5 lessons
    And the member has completed 3 lessons
    When the admin deletes the course "Python Basics"
    And the member requests their progress for "Python Basics"
    Then the progress should still show 3 completed lessons
    And the completion percentage should be 60%

  @edge_case
  Scenario: Next incomplete lesson is null when course is complete
    Given the user "member@example.com" is authenticated
    And a course "Python Basics" exists with 3 lessons
    And the member has completed all lessons
    When the member requests the course progress
    Then the next_incomplete_lesson_id should be null

  @edge_case
  Scenario: Progress excludes soft-deleted lessons from percentage
    Given the user "member@example.com" is authenticated
    And a course exists with 4 lessons
    And the member has completed 2 lessons
    When the admin deletes lesson 3
    And the member requests the course details
    Then the course should show 67% completion (2 of 3 remaining lessons)

  # =============================================================================
  # EMPTY STATES
  # =============================================================================

  @edge_case
  Scenario: Course with no modules shows empty state to member
    Given the user "member@example.com" is authenticated
    And a course "Empty Course" exists with no modules
    When the member views the course details
    Then the response should show "No content available yet"

  @edge_case
  Scenario: Module with no lessons shows empty state
    Given the user "member@example.com" is authenticated
    And a course exists with a module "Empty Module" that has no lessons
    When the member views the course details
    Then the module should show "No lessons yet"

  # =============================================================================
  # SECURITY
  # =============================================================================

  @security
  Scenario: Unauthenticated user cannot view courses
    Given an unauthenticated request
    When the request attempts to view the course list
    Then the request should fail with "authentication required" error

  @security
  Scenario: Non-admin cannot create a course
    Given the user "member@example.com" is authenticated
    And the user is not an admin
    When the user attempts to create a course
    Then the request should fail with "unauthorized" error

  @security
  Scenario: Non-admin cannot edit a course
    Given the user "member@example.com" is authenticated
    And the user is not an admin
    And a course "Python Basics" exists
    When the user attempts to edit the course
    Then the request should fail with "unauthorized" error

  @security
  Scenario: Non-admin cannot delete a course
    Given the user "member@example.com" is authenticated
    And the user is not an admin
    And a course "Python Basics" exists
    When the user attempts to delete the course
    Then the request should fail with "unauthorized" error

  @security
  Scenario: Non-admin cannot manage modules
    Given the user "member@example.com" is authenticated
    And the user is not an admin
    And a course "Python Basics" exists
    When the user attempts to add a module to the course
    Then the request should fail with "unauthorized" error

  @security
  Scenario: Non-admin cannot manage lessons
    Given the user "member@example.com" is authenticated
    And the user is not an admin
    And a module exists
    When the user attempts to add a lesson to the module
    Then the request should fail with "unauthorized" error

  @security
  Scenario: Rich text content is sanitized to prevent XSS
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin creates a text lesson with content "<script>alert('xss')</script>Hello"
    Then the lesson should be saved successfully
    And the content should be sanitized to remove script tags
    And the content should contain "Hello"

  @security
  Scenario: Video embed URLs are validated to prevent XSS
    Given the user "admin@example.com" is authenticated
    And a course exists with a module "Getting Started"
    When the admin attempts to create a video lesson with content "javascript:alert('xss')"
    Then lesson creation should fail with "invalid video URL" error

  @security
  Scenario: Member can only view their own progress
    Given the user "member@example.com" is authenticated
    And the user "other@example.com" exists with progress on "Python Basics"
    When the user "member@example.com" attempts to view progress of "other@example.com"
    Then the request should fail with "unauthorized" error

  @security
  Scenario: Course creation is rate limited
    Given the user "admin@example.com" is authenticated
    When the admin sends 20 course creation requests within 1 minute
    Then the requests should be rate limited after the threshold
    And subsequent requests should fail with "rate limit exceeded" error
