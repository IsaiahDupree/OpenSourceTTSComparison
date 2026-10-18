# OpenVoice Test Instructions

## Quick Test (Recommended)

Run the complete test suite in a **separate terminal**:

```bash
python run_all_tests.py
```

This will:
1. Check if the server is running
2. Test 3 different voice generations
3. Show a summary of results

## Step-by-Step Testing

### Step 1: Start OpenVoice (Terminal 1)

```bash
python run_openvoice_local.py
```

Wait until you see:
```
Running on local URL:  http://0.0.0.0:7860
```

### Step 2: Run Tests (Terminal 2)

Open a **new terminal** and run:

```bash
python run_all_tests.py
```

The script will:
- Check server connection
- Test API accessibility
- Run 3 generation tests
- Show detailed results

## Individual Test Scripts

### Startup Tests Only
```bash
python test_startup.py
```

Tests:
- Python version
- All imports
- Checkpoint files
- Resource files
- Model loading

### Generation Tests (via API)
```bash
python test_generations_api.py
```

Tests voice generation via the Gradio API.

## Expected Results

### ✅ Successful Test Output:
```
✅ Python 3.8.10
✅ Server is running on http://localhost:7860
✅ API is accessible
✅ All generation tests PASSED
```

### ⚠️ If Tests Fail:

1. **Server not running**: Start OpenVoice first
2. **Connection refused**: Check if port 7860 is in use
3. **Generation errors**: Check the error message in the output

## Test Cases

The test suite runs 3 generation tests:

1. **Short English - Default Style**
   - Text: "Hello, this is a test of the OpenVoice system."
   - Style: default
   - Reference: demo_speaker2.mp3

2. **English - Whispering Style**
   - Text: "This is a whispering test."
   - Style: whispering
   - Reference: demo_speaker2.mp3

3. **English - Cheerful Style**
   - Text: "This is a cheerful test!"
   - Style: cheerful
   - Reference: demo_speaker0.mp3

## Notes

- First generation takes 30-60 seconds (models load on first use)
- Subsequent generations are faster (5-15 seconds)
- All generated audio files are saved to `openvoice_deploy/outputs/`

