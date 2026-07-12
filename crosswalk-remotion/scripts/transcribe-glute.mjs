import path from 'path';
import fs from 'fs';
import { execFileSync } from 'child_process';
import {
  installWhisperCpp,
  downloadWhisperModel,
  transcribe,
  toCaptions,
} from '@remotion/install-whisper-cpp';
import { createTikTokStyleCaptions } from '@remotion/captions';

const ROOT = process.cwd();
const WH = path.join(ROOT, 'whisper.cpp');
const MODEL = 'small.en'; // good accuracy on clear scripted speech, ~466MB
const SRC = path.join(ROOT, 'public', 'glute-intro-raw.mov');
const WAV = path.join(ROOT, 'public', 'glute-intro-16k.wav');
const COMP = path.join(ROOT, 'node_modules', '@remotion', 'compositor-darwin-arm64');
const OUT = path.join(ROOT, 'src', 'data', 'glute-captions.json');

console.log('1/5 install whisper.cpp...');
await installWhisperCpp({ to: WH, version: '1.5.5' });

console.log('2/5 download model', MODEL);
await downloadWhisperModel({ model: MODEL, folder: WH });

console.log('3/5 extract 16kHz mono wav...');
execFileSync(
  path.join(COMP, 'ffmpeg'),
  ['-y', '-i', SRC, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', WAV],
  { env: { ...process.env, DYLD_FALLBACK_LIBRARY_PATH: COMP }, stdio: 'inherit' }
);

console.log('4/5 transcribe (token-level timestamps)...');
const whisperCppOutput = await transcribe({
  model: MODEL,
  whisperPath: WH,
  inputPath: WAV,
  tokenLevelTimestamps: true,
});

const { captions } = toCaptions({ whisperCppOutput });
console.log('   tokens:', captions.length);

const { pages } = createTikTokStyleCaptions({
  captions,
  combineTokensWithinMilliseconds: 1200,
});

fs.writeFileSync(OUT, JSON.stringify(pages, null, 2));
console.log('5/5 wrote', OUT, '| pages:', pages.length);
