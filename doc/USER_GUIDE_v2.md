# Tiger OSINT User Guide
## AI-Powered Web Intelligence & Social Media Analysis Platform

**Version:** 2.0.0  
**Document Date:** March 6, 2026  
**Product:** Tiger OSINT - Defender Framework Tool

---

## Document Information

| Item | Details |
|------|---------|
| **Application Name** | Tiger OSINT |
| **Version** | 2.0.0 |
| **Platform Type** | Web-Based Intelligence Tool |
| **Deployment** | Cloud/On-Premise |
| **Support Contact** | saibalg@defendmycountry.com |
| **Developer** | Apt Software Avenues Pvt. Ltd. |
| **Framework** | Defender Framework |
| **Document Audience** | End Users, Analysts, Administrators |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [User Interface Overview](#3-user-interface-overview)
4. [Event Search & Analysis](#4-event-search--analysis)
5. [Social Media Intelligence](#5-social-media-intelligence)
6. [Results Management](#6-results-management)
7. [Data Export Features](#7-data-export-features)
8. [User Profile Management](#8-user-profile-management)
9. [LLM Configuration](#9-llm-configuration)
10. [Administrator Features](#10-administrator-features)
11. [Best Practices & Tips](#11-best-practices--tips)
12. [Troubleshooting](#12-troubleshooting)
13. [Frequently Asked Questions](#13-frequently-asked-questions)
14. [Glossary](#14-glossary)
15. [Support & Contact](#15-support--contact)

---

## 1. Introduction

### 1.1 About Tiger OSINT

Tiger OSINT is an advanced AI-powered web intelligence platform designed for open-source intelligence (OSINT) gathering, analysis, and reporting. Built on the Defender Framework, it combines cutting-edge artificial intelligence, natural language processing, and multi-source data aggregation to provide actionable intelligence from public sources.

### 1.2 Key Capabilities

**Intelligence Gathering**
- Multi-source web scraping with robots.txt compliance
- Real-time social media monitoring (YouTube, Twitter, Facebook, Instagram, Google)
- AI-powered event extraction and classification
- Entity recognition (people, organizations, locations)

**Analysis & Processing**
- Advanced LLM integration (Claude AI, Ollama)
- 23 event type classifications
- Relevance scoring and ranking
- Sentiment and engagement analysis
- Multi-platform content aggregation

**Data Management**
- Comprehensive filtering and search
- Pagination and sorting capabilities
- Excel export with full metadata
- Session-based result caching
- User activity tracking

**Security & Compliance**
- Role-based access control (User/Admin)
- Secure authentication system
- Usage tracking and cost monitoring
- Rate limiting and fair use policies

### 1.3 Use Cases

**Security & Intelligence**
- Monitor security incidents and threats
- Track protest and civil unrest activities
- Analyze cyber attack patterns
- Emergency response coordination

**Research & Analysis**
- Academic research data collection
- Market intelligence gathering
- Competitive analysis
- Trend monitoring and forecasting

**Media & Journalism**
- Story research and fact-checking
- Source verification
- Breaking news tracking
- Investigative journalism support

**Enterprise Applications**
- Brand reputation monitoring
- Crisis management support
- Compliance monitoring
- Risk assessment

### 1.4 System Requirements

**Browser Compatibility**
- Google Chrome 90+ (Recommended)
- Mozilla Firefox 88+
- Microsoft Edge 90+
- Safari 14+ (macOS)

**Network Requirements**
- Stable internet connection (minimum 5 Mbps)
- HTTPS access enabled
- JavaScript enabled
- Cookies enabled for session management

**Display Requirements**
- Minimum resolution: 1280x720
- Recommended resolution: 1920x1080 or higher
- Responsive design supports mobile devices

---

## 2. Getting Started

### 2.1 Accessing the Platform

1. **Open your web browser**
2. **Navigate to your organization's Tiger OSINT URL**
   - Example: `https://tigerosint.yourdomain.com`
   - Contact your administrator for the exact URL
3. **Verify SSL certificate** - Look for the padlock icon in the address bar

### 2.2 Initial Login

**Login Credentials**
- Your administrator will provide your login credentials
- Username: Your assigned email address
- Password: Temporary password (must be changed on first login)

**Login Process**
1. Enter your **Email Address** in the email field
2. Enter your **Password**
3. (Optional) Check **"Remember me"** for extended session (30 days)
4. Click **"Sign In"**

**First-Time Login**
- You will be prompted to change your temporary password
- Choose a strong password (see Password Requirements below)
- Update your profile information

**Password Requirements**
- Minimum 8 characters
- Must include uppercase letter
- Must include lowercase letter
- Must include number
- Must include special character (!@#$%^&*)

### 2.3 Dashboard Overview

After successful login, you'll see:

**Header Navigation**
- **Tiger OSINT Logo** - Click to return to home
- **User Display Name** - Shows your company/name/username
- **Profile Menu** - Access profile settings and password change
- **LLM Configuration** - Select AI model preferences
- **Logout** - End your session securely

**Main Search Interface**
- Search form with filters
- LLM model selector
- Search execution controls

**Footer Information**
- Developer credits
- Make in India branding
- Version information

### 2.4 User Roles

**Standard User**
- Access search and analysis features
- View and export results
- Manage personal profile
- Configure LLM preferences
- View personal usage statistics

**Administrator**
- All standard user features
- User management (create, edit, disable users)
- System-wide usage reports
- Cost tracking and analysis
- Platform statistics monitoring

---

## 3. User Interface Overview

### 3.1 Header Section

**Logo & Branding**
- Application identifier
- Quick home navigation

**User Information Display**
- Shows: Company name (if set) → Full name → Username (priority order)
- Indicates current logged-in user

**Profile Menu** (User Icon)
- Edit Profile
- Change Password
- View Usage Statistics (Standard users)
- Logout

**LLM Configuration Dropdown**
- Select AI provider (Claude/Ollama)
- Choose specific model
- View usage statistics
- Reset statistics (if permitted)

### 3.2 Search Form Components

**Main Search Field**
- Primary text input for search queries
- Placeholder text guides input format
- Supports complex query strings

**Social Media Platforms Selector**
- Multi-select checkboxes
- Platforms: YouTube, Twitter, Facebook, Instagram, Google
- Select all or targeted platforms

**Additional Filters**
- Location filter (city, state, country)
- Event type classification
- Date range selector (start and end dates)
- Number of results limiter

**Action Buttons**
- Search - Execute query
- Clear - Reset all fields
- Cancel - Stop ongoing search (appears during search)

### 3.3 Results Display Area

**Event Results**
- Event cards with complete information
- Relevance scoring indicators
- Sorting and filtering options
- Pagination controls (50 events per page)
- Selection checkboxes for export

**Social Media Results**
- Tabbed interface by platform
- Content cards with thumbnails
- Engagement metrics
- Load more functionality
- Content analysis options

**Progress Indicators**
- Real-time search progress bar
- Status messages
- Article count updates
- Completion notifications

### 3.4 Footer Section

**Branding**
- Make in India logo
- Developer information
- Defender Framework branding

---

## 4. Event Search & Analysis

### 4.1 Basic Event Search

**Simple Search**
1. Enter search phrase in main text field
   - Example: `"cyber attack on banks"`
   - Example: `"protest in Mumbai"`
2. Click **Search** button
3. Wait for results (typically 30-60 seconds)

**Search Query Best Practices**
- Use specific phrases, not single keywords
- Include context words for better relevance
- Use quotes for exact phrase matching
- Combine location with event type

**Examples of Effective Queries**
```
✓ "data breach healthcare companies India"
✓ "political rally violence Delhi"
✓ "cyber attack financial sector"
✓ "earthquake damage Kashmir region"

✗ "attack" (too broad)
✗ "news" (no specific event)
✗ "India" (too general)
```

### 4.2 Advanced Filtering

**Location Filter**

Narrow results to specific geographic areas:

```
City Level:     Mumbai, Delhi, Bangalore
State/Province: Maharashtra, California, Tamil Nadu
Country:        India, United States, United Kingdom
Region:         Middle East, Southeast Asia
Virtual:        Online, Cyberspace
```

**How it works:**
- Searches the event location fields
- Accepts partial matches
- Case-insensitive search
- Checks city, state, and country fields

**Event Type Classification**

23 event types across 7 major categories:

**Violence & Security Events**
- Protest - Organized public demonstrations
- Demonstration - Public displays of opinion
- Attack - Physical attacks on people/property
- Explosion - Explosive incidents
- Bombing - IED or bomb attacks
- Shooting - Firearm-related incidents
- Theft - Robbery and theft incidents
- Kidnapping - Abduction cases

**Cyber Events**
- Cyber Attack - Malicious cyber operations
- Cyber Incident - Security breaches
- Data Breach - Unauthorized data access

**Meetings & Conferences**
- Conference - Professional conferences
- Meeting - Official meetings
- Summit - High-level diplomatic meetings

**Disasters & Accidents**
- Accident - Unintentional incidents
- Natural Disaster - Earthquakes, floods, etc.

**Political & Military**
- Election - Electoral events
- Political Event - Political activities
- Military Operation - Military actions

**Crisis Events**
- Terrorist Activity - Terrorism-related events
- Civil Unrest - Social disorder
- Humanitarian Crisis - Large-scale emergencies

**Other**
- Other - Events not fitting other categories

**Date Range Filter**

Limit results to specific time periods:

**Date Format:** YYYY-MM-DD (e.g., 2026-03-06)

**Filter Options:**
- **Start Date Only** - Events on or after date
- **End Date Only** - Events on or before date
- **Date Range** - Events between two dates
- **Specific Date** - Set same start and end date

**Common Date Ranges:**
```
Last Week:     2026-02-27 to 2026-03-06
Last Month:    2026-02-01 to 2026-02-28
Last Quarter:  2026-01-01 to 2026-03-31
Last Year:     2025-01-01 to 2025-12-31
Specific Event: 2026-01-15 to 2026-01-15
```

### 4.3 Search Execution

**During Search**
- Progress bar shows completion status
- Real-time updates on articles scraped
- Current processing stage displayed
- Cancel button available to stop search

**Progress Stages:**
1. Fetching articles from sources
2. Scraping content
3. Extracting events with AI
4. Calculating relevance scores
5. Preparing results

**Search Metrics Displayed:**
- Total articles found
- Articles successfully scraped
- Events extracted
- Processing time
- Matching events count

### 4.4 Understanding Results

**Event Card Structure**

Each event displays:

**Header Section**
- ☑ Selection checkbox
- Event title (clickable link to source)
- Event type chip (color-coded)

**Event Details**
- 📅 **Date:** Event occurrence date
- 📍 **Location:** City, State, Country
- 🏢 **Organizer:** Responsible organization (if applicable)
- 🏛️ **Venue:** Specific location (if available)

**Description**
- AI-generated event summary
- 2-4 sentence overview
- Key facts and participants

**Metadata**
- **Relevance Score:** 0-100% match quality
  - 🟢 70-100%: High relevance
  - 🟠 50-69%: Medium relevance
  - ⚪ 0-49%: Low relevance
- **Source:** Original article link with timestamp
- **Event URL:** Direct event link (if different from source)

**Relevance Scoring**

How relevance is calculated:
- Keyword match in title and description
- Event type match
- Location match criteria
- Date range compliance
- Entity extraction confidence
- Source credibility

**Result Statistics**

Top banner shows:
```
Found X matching events from Y extracted events
(Z articles scraped). Processing time: AA.BB seconds
```

- **Matching Events:** Events fitting all filter criteria
- **Extracted Events:** Total AI-detected events
- **Articles Scraped:** Source articles processed
- **Processing Time:** Total search duration

---

## 5. Social Media Intelligence

### 5.1 Social Media Search

**Supported Platforms**
- **YouTube** - Videos, channels, comments
- **Twitter (X)** - Posts, threads, user profiles
- **Facebook** - Public posts, pages, groups
- **Instagram** - Public posts, profiles, hashtags
- **Google** - Web results, blogs, news

**Social Search Process**

1. **Enable Platform Selection**
   - Check desired platform boxes in search form
   - Can select single or multiple platforms
   - All platforms selected by default

2. **Execute Search**
   - Social search runs parallel to event search
   - Results appear in separate panel
   - Platform-specific result counts displayed

3. **View Platform Results**
   - Tabbed interface by platform
   - Badge shows result count per platform
   - "All" tab shows combined results

### 5.2 Social Results Panel

**Result Card Components**

Each social media result shows:

**Image/Thumbnail**
- Platform-specific visual content
- Video thumbnails for YouTube
- Post images for Instagram/Facebook
- Profile pictures for Twitter

**Content Preview**
- Title/headline
- Description snippet (first 200 characters)
- Author/channel information
- Publication date

**Platform Identifier**
- Color-coded platform icon
- Platform name chip
- Source site link

**Engagement Metrics** (when available)
- Views count
- Likes count
- Comments count
- Shares/retweets count
- Engagement rate calculation

**Action Buttons**
- **View Details** - Open full content in modal
- **Analyze** - AI analysis of content
- **Open Original** - External link to platform

### 5.3 Content Analysis

**Fetch Full Content**

1. Click **"View Details"** on any social result
2. System fetches complete content from platform
3. Modal displays full post/video details

**Content Details Available:**

**YouTube Videos**
- Full title and description
- Video duration
- Upload date and channel info
- View count, likes, comments
- Video thumbnail
- Category and tags
- Channel subscriber count

**Twitter Posts**
- Complete tweet thread
- User profile information
- Engagement metrics
- Media attachments
- Retweet and quote counts
- Posted timestamp

**Facebook Posts**
- Full post text
- Media attachments
- Reaction counts
- Comment count
- Share count
- Page/profile information

**Instagram Posts**
- Caption and hashtags
- Image/video content
- Like and comment counts
- Posted date
- Profile information

**AI Content Analysis**

Click **"Analyze"** button to:
- Extract key entities (people, organizations, locations)
- Identify event types mentioned
- Summarize main points
- Detect sentiment
- Highlight important dates
- Extract relevant URLs

**Analysis Results Display:**
- AI-generated summary
- Entity extraction results
- Event type classification
- Key insights
- Processing status

### 5.4 Load More Results

**Per-Platform Pagination**

Each platform supports loading additional results:

**Load More Process:**
1. Scroll to platform tab
2. Click **"Load More Results"** button
3. System fetches next 10 results
4. New results append to existing list
5. Button updates with new count

**Result Limits:**
- Google Custom Search API limit: 100 results per platform
- Results loaded in batches of 10
- Exhausted platforms show "No more results" message
- Load more button disabled when limit reached

**Platform Exhaustion Indicators:**
- Button changes to "No More Results"
- Information tooltip explains limit
- Platform badge indicates exhaustion status

---

## 6. Results Management

### 6.1 Viewing Results

**Event List Display**

**Layout:**
- Centered content area (66% width on desktop)
- Paper elevation for depth
- Responsive design for mobile/tablet

**Statistics Header:**
- Total events found
- Current page range display
- Page indicator (e.g., "Showing 1-50 of 247")

**Control Panel:**
- Sort dropdown
- Selection buttons
- Export controls
- Pagination

### 6.2 Sorting Results

**Sort Options**

**By Relevance** (Default)
- Highest relevance score first
- Best for finding most matching results
- Recommended for initial review

**By Date**
- Earliest date first (ascending chronological)
- Best for timeline analysis
- Useful for tracking event progression

**By Title**
- Alphabetical order (A-Z)
- Best for scanning large result sets
- Useful for grouping similar events

**How to Sort:**
1. Click **"Sort By"** dropdown
2. Select desired option
3. Results reorder immediately
4. Sort preference persists during session

### 6.3 Selecting Events

**Selection Methods**

**Individual Selection**
- Click checkbox on event card
- Or click anywhere on card to toggle
- Selected cards highlight in blue

**Page Selection**
- Click **"Page"** button
- Selects all events on current page only
- Useful for bulk operations per page

**Global Selection**
- Click **"All"** button
- Selects all events across all pages
- Selection count updates in alert

**Deselection**
- Click **"Clear"** button
- Removes all selections
- Confirmation not required

**Selection Indicator**
Blue alert displays: "X events selected for export"

### 6.4 Pagination

**Navigation Controls**

Located at bottom of event list:

**Elements:**
- Page number buttons (1, 2, 3, ...)
- Previous/Next arrows
- Current page highlighted
- Total page count displayed

**Page Settings:**
- 50 events per page (fixed)
- Optimized for performance
- Smooth scroll to top on page change

**Pagination Behavior:**
- Selection persists across pages
- Sort order maintained
- Filters remain applied
- Current page stored in session

---

## 7. Data Export Features

### 7.1 Excel Export

**Export Options**

**Export All Events**
- No events selected
- Click **"Export All to Excel"**
- Downloads complete result set

**Export Selected Events**
- Select desired events (one or more)
- Click **"Export X Selected to Excel"**
- Downloads only selected events

**Export Process:**
1. Click appropriate export button
2. Processing indicator appears
3. File downloads automatically
4. Success notification displayed

### 7.2 Excel File Structure

**Spreadsheet Columns**

| Column Name | Description | Example |
|-------------|-------------|---------|
| Title | Event headline/title | "Cyber Attack on Banking Sector" |
| Date | Event date | 2026-03-06 |
| City | City name | Mumbai |
| State | State/province | Maharashtra |
| Country | Country name | India |
| Venue | Specific location | "Reserve Bank of India Building" |
| Event Type | Classification | Cyber Attack |
| Description | Event summary | AI-generated 2-4 sentence summary |
| Organizer | Responsible entity | "Hacker Group XYZ" |
| Relevance Score | Match percentage | 87.5 |
| Source URL | Original article link | https://news.example.com/... |
| Event URL | Direct event URL | https://event.example.com/... |
| Extraction Confidence | AI confidence score | 95.0 |
| Created At | Timestamp | 2026-03-06T10:30:00Z |

**File Properties**
- Format: .xlsx (Excel 2007+)
- Compatibility: Excel, LibreOffice, Google Sheets
- Encoding: UTF-8
- Styling: Header row formatted, auto-width columns

### 7.3 File Naming Convention

**Automatic Naming:**
```
events_[search_phrase]_[date].xlsx
```

**Examples:**
```
events_cyber_attack_banks_2026-03-06.xlsx
events_protest_mumbai_2026-03-06.xlsx
events_export_2026-03-06.xlsx
```

**Naming Rules:**
- Spaces replaced with underscores
- Special characters removed
- Date in YYYY-MM-DD format
- Maximum 255 characters
- Unique timestamp prevents overwrites

### 7.4 Post-Export Analysis

**Working with Exported Data**

**In Microsoft Excel:**
- Apply additional filters
- Create pivot tables
- Generate charts and graphs
- Conditional formatting
- Advanced formulas

**In Google Sheets:**
- Cloud-based collaboration
- Share with team members
- Real-time co-editing
- Integration with Google services

**Data Analysis Tips:**
- Sort by relevance score for quality review
- Filter by location for geographic analysis
- Group by event type for pattern detection
- Time-series analysis using date field
- Entity extraction from descriptions

---

## 8. User Profile Management

### 8.1 Viewing Profile

**Access Profile**
1. Click **user icon** in top-right header
2. Select **"Edit Profile"** from dropdown menu
3. Profile dialog opens

**Profile Information Displayed:**
- Email address (read-only)
- Username (read-only)
- Full name (editable)
- Company name (editable)
- Profile image (editable)
- Account creation date
- Last login timestamp

### 8.2 Editing Profile

**Editable Fields**

**Full Name**
- Your complete name
- Used in display if company not set
- Optional but recommended

**Company Name**
- Your organization name
- Highest priority for display
- Appears in header if set

**Profile Image**
- Supports: JPG, PNG, GIF
- Maximum size: 5 MB
- Recommended: 200x200 pixels
- Displays as avatar in header

**Profile Image Upload:**
1. Click **"Choose File"** or **"Upload Image"** button
2. Select image from computer
3. Preview displays immediately
4. Image encodes to base64
5. Stores in user profile

**How to Update:**
1. Click **"Edit Profile"** in profile menu
2. Modify desired fields
3. Upload new image (optional)
4. Click **"Save Changes"**
5. Confirmation message appears
6. Profile updates immediately

**Name Display Priority:**
```
1. Company name (if set)
2. Full name (if set, no company)
3. Username (if neither set)
```

### 8.3 Changing Password

**Password Change Process**

**Access:**
1. Click user icon in header
2. Select **"Change Password"**
3. Password dialog opens

**Required Fields:**
- **Old Password** - Your current password
- **New Password** - Your desired new password
- **Confirm Password** - Re-enter new password

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*)
- Cannot be same as old password
- Passwords must match

**Show/Hide Password:**
- Click eye icon to reveal password
- Click again to hide
- Available for all three fields

**Steps:**
1. Enter current password
2. Enter new password (meets requirements)
3. Re-enter new password (must match)
4. Click **"Change Password"**
5. Success confirmation or error message
6. Dialog closes automatically on success

**Security Notes:**
- Old password verified before change
- Failed attempts logged
- Password encrypted before storage
- Session continues after change
- No forced re-login required

### 8.4 Usage Statistics (Standard Users)

**Personal Usage Report**

Access via Profile Menu → **"View Usage"**

**Statistics Available:**

**Current Month Summary:**
- Total searches performed
- Social media searches by platform
  - YouTube searches
  - Twitter searches
  - Facebook searches
  - Instagram searches
  - Google searches
- Total articles scraped
- Events extracted
- Data exported

**Historical Trends:**
- Month-over-month comparison
- Usage patterns
- Peak activity periods

**Cost Information:** (if enabled by admin)
- Estimated usage cost
- API call consumption
- LLM token usage

---

## 9. LLM Configuration

### 9.1 Understanding LLM

**What is LLM?**

LLM (Large Language Model) is the AI engine that powers:
- Event extraction from articles
- Content summarization
- Entity recognition
- Relevance scoring
- Social media content analysis

**Available Providers**

**Claude AI** (Anthropic)
- Cloud-based AI service
- Latest models: Claude 3.5 Haiku, Claude 3.5 Sonnet
- High accuracy and reliability
- Pay-per-use pricing
- Internet connection required

**Ollama** (Local LLM)
- Self-hosted AI models
- Models: Llama 3.1, Qwen 2.5, others
- No per-use cost after setup
- Privacy-focused (data stays local)
- No internet required for inference

### 9.2 Selecting LLM Provider

**Access LLM Configuration**
1. Click **"Configure"** dropdown in header
2. LLM configuration panel expands

**Configuration Options:**

**Provider Selection**
- Click dropdown: "Claude" or "Ollama"
- Available models update automatically
- Default models pre-selected

**Model Selection**
- Choose specific model version
- Model descriptions displayed
- Performance characteristics shown
- Pricing information (for Claude)

**Available Claude Models:**
- **Claude 3.5 Haiku** (Default)
  - Fast and efficient
  - Lower cost
  - Good for high-volume processing
  
- **Claude 3.5 Sonnet**
  - Higher accuracy
  - Better reasoning
  - Recommended for complex analysis

**Available Ollama Models:**
- **Qwen 2.5:3b** (Default - lightweight)
- **Llama 3.1:8b** (Balanced)
- **Other models** (as configured by admin)

### 9.3 Usage Statistics

**LLM Usage Panel**

Located in LLM Configuration dropdown:

**Metrics Displayed:**

**Request Statistics:**
- Total requests made
- Successful requests
- Failed requests
- Average response time

**Token Usage** (Claude only):
- Input tokens consumed
- Output tokens generated
- Cached tokens used
- Cache hit rate

**Cost Information** (Claude only):
- Total cost (USD)
- Cost per request
- Cache savings
- Monthly spend

**Pricing Details:**
- Input tokens: $X per 1M tokens
- Output tokens: $Y per 1M tokens
- Cache discount: Z% off
- Detailed breakdown available

### 9.4 Resetting Statistics

**When to Reset:**
- Start of new billing period
- After major changes
- For testing purposes
- Monthly reporting cycles

**How to Reset:**
1. Click **"Configure"** in header
2. Expand LLM configuration panel
3. Click **"Reset Statistics"** button
4. Confirm action in prompt
5. Statistics reset to zero
6. Confirmation message displayed

**Note:** Only resets display statistics, not actual usage billing

---

## 10. Administrator Features

*This section is only accessible to users with Administrator role*

### 10.1 Admin Dashboard Access

**Accessing Admin Panel**
- Administrators automatically redirect to admin dashboard after login
- Standard users cannot access admin features

**Dashboard Tabs:**
1. **Users** - User management
2. **Usage Reports** - System-wide usage analytics

### 10.2 User Management

**User List View**

Displays all system users in table format:

**Columns:**
- Profile image avatar
- Username
- Email address
- Full name
- Company
- Role (User/Admin)
- Status (Active/Inactive)
- Created date
- Last login
- Actions (Edit/Delete)

**User Actions**

**Create New User**
1. Click **"Add User"** button
2. Fill registration form:
   - Email (required, must be unique)
   - Username (required, must be unique)
   - Password (required, follows strength rules)
   - Full name (optional)
   - Company (optional)
3. Set role: User or Admin
4. Set status: Active or Inactive
5. Click **"Create User"**
6. User receives credentials (if email configured)

**Edit Existing User**
1. Click **edit icon** (pencil) in Actions column
2. Modify details:
   - Full name
   - Company
   - Role (User ⟷ Admin)
   - Status (Active ⟷ Inactive)
   - Profile image URL
3. Cannot edit: email, username, password
4. Click **"Update User"**
5. Changes apply immediately

**Delete User**
1. Click **delete icon** (trash) in Actions column
2. Confirmation dialog appears
3. Review user details
4. Click **"Delete"** to confirm
5. User permanently removed
6. User's search history retained for auditing

**User Status Management**

**Active Users:**
- Can log in and use system
- All features available
- Usage counted in reports

**Inactive Users:**
- Cannot log in
- Existing sessions terminated
- Data preserved
- Can be reactivated

**Change User Password**
1. Click edit icon for user
2. Click **"Change Password"** button in dialog
3. Enter new password (admin provides)
4. User must change on next login
5. Temporary password can be communicated securely

### 10.3 Usage Reports

**Report Types**

**Monthly Summary Reports**
- Select month/year from dropdown
- System-wide aggregated metrics
- Cost analysis
- Platform breakdown

**User-Specific Reports**
- Select user from dropdown
- Select month/year
- Individual usage patterns
- Cost allocation

**Metrics Tracked**

**Search Activity:**
- Total searches performed
- Searches by platform:
  - YouTube searches
  - Twitter searches
  - Facebook searches
  - Instagram searches
  - Google searches
- Search success rate
- Average results per search

**Scraping Activity:**
- Total articles scraped
- Paid vs. free scraping
- Source breakdown
- Failed scrape attempts
- Robots.txt compliance rate

**Analysis Activity:**
- Total AI analyses performed
- Events extracted
- Entity recognitions
- Content summarizations
- Average confidence scores

**API Usage:**
- Google Custom Search API calls
- ScrapeCreators credits consumed
- Claude API requests
- Token consumption

**Cost Breakdown:**
- Total monthly cost (USD)
- Cost by service:
  - Google CSE: $0 (first 100), $5/1000 queries after
  - YouTube (free): $0
  - Twitter, Facebook, Instagram: $0.001 per fetch
  - Claude API: Token-based pricing
- Daily cost trends
- User-wise cost allocation
- Cost projections

**Report Features:**

**Tabular Display:**
- Sortable columns
- Date range filtering
- Export to Excel (future feature)

**Daily Breakdown:**
- Drill down into specific days
- Hourly usage patterns
- Peak usage identification

**Visualizations:**
- Cost trend graphs (future feature)
- Platform usage pie charts (future feature)
- User activity heatmaps (future feature)

### 10.4 System Statistics

**Overview Metrics**

Displayed at top of admin dashboard:

- Total registered users
- Active users count
- Total searches today
- Total searches this month
- Current month cost
- System uptime
- Database size

**Health Monitoring**

- API connectivity status
- LLM provider status
- Database status
- Cache performance
- Error rates

---

## 11. Best Practices & Tips

### 11.1 Effective Searching

**Query Optimization**

**DO:**
✓ Be specific with 3-5 relevant keywords
✓ Use location qualifiers
✓ Include event type in query
✓ Use date filters for recent events
✓ Combine filters for precision

**DON'T:**
✗ Use single generic words
✗ Search without context
✗ Ignore relevance scores
✗ Export without reviewing
✗ Overuse wildcards

**Example Query Progressions:**

**Scenario: Track cybersecurity incidents**

```
Attempt 1: "cyber attack"
Result: Too broad, 500+ results

Attempt 2: "cyber attack banks India"
Result: Better, 67 results

Attempt 3: "cyber attack banks India" + Event Type: Cyber Attack
Result: Refined, 34 results

Attempt 4: Above + Date: Last 30 days
Result: Focused, 12 results ✓
```

### 11.2 Social Media Monitoring

**Platform-Specific Strategies**

**YouTube Monitoring:**
- Search video titles and descriptions
- Filter by upload date
- Monitor specific channels
- Track comment sentiment
- Identify trending topics

**Twitter (X) Monitoring:**
- Track real-time events
- Monitor hashtags
- Identify influencers
- Detect viral content
- Sentiment analysis

**Facebook Monitoring:**
- Public page monitoring
- Group activity tracking
- Event announcements
- Community sentiment

**Instagram Monitoring:**
- Visual content analysis
- Hashtag trending
- Story monitoring (if accessible)
- Influencer activity

### 11.3 Data Quality Management

**Result Validation**

**Always:**
- Review relevance scores
- Check source credibility
- Verify dates and locations
- Cross-reference multiple sources
- Validate with original articles

**Quality Indicators:**
- Relevance score ≥ 70%
- Complete event details
- Credible source domain
- Recent publication date
- Multiple corroborating sources

**False Positive Identification:**
- Low relevance score (< 40%)
- Vague or generic descriptions
- Incorrect event type classification
- Location mismatches
- Outdated information

### 11.4 Export Best Practices

**Before Exporting:**
1. Review all selected events
2. Verify relevance scores
3. Remove false positives
4. Sort by priority criteria
5. Check completeness

**File Management:**
- Use descriptive filenames
- Organize by date/topic
- Maintain version control
- Backup important exports
- Document export criteria

**Post-Export:**
- Validate data integrity
- Remove duplicate entries
- Enrich with additional data
- Share with appropriate stakeholders
- Archive for future reference

### 11.5 Performance Optimization

**Faster Searches:**
- Use specific date ranges
- Limit number of sources
- Select targeted platforms
- Apply filters upfront
- Cache common queries

**Manage Large Result Sets:**
- Use pagination effectively
- Filter before export
- Sort by relevance first
- Export in batches
- Process incrementally

### 11.6 Security & Privacy

**Account Security:**
- Use strong, unique passwords
- Change password periodically
- Never share credentials
- Log out on shared computers
- Report suspicious activity

**Data Handling:**
- Follow organizational policies
- Protect sensitive information
- Secure exported files
- Limit data sharing
- Comply with privacy regulations

**Responsible Use:**
- Respect rate limits
- Don't circumvent restrictions
- Follow terms of service
- Ethical OSINT practices
- Attribution to sources

---

## 12. Troubleshooting

### 12.1 Login Issues

**Problem: Cannot Login**

**Symptoms:**
- "Incorrect email or password" error
- Login button not responding
- Blank screen after login

**Solutions:**
1. Verify credentials (check caps lock)
2. Clear browser cache and cookies
3. Try different browser
4. Reset password via admin
5. Check internet connection
6. Verify account is active (contact admin)

**Problem: "Account Disabled" Message**

**Solution:**
Contact your administrator to activate your account

**Problem: Password Reset Not Working**

**Solution:**
1. Ensure old password is correct
2. Meet password strength requirements
3. Confirm both new passwords match
4. Contact admin for password reset

### 12.2 Search Issues

**Problem: No Results Found**

**Possible Causes & Solutions:**

1. **Query too specific**
   - Broaden search terms
   - Remove some filters
   - Try synonyms

2. **Date range too narrow**
   - Expand date range
   - Remove date filter
   - Try different time periods

3. **No sources configured**
   - Contact administrator
   - Verify source configuration

4. **Network/API issues**
   - Check internet connection
   - Retry search
   - Contact support if persists

**Problem: Search Takes Too Long (> 2 minutes)**

**Solutions:**
1. Wait for completion (can take up to 5 minutes)
2. Use Cancel button if needed
3. Narrow search criteria for next attempt
4. Check server load with admin
5. Try during off-peak hours

**Problem: Search Stops/Hangs**

**Solutions:**
1. Click Cancel button
2. Refresh page
3. Clear browser cache
4. Try again with fewer filters
5. Report to administrator if recurring

**Problem: Irrelevant Results**

**Solutions:**
1. Review and refine search query
2. Add event type filter
3. Use location filter
4. Check relevance scores
5. Sort by relevance
6. Use more specific keywords

### 12.3 Social Media Issues

**Problem: Social Results Not Loading**

**Possible Causes:**
1. Platform API limits reached (daily quotas)
2. Network connectivity issues
3. Platform temporarily unavailable
4. API keys not configured (contact admin)

**Solutions:**
1. Wait and retry later
2. Try different platform
3. Check platform status pages
4. Contact administrator

**Problem: "No More Results" Appears Too Early**

**Explanation:**
- Google Custom Search API limited to 100 results per platform
- This is a platform limitation, not a bug

**Workaround:**
Refine search query to get more relevant top results

**Problem: Content Analysis Fails**

**Solutions:**
1. Retry analysis
2. Check if content still available
3. Try different content
4. Report persistent issues
5. Check LLM configuration

### 12.4 Export Issues

**Problem: Export Button Disabled**

**Causes:**
- No events in results
- Export already in progress
- Browser blocking download

**Solutions:**
1. Wait for current export to complete
2. Check popup blocker settings
3. Ensure events are loaded
4. Try different browser

**Problem: Downloaded File Won't Open**

**Solutions:**
1. Verify file downloaded completely
2. Check file extension (.xlsx)
3. Install/update Excel or LibreOffice
4. Try Google Sheets online
5. Re-download file

**Problem: Export Shows "Failed"**

**Solutions:**
1. Check internet connection
2. Retry export
3. Try exporting fewer events
4. Clear browser cache
5. Contact support with error details

### 12.5 Performance Issues

**Problem: Slow Page Loading**

**Solutions:**
1. Check internet speed
2. Close unnecessary browser tabs
3. Clear browser cache
4. Disable browser extensions
5. Try different browser

**Problem: UI Not Responding**

**Solutions:**
1. Wait for current operation to complete
2. Refresh page (may lose unsaved work)
3. Close and reopen browser
4. Check system resources
5. Report to administrator

**Problem: Results Not Displaying**

**Solutions:**
1. Wait for complete load
2. Scroll down page
3. Check browser console for errors (F12)
4. Refresh page
5. Try different browser

### 12.6 General Error Messages

**"Session Expired - Please Login Again"**
- Your session timed out
- Click OK and log in again
- Sessions last 24 hours (or 30 days with "Remember Me")

**"Server Error - Please Try Again"**
- Temporary server issue
- Wait a moment and retry
- If persists, contact support

**"Rate Limit Exceeded"**
- Too many requests in short time
- Wait 5-10 minutes
- Retry operation
- If urgent, contact admin

**"Unable to Connect to Server"**
- Network connectivity issue
- Check internet connection
- Verify URL is correct
- Check if server is operational
- Contact IT support

---

## 13. Frequently Asked Questions

### 13.1 General Questions

**Q: How current is the data?**
A: Data sources are scraped in real-time during searches. Social media results reflect current publicly available content. Event extraction depends on when articles were published.

**Q: Can I save my searches?**
A: Currently, searches are not saved permanently. Results are session-based. Export your results to Excel for permanent storage.

**Q: Is there a mobile app?**
A: There is no dedicated mobile app, but the web interface is responsive and works on mobile browsers. Desktop/tablet recommended for best experience.

**Q: How many searches can I perform?**
A: No hard limit for standard users, but admins can set quotas. Excessive use may trigger rate limiting. Check with your administrator for organizational policies.

**Q: Can I use this for commercial purposes?**
A: Depends on your organization's license. Consult with your administrator regarding permitted use cases.

### 13.2 Search & Results

**Q: Why do some events have low relevance scores?**
A: The AI extracts all potential events from articles. Lower scores indicate weaker match to your query criteria. Filter by relevance score ≥ 70% for best results.

**Q: How many results can I get per search?**
A: No fixed limit for event extraction. Social media limited to 100 results per platform due to API restrictions. Event results depend on sources and date range.

**Q: Can I search in languages other than English?**
A: Currently optimized for English. Some support for other languages if sources and LLM support them, but accuracy may vary.

**Q: Why are some event details missing (like venue or organizer)?**
A: AI extracts what's available in source articles. Missing fields indicate information wasn't present or couldn't be reliably extracted.

**Q: How accurate is the event extraction?**
A: Accuracy depends on LLM model used and source quality. Claude models: 85-95% accuracy. Ollama models: 70-85% accuracy. Always verify critical information.

### 13.3 Social Media

**Q: Why can't I see private social media posts?**
A: System only accesses publicly available content. Private posts, stories, and restricted content are not accessible.

**Q: Do I need social media accounts to search?**
A: No. The system uses API access and doesn't require your personal social media accounts.

**Q: Why are engagement metrics sometimes missing?**
A: Platform APIs don't always provide complete metrics. Some counts may be unavailable or restricted by privacy settings.

**Q: Can I monitor specific accounts or hashtags?**
A: Currently, searches are keyword-based. Include account names or hashtags in your search query to find related content.

**Q: What's the difference between "Fetch Content" and "Analyse"?**
A: "Fetch" retrieves full content from platform. "Analyse" applies AI to extract entities, events, and insights from that content.

### 13.4 Export & Data

**Q: Can I export to formats other than Excel?**
A: Currently only Excel (.xlsx) is supported. You can open .xlsx files and save as CSV in Excel/LibreOffice if needed.

**Q: Is there a limit on export size?**
A: Typically limited to 1000 events per export for performance. If you need more, export in multiple batches.

**Q: Can I customize export columns?**
A: Currently all columns are exported. You can hide unwanted columns in Excel after export.

**Q: Are timestamps in my local timezone?**
A: Timestamps are in UTC. Convert to your timezone in Excel using timezone formulas.

**Q: Can I schedule automated exports?**
A: Not currently available in the UI. Contact administrator about API access for automated workflows.

### 13.5 Account & Security

**Q: How long do sessions last?**
A: 24 hours for regular login, 30 days with "Remember Me" checked. Sessions terminate on logout.

**Q: Can I have multiple sessions?**
A: Yes, you can log in from multiple devices/browsers simultaneously.

**Q: Who can see my search history?**
A: Administrators can view usage statistics (counts, not specific queries). Search content is not logged for standard users.

**Q: Is my data encrypted?**
A: Yes, all communication uses HTTPS/TLS encryption. Passwords are hashed. APIs use secure keys.

**Q: Can I delete my account?**
A: Contact your administrator. Administrators can deactivate or delete accounts.

### 13.6 Technical

**Q: What browsers are supported?**
A: Chrome 90+, Firefox 88+, Edge 90+, Safari 14+. Chrome recommended for best experience.

**Q: Do I need to install anything?**
A: No, it's web-based. Just a modern browser and internet connection.

**Q: Why does LLM configuration matter?**
A: Different models have different accuracy, speed, and cost. Claude is more accurate but costs per use. Ollama is free but may be less accurate for complex tasks.

**Q: What happens if I lose internet connection during a search?**
A: Search will fail. Results obtained before disconnection may be lost. Stable connection recommended.

**Q: Can I use this offline?**
A: No, internet connection required. Some features like Ollama LLM can work with local models, but scraping requires internet.

---

## 14. Glossary

**AI (Artificial Intelligence)**
Computer systems that perform tasks normally requiring human intelligence, such as understanding natural language, recognizing patterns, and making decisions.

**API (Application Programming Interface)**
A set of protocols that allow different software applications to communicate. Tiger OSINT uses APIs to access social media platforms and AI services.

**Cache**
Temporary storage of data for faster retrieval. Tiger OSINT caches social media content and search results.

**Claude AI**
Anthropic's large language model family used for event extraction and content analysis. Available models include Haiku and Sonnet.

**Confidence Score**
A percentage (0-100%) indicating how confident the AI is in its extraction or classification. Higher scores indicate greater certainty.

**Entity**
A specific item identified in text, such as a person, organization, location, or date. Extracted using Named Entity Recognition (NER).

**Event Extraction**
The AI process of identifying and structuring event information from unstructured text (articles, posts).

**Event Type**
Classification category for events (e.g., Protest, Cyber Attack, Conference). System supports 23 types across 7 categories.

**Excel Export**
Feature to download search results as an Excel spreadsheet (.xlsx file) for offline analysis.

**LLM (Large Language Model)**
Advanced AI models trained on vast text data to understand and generate human-like text. Used for content analysis and event extraction.

**NER (Named Entity Recognition)**
NLP technique to identify and classify entities (people, places, organizations) in text.

**NLP (Natural Language Processing)**
Subfield of AI focused on enabling computers to understand, interpret, and generate human language.

**Ollama**
Open-source platform for running large language models locally. Alternative to cloud-based Claude AI.

**OSINT (Open Source Intelligence)**
Intelligence gathered from publicly available sources, including websites, social media, and public databases.

**Pagination**
Dividing large result sets into smaller pages (50 events per page) for easier viewing and better performance.

**Rate Limiting**
Restriction on number of requests in a given time period to prevent server overload and ensure fair use.

**Relevance Score**
Percentage (0-100%) indicating how well a result matches your search criteria. Higher scores indicate better matches.

**Robots.txt**
File on websites specifying which parts can be accessed by automated tools. Tiger OSINT respects these rules.

**Scraping**
Automated extraction of data from websites. Tiger OSINT scrapes news articles for event information.

**Session**
Period of activity between login and logout. Used to maintain your state and cache results.

**Social Media Intelligence**
Intelligence gathered from social media platforms (YouTube, Twitter, Facebook, Instagram).

**Source**
Website or news provider configured in the system for article scraping.

**Token**
Unit of text processed by LLMs, roughly equivalent to a word or word fragment. Usage and costs calculated in tokens.

**UTC (Coordinated Universal Time)**
Global time standard timezone (equivalent to GMT+0). All timestamps in Tiger OSINT use UTC.

---

## 15. Support & Contact

### 15.1 Getting Help

**Support Channels**

**Primary Contact:**
- **Email:** saibalg@defendmycountry.com
- **Response Time:** Within 24 business hours

**Include in Support Requests:**
1. Your username (not password)
2. Detailed description of issue
3. Steps to reproduce problem
4. Browser and version
5. Screenshots (if relevant)
6. Error messages (exact text)
7. Date/time of occurrence

**Support Request Template:**
```
Subject: [Tiger OSINT] - Brief Issue Description

Username: your_username@example.com
Browser: Chrome 120.0.6099.109
Date/Time: 2026-03-06 14:30 UTC
Issue Type: [Login/Search/Export/Performance/Other]

Description:
[Detailed description of the issue]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Result:
[What should happen]

Actual Result:
[What actually happens]

Error Message (if any):
[Exact error text]

Screenshots:
[Attached if relevant]
```

### 15.2 Administrator Contact

For administrative matters:
- User account issues (activation, reset)
- Access permissions
- Organizational policy questions
- Usage quota inquiries
- Billing questions
- Feature requests

Contact your organization's Tiger OSINT administrator.

### 15.3 Training & Documentation

**Available Resources:**

**Documentation:**
- This User Guide (latest version)
- API Documentation (for developers)
- Deployment Guide (for administrators)
- Source Code Documentation (GitHub)

**Training Materials:** (if available)
- Video tutorials
- Webinar recordings
- Quick start guides
- Use case examples

**Request Training:**
Contact saibalg@defendmycountry.com for:
- Group training sessions
- Department-specific training
- Advanced feature workshops
- Administrator training

### 15.4 Feedback & Feature Requests

**We value your feedback!**

**Provide Feedback On:**
- User interface improvements
- Feature suggestions
- Bug reports
- Documentation clarity
- Performance issues
- Workflow enhancements

**Submit Feedback:**
- Email: saibalg@defendmycountry.com
- Subject: "[Tiger OSINT Feedback] - Your Topic"

**Feature Request Format:**
- **Feature Description:** Clear explanation
- **Use Case:** Why you need it
- **Priority:** High/Medium/Low
- **Alternative Solutions:** Current workarounds
- **Expected Benefit:** Impact on workflow

### 15.5 Product Information

**Developer:**
Apt Software Avenues Pvt. Ltd.

**Product Family:**
Defender Framework

**Branding:**
Make in India Initiative

**Version Information:**
- Application Version: Check footer or header
- User Guide Version: 2.0.0
- Last Updated: March 6, 2026

**License & Copyright:**
© 2026 Apt Software Avenues Pvt. Ltd.
All rights reserved.

---

## 16. Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0.0 | 2026-03-06 | Technical Writing Team | Complete rewrite - comprehensive product-grade documentation |
| 1.0.0 | 2025-12-02 | Initial Team | Initial release - basic user guide |

---

## Appendix A: Keyboard Shortcuts

| Action | Shortcut | Context |
|--------|----------|---------|
| Focus search field | Alt + S | Anywhere |
| Execute search | Enter | In search field |
| Clear search form | Ctrl + K | In search form |
| Open profile menu | Alt + P | Anywhere |
| Open LLM config | Alt + L | Anywhere |
| Select all events | Ctrl + A | In results list |
| Export selected | Ctrl + E | When events selected |
| Next page | Right Arrow | In pagination |
| Previous page | Left Arrow | In pagination |
| Close modal | Escape | In any modal |

---

## Appendix B: API Pricing Reference

*For administrator reference - actual costs may vary*

**Google Custom Search Engine:**
- First 100 queries/day: Free
- Additional queries: $5 per 1,000 queries
- Maximum: 10,000 queries per day

**Social Media Scraping (ScrapeCreators):**
- Twitter: $0.001 per post
- Facebook: $0.001 per post
- Instagram: $0.001 per post

**YouTube API:**
- Free (quota-based)
- 10,000 units per day (default quota)

**Claude AI (Anthropic):**
- Input tokens: Varies by model
- Output tokens: Varies by model
- Prompt caching: 90% discount on cached content

**Ollama:**
- Free (self-hosted)
- Only infrastructure costs

---

## Appendix C: Supported Event Types Reference

### Complete Event Type Hierarchy

**1. Violence & Security Events**
- `protest` - Organized public demonstrations
- `demonstration` - Public displays of opinion
- `attack` - Physical attacks on people/property
- `explosion` - Explosive incidents
- `bombing` - IED or bomb attacks
- `shooting` - Firearm-related incidents
- `theft` - Robbery and theft incidents
- `kidnapping` - Abduction and kidnapping

**2. Cyber Events**
- `cyber_attack` - Malicious cyber operations
- `cyber_incident` - Security breaches and incidents
- `data_breach` - Unauthorized data access

**3. Meetings & Conferences**
- `conference` - Professional conferences
- `meeting` - Official meetings
- `summit` - High-level diplomatic meetings

**4. Disasters & Accidents**
- `accident` - Unintentional incidents
- `natural_disaster` - Earthquakes, floods, hurricanes, etc.

**5. Political & Military**
- `election` - Electoral events
- `political_event` - Political activities and rallies
- `military_operation` - Military actions and operations

**6. Crisis Events**
- `terrorist_activity` - Terrorism-related events
- `civil_unrest` - Social disorder and unrest
- `humanitarian_crisis` - Large-scale emergencies

**7. Other**
- `other` - Events not fitting above categories

---

**END OF USER GUIDE**

---

*This document is proprietary to Apt Software Avenues Pvt. Ltd. and is provided for authorized users of the Tiger OSINT platform. Unauthorized distribution or reproduction is prohibited.*

*For the latest version of this document, contact: saibalg@defendmycountry.com*
