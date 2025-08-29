#!/usr/bin/env node
/**
 * Node-based YouTube audio downloader using ytdl-core
 * - Streams audio-only to files in audio_samples/
 * - Prefers highest audio quality (usually m4a/webm)
 * - No ffmpeg required for raw download
 */

const fs = require('fs');
const path = require('path');
const ytdl = require('ytdl-core');

const OUTPUT_DIR = path.resolve(__dirname, '..', 'audio_samples');

// Ensure output directory exists
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// Default URLs (replace or pass via CLI)
const DEFAULT_URLS = [
  'https://www.youtube.com/watch?v=Uh34kDEF500',
  'https://www.youtube.com/watch?v=KpuEkonkuiU',
  'https://www.youtube.com/watch?v=JXHPIahTayU',
  'https://www.youtube.com/watch?v=w4sarAE9h9I',
  'https://www.youtube.com/watch?v=0YWpkJkbXxs',
];

// Allow passing URLs via CLI, otherwise use defaults
const urls = process.argv.slice(2).length ? process.argv.slice(2) : DEFAULT_URLS;

const USER_AGENT =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

function sanitize(name) {
  return name.replace(/[^a-zA-Z0-9-_ ]/g, '').trim();
}

async function downloadOne(url, index, total) {
  try {
    console.log(`\n[${index}/${total}] Fetching info: ${url}`);
    const info = await ytdl.getInfo(url, {
      requestOptions: {
        headers: { 'user-agent': USER_AGENT },
      },
    });

    const title = sanitize(info.videoDetails.title).slice(0, 60) || info.videoDetails.videoId;
    const videoId = info.videoDetails.videoId;

    // Pick highest bitrate audio-only format
    const fmt = ytdl.chooseFormat(info.formats, {
      quality: 'highestaudio',
      filter: 'audioonly',
    });

    if (!fmt || !fmt.mimeType) {
      console.warn(`No suitable audio format for ${url}`);
      return false;
    }

    const extMatch = /audio\/(mp4|webm)/.exec(fmt.mimeType);
    const ext = extMatch ? (extMatch[1] === 'mp4' ? 'm4a' : 'webm') : 'webm';

    const outName = `${videoId}_${title}.${ext}`;
    const outPath = path.join(OUTPUT_DIR, outName);

    console.log(`Downloading: ${title} (${videoId}) => ${outName}`);

    await new Promise((resolve, reject) => {
      ytdl(url, {
        quality: fmt.itag,
        filter: 'audioonly',
        requestOptions: {
          headers: { 'user-agent': USER_AGENT },
        },
      })
        .on('progress', (_, downloaded, totalBytes) => {
          if (totalBytes) {
            const pct = ((downloaded / totalBytes) * 100).toFixed(1);
            process.stdout.write(`\r  ${pct}%`);
          }
        })
        .on('error', (err) => {
          process.stdout.write('\n');
          reject(err);
        })
        .pipe(fs.createWriteStream(outPath))
        .on('finish', () => {
          process.stdout.write('\n');
          resolve();
        })
        .on('error', (err) => {
          process.stdout.write('\n');
          reject(err);
        });
    });

    console.log(`✅ Saved: ${outName}`);
    return true;
  } catch (err) {
    console.error(`❌ Failed: ${url}`);
    console.error(err && err.message ? err.message : err);
    return false;
  }
}

(async () => {
  console.log('🎬 ytdl-core audio downloader');
  console.log('Output dir:', OUTPUT_DIR);

  let ok = 0;
  for (let i = 0; i < urls.length; i++) {
    const success = await downloadOne(urls[i], i + 1, urls.length);
    if (success) ok++;
  }

  console.log(`\nDone. Successful: ${ok}/${urls.length}`);
  if (ok > 0) {
    console.log('Next step:');
    console.log('  python tools\\audio_processor.py --input audio_samples --output processed_segments');
  }
})();
