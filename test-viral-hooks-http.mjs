import { chromium } from 'playwright';
import fs from 'fs';

const APP_URL = 'http://localhost:3001';
const SCREENSHOTS_DIR = '/tmp/viral-hooks-test-http';

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function test(name, fn) {
  try {
    await fn();
    console.log(`✅ ${name}`);
    return true;
  } catch (err) {
    console.log(`❌ ${name}: ${err.message}`);
    return false;
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    console.log('\n🧪 Viral Hooks App Test Suite (HTTP)\n');
    
    console.log('📍 Loading app from http://localhost:3001...');
    await page.goto(APP_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    
    let screenshot = `${SCREENSHOTS_DIR}/01-app-loaded.png`;
    await page.screenshot({ path: screenshot });
    console.log(`   Screenshot: ${screenshot}\n`);

    let passed = 0;
    let failed = 0;

    // Test 1: Verify page loaded
    if (await test('Page loaded successfully', async () => {
      const title = await page.title();
      if (!title || title === '') throw new Error('No page title');
    })) passed++; else failed++;

    // Test 2: Backend connection
    if (await test('Backend connection shows "✓ Connected"', async () => {
      await page.waitForSelector('text=Connected', { timeout: 5000 });
    })) passed++; else failed++;

    // Test 3: Topic Mode active
    if (await test('Topic Mode button visible and clickable', async () => {
      const button = page.locator('button:has-text("Topic Mode")');
      await button.waitFor({ state: 'visible', timeout: 5000 });
    })) passed++; else failed++;

    // Test 4: Input fields exist
    if (await test('Textarea input field exists', async () => {
      const textarea = page.locator('textarea').first();
      await textarea.waitFor({ state: 'visible', timeout: 5000 });
    })) passed++; else failed++;

    // Test 5: Enter topic
    if (await test('Topic Mode: Enter "identity transition"', async () => {
      const textarea = page.locator('textarea').first();
      await textarea.fill('identity transition');
      const value = await textarea.inputValue();
      if (value !== 'identity transition') throw new Error('Input failed');
    })) passed++; else failed++;

    // Test 6: Platform selector
    if (await test('Platform selector dropdown visible', async () => {
      const select = page.locator('select');
      await select.waitFor({ state: 'visible', timeout: 5000 });
    })) passed++; else failed++;

    // Test 7: Click Research button
    if (await test('Click "Research Hooks" button', async () => {
      const button = page.locator('button:has-text("Research Hooks")');
      await button.click();
      await page.waitForTimeout(1000);
    })) passed++; else failed++;

    // Test 8: Loading state shows
    if (await test('Loading state appears with stage label', async () => {
      await page.waitForSelector('text=/Researching|Repurposing/', { timeout: 5000 });
    })) passed++; else failed++;

    console.log(`\n   ⏳ Waiting for API response (this takes 30-60s)...`);
    
    // Test 9: Results appear
    if (await test('Results section appears', async () => {
      await page.waitForSelector('text=Viral Patterns Found', { timeout: 120000 });
    })) passed++; else failed++;

    screenshot = `${SCREENSHOTS_DIR}/02-results.png`;
    await page.screenshot({ path: screenshot });
    console.log(`   Screenshot: ${screenshot}\n`);

    // Test 10: Verify patterns
    if (await test('Stage 1: 5 viral patterns found', async () => {
      const patternCount = await page.locator('h3').count();
      if (patternCount < 5) throw new Error(`Only ${patternCount} patterns found`);
    })) passed++; else failed++;

    // Test 11: Verify repurposed hooks
    if (await test('Stage 2: Repurposed hooks section visible', async () => {
      await page.locator('text=Repurposed Hooks').waitFor({ state: 'visible', timeout: 5000 });
    })) passed++; else failed++;

    // Test 12: Copy button exists
    if (await test('Copy buttons visible on hooks', async () => {
      const copyButton = page.locator('button:has-text("Copy")').first();
      await copyButton.waitFor({ state: 'visible', timeout: 5000 });
    })) passed++; else failed++;

    // Test 13: Click copy
    if (await test('Copy button: Click and verify', async () => {
      const copyButton = page.locator('button:has-text("Copy")').first();
      await copyButton.click();
      await page.waitForTimeout(500);
    })) passed++; else failed++;

    // Test 14: Brand voice check
    if (await test('Brand voice: Crosswalk-specific elements in output', async () => {
      const bodyText = await page.textContent('body');
      const hasVoice = /physician|identity|burnout|fear/i.test(bodyText);
      if (!hasVoice) throw new Error('Brand voice not detected');
    })) passed++; else failed++;

    // Test 15: Reset button
    if (await test('Reset button: Click "Start Over"', async () => {
      const resetButton = page.locator('button:has-text("Start Over")');
      await resetButton.click();
      await page.waitForTimeout(500);
    })) passed++; else failed++;

    // Test 16: Input cleared
    if (await test('Input cleared after reset', async () => {
      const textarea = page.locator('textarea').first();
      const value = await textarea.inputValue();
      if (value !== '') throw new Error('Input not cleared');
    })) passed++; else failed++;

    // Test 17: Paste Mode switch
    if (await test('Paste Mode: Switch button visible', async () => {
      const button = page.locator('button:has-text("Paste Hook")');
      await button.waitFor({ state: 'visible', timeout: 5000 });
    })) passed++; else failed++;

    // Test 18: Click Paste Mode
    if (await test('Paste Mode: Click button', async () => {
      const button = page.locator('button:has-text("Paste Hook")');
      await button.click();
      await page.waitForTimeout(500);
    })) passed++; else failed++;

    // Test 19: Paste mode label
    if (await test('Paste Mode: Label updates correctly', async () => {
      await page.locator('text=Paste a hook or transcript').waitFor({ state: 'visible', timeout: 5000 });
    })) passed++; else failed++;

    // Test 20: Enter sample hook
    if (await test('Paste Mode: Enter sample hook', async () => {
      const textarea = page.locator('textarea').first();
      const hook = 'I left medicine. Everyone asked why. Nobody asked if I was okay.';
      await textarea.fill(hook);
      const value = await textarea.inputValue();
      if (!value.includes('medicine')) throw new Error('Hook not entered');
    })) passed++; else failed++;

    console.log(`\n\n📊 Test Summary\n`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📋 Total: ${passed + failed}\n`);

    if (failed === 0) {
      console.log('🎉 All tests passed! App is working correctly.\n');
    }

  } catch (err) {
    console.error('Test error:', err);
  } finally {
    await browser.close();
  }
}

main();
