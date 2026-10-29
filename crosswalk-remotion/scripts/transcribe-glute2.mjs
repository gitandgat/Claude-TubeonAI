import path from 'path';
import fs from 'fs';
import { transcribe, toCaptions } from '@remotion/install-whisper-cpp';
import { createTikTokStyleCaptions } from '@remotion/captions';

const ROOT = process.cwd();
const WH = path.join(ROOT, 'whisper.cpp');
const MODEL = 'small.en';
const WAV = path.join(ROOT, 'public', 'glute-intro-16k.wav'); // already extracted
const OUT = path.join(ROOT, 'src', 'data', 'glute-captions.json');

console.log('transcribe (token-level timestamps)...');
const whisperCppOutput = await transcribe({
  model: MODEL,
  whisperPath: WH,
  whisperCppVersion: '1.5.5', // required by this @remotion/install-whisper-cpp version
  inputPath: WAV,
  tokenLevelTimestamps: true,
});

const { captions } = toCaptions({ whisperCppOutput });
console.log('tokens:', captions.length);

const { pages } = createTikTokStyleCaptions({
  captions,
  combineTokensWithinMilliseconds: 1200,
});

fs.writeFileSync(OUT, JSON.stringify(pages, null, 2));
console.log('wrote', OUT, '| pages:', pages.length);
