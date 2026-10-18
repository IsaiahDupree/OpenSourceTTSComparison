/**
 * Test OpenVoice V2 connectivity and API format
 */

import fetch from 'node-fetch';

async function testConnectivity() {
    console.log("=".repeat(70));
    console.log(" OpenVoice V2 Connectivity Test");
    console.log("=".repeat(70));

    const endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/";

    // Test 1: Check if endpoint is accessible
    console.log("\n[1] Testing endpoint accessibility...");
    try {
        const response = await fetch(endpoint);
        console.log(`  Status: ${response.status}`);
        if (response.ok) {
            console.log("  [OK] Endpoint is accessible");
        }
    } catch (error) {
        console.log(`  [ERROR] ${error.message}`);
    }

    // Test 2: Check API info
    console.log("\n[2] Checking API info...");
    try {
        const response = await fetch(`${endpoint}api/`);
        if (response.ok) {
            const apiInfo = await response.json();
            console.log(`  [OK] API info retrieved: ${apiInfo.length} endpoints`);
            console.log("  Endpoints:", JSON.stringify(apiInfo, null, 2));
        } else {
            console.log(`  [ERROR] HTTP ${response.status}`);
        }
    } catch (error) {
        console.log(`  [ERROR] ${error.message}`);
    }

    // Test 3: Try simple prediction with minimal data
    console.log("\n[3] Testing prediction API format...");
    console.log("  Note: This will likely fail, but we'll see the error format");
    
    const testData = {
        data: [
            "Hello",
            "en_default",
            "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
            true
        ],
        fn_index: 1
    };

    try {
        const response = await fetch(`${endpoint}api/predict/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(testData)
        });

        console.log(`  Status: ${response.status}`);
        const result = await response.text();
        console.log(`  Response: ${result.substring(0, 500)}`);
        
        if (response.ok) {
            console.log("  [SUCCESS] API call worked!");
        } else {
            console.log("  [INFO] API returned error (expected for testing)");
        }
    } catch (error) {
        console.log(`  [ERROR] ${error.message}`);
    }

    console.log("\n" + "=".repeat(70));
    console.log(" Note: The Python gradio_client library handles the API format");
    console.log("       automatically. For JavaScript, you may need to use");
    console.log("       the @gradio/client package in a browser environment.");
    console.log("=".repeat(70));
}

testConnectivity();

