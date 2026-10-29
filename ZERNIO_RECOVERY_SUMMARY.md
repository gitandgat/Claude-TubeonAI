# Zernio Post Recovery Summary

## What Happened

Attempted to add **"comment TRUTH and I'll send it"** CTA to all scheduled posts from May 28 onwards via Zernio API.

### The Problem
- **102 posts updated successfully** with the CTA
- **106 posts accidentally converted to DRAFT status** (should be scheduled)
- API PUT requests to update `firstComment` field inadvertently changed post status from scheduled → draft

## Current State

**Total Posts by Status:**
- 106 **DRAFT** ← Need to fix
- 77 Published (past posts - OK)
- 9 Scheduled (the ones that stayed scheduled - OK)
- 7 Partial
- 1 Failed

## What Needs to Be Done

### Option 1: Manual Fix (Safest)
In Zernio Dashboard:
1. Filter posts by **Status: Draft**
2. Select all 106 draft posts
3. Change status to **Scheduled**
4. Save

### Option 2: API Fix (If Zernio Supports It)
- Need to confirm with Zernio if status can be changed via API
- Previous attempts returned **403 Forbidden** errors
- May need different endpoint or special permissions

### Option 3: Contact Zernio Support
- Ask them how to bulk-change post status via API
- Or ask if there's a specific endpoint for scheduling drafts

## What WAS Successfully Done ✅

**All 102 posts now have the first comment:**
- **51 posts** with resource links: `comment TRUTH and I'll send it\n\nhttps://crosswalkwisdom.com/blog/[article-slug]`
- **51 posts** without links: `comment TRUTH and I'll send it`

The CTA content is correct — just the status field needs to be restored.

## Next Steps

1. **Manual fix recommended:** Go to Zernio → Draft filter → Bulk select all 106 → Change to Scheduled
2. **Or wait for API guidance** before trying to automate again

## Note for Future Reference

When using Zernio API to update posts:
- Simple field updates (like `firstComment`) may inadvertently reset the `status` field
- Always send the FULL post data back, or confirm the API preserves unchanged fields
- Test with 1 post first before bulk operations
