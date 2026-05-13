/**
 * Test OpenVoice V2 API using Node.js with direct HTTP requests
 * Run with: node test_openvoice_v2_node.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import https from 'https';
import http from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function fetch(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        client.get(url, (res) => {
            const chunks = [];
            res.on('data', chunk => chunks.push(chunk));
            res.on('end', () => {
                resolve({
                    blob: async () => Buffer.concat(chunks),
                    arrayBuffer: async () => Buffer.concat(chunks)
                });
            });
        }).on('error', reject);
    });
}

async function testOpenVoiceV2() {
    console.log("=".repeat(70));
    console.log(" Testing OpenVoice V2 API (Node.js HTTP)");
    console.log("=".repeat(70));

    const endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/";
    const apiUrl = `${endpoint}api/predict/`;

    try {
        console.log("\n[1] Fetching reference audio...");
        const audioUrl = "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav";
        const audioResponse = await fetch(audioUrl);
        const audioBlob = await audioResponse.blob();
        console.log("  [OK] Audio fetched");

        console.log("\n[2] Preparing request...");
        const text = "Howdy! This is a test of OpenVoice V2 using Node.js.";
        const style = "en_default";
        const agree = true;

        // Convert audio to base64
        const audioBase64 = audioBlob.toString('base64');
        
        // Prepare the request data
        const requestData = {
            data: [
                text,
                style,
                `data:audio/wav;base64,${audioBase64}`,
                agree
            ],
            fn_index: 1
        };

        console.log("  Text:", text);
        console.log("  Style:", style);
        console.log("  (This may take 30-60 seconds for cold start...)");

        console.log("\n[3] Making API request...");
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        
        console.log("\n  [SUCCESS] Request completed!");
        console.log("  Info:", result.data[0]);
        console.log("  Output Audio:", result.data[1]);
        console.log("  Reference Used:", result.data[2]);

        // Save the audio if it's a file
        if (result.data[1] && result.data[1].data) {
            const audioData = result.data[1].data;
            const outputPath = path.join(__dirname, "output_v2.wav");
            fs.writeFileSync(outputPath, Buffer.from(audioData, 'base64'));
            console.log(`\n  [OK] Audio saved to: ${outputPath}`);
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

// Run the test
testOpenVoiceV2();

