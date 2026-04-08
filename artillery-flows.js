async function submitForm(page) {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.fill('input[name="username"]', 'ArtilleryUser');
    await page.click('button[type="submit"]');
    const result = page.locator('#result');
    await result.waitFor({ state: 'visible' });
    const saved = await result.textContent();
    if (!saved || !saved.includes('Saved: ArtilleryUser')) {
        throw new Error(`unexpected #result: ${saved}`);
    }
    const title = await page.locator('h1').textContent();
    if (title.trim() !== 'Stress Test Target') {
        throw new Error(`unexpected h1: ${title}`);
    }
}

module.exports = { submitForm };
