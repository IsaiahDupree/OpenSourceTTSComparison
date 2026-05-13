/**
 * Test OpenVoice V2 from Node.js by calling Python script
 * This is the most reliable way to use Gradio APIs from Node.js
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testViaPython() {
    console.log("=".repeat(70));
    console.log(" Testing OpenVoice V2 via Python (from Node.js)");
    console.log("=".repeat(70));

    const pythonScript = path.join(__dirname, 'test_v2_simple.py');

    return new Promise((resolve, reject) => {
        console.log("\n[1] Running Python test script...");
        console.log(`  Script: ${pythonScript}`);

        const python = spawn('python', [pythonScript], {
            stdio: 'inherit',
            shell: true
        });

        python.on('close', (code) => {
            if (code === 0) {
                console.log("\n[SUCCESS] Test completed via Python!");
                resolve(true);
            } else {
                console.log(`\n[ERROR] Python script exited with code ${code}`);
                reject(new Error(`Exit code: ${code}`));
            }
        });

        python.on('error', (error) => {
            console.error(`[ERROR] Failed to start Python: ${error.message}`);
            reject(error);
        });
    });
}

testViaPython().catch(console.error);

