# Automated Testing Guide

## Quick Start

Run this single command to restart the server and run all tests:

```bash
python restart_and_test.py
```

This will:
1. Check for existing server and wait for it to stop
2. Start a new server with fixed code in a separate window
3. Wait for server to be ready
4. Run all tests automatically
5. Display a pass/fail summary at the end

## Test Results Summary

At the end of the test run, you'll see:

```
======================================================================
 TEST RESULTS SUMMARY
======================================================================

[PASS] - Startup Tests
[FAIL] - Short English - Default Style
[FAIL] - English - Whispering Style
[FAIL] - English - Cheerful Style

======================================================================
Overall: 0/3 generation tests passed
======================================================================
```

## Manual Two-Terminal Setup

If you prefer to run server and tests separately:

### Terminal 1: Start Server
```bash
python start_server.py
```

### Terminal 2: Run Tests
```bash
python run_all_tests.py
```

## Current Issues

1. **`KeyError: 'log'`** - This is a `gradio_client` compatibility issue with Gradio 3.48.0. The tests are connecting but the client library has a bug handling certain message types.

2. **`whisper_timestamped` error** - This should be fixed in the code. Make sure the server is restarted to load the updated `se_extractor.py` with the fallback logic.

## Next Steps

To fix the API connection issues:
- Consider upgrading `gradio_client` to a newer version
- Or downgrade Gradio to a version compatible with the current `gradio_client`
- Or use direct HTTP requests instead of `gradio_client`

The test framework is working correctly - it's detecting failures and showing the summary as requested.

