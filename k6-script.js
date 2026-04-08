import { browser } from 'k6/browser';
import { check } from 'https://jslib.k6.io/k6-utils/1.5.0/index.js';

export const options = {
    scenarios: {
        ui: {
            executor: 'constant-vus',
            vus: 3,
            duration: '10s',
            options: {
                browser: { type: 'chromium' },
            },
        },
    },
};

export default async function () {
    const page = await browser.newPage();
    try {
        await page.goto('http://webapp:5000/', { waitUntil: 'domcontentloaded' });
        await page.locator('input[name="username"]').type('TestUser');
        await page.locator('button[type="submit"]').click();
        await page.locator('#result').waitFor({ state: 'visible' });
        await check(page.locator('#result'), {
            'saved response': async (lo) =>
                (await lo.textContent())?.includes('Saved: TestUser') ?? false,
        });
        await check(page.locator('h1'), {
            'header is visible': async (lo) => (await lo.textContent()) === 'Stress Test Target',
        });
    } finally {
        await page.close();
    }
}
