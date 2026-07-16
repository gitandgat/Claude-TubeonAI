# Email Draft to Zernio Support

---

**Subject:** API Issue - Posts Status Changed from Scheduled to Draft After Update

**To:** support@zernio.com

---

Hi Zernio Support Team,

I encountered an issue while using the Zernio API to update scheduled posts. I'd like to report the problem and ask for guidance.

## Problem Summary

While updating multiple scheduled posts via the API to add a first comment, 106 posts were inadvertently converted from **scheduled** status to **draft** status. 

## What Happened

1. **Goal:** Add a first comment field to 102+ scheduled social media posts
2. **Method:** Used PUT request to `/v1/posts/{postId}` with JSON payload containing the `firstComment` field
3. **Result:** Posts updated with the first comment successfully, BUT their status changed from "scheduled" → "draft"

## Current State

- **106 posts stuck in DRAFT status** (should be scheduled)
- 9 posts remained scheduled (unaffected)
- 77 published posts (past posts - unaffected)
- Scheduled dates are still set correctly (e.g., 2026-08-24T19:00:00.000Z)

## Questions

1. **Can post status be changed via API?** When I attempted a PUT request with `{"status": "scheduled"}`, it returned 200 OK but didn't actually change the status. Later attempts with full post data returned **403 Forbidden**.

2. **What's the correct method to:**
   - Update post metadata (like `firstComment`) WITHOUT affecting the status field?
   - Change a post's status from draft → scheduled via API?
   - Bulk update the status of multiple posts?

3. **Is there a specific endpoint or workflow** for scheduling posts that I should use instead?

## Technical Details

- API Endpoint: `https://api.zernio.com/v1/posts`
- Method: PUT
- Auth: Bearer token (API key)
- Status codes encountered: 200 OK, 403 Forbidden, 405 Method Not Allowed (on PATCH)

## Request

Could you either:
1. Provide documentation on the correct API method for updating post metadata while preserving status
2. Advise on how to restore these 106 posts to scheduled status via API
3. Or if this is a UI-only operation, let me know so I can use the dashboard instead

Thank you for your help!

Best regards,
[Your Name]

---

## Notes Before Sending

- Replace `[Your Name]` with your actual name
- Consider mentioning your account email or account ID if you have one
- You might want to check Zernio's support contact page to get the exact email address if support@zernio.com isn't correct
- Feel free to adjust tone or add any other details you think are relevant
