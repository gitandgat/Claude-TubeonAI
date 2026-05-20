/**
 * generate-voiceovers.js
 * Generates voiceovers for all 4 Crosswalk Wisdom explainer videos
 * using VoiSpark API (OpenAI onyx voice via gpt-4o-mini-tts)
 *
 * Output: crosswalk-remotion/public/voiceover-[name].wav
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// ── Load env ──────────────────────────────────────────────────────────────────
const envPath = path.join(__dirname, '..', '.env');
const envContent = fs.readFileSync(envPath, 'utf8');
const VOISPARK_KEY = envContent.match(/VOISPARK_API_KEY=(.+)/)?.[1]?.trim();
if (!VOISPARK_KEY) { console.error('❌ VOISPARK_API_KEY not found in .env'); process.exit(1); }

const OUTPUT_DIR = path.join(__dirname, '..', 'crosswalk-remotion', 'public');

// ── Narration scripts (each ~75-90 words = ~30s at natural pace) ─────────────
const VOICEOVERS = [
  {
    id: 'fear-explainer',
    filename: 'voiceover-fear-explainer.wav',
    text: `You're not burned out because you work too hard.
You're burned out because you're trapped inside an identity you didn't choose.
Every healthcare worker who feels stuck faces the same three fears.
Will I lose everything I've built? What will people think? And — who am I if I'm not this?
These aren't weaknesses. They're a map.
Name your fear. That's where freedom starts.
The Fear Audit is waiting for you at crosswalk wisdom dot com.`,
  },
  {
    id: 'crosswalk-method-explainer',
    filename: 'voiceover-crosswalk-method.wav',
    text: `Sixty-three percent of healthcare workers report burnout.
But burnout isn't the real problem. It's a signal — that you're stuck inside a method that isn't working anymore.
The Crosswalk Method has four stages.
START — you see the problem, but you haven't moved yet.
STOP — you pause, and you look both ways.
ELDER — you seek wisdom from someone who has crossed before you.
HUMAN — you finally choose yourself.
You're already in the method. The only question is: which stage are you in?
Find out at crosswalk wisdom dot com.`,
  },
  {
    id: 'ai-bridge-explainer',
    filename: 'voiceover-ai-bridge.wav',
    text: `You have forty-seven transferable skills that have nothing to do with your job title.
You just can't see them yet.
AI can.
In thirty minutes with the right prompts, you can map your next chapter — without quitting your current one.
Most people spend six months overthinking what thirty minutes of honest conversation with an AI could answer.
Name your fear. Build your bridge.
Start at crosswalk wisdom dot com.`,
  },
  {
    id: 'grief-explainer',
    filename: 'voiceover-grief-explainer.wav',
    text: `Nobody tells you that leaving medicine feels like a death.
That's not a metaphor.
Your brain processes the loss of a professional identity the same way it processes losing a person you love.
The numbness. The anger. The bargaining. The day you drive to work and sit in the parking lot, unable to go in.
The grief is real.
And it doesn't mean you made the wrong choice.
It means something mattered.
The crossing guard crosses anyway.
Start walking at crosswalk wisdom dot com.`,
  },
];

// ── VoiSpark API helpers ──────────────────────────────────────────────────────
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
    protocol.get(url, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        file.close();
        return downloadFile(response.headers.location, destPath).then(resolve).catch(reject);
      }
      response.pipe(file);
      file.on('finish', () => { file.close(); resolve(); });
    }).on('error', (err) => {
      fs.unlink(destPath, () => {});
      reject(err);
    });
  });
}

// ── Main ──────────────────────────────────────────────────────────────────────
(async () => {
  console.log('🎙️  Crosswalk Wisdom — VoiSpark Voiceover Generator');
  console.log('─'.repeat(52));

  for (const vo of VOICEOVERS) {
    const destPath = path.join(OUTPUT_DIR, vo.filename);
    console.log(`\n▶ Generating: ${vo.id}`);
    console.log(`  Words: ${vo.text.split(/\s+/).length}`);

    try {
      const audioUrl = await generateTTS(vo.text);
      if (!audioUrl) throw new Error('No audio URL in response');
      console.log(`  ✅ Audio URL received`);

      await downloadFile(audioUrl, destPath);
      const size = (fs.statSync(destPath).size / 1024).toFixed(0);
      console.log(`  💾 Saved: ${vo.filename} (${size} KB)`);
    } catch (err) {
      console.error(`  ❌ Failed: ${err.message}`);
    }
  }

  console.log('\n✨ Done! Files saved to crosswalk-remotion/public/');
  console.log('Next: add <Audio src={staticFile("voiceover-*.wav")} /> to each composition.');
})();
