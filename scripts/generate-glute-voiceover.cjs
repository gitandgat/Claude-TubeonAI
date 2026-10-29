const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const envContent = fs.readFileSync('/Users/toto/Claude TubeonAI/.env', 'utf8');
const VOISPARK_KEY = envContent.match(/VOISPARK_API_KEY=(.+)/)[1].trim();
const OUTPUT_DIR = '/Users/toto/Claude TubeonAI/crosswalk-remotion/public';

const SCRIPT = `If you're watching this, you just applied for the Glute Longevity 6-Week Protocol. So first, thank you. Give me two minutes and I'll show you exactly what you've signed up to explore, and why it's different from anything you've tried.

Here's what most people miss. Your glutes aren't about looks. They're the foundation of how you move, stand, and stay pain-free as you age. When they go quiet, from sitting all day, from age, from training the wrong way, your posture starts to collapse. Your knees and your lower back quietly pick up the slack. And getting older starts to feel like breaking down. Most glute programs chase the burn. They never rebuild the strength underneath it.

I'm a former physician. And I got tired of watching capable people accept that decline as if it were inevitable. It isn't. So I built this protocol around what the research actually supports, progressive, well-dosed strength work that treats your glutes as the engine of longevity. Six weeks, six modules, a simple weekly plan you'll actually keep up with, not a punishing one you'll quit in week two. It meets you where you are and builds from there.

You get the full protocol, the training modules, lifetime access, and a money-back guarantee. Do the work as designed, and if your strength, posture, and comfort haven't improved, I refund you. The risk is mine, not yours.

So here's what happens next. I personally review your application within twenty-four hours, then send your enrollment details. When that email lands, just reply, I'm in. Founding spots are limited on purpose. I keep this group small so I can stay close to it.

Talk soon.`;

async function generateTTS(text) {
  const res = await fetch('https://api.voispark.com/api/tts/generate', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${VOISPARK_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      provider: 'openai',
      model_id: 'gpt-4o-mini-tts',
      voice: { type: 'preset', voice_id: 'onyx' },
      sync: true,
    }),
  });
  const data = await res.json();
  if (data.code !== 0) throw new Error(`VoiSpark error: ${data.message}`);
  return data.data?.details?.url;
}

function downloadFile(url, destPath) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    const file = fs.createWriteStream(destPath);
    protocol
      .get(url, (response) => {
        if (response.statusCode === 301 || response.statusCode === 302) {
          file.close();
          return downloadFile(response.headers.location, destPath).then(resolve).catch(reject);
        }
        response.pipe(file);
        file.on('finish', () => {
          file.close();
          resolve();
        });
      })
      .on('error', (err) => {
        fs.unlink(destPath, () => {});
        reject(err);
      });
  });
}

(async () => {
  console.log('Requesting VoiSpark TTS (onyx)...');
  const audioUrl = await generateTTS(SCRIPT);
  const dest = path.join(OUTPUT_DIR, 'voiceover-glute-intro.wav');
  await downloadFile(audioUrl, dest);
  console.log('Done:', dest);
})();
