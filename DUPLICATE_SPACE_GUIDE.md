# Duplicate Space Guide - What's Needed

## Required Secrets

The modal shows **3 secrets** that need to be configured:

1. **API_URL**
2. **RESULT_URL** 
3. **TOKEN**

## What These Secrets Are For

These secrets are used by the OpenVoiceV2 Space to connect to backend services. The Space itself is a frontend that calls external APIs.

### Understanding the Architecture

OpenVoiceV2 Space likely:
- Uses `API_URL` to call the actual voice cloning API
- Uses `RESULT_URL` to store/retrieve generated audio
- Uses `TOKEN` for authentication

## Finding the Secret Values

### Option 1: Check the Original Space's Code

1. Go to: https://huggingface.co/spaces/myshell-ai/OpenVoiceV2/tree/main
2. Look for `app.py` or `.env` files
3. Check for how these secrets are used

### Option 2: Check Space Settings (if accessible)

The original Space owner has these configured. You may need to:
- Contact myshell-ai
- Check their documentation
- Look at the GitHub repo

### Option 3: Use Default/Public Values

Some Spaces use public endpoints. You might be able to:
- Leave them empty initially and see what errors you get
- Use placeholder values to get the Space running
- The Space might work with defaults

## Recommended Approach

### Step 1: Duplicate with Placeholders

1. **Owner:** theisaiahdupree (your account)
2. **Space name:** OpenVoiceV2 (or your custom name)
3. **Visibility:** Public (or Private if you prefer)
4. **Hardware:** CPU Basic (free tier) - upgrade later if needed
5. **Secrets:** 
   - `API_URL`: Leave empty or use placeholder
   - `RESULT_URL`: Leave empty or use placeholder  
   - `TOKEN`: Your HF_TOKEN (${HF_TOKEN})

### Step 2: Test the Duplicated Space

After duplication:
1. Visit your new Space: `https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2`
2. Try using it in the UI
3. Check for error messages that might reveal what the secrets should be

### Step 3: Update Secrets Based on Errors

If the Space shows errors, they might indicate:
- What API_URL is expected
- What RESULT_URL format is needed
- Whether TOKEN needs specific permissions

## Alternative: Check the Source Code

The Space code is available. You can:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/myshell-ai/OpenVoice.git
   ```

2. **Check for environment variables:**
   - Look in `app.py` or Space files
   - See how these secrets are used
   - Find the actual endpoint URLs

3. **Deploy your own version:**
   - Use the code you find
   - Configure your own backend
   - Don't need the secrets if you control everything

## What You Can Do Right Now

### Quick Test:

1. **Duplicate the Space** with:
   - Your HF_TOKEN in the TOKEN secret
   - Empty or placeholder values for API_URL and RESULT_URL
   
2. **See if it works** - The Space might:
   - Use default/public endpoints
   - Work with just the TOKEN
   - Show helpful error messages

3. **Update secrets** based on what you learn

### For Production:

If you need a fully working instance:
- **Option A:** Clone the GitHub repo and run locally (no secrets needed)
- **Option B:** Contact myshell-ai for secret values
- **Option C:** Reverse engineer from the Space's network requests

## Next Steps

1. Try duplicating with your HF_TOKEN and see what happens
2. Check the Space's app.py file for clues
3. Consider running locally instead (no secrets needed)

The pub/sub system is ready - once you have a working Space (duplicated or local), it will work!

