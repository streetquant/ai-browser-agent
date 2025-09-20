"""
Browser Controller
Manages Playwright browser instances and page interactions
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger


class BrowserController:
    """Main browser controller using Playwright"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.playwright = None
        self.browser = None
        
    async def initialize(self):
        """Initialize Playwright and browser"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            
        browser_type = getattr(self.playwright, self.config.get('browser', 'chromium'))
        self.browser = await browser_type.launch(
            headless=self.config.get('headless', True),
            args=self.config.get('args', [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ])
        )
        
        logger.info(f"Browser initialized: {self.config.get('browser', 'chromium')}")
        
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    @asynccontextmanager
    async def create_context(self, headless: Optional[bool] = None):
        """Create a browser context with automatic cleanup"""
        await self.initialize()
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.config.get('user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ),
            ignore_https_errors=True
        )
        
        try:
            yield context
        finally:
            await context.close()
            
    async def take_screenshot(self, page: Page, path: str = None) -> bytes:
        """Take a screenshot of the current page"""
        screenshot = await page.screenshot(
            path=path,
            full_page=True,
            type='png'
        )
        return screenshot
        
    async def get_page_content(self, page: Page) -> Dict[str, Any]:
        """Extract comprehensive page content for LLM analysis"""
        try:
            # Get basic page info
            title = await page.title()
            url = page.url
            
            # Get visible text content
            text_content = await page.evaluate("""
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style');
                    scripts.forEach(el => el.remove());
                    
                    // Get visible text
                    return document.body.innerText || document.body.textContent || '';
                }
            """)
            
            # Get interactive elements
            interactive_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        'button', 'input', 'select', 'textarea', 
                        'a[href]', '[onclick]', '[role="button"]'
                    ];
                    
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach((el, index) => {
                            if (el.offsetParent !== null) { // Only visible elements
                                elements.push({
                                    tag: el.tagName.toLowerCase(),
                                    type: el.type || '',
                                    text: el.innerText?.slice(0, 100) || '',
                                    placeholder: el.placeholder || '',
                                    href: el.href || '',
                                    selector: selector + ':nth-of-type(' + (index + 1) + ')'
                                });
                            }
                        });
                    });
                    
                    return elements.slice(0, 50); // Limit to first 50 elements
                }
            """)
            
            # Get form information
            forms = await page.evaluate("""
                () => {
                    const forms = [];
                    document.querySelectorAll('form').forEach((form, index) => {
                        const fields = [];
                        form.querySelectorAll('input, select, textarea').forEach(field => {
                            fields.push({
                                name: field.name || '',
                                type: field.type || '',
                                placeholder: field.placeholder || '',
                                required: field.required
                            });
                        });
                        
                        forms.push({
                            action: form.action || '',
                            method: form.method || 'get',
                            fields: fields,
                            selector: 'form:nth-of-type(' + (index + 1) + ')'
                        });
                    });
                    
                    return forms;
                }
            """)
            
            return {
                'title': title,
                'url': url,
                'text_content': text_content[:5000],  # Limit content length
                'interactive_elements': interactive_elements,
                'forms': forms,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error extracting page content: {e}")
            return {
                'title': await page.title(),
                'url': page.url,
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }
            
    async def execute_action(self, page: Page, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a browser action based on LLM instruction"""
        try:
            action_type = action.get('type')
            
            if action_type == 'click':
                selector = action.get('selector')
                await page.click(selector, timeout=10000)
                return {'success': True, 'message': f'Clicked {selector}'}
                
            elif action_type == 'type':
                selector = action.get('selector')
                text = action.get('text')
                await page.fill(selector, text, timeout=10000)
                return {'success': True, 'message': f'Typed in {selector}'}
                
            elif action_type == 'navigate':
                url = action.get('url')
                await page.goto(url, timeout=30000)
                return {'success': True, 'message': f'Navigated to {url}'}
                
            elif action_type == 'wait':
                selector = action.get('selector')
                timeout = action.get('timeout', 10000)
                await page.wait_for_selector(selector, timeout=timeout)
                return {'success': True, 'message': f'Waited for {selector}'}
                
            elif action_type == 'scroll':
                direction = action.get('direction', 'down')
                amount = action.get('amount', 500)
                
                if direction == 'down':
                    await page.evaluate(f'window.scrollBy(0, {amount})')
                elif direction == 'up':
                    await page.evaluate(f'window.scrollBy(0, -{amount})')
                    
                return {'success': True, 'message': f'Scrolled {direction}'}
                
            elif action_type == 'select':
                selector = action.get('selector')
                value = action.get('value')
                await page.select_option(selector, value, timeout=10000)
                return {'success': True, 'message': f'Selected {value} in {selector}'}
                
            else:
                return {'success': False, 'message': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {'success': False, 'message': f'Action failed: {str(e)}'}
