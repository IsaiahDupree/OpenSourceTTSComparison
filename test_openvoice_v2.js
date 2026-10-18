/**
 * Test OpenVoice V2 API using JavaScript/Node.js
 * Run with: node test_openvoice_v2.js
 */

import { client } from "@gradio/client";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testOpenVoiceV2() {
    console.log("=".repeat(70));
    console.log(" Testing OpenVoice V2 API (JavaScript)");
    console.log("=".repeat(70));

    const endpoint = "https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/";

    try {
        console.log("\n[1] Connecting to OpenVoice V2...");
        const app = await client(endpoint);
        console.log("  [OK] Connected successfully!");

        console.log("\n[2] Fetching reference audio...");
        const audioUrl = "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav";
        const response = await fetch(audioUrl);
        const exampleAudio = await response.blob();
        console.log("  [OK] Audio fetched");

        console.log("\n[3] Making prediction...");
        console.log("  Text: 'Howdy! This is a test of OpenVoice V2 using JavaScript.'");
        console.log("  Style: 'en_default'");
        console.log("  (This may take 30-60 seconds for cold start...)");

        const result = await app.predict(1, [
            "Howdy! This is a test of OpenVoice V2 using JavaScript.",
            "en_default",
            exampleAudio,
            true
        ]);

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

