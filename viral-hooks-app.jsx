import React, { useState, useRef, useEffect } from 'react';

const BRAND_VOICE = `You are a creative content strategist for Crosswalk Wisdom — a wellness and storytelling brand built by Sahawat, a former physician from Thailand who left clinical medicine, worked as a crossing guard in Toronto, and now helps burned-out high achievers navigate identity and career transitions.

Voice: Warm, grounded, a little playful. Elizabeth Gilbert's register — story-first, accessible, no jargon. Short sentences. Punchy and honest.

Key story assets:
- COVID night shifts as a physician
- First week after leaving medicine
- The crosswalk moment in a yellow vest holding a stop sign
- The fear of disappointing his younger self

Target audience: Burned-out high achievers (doctors, lawyers, engineers) who feel trapped in the identity they built to survive.

Write in this voice. Be specific, avoid generic wellness platitudes. Use the story assets when they fit naturally.`;

const PLATFORMS = {
  all: 'All platforms (YouTube Shorts, TikTok, Instagram Reels)',
  youtube: 'YouTube Shorts (vertical, 15-60s)',
  tiktok: 'TikTok (9:16, 0-60s)',
  instagram: 'Instagram Reels (9:16, 15-90s)'
};

export default function ViralHooksApp() {
  const [mode, setMode] = useState('topic'); // 'topic' or 'paste'
  const [apiKey, setApiKey] = useState('');
  const [showApiForm, setShowApiForm] = useState(true);
  const [input, setInput] = useState('');
  const [platform, setPlatform] = useState('all');
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [stage1Results, setStage1Results] = useState(null);
  const [stage2Results, setStage2Results] = useState(null);
  const [videoScript, setVideoScript] = useState('');
  const [generateScript, setGenerateScript] = useState(false);
  const [error, setError] = useState('');
  const resultsRef = useRef(null);

  useEffect(() => {
    const stored = localStorage.getItem('anthropic_api_key');
    if (stored) {
      setApiKey(stored);
      setShowApiForm(false);
    }
  }, []);

  const saveApiKey = () => {
    if (!apiKey.trim()) {
      setError('API key cannot be empty');
      return;
    }
    localStorage.setItem('anthropic_api_key', apiKey);
    setShowApiForm(false);
    setError('');
  };

  const callApi = async (prompt, maxTokens = 1000) => {
    if (!apiKey) {
      setError('API key is required. Enter it above.');
      return null;
    }

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: maxTokens,
          system: BRAND_VOICE,
          messages: [{ role: 'user', content: prompt }]
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error?.message || `API error: ${response.status}`);
      }

      const data = await response.json();
      return data.content?.[0]?.text || '';
    } catch (err) {
      setError(`API Error: ${err.message}`);
      return null;
    }
  };

  const parseJsonResponse = (text) => {
    try {
      const jsonMatch = text.match(/\[[\s\S]*\]|\{[\s\S]*\}/);
      if (!jsonMatch) throw new Error('No JSON found in response');
      return JSON.parse(jsonMatch[0]);
    } catch (err) {
      setError(`Failed to parse response: ${err.message}`);
      return null;
    }
  };

  const handleTopicMode = async () => {
    if (!input.trim()) {
      setError('Please enter a topic');
      return;
    }

    setError('');
    setLoading(true);
    setStage1Results(null);
    setStage2Results(null);
    setVideoScript('');

    // Stage 1: Research viral hooks
    setLoadingStage('Researching patterns from top creators...');
    const stage1Prompt = `Research 5 viral hook structures from wellness/identity/career niche creators (Dan Koe, Ali Abdaal, Jay Shetty, Diary of a CEO, HealthyGamerGG) related to: "${input}"

For each hook, identify:
- The structural pattern (e.g., "contrast hook", "curiosity gap", "reframe pattern", etc.)
- A real example of this pattern in the wild
- Why it works psychologically

Return ONLY valid JSON array with no markdown, no preamble. Structure:
[
  { "pattern": "...", "example": "...", "why": "..." },
  ...
]`;

    const stage1Text = await callApi(stage1Prompt);
    if (!stage1Text) {
      setLoading(false);
      return;
    }

    const stage1Data = parseJsonResponse(stage1Text);
    if (!stage1Data) {
      setLoading(false);
      return;
    }

    setStage1Results(stage1Data);

    // Stage 2: Repurpose into brand voice
    setLoadingStage('Repurposing into Crosswalk Wisdom voice...');
    const stage2Prompt = `You have these viral hook patterns:
${stage1Data.map((h, i) => `${i + 1}. Pattern: ${h.pattern}\n   Example: ${h.example}`).join('\n')}

Topic: "${input}"
Platform focus: ${PLATFORMS[platform]}

Rewrite each hook in the Crosswalk Wisdom voice. Each should:
- Open with a genuine truth about burnout, identity, or career transition
- Use short sentences and conversational tone
- Feel like a warm conversation, not marketing
- Optionally reference the story assets (physician days, crosswalk moment, identity fear)
- Be specific to the topic, not generic

Return ONLY valid JSON array with 5 repurposed hook strings, no markdown, no preamble:
["Hook 1", "Hook 2", "Hook 3", "Hook 4", "Hook 5"]`;

    const stage2Text = await callApi(stage2Prompt);
    if (!stage2Text) {
      setLoading(false);
      return;
    }

    const stage2Data = parseJsonResponse(stage2Text);
    if (!stage2Data) {
      setLoading(false);
      return;
    }

    setStage2Results(stage2Data);

    // Optional: Generate video script from first hook
    if (generateScript && stage2Data[0]) {
      setLoadingStage('Generating 60-second video script...');
      const scriptPrompt = `Topic: "${input}"
Hook: "${stage2Data[0]}"
Platform: ${PLATFORMS[platform]}

Write a 60-second video script (max 180 words) with this structure:
- Hook (0–3s): The opening line (same as above)
- Story beat (3–30s): A brief personal or relatable moment that sets context
- Insight (30–45s): The reframe or key takeaway
- Soft CTA (45–60s): A gentle ask (follow for more, check link in bio, etc.)

Use Crosswalk Wisdom voice. Format as plain text with time markers in [brackets].`;

      const scriptText = await callApi(scriptPrompt, 500);
      if (scriptText) {
        setVideoScript(scriptText);
      }
    }

    setLoading(false);
    setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  };

  const handlePasteMode = async () => {
    if (!input.trim()) {
      setError('Please paste a hook or transcript');
      return;
    }

    setError('');
    setLoading(true);
    setStage1Results(null);
    setStage2Results(null);
    setVideoScript('');

    // Stage 1: Analyze
    setLoadingStage('Analyzing hook structure...');
    const stage1Prompt = `Analyze this hook/transcript:

"${input}"

Identify:
- The structural pattern (what makes it work?)
- The psychological trigger (why does it stop the scroll?)
- The core message or insight

Return ONLY valid JSON with no markdown, no preamble:
{
  "pattern": "...",
  "trigger": "...",
  "core_message": "..."
}`;

    const stage1Text = await callApi(stage1Prompt);
    if (!stage1Text) {
      setLoading(false);
      return;
    }

    const stage1Data = parseJsonResponse(stage1Text);
    if (!stage1Data) {
      setLoading(false);
      return;
    }

    setStage1Results(stage1Data);

    // Stage 2: Repurpose into 5 hooks
    setLoadingStage('Repurposing into 5 Crosswalk Wisdom hooks...');
    const stage2Prompt = `Original hook analysis:
Pattern: ${stage1Data.pattern}
Trigger: ${stage1Data.trigger}
Core message: ${stage1Data.core_message}

Original text: "${input}"

Platform focus: ${PLATFORMS[platform]}

Create 5 different hooks in Crosswalk Wisdom voice that use the same pattern and trigger but adapted for different angles or audiences within the burned-out high achiever space. Each should:
- Feel warm, genuine, conversational
- Use short sentences
- Be specific, not generic
- Optionally reference story assets (physician days, crosswalk, identity fear)
- Stand alone as a powerful opening line

Return ONLY valid JSON array with 5 hook strings, no markdown, no preamble:
["Hook 1", "Hook 2", "Hook 3", "Hook 4", "Hook 5"]`;

    const stage2Text = await callApi(stage2Prompt);
    if (!stage2Text) {
      setLoading(false);
      return;
    }

    const stage2Data = parseJsonResponse(stage2Text);
    if (!stage2Data) {
      setLoading(false);
      return;
    }

    setStage2Results(stage2Data);

    // Optional: Generate video script
    if (generateScript && stage2Data[0]) {
      setLoadingStage('Generating 60-second video script...');
      const scriptPrompt = `Hook: "${stage2Data[0]}"
Platform: ${PLATFORMS[platform]}

Write a 60-second video script (max 180 words) with this structure:
- Hook (0–3s): The opening line
- Story beat (3–30s): A brief relatable moment that sets context
- Insight (30–45s): The reframe or key takeaway
- Soft CTA (45–60s): A gentle ask

Use Crosswalk Wisdom voice. Format as plain text with time markers in [brackets].`;

      const scriptText = await callApi(scriptPrompt, 500);
      if (scriptText) {
        setVideoScript(scriptText);
      }
    }

    setLoading(false);
    setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const resetForm = () => {
    setInput('');
    setStage1Results(null);
    setStage2Results(null);
    setVideoScript('');
    setError('');
  };

  if (showApiForm) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ backgroundColor: '#f5f0e8' }}>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;700&display=swap');
          body { font-family: 'DM Sans', sans-serif; }
          h1, h2, h3 { font-family: 'Playfair Display', serif; }
        `}</style>
        <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-lg border-2" style={{ borderColor: '#b8860b' }}>
          <h1 className="text-3xl mb-2" style={{ color: '#1a1a1a' }}>Viral Hooks</h1>
          <p className="text-sm mb-6" style={{ color: '#666' }}>Crosswalk Wisdom Edition</p>

          <div className="mb-6">
            <label className="block text-sm font-500 mb-2" style={{ color: '#1a1a1a' }}>
              Anthropic API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-ant-..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-600"
              onKeyPress={(e) => e.key === 'Enter' && saveApiKey()}
            />
            <p className="text-xs mt-2" style={{ color: '#999' }}>
              🔒 Stored locally in your browser. Never sent anywhere except Anthropic's API.
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            onClick={saveApiKey}
            className="w-full py-2 px-4 text-white font-500 rounded-lg hover:opacity-90 transition"
            style={{ backgroundColor: '#b8860b' }}
          >
            Continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#f5f0e8' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;700&display=swap');
        body { font-family: 'DM Sans', sans-serif; }
        h1, h2, h3 { font-family: 'Playfair Display', serif; }
      `}</style>

      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl mb-1" style={{ color: '#1a1a1a' }}>Viral Hooks</h1>
              <p className="text-sm" style={{ color: '#666' }}>Research & repurpose. Crosswalk Wisdom voice.</p>
            </div>
            <button
              onClick={() => {
                setShowApiForm(true);
                localStorage.removeItem('anthropic_api_key');
              }}
              className="text-xs px-3 py-2 rounded border border-gray-300 hover:bg-gray-100"
              style={{ color: '#1a1a1a' }}
            >
              Change API Key
            </button>
          </div>
        </div>

        {/* Mode Toggle */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => { setMode('topic'); resetForm(); }}
            className={`px-4 py-2 rounded-lg font-500 transition ${
              mode === 'topic'
                ? 'text-white'
                : 'border-2 text-gray-700 hover:bg-gray-100'
            }`}
            style={mode === 'topic' ? { backgroundColor: '#b8860b' } : { borderColor: '#ccc', color: '#1a1a1a' }}
          >
            Topic Mode
          </button>
          <button
            onClick={() => { setMode('paste'); resetForm(); }}
            className={`px-4 py-2 rounded-lg font-500 transition ${
              mode === 'paste'
                ? 'text-white'
                : 'border-2 text-gray-700 hover:bg-gray-100'
            }`}
            style={mode === 'paste' ? { backgroundColor: '#b8860b' } : { borderColor: '#ccc', color: '#1a1a1a' }}
          >
            Paste Hook
          </button>
        </div>

        {/* Input Section */}
        <div className="bg-white p-6 rounded-lg mb-6 shadow-sm">
          <label className="block font-500 mb-2" style={{ color: '#1a1a1a' }}>
            {mode === 'topic' ? 'Enter a topic or theme' : 'Paste a hook or transcript'}
          </label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={mode === 'topic' ? 'E.g., Identity transition, fear of failure...' : 'Paste the full hook or transcript here...'}
            className="w-full h-24 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-600 resize-none"
            style={{ color: '#1a1a1a' }}
          />
          <p className="text-xs mt-2" style={{ color: '#999' }}>
            {mode === 'topic' ? 'What topic should the hooks focus on?' : 'Paste a real hook you want to analyze and adapt.'}
          </p>
        </div>

        {/* Platform Selector */}
        <div className="bg-white p-6 rounded-lg mb-6 shadow-sm">
          <label className="block font-500 mb-3" style={{ color: '#1a1a1a' }}>
            Platform Focus
          </label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none"
            style={{ color: '#1a1a1a' }}
          >
            {Object.entries(PLATFORMS).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* Options */}
        <div className="bg-white p-6 rounded-lg mb-6 shadow-sm">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={generateScript}
              onChange={(e) => setGenerateScript(e.target.checked)}
              className="w-4 h-4"
            />
            <span style={{ color: '#1a1a1a' }}>Generate 60-second video script from first hook</span>
          </label>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded" style={{ color: '#c53030' }}>
            <p className="font-500 mb-1">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="mb-6 p-6 bg-white rounded-lg text-center">
            <div className="inline-block w-8 h-8 border-4 border-gray-300 border-t-amber-600 rounded-full animate-spin mb-4"></div>
            <p style={{ color: '#1a1a1a' }}>{loadingStage}</p>
          </div>
        )}

        {/* Submit Button */}
        {!loading && (
          <button
            onClick={mode === 'topic' ? handleTopicMode : handlePasteMode}
            className="w-full py-3 px-6 text-white font-600 rounded-lg hover:opacity-90 transition mb-6"
            style={{ backgroundColor: '#b8860b' }}
            disabled={!input.trim()}
          >
            {mode === 'topic' ? 'Research Hooks' : 'Analyze & Repurpose'}
          </button>
        )}

        {/* Results Section */}
        {(stage1Results || stage2Results) && (
          <div ref={resultsRef} className="space-y-6">
            {/* Stage 1 Results */}
            {stage1Results && mode === 'topic' && (
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h2 className="text-2xl mb-4" style={{ color: '#1a1a1a' }}>Viral Patterns Found</h2>
                <div className="space-y-4">
                  {stage1Results.map((item, idx) => (
                    <div key={idx} className="p-4 border border-gray-200 rounded">
                      <h3 className="font-600 mb-2" style={{ color: '#b8860b' }}>{item.pattern}</h3>
                      <p className="text-sm mb-2" style={{ color: '#1a1a1a' }}>
                        <span className="font-500">Example:</span> {item.example}
                      </p>
                      <p className="text-sm" style={{ color: '#666' }}>
                        <span className="font-500">Why it works:</span> {item.why}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Stage 1 Results (Paste Mode) */}
            {stage1Results && mode === 'paste' && typeof stage1Results === 'object' && !Array.isArray(stage1Results) && (
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h2 className="text-2xl mb-4" style={{ color: '#1a1a1a' }}>Hook Analysis</h2>
                <div className="space-y-3">
                  <div>
                    <p className="font-500 mb-1" style={{ color: '#b8860b' }}>Pattern</p>
                    <p style={{ color: '#1a1a1a' }}>{stage1Results.pattern}</p>
                  </div>
                  <div>
                    <p className="font-500 mb-1" style={{ color: '#b8860b' }}>Psychological Trigger</p>
                    <p style={{ color: '#1a1a1a' }}>{stage1Results.trigger}</p>
                  </div>
                  <div>
                    <p className="font-500 mb-1" style={{ color: '#b8860b' }}>Core Message</p>
                    <p style={{ color: '#1a1a1a' }}>{stage1Results.core_message}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Stage 2 Results */}
            {stage2Results && (
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h2 className="text-2xl mb-4" style={{ color: '#1a1a1a' }}>
                  {mode === 'topic' ? 'Repurposed Hooks' : '5 Crosswalk Wisdom Hooks'}
                </h2>
                <div className="space-y-3">
                  {stage2Results.map((hook, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded border border-gray-200">
                      <span className="font-600 text-sm mt-1" style={{ color: '#b8860b' }}>
                        {idx + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p style={{ color: '#1a1a1a' }} className="break-words">{hook}</p>
                      </div>
                      <button
                        onClick={() => copyToClipboard(hook)}
                        className="flex-shrink-0 px-2 py-1 text-xs font-500 rounded border border-gray-300 hover:bg-gray-100 ml-2"
                        style={{ color: '#1a1a1a' }}
                      >
                        Copy
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Video Script */}
            {videoScript && (
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h2 className="text-2xl mb-4" style={{ color: '#1a1a1a' }}>60-Second Video Script</h2>
                <div className="p-4 bg-gray-50 rounded border border-gray-200 mb-4">
                  <p style={{ color: '#1a1a1a' }} className="whitespace-pre-wrap text-sm">{videoScript}</p>
                </div>
                <button
                  onClick={() => copyToClipboard(videoScript)}
                  className="px-4 py-2 text-sm font-500 rounded border-2 hover:bg-gray-100"
                  style={{ borderColor: '#b8860b', color: '#b8860b' }}
                >
                  Copy Script
                </button>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={resetForm}
                className="flex-1 py-3 px-4 font-600 rounded-lg border-2 hover:bg-gray-100"
                style={{ borderColor: '#b8860b', color: '#b8860b' }}
              >
                Start Over
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
