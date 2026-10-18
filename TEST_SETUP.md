# Test Setup Instructions

## Two-Terminal Setup

### Terminal 1: Start Server
```bash
python start_server.py
```

Wait until you see:
```
Running on local URL:  http://0.0.0.0:7860
```

### Terminal 2: Run Tests
```bash
python run_all_tests.py
```

The test script will:
- Wait 3 seconds for server to be ready
- Check server connection
- Run 3 generation tests
- Show detailed results with console logging

## Quick Test (Single Command)

If you want to test without the interactive prompt:

```bash
python run_all_tests.py
```

It will automatically wait 3 seconds and start testing.

## What Gets Tested

1. **Startup Tests:**
   - Python version check
   - Server connection
   - API accessibility

2. **Generation Tests:**
   - Short English - Default Style
   - English - Whispering Style  
   - English - Cheerful Style

## Console Logging Format

All output uses `@pwsh` format:
```
[HH:MM:SS] @pwsh [LEVEL] message
```

Levels:
- `[TEST]` - Test section headers
- `[INFO]` - Informational messages
- `[SUCCESS]` - Successful operations
- `[ERROR]` - Errors and failures

