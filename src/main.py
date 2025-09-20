"""
AI Browser Agent - Main Entry Point
Intelligent browser automation using Playwright and Gemini Flash 2.5 LLM
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from cli.parser import create_cli_parser
from browser.controller import BrowserController
from llm.gemini_client import GeminiClient
from security.credential_manager import CredentialManager
from config.settings import Settings


async def main():
    """Main application entry point"""
    try:
        # Parse command line arguments
        parser = create_cli_parser()
        args = parser.parse_args()
        
        # Load configuration
        settings = Settings()
        
        # Initialize components
        credential_manager = CredentialManager()
        llm_client = GeminiClient(settings.gemini_api_key)
        browser_controller = BrowserController(settings.browser_config)
        
        # Execute command
        if args.command == 'navigate':
            await execute_navigate_command(args, browser_controller)
        elif args.command == 'task':
            await execute_task_command(args, browser_controller, llm_client)
        elif args.command == 'login':
            await execute_login_command(args, browser_controller, credential_manager)
        elif args.command == 'interactive':
            await execute_interactive_mode(args, browser_controller, llm_client)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


async def execute_navigate_command(args, browser_controller):
    """Execute navigation command"""
    async with browser_controller.create_context(headless=args.headless) as context:
        page = await context.new_page()
        await page.goto(args.url)
        
        if args.wait_for:
            await page.wait_for_selector(args.wait_for)
        
        print(f"✅ Navigated to: {args.url}")
        
        if not args.headless:
            input("Press Enter to close browser...")


async def execute_task_command(args, browser_controller, llm_client):
    """Execute LLM-guided task"""
    async with browser_controller.create_context(headless=args.headless) as context:
        page = await context.new_page()
        
        # Start with current page or navigate to URL
        if args.url:
            await page.goto(args.url)
        
        # Let LLM analyze and execute the task
        result = await llm_client.execute_task(page, args.prompt)
        print(f"✅ Task completed: {result}")


async def execute_login_command(args, browser_controller, credential_manager):
    """Execute login command"""
    async with browser_controller.create_context(headless=args.headless) as context:
        page = await context.new_page()
        
        # Get or store credentials
        if args.username and args.password:
            credential_manager.store_credentials(args.site, args.username, args.password)
        
        credentials = credential_manager.get_credentials(args.site)
        if not credentials:
            print("❌ No credentials found for site")
            return
        
        # Navigate and login
        await page.goto(f"https://{args.site}")
        # Login logic would be implemented here
        print(f"✅ Logged in to: {args.site}")


async def execute_interactive_mode(args, browser_controller, llm_client):
    """Execute interactive mode"""
    print("🤖 Starting interactive mode...")
    print("Type 'exit' to quit, 'help' for commands")
    
    async with browser_controller.create_context(headless=False) as context:
        page = await context.new_page()
        
        if args.site:
            await page.goto(args.site)
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() in ['exit', 'quit']:
                    break
                elif command.lower() == 'help':
                    print("Available commands: navigate <url>, task <description>, exit")
                elif command.startswith('navigate '):
                    url = command[9:].strip()
                    await page.goto(url)
                    print(f"✅ Navigated to: {url}")
                elif command.startswith('task '):
                    task = command[5:].strip()
                    result = await llm_client.execute_task(page, task)
                    print(f"✅ {result}")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
    
    print("👋 Interactive mode ended")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
