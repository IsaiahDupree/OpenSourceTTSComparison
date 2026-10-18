/**
 * Test OpenVoice V2 API using proper Gradio API format
 * Run: node test_openvoice_v2_fixed.js
 */

import fetch from 'node-fetch';
import { FormData, Blob } from 'formdata-node';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testOpenVoiceV2() {
    console.log("=".repeat(70));
    console.log(" Testing OpenVoice V2 API (Node.js - Fixed)");
    console.log("=".repeat(70));

    const endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/";

    try {
        console.log("\n[1] Fetching reference audio...");
        const audioUrl = "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav";
        const audioResponse = await fetch(audioUrl);
        const audioBuffer = await audioResponse.buffer();
        console.log("  [OK] Audio fetched");

        console.log("\n[2] Uploading audio file...");
        // First upload the audio file
        const formData = new FormData();
        const blob = new Blob([audioBuffer], { type: 'audio/wav' });
        formData.append('files', blob, 'audio_sample.wav');
        
        const uploadResponse = await fetch(`${endpoint}upload`, {
            method: 'POST',
            body: formData
        });

        let audioFile;
        if (uploadResponse.ok) {
            const uploadResult = await uploadResponse.json();
            audioFile = uploadResult[0] || audioUrl; // Use uploaded file or fallback to URL
            console.log("  [OK] Audio uploaded:", audioFile);
        } else {
            // Fallback to URL
            audioFile = audioUrl;
            console.log("  [INFO] Using audio URL directly:", audioFile);
        }

        console.log("\n[3] Making prediction request...");
        const text = "Howdy! This is a test of OpenVoice V2 using Node.js.";
        const style = "en_default";
        
        const requestData = {
            data: [
                text,
                style,
                audioFile,  // Use uploaded file path or URL
                true
            ],
            fn_index: 1
        };

        console.log("  Text:", text);
        console.log("  Style:", style);
        console.log("  Audio:", audioFile);
        console.log("  (This may take 30-60 seconds for cold start...)");

        const response = await fetch(`${endpoint}api/predict/`, {
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

        // Save the audio if it's a file
        if (result.data[1]) {
            if (typeof result.data[1] === 'string' && result.data[1].startsWith('http')) {
                console.log(`\n  [INFO] Audio available at: ${result.data[1]}`);
            } else if (result.data[1].data) {
                const outputPath = path.join(__dirname, "output_v2.wav");
                fs.writeFileSync(outputPath, Buffer.from(result.data[1].data, 'base64'));
                console.log(`\n  [OK] Audio saved to: ${outputPath}`);
            }
        }

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

