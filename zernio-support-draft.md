# Zernio Support Request - Draft

**Subject:** API Status Change Not Working / Draft Posts Publishing Behavior

---

Hi Zernio Support,

I'm working with your API to manage 106 scheduled social posts (LinkedIn, Instagram, Facebook, TikTok, YouTube). I've encountered two related issues and need clarification:

## Issue 1: Draft Posts Publishing
We have 106 posts in **draft status** with `scheduledFor` dates set correctly (June 6-27, 2026). 

**Question:** Do draft posts automatically publish at their `scheduledFor` times, or do they need to be in "scheduled" status to publish?

## Issue 2: API Status Changes Not Working
We've attempted to change post status from draft → scheduled via the API using:

**Method 1 (Minimal Payload):**
```json
PUT /posts/{id}
{
  "status": "scheduled"
}
```
Result: Returns 200 but status doesn't change ❌

**Method 2 (Full Post Body):**
```json
PUT /posts/{id}
{
  ... entire post object ...
  "status": "scheduled"
}
```
Result: Returns 200 but status doesn't change ❌

**Method 3 (PATCH):**
Returns 405 Method Not Allowed ❌

**Method 4 (Publish Endpoint):**
`POST /posts/{id}/publish` returns 404 ❌

**Questions:**
1. What is the correct API method/endpoint to change a post's status from draft to scheduled?
2. Do we need special permissions or a different account setting?
3. Is there a different field name we should be using (e.g., `publishStatus`, `state`, etc.)?

## Current Status
- 106 posts created with correct `scheduledFor` timestamps ✓
- All posts in draft status (unable to change via API)
- All scheduled dates set for June 6-27, 2026 ✓

Any guidance would be appreciated!

---

**Account ID:** [ADD YOUR ZERNIO ACCOUNT ID]  
**Date:** May 28, 2026  
**API Version:** v1
