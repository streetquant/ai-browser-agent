"""
Command Line Interface Parser
Handles argument parsing and command structure
"""

import argparse
from typing import Optional


def create_cli_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser"""
    
    parser = argparse.ArgumentParser(
        description="AI Browser Agent - Intelligent browser automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s navigate --url "https://example.com" --headless
  %(prog)s task --prompt "Click the login button" --url "https://site.com"
  %(prog)s login --site "github.com" --username "user" --password "pass"
  %(prog)s interactive --site "https://admin.dashboard.com"
        """
    )
    
    # Global options
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    
    parser.add_argument(
        '--headed',
        action='store_true',
        help='Run browser in headed mode (overrides --headless)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30000,
        help='Default timeout in milliseconds (default: 30000)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Navigate command
    navigate_parser = subparsers.add_parser(
        'navigate',
        help='Navigate to a URL'
    )
    navigate_parser.add_argument(
        '--url',
        required=True,
        help='URL to navigate to'
    )
    navigate_parser.add_argument(
        '--wait-for',
        help='CSS selector to wait for after navigation'
    )
    
    # Task command
    task_parser = subparsers.add_parser(
        'task',
        help='Execute a task using LLM guidance'
    )
    task_parser.add_argument(
        '--prompt',
        required=True,
        help='Task description for the LLM'
    )
    task_parser.add_argument(
        '--url',
        help='URL to start the task from'
    )
    task_parser.add_argument(
        '--max-steps',
        type=int,
        default=10,
        help='Maximum number of automation steps (default: 10)'
    )
    
    # Login command
    login_parser = subparsers.add_parser(
        'login',
        help='Login to a website'
    )
    login_parser.add_argument(
        '--site',
        required=True,
        help='Website domain (e.g., github.com)'
    )
    login_parser.add_argument(
        '--username',
        help='Username for login'
    )
    login_parser.add_argument(
        '--password',
        help='Password for login'
    )
    login_parser.add_argument(
        '--save',
        action='store_true',
        help='Save credentials securely'
    )
    
    # Interactive command
    interactive_parser = subparsers.add_parser(
        'interactive',
        help='Start interactive mode'
    )
    interactive_parser.add_argument(
        '--site',
        help='Initial website to navigate to'
    )
    
    return parser


def post_process_args(args):
    """Post-process parsed arguments"""
    # Handle headed/headless logic
    if args.headed:
        args.headless = False
    
    return args
