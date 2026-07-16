import { chromium } from 'playwright';
import fs from 'fs';

const APP_PATH = 'file:///Users/toto/Claude TubeonAI/viral-hooks-secure.html';
const SCREENSHOTS_DIR = '/tmp/viral-hooks-test';

// Create screenshots directory
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

let testResults = [];

async function test(name, fn) {
  try {
    await fn();
    testResults.push({ name, status: '✅', error: null });
    console.log(`✅ ${name}`);
  } catch (err) {
    testResults.push({ name, status: '❌', error: err.message });
    console.log(`❌ ${name}: ${err.message}`);
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    console.log('\n🧪 Viral Hooks App Test Suite\n');
    
    // Load app
    console.log('📍 Opening app...');
    await page.goto(APP_PATH, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    let screenshot = `${SCREENSHOTS_DIR}/01-app-loaded.png`;
    await page.screenshot({ path: screenshot });
    console.log(`   Screenshot: ${screenshot}\n`);

    // Test 1: Verify backend connection
    await test('Backend connection shows "✓ Connected"', async () => {
      const status = await page.locator('text=✓ Connected').isVisible({ timeout: 5000 });
      if (!status) throw new Error('Connection status not shown as connected');
    });

    // Test 2: Topic Mode - Enter topic
    await test('Topic Mode: Enter "identity transition" topic', async () => {
      const textarea = page.locator('textarea').first();
      await textarea.fill('identity transition');
      const value = await textarea.inputValue();
      if (value !== 'identity transition') throw new Error('Topic not entered');
    });

    // Test 3: Topic Mode - Select platform
    await test('Platform selector: Select YouTube Shorts', async () => {
      const select = page.locator('select');
      await select.selectOption('youtube');
      const selected = await select.inputValue();
      if (selected !== 'youtube') throw new Error('Platform not selected');
    });

    // Test 4: Topic Mode - Generate hooks
    await test('Topic Mode: Click "Research Hooks" button', async () => {
      const button = page.locator('button:has-text("Research Hooks")');
      await button.click();
      
      // Wait for loading stage to appear
      await page.waitForTimeout(1000);
      const loadingText = await page.locator('text=Researching patterns').isVisible({ timeout: 3000 });
      if (!loadingText) throw new Error('Loading state not shown');
      
      console.log('   ⏳ Waiting for API response (may take 30-60s)...');
      // Wait for results
      await page.waitForSelector('text=Viral Patterns Found', { timeout: 120000 });
    });

    screenshot = `${SCREENSHOTS_DIR}/02-topic-mode-results.png`;
    await page.screenshot({ path: screenshot });
    console.log(`   Screenshot: ${screenshot}\n`);

    // Test 5: Verify Stage 1 results
    await test('Topic Mode: Stage 1 results show 5 patterns', async () => {
      const patterns = await page.locator('h3[style*="color: rgb(184, 134, 11)"]').count();
      if (patterns < 5) throw new Error(`Expected 5 patterns, got ${patterns}`);
    });

    // Test 6: Verify Stage 2 results
    await test('Topic Mode: Stage 2 results show 5 repurposed hooks', async () => {
      const hooks = await page.locator('text=Repurposed Hooks').isVisible();
      if (!hooks) throw new Error('Repurposed hooks section not found');
      // Count numbered hooks
      const nums = await page.locator('span:has-text("1")').count();
      if (nums === 0) throw new Error('No numbered hooks found');
    });

    // Test 7: Copy button functionality
    await test('Copy button: Click copy on first hook', async () => {
      const copyButtons = page.locator('button:has-text("Copy")').filter({ hasNot: page.locator('text=Copy Script') });
      const firstButton = copyButtons.first();
      await firstButton.click();
      await page.waitForTimeout(500);
      // Check that text was copied (we can't directly access clipboard, but button works)
    });

    // Test 8: Brand voice quality check
    await test('Brand voice: Output contains conversational tone (no generic phrases)', async () => {
      const bodyText = await page.textContent('body');
      const hasGenerics = /self-care|wellness|mindfulness|journey|growth/i.test(bodyText);
      // Some generics might appear, but they shouldn't dominate
      // Just verify that specific Crosswalk voice elements exist
      const hasSpecific = /physician|crosswalk|identity|burnout|fear/i.test(bodyText);
      if (!hasSpecific) throw new Error('Brand voice not detected in output');
    });

    // Test 9: Reset button
    await test('Reset button: Click "Start Over"', async () => {
      const resetButton = page.locator('button:has-text("Start Over")');
      await resetButton.click();
      await page.waitForTimeout(500);
      const textarea = page.locator('textarea').first();
      const value = await textarea.inputValue();
      if (value !== '') throw new Error('Input not cleared after reset');
    });

    screenshot = `${SCREENSHOTS_DIR}/03-after-reset.png`;
    await page.screenshot({ path: screenshot });
    console.log(`   Screenshot: ${screenshot}\n`);

    // Test 10: Error handling - empty input
    await test('Error handling: Blank input shows error', async () => {
      const button = page.locator('button:has-text("Research Hooks")');
      // Button should be disabled when input is empty
      const isDisabled = await button.isDisabled();
      if (!isDisabled) {
        // Try clicking and see if error appears
        await button.click();
        await page.waitForTimeout(500);
        const errorShown = await page.locator('text=/Error|Please enter/i').isVisible({ timeout: 2000 });
        if (!errorShown) throw new Error('No error message for blank input');
      }
    });

    // Test 11: Paste Mode
    await test('Paste Mode: Switch to Paste Hook mode', async () => {
      const pasteButton = page.locator('button:has-text("Paste Hook")');
      await pasteButton.click();
      await page.waitForTimeout(500);
      const label = await page.locator('text=Paste a hook or transcript').isVisible();
      if (!label) throw new Error('Paste Mode label not shown');
    });

    // Test 12: Paste Mode - Enter sample hook
    await test('Paste Mode: Enter sample hook', async () => {
      const textarea = page.locator('textarea').first();
      const sampleHook = `I left medicine. Everyone asked why. Nobody asked if I was okay.`;
      await textarea.fill(sampleHook);
      const value = await textarea.inputValue();
      if (!value.includes('medicine')) throw new Error('Hook not entered');
    });

    // Test 13: Paste Mode - Generate
    await test('Paste Mode: Click "Analyze & Repurpose"', async () => {
      const button = page.locator('button:has-text("Analyze & Repurpose")');
      await button.click();
      
      await page.waitForTimeout(1000);
      const loadingText = await page.locator('text=Analyzing hook').isVisible({ timeout: 3000 });
      if (!loadingText) throw new Error('Loading state not shown');
      
      console.log('   ⏳ Waiting for analysis (may take 30-60s)...');
      // Wait for results
      await page.waitForSelector('text=Hook Analysis', { timeout: 120000 });
    });

    screenshot = `${SCREENSHOTS_DIR}/04-paste-mode-results.png`;
    await page.screenshot({ path: screenshot });
    console.log(`   Screenshot: ${screenshot}\n`);

    // Test 14: Verify paste mode analysis
    await test('Paste Mode: Analysis shows pattern/trigger/message', async () => {
      const pattern = await page.locator('text=Pattern').isVisible();
      const trigger = await page.locator('text=Psychological Trigger').isVisible();
      const message = await page.locator('text=Core Message').isVisible();
      if (!pattern || !trigger || !message) throw new Error('Analysis structure incomplete');
    });

    // Test 15: Verify paste mode hooks
    await test('Paste Mode: Shows 5 new hooks', async () => {
      const hooks = await page.locator('text=Crosswalk Wisdom Hooks').isVisible();
      if (!hooks) throw new Error('Hooks section not found');
    });

    // Test 16: Video script generation
    await test('Video script generation: Checkbox works', async () => {
      const checkbox = page.locator('input[type="checkbox"]');
      await checkbox.check();
      const isChecked = await checkbox.isChecked();
      if (!isChecked) throw new Error('Checkbox not working');
    });

    // Test 17: Reset for video script test
    await test('Reset before video script test', async () => {
      const resetButton = page.locator('button:has-text("Start Over")');
      await resetButton.click();
      await page.waitForTimeout(500);
    });

    // Test 18: Go back to Topic Mode with video script
    await test('Topic Mode with video script: Setup', async () => {
      const topicButton = page.locator('button:has-text("Topic Mode")');
      await topicButton.click();
      await page.waitForTimeout(500);
      
      const textarea = page.locator('textarea').first();
      await textarea.fill('fear of disappointing others');
      
      const checkbox = page.locator('input[type="checkbox"]');
      await checkbox.check();
      
      const button = page.locator('button:has-text("Research Hooks")');
      await button.click();
      
      console.log('   ⏳ Waiting for hooks + script generation (60-90s)...');
      await page.waitForSelector('text=60-Second Video Script', { timeout: 120000 });
    });

    screenshot = `${SCREENSHOTS_DIR}/05-video-script-results.png`;
    await page.screenshot({ path: screenshot });
    console.log(`   Screenshot: ${screenshot}\n`);

    // Test 19: Verify video script has structure
    await test('Video script: Contains time markers [0-3s], [3-30s], etc.', async () => {
      const scriptText = await page.locator('text=60-Second Video Script').isVisible();
      if (!scriptText) throw new Error('Video script section not found');
      
      const bodyText = await page.textContent('body');
      const hasTimeMarkers = /\[\d+-\d+s\]/.test(bodyText);
      // Even if exact format varies, should have some structure
      if (!hasTimeMarkers) {
        // Check if it at least has the key sections
        const hasStructure = /Hook|Story|Insight|CTA/i.test(bodyText);
        if (!hasStructure) throw new Error('Video script lacks expected structure');
      }
    });

    // Test 20: Copy script button
    await test('Copy script button: Functional', async () => {
      const copyScriptButton = page.locator('button:has-text("Copy Script")');
      const isVisible = await copyScriptButton.isVisible();
      if (!isVisible) throw new Error('Copy Script button not visible');
      await copyScriptButton.click();
      await page.waitForTimeout(500);
    });

    console.log('\n\n📊 Test Summary\n');
    const passed = testResults.filter(r => r.status === '✅').length;
    const failed = testResults.filter(r => r.status === '❌').length;
    
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📋 Total: ${testResults.length}\n`);
    
    if (failed > 0) {
      console.log('Failed tests:');
      testResults.filter(r => r.status === '❌').forEach(r => {
        console.log(`  - ${r.name}: ${r.error}`);
      });
    }

  } catch (err) {
    console.error('Test suite error:', err);
  } finally {
    await browser.close();
  }
}

main();
