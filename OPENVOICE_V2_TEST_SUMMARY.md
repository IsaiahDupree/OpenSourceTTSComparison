# OpenVoice V2 API Test Summary

## Status

✅ **Connection Successful** - The OpenVoice V2 API endpoint is accessible:
- Endpoint: `https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/`
- Python `gradio_client`: ✅ Works (connected successfully)
- JavaScript/Node.js: ⚠️ HTTP 500 errors (server-side issue)

## API Format

### Python (Working)
```python
from gradio_client import Client

client = Client("https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/")
result = client.predict(
    "Howdy!",
    "en_default",
    "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
    True,
    fn_index=1
)
```

### JavaScript (Browser - from docs)
```javascript
import { client } from "@gradio/client";

const app = await client("https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/");
const result = await app.predict(1, [
    "Howdy!",
    "en_default",
    exampleAudio,  // blob
    true
]);
```

### Node.js (Current Issue)
- Direct HTTP requests return HTTP 500
- `@gradio/client` package is browser-only (requires `window` object)
- Need to use Python or browser JavaScript

## Differences from V1

1. **Style Format**: Language-specific styles
   - V1: `default`, `whispering`, `cheerful`, etc.
   - V2: `en_default`, `en_us`, `es_default`, `fr_default`, etc.

2. **Multi-lingual**: Native support for 6 languages
   - English (multiple variants), Spanish, French, Chinese, Japanese, Korean

3. **Better Quality**: Improved audio quality

4. **MIT License**: Free for commercial use

## Recommendations

1. **Use Python** for server-side/Node.js environments
2. **Use Browser JavaScript** for client-side applications
3. **For Node.js**: Consider creating a Python microservice or using child_process to call Python scripts

## Test Files Created

- `test_openvoice_v2_official.py` - Python test (works)
- `test_v2_simple.py` - Python simple test (works)
- `test_openvoice_v2.js` - JavaScript test (browser-only)
- `test_openvoice_v2_simple.js` - Node.js test (HTTP 500)
- `test_openvoice_v2_fixed.js` - Node.js with file upload (HTTP 500)
- `test_v2_connectivity.js` - Connectivity test

