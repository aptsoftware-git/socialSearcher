# Search Query Construction Explained

## Overview

The system takes form field inputs and constructs an enhanced Google search query string. The query construction happens in **two stages**: Frontend form submission and Backend query enhancement.

---

## Example Input (Form Fields)

```
Search Phrase: People Killed In Iran Protests
Location: IRAN
Event Type: Protest
Start Date: 10-01-2026 (January 10, 2026)
End Date: 11-01-2026 (January 11, 2026)
```

---

## Stage 1: Frontend Form Submission

**File**: `frontend/src/components/SearchForm.tsx`

### Form Data Structure

When you submit the form, it creates a `SearchQuery` object:

```typescript
const formData: SearchQuery = {
  phrase: "People Killed In Iran Protests",  // User input
  location: "IRAN",                           // Optional filter
  event_type: "protest",                      // EventType enum (lowercase)
  date_from: "2026-01-10",                    // ISO format YYYY-MM-DD
  date_to: "2026-01-11"                       // ISO format YYYY-MM-DD
};
```

### What Happens on Submit

1. **Validation**: Checks that phrase is not empty
2. **Date Validation**: Ensures start_date ≤ end_date
3. **Two Search Modes**:

#### Mode A: Social Media Search (if `use_social_search` checkbox is checked)
- **API Call**: `POST /api/v1/social-search`
- **Query**: Just the phrase - `"People Killed In Iran Protests"`
- **No enhancement** - uses phrase as-is
- **Searches**: YouTube, Twitter/X, Facebook, Instagram

#### Mode B: Regular Streaming Search (default)
- **API Call**: `GET /api/v1/search/stream`
- **Query Parameters**:
  ```
  ?phrase=People Killed In Iran Protests
  &location=IRAN
  &event_type=protest
  &date_from=2026-01-10
  &date_to=2026-01-11
  ```

---

## Stage 2: Backend Query Enhancement

**File**: `backend/app/services/search_service.py` (lines 260-300)

### The Enhancement Logic

The backend receives the form data and **enhances the search phrase** with date context:

```python
search_phrase = query.phrase  # Start with original phrase

# Case 1: Both start and end dates provided
if query.date_from and query.date_to:
    date_from_str = "January 2026"  # Formatted from 2026-01-10
    date_to_str = "January 2026"    # Formatted from 2026-01-11
    
    # Same month/year? Use single date
    if date_from_str == date_to_str:
        search_phrase = f"{query.phrase} {date_from_str}"
        # Result: "People Killed In Iran Protests January 2026"
    else:
        # Different months - use range
        search_phrase = f"{query.phrase} {date_from_str} to {date_to_str}"
        # Example: "People Killed In Iran Protests January 2026 to February 2026"

# Case 2: Only start date
elif query.date_from:
    date_from_str = "January 2026"
    search_phrase = f"{query.phrase} after {date_from_str}"
    # Result: "People Killed In Iran Protests after January 2026"

# Case 3: Only end date
elif query.date_to:
    date_to_str = "January 2026"
    search_phrase = f"{query.phrase} before {date_to_str}"
    # Result: "People Killed In Iran Protests before January 2026"

# Case 4: No dates specified
else:
    search_phrase = f"{query.phrase} recent"
    # Result: "People Killed In Iran Protests recent"
```

### For Your Example

**Input**:
- Phrase: `"People Killed In Iran Protests"`
- Date From: `2026-01-10`
- Date To: `2026-01-11`

**Processing**:
1. Convert dates to month/year: Both become `"January 2026"`
2. Since same month/year, use single date format
3. Append to phrase

**Final Enhanced Query**:
```
"People Killed In Iran Protests January 2026"
```

---

## What About Location and Event Type?

### Important: These are NOT added to the search string!

**Location** (`"IRAN"`) and **Event Type** (`"protest"`) are:
- ✅ Stored in the `SearchQuery` object
- ✅ Logged for debugging
- ✅ Available for post-processing filters
- ❌ **NOT** appended to the Google search query

### Why Not?

The system relies on:
1. **Google's semantic search** to understand context from the phrase
2. **AI analysis** to filter results by event type and location
3. **Relevance scoring** to rank results

If you want location in the search:
- **Include it in the phrase**: `"People Killed In Iran Protests"` already contains "Iran"
- Or manually add: `"Protests in Iran deaths"`

---

