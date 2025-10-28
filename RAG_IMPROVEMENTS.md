# 🎯 RAG Improvements - Fix Search Issues

## ❌ Problems Reported

User reported RAG not finding correct information for:
1. **SEL trong nhận thức bản thân** - Không tìm ra được
2. **Quy chế thi của trường** - Trả lời bị sai

## ✅ Improvements Made

### 1. Vietnamese Text Normalization (Bỏ Dấu)

Added `normalize_vietnamese()` method that removes diacritics:
- **Before**: "nhận thức" ≠ "nhan thuc"
- **After**: Both match as "nhan thuc"

This helps match Vietnamese words regardless of accent marks.

### 2. Dual Keyword Matching

Search now uses BOTH:
- Original keywords (with diacritics)
- Normalized keywords (without diacritics)

Takes the **maximum score** from both approaches.

### 3. Improved Scoring Algorithm

**New Weights:**
- Jaccard Similarity: 35% (was 40%)
- Frequency Matching: 25% (was 30%)
- Position Bonus: 15% (was 20%)
- Phrase Matching: 25% (was 10%) ← **Increased**

**Frequency Scoring:**
- Counts matches in both original and normalized text
- Normalized matches get 0.8x weight

**Position Scoring:**
- Keywords in first half: +0.15
- Normalized keywords in first half: +0.10

**Phrase Matching:**
- Exact phrase match: +0.4
- Normalized phrase match: +0.3

### 4. Configuration Changes

**In `app/core/config.py`:**
```python
TOP_K_CHUNKS: int = 5  # Was 3 → More results
SIMILARITY_THRESHOLD: float = 0.08  # Was 0.15 → Lower threshold
```

## 📊 Expected Results

### Before (Old RAG):
```
Query: "SEL nhận thức bản thân"
Found: 1 chunk (score: 0.189)
Threshold: 0.15
```

### After (Improved RAG):
```
Query: "SEL nhận thức bản thân"
Expected: 5+ chunks
Normalized: "sel nhan thuc ban than"
Better matching across documents
```

## 🔧 Technical Details

### New Methods in `RAGService`:

```python
def normalize_vietnamese(text: str) -> str:
    """Remove Vietnamese diacritics"""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text 
                   if unicodedata.category(char) != 'Mn')
    return text.lower()

def get_normalized_keywords(text: str) -> List[str]:
    """Get keywords without diacritics"""
    normalized = self.normalize_vietnamese(text)
    return self.get_keywords(normalized)
```

### Enhanced search_chunks():

1. Extract both original and normalized keywords from query
2. For each chunk:
   - Extract both original and normalized keywords
   - Calculate Jaccard similarity (both ways)
   - Count keyword frequency (both ways)
   - Check position (both ways)
   - Check phrase matching (both ways)
3. Combine scores with new weights
4. Return top 5 chunks above 0.08 threshold

## 🧪 How to Test

### In UI (Recommended):

1. **Open**: http://localhost:3000
2. **Login** as student
3. **Test queries:**
   - "SEL trong nhận thức bản thân là gì?"
   - "Quy chế thi của trường như thế nào?"
   - "Kỹ năng SEL"
   - "Hướng nghiệp"

### Via Test Script:

```bash
cd backend
python test_improved_rag.py
```

## 📈 Performance

**Documents in DB:** 16 PDFs  
**Total Chunks:** 2,128 chunks  

**Matching Strategy:**
- Original text matching (with diacritics)
- Normalized matching (without diacritics)
- Phrase matching (exact and normalized)
- Position weighting (early text = more important)

## 💡 Why This Works Better

1. **Flexible Matching**: Works with or without diacritics
2. **Multiple Factors**: Not just keyword overlap
3. **Context Aware**: Position matters
4. **Phrase Matching**: Gives bonus for exact phrases
5. **Lower Threshold**: More results = better chance of finding relevant info

## 🎯 What Changed

### Files Modified:
1. ✅ `app/services/rag.py` - Core RAG algorithm
2. ✅ `app/core/config.py` - Configuration parameters

### Changes Summary:
- Added `unicodedata` import
- Added `normalize_vietnamese()` method
- Added `get_normalized_keywords()` method
- Updated `search_chunks()` with dual matching
- Changed TOP_K_CHUNKS: 3 → 5
- Changed SIMILARITY_THRESHOLD: 0.15 → 0.08

## ✨ Result

RAG should now find relevant documents for:
- ✅ SEL và nhận thức bản thân
- ✅ Quy chế thi
- ✅ Any Vietnamese query with accents

**Backend needs restart** to apply changes!

```bash
cd backend
pkill -f uvicorn
./start.sh
```

Then test in UI at http://localhost:3000

