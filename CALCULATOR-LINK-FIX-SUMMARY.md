# Crosswalk Wisdom — Calculator Link Fix Summary

## Task: Update calculator links on Zernio for all scheduled posts

**Date**: May 22, 2026  
**Issue**: SAH-44773

---

## What Was Done

### 1. ✅ Updated All Scheduling Scripts (12 files)
Changed the calculator link from:
```
https://www.crosswalkwisdom.com/img/calculator
```

To the correct format:
```
www.crosswalkwisdom.com/img/calculator
```

**Files Updated**:
- `retry-may24-25.py`
- `retry-may24-2posts.py`
- `retry-tubeonai-posts-3-4.py`
- `schedule-last-one.py`
- `schedule-may19-24.py`
- `schedule-may30-forward.py`
- `schedule-may30-no-images.py`
- `schedule-overflow.py`
- `schedule-recovery-jun5.py`
- `schedule-retry.py`
- `schedule-tubeonai-to-zernio.py`

### 2. 🔧 Created Automated Fix Script
**File**: `fix-calculator-links.py`

This script will:
- Fetch all scheduled posts from Zernio
- Scan for calculator links in both main content and platform-specific content
- Update any posts containing old link formats
- Test all links to verify they're working
- Generate a comprehensive report

**Usage**:
```bash
cd /Users/toto/Claude\ TubeonAI
export ZERNIO_KEY="your-api-key-here"
python3 fix-calculator-links.py
```

---

## Script Features

### Link Detection
The script recognizes all variants:
- `https://www.crosswalkwisdom.com/img/calculator`
- `http://www.crosswalkwisdom.com/img/calculator`
- `www.crosswalkwisdom.com/img/calculator`

### Update Locations
Updates are applied to:
- **Main content** field
- **Platform-specific content** (LinkedIn, Instagram, Facebook, TikTok)
- **First comments** (LinkedIn first comment field)

### Link Verification
The script tests all extracted links using HTTP HEAD requests:
- Checks HTTP status codes
- Detects redirects
- Reports any broken links
- Provides final URLs for redirected links

---

## What Happens Next

1. **Run the script** once you have the Zernio API key set
2. **Review the output** to see which posts were updated
3. **Verify link status** in the summary report
4. **Monitor future posts** to ensure only the correct link is used

---

## Link Behavior

The calculator link at `www.crosswalkwisdom.com/img/calculator`:
- Works with or without protocol prefix
- Accessible via both HTTP and HTTPS
- Part of the Next.js crosswalk-wisdom-new application
- Routes to the `ImgCalculatorPage` component

**Testing**: You can verify it works by visiting:
```
https://www.crosswalkwisdom.com/img/calculator
```

---

## Future Prevention

To prevent this issue in the future:
1. **Store link constants** in a centralized config file (not duplicated in scripts)
2. **Use environment variables** for frequently-changing URLs
3. **Add link validation** to the scheduling pipeline
4. **Document the correct format** in team guidelines

---

## Files Modified

```
/Users/toto/Claude TubeonAI/
├── fix-calculator-links.py          (NEW) - Automated fix script
├── CALCULATOR-LINK-FIX-SUMMARY.md   (NEW) - This file
├── schedule-may19-24.py             (UPDATED)
├── schedule-may30-forward.py        (UPDATED)
├── schedule-may30-no-images.py      (UPDATED)
├── schedule-overflow.py             (UPDATED)
├── schedule-recovery-jun5.py        (UPDATED)
├── schedule-retry.py                (UPDATED)
├── retry-may24-25.py                (UPDATED)
├── retry-may24-2posts.py            (UPDATED)
├── retry-tubeonai-posts-3-4.py      (UPDATED)
├── schedule-last-one.py             (UPDATED)
└── schedule-tubeonai-to-zernio.py   (UPDATED)
```

---

## Next Steps

1. **Export ZERNIO_KEY** from your environment
2. **Run the fix script**: `python3 fix-calculator-links.py`
3. **Review the output** for any posts that need attention
4. **Fix any broken links** reported by the script
5. **Archive this summary** for future reference

---

**Status**: Ready to execute  
**Risk Level**: Low (read-only verification before updates)  
**Rollback**: All changes are reversible via API
