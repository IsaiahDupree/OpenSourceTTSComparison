/**
 * Simple test using node-fetch for better compatibility
 * Run: npm install node-fetch@2 && node test_openvoice_v2_simple.js
 */

import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testOpenVoiceV2() {
    console.log("=".repeat(70));
    console.log(" Testing OpenVoice V2 API (Node.js)");
    console.log("=".repeat(70));

    const endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/";
    const apiUrl = `${endpoint}api/predict/`;

    try {
        console.log("\n[1] Fetching reference audio...");
        const audioUrl = "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav";
        const audioResponse = await fetch(audioUrl);
        const audioBuffer = await audioResponse.buffer();
        const audioBase64 = audioBuffer.toString('base64');
        console.log("  [OK] Audio fetched");

        console.log("\n[2] Making API request...");
        const text = "Howdy! This is a test of OpenVoice V2 using Node.js.";
        const style = "en_default";
        
        const requestData = {
            data: [
                text,
                style,
                `data:audio/wav;base64,${audioBase64}`,
                true
            ],
            fn_index: 1
        };

        console.log("  Text:", text);
        console.log("  Style:", style);
        console.log("  (This may take 30-60 seconds...)");

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        
        console.log("\n  [SUCCESS] Request completed!");
        console.log("  Info:", result.data[0]);
        console.log("  Output Audio:", result.data[1]);
        console.log("  Reference Used:", result.data[2]);

        console.log("\n" + "=".repeat(70));
        console.log(" [SUCCESS] Test completed!");
        console.log("=".repeat(70));

    } catch (error) {
        console.error("\n[ERROR] Test failed:", error.message);
        if (error.stack) {
            console.error(error.stack);
        }
        process.exit(1);
    }
}

testOpenVoiceV2();