## Complete Query Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: SearchForm.tsx                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Input:                                                     │
│  • Phrase: "People Killed In Iran Protests"                     │
│  • Location: "IRAN"                                              │
│  • Event Type: "protest"                                         │
│  • Date From: 2026-01-10                                         │
│  • Date To: 2026-01-11                                           │
│                                                                  │
│  ↓ Submit Form                                                   │
│                                                                  │
│  SearchQuery Object:                                             │
│  {                                                               │
│    phrase: "People Killed In Iran Protests",                    │
│    location: "IRAN",                                             │
│    event_type: "protest",                                        │
│    date_from: "2026-01-10",                                      │
│    date_to: "2026-01-11"                                         │
│  }                                                               │
│                                                                  │
│  ↓ API Call                                                      │
│                                                                  │
│  GET /api/v1/search/stream?phrase=People...&location=IRAN&...   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: main.py → search_service.py                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Parse Query Parameters:                                         │
│  • phrase = "People Killed In Iran Protests"                    │
│  • location = "IRAN"                                             │
│  • event_type = "protest"                                        │
│  • date_from = "2026-01-10"                                      │
│  • date_to = "2026-01-11"                                        │
│                                                                  │
│  ↓ Enhance Query (search_service.py lines 276-300)              │
│                                                                  │
│  Date Enhancement Logic:                                         │
│  1. Convert dates to "Month Year" format                         │
│     • 2026-01-10 → "January 2026"                                │
│     • 2026-01-11 → "January 2026"                                │
│                                                                  │
│  2. Same month/year? Use single date:                            │
│     search_phrase = f"{phrase} {month_year}"                     │
│                                                                  │
│  3. Different? Use range:                                        │
│     search_phrase = f"{phrase} {from} to {to}"                   │
│                                                                  │
│  Enhanced Search Query:                                          │
│  "People Killed In Iran Protests January 2026"                  │
│                                                                  │
│  ↓ Send to Google Custom Search                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ GOOGLE CUSTOM SEARCH ENGINE                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Receives:                                                       │
│  "People Killed In Iran Protests January 2026"                  │
│                                                                  │
│  Searches configured news sources:                               │
│  • BBC News                                                      │
│  • Reuters                                                       │
│  • Al Jazeera                                                    │
│  • CNN                                                           │
│  • etc.                                                          │
│                                                                  │
│  Returns article URLs matching the query                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: Article Processing & AI Analysis                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  For each article:                                               │
│  1. Scrape content                                               │
│  2. Extract events using AI (Ollama/Claude)                      │
│  3. Filter by location="IRAN" (post-processing)                  │
│  4. Filter by event_type="protest" (post-processing)             │
│  5. Filter by date range (post-processing)                       │
│                                                                  │
│  Stream results to frontend in real-time                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary: What Gets Sent to Google?

### Your Example Input:
```
Phrase: "People Killed In Iran Protests"
Location: "IRAN"
Event Type: "protest"
Date From: 2026-01-10
Date To: 2026-01-11
```

### Google Receives:
```
"People Killed In Iran Protests January 2026"
```

### What's NOT in the Google Query:
- ❌ Location ("IRAN") - not added
- ❌ Event Type ("protest") - not added
- ✅ BUT: The phrase already mentions "Iran" and "Protests"

### Why This Works:
1. **Phrase naturally contains context**: "Iran" and "Protests" are in the search phrase
2. **Date provides temporal filtering**: "January 2026" helps Google find relevant articles
3. **AI post-processing**: Backend filters results by exact location and event type
4. **Relevance scoring**: Ensures best matches are returned

---

## Date Enhancement Examples

### Example 1: Same Month
**Input**: 
- Phrase: `"Bombing in Kabul"`
- Date From: `2023-03-10`
- Date To: `2023-03-25`

**Enhanced Query**: 
```
"Bombing in Kabul March 2023"
```

### Example 2: Different Months
**Input**: 
- Phrase: `"Terrorist Attack"`
- Date From: `2023-01-01`
- Date To: `2023-02-28`

**Enhanced Query**: 
```
"Terrorist Attack January 2023 to February 2023"
```

### Example 3: Only Start Date
**Input**: 
- Phrase: `"Protests"`
- Date From: `2023-06-01`
- Date To: (empty)

**Enhanced Query**: 
```
"Protests after June 2023"
```

### Example 4: Only End Date
**Input**: 
- Phrase: `"Election"`
- Date From: (empty)
- Date To: `2023-12-31`

**Enhanced Query**: 
```
"Election before December 2023"
```

### Example 5: No Dates
**Input**: 
- Phrase: `"Cyber Attack"`
- Date From: (empty)
- Date To: (empty)

**Enhanced Query**: 
```
"Cyber Attack recent"
```

---

## Key Takeaways

1. **Only the phrase and dates** are used in the Google search query
2. **Location and Event Type** are filters applied AFTER results are returned
3. **Dates are formatted as "Month Year"** for natural language search
4. **"recent" keyword** is added when no dates specified
5. **Your phrase should include important context** (like "Iran" and "Protests")

---

## Code References

### Frontend Query Building
- **File**: `frontend/src/components/SearchForm.tsx`
- **Lines**: 140-250
- **Function**: `handleSubmit()`

### Backend Query Enhancement
- **File**: `backend/app/services/search_service.py`
- **Lines**: 276-300
- **Function**: `search()`

### Date Formatting Logic
```python
# Converts "2026-01-10" to "January 2026"
date_str = date_obj.strftime('%B %Y')
```

---

**Last Updated**: 2026-01-14
