"""
Gemini LLM Client
Handles integration with Google's Gemini Flash 2.5 API for intelligent browser automation
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from playwright.async_api import Page
import google.generativeai as genai
from loguru import logger
from .prompt_templates import PromptTemplates
from .response_parser import ResponseParser


class GeminiClient:
    """Client for Gemini Flash 2.5 LLM integration"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.conversation_history = []
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.prompt_templates = PromptTemplates()
        self.response_parser = ResponseParser()
        
        logger.info(f"Gemini client initialized with model: {model_name}")
        
    async def analyze_page_and_plan(self, page_content: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Analyze page content and create action plan for the task"""
        try:
            # Prepare the analysis prompt
            prompt = self.prompt_templates.get_task_analysis_prompt(page_content, task)
            
            # Generate response
            response = await self._generate_content(prompt)
            
            # Parse the response
            action_plan = self.response_parser.parse_action_plan(response.text)
            
            # Store in conversation history
            self.conversation_history.append({
                'type': 'page_analysis',
                'task': task,
                'page_url': page_content.get('url'),
                'action_plan': action_plan,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            return action_plan
            
        except Exception as e:
            logger.error(f"Error in page analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'actions': []
            }
    
    async def execute_task(self, page: Page, task: str, max_steps: int = 10) -> str:
        """Execute a complete task with iterative LLM guidance"""
        logger.info(f"Starting task execution: {task}")
        
        step_count = 0
        task_completed = False
        execution_log = []
        
        while step_count < max_steps and not task_completed:
            step_count += 1
            logger.info(f"Executing step {step_count}/{max_steps}")
            
            try:
                # Get current page state
                from ..browser.controller import BrowserController
                controller = BrowserController({})
                page_content = await controller.get_page_content(page)
                
                # Get LLM analysis and next action
                analysis = await self.analyze_page_and_plan(page_content, task)
                
                if not analysis.get('success', True):
                    return f"Task failed at step {step_count}: {analysis.get('error')}"
                
                actions = analysis.get('actions', [])
                
                if not actions:
                    task_completed = True
                    break
                
                # Execute the first action
                action = actions[0]
                result = await controller.execute_action(page, action)
                
                execution_log.append({
                    'step': step_count,
                    'action': action,
                    'result': result
                })
                
                # Check if task is complete
                if action.get('completes_task', False) or result.get('task_complete', False):
                    task_completed = True
                    
                # Wait a bit between actions
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in step {step_count}: {e}")
                execution_log.append({
                    'step': step_count,
                    'error': str(e)
                })
                break
        
        # Generate summary
        if task_completed:
            summary = f"✅ Task completed successfully in {step_count} steps"
        else:
            summary = f"⚠️ Task reached maximum steps ({max_steps}) without completion"
            
        # Store execution in history
        self.conversation_history.append({
            'type': 'task_execution',
            'task': task,
            'steps': step_count,
            'completed': task_completed,
            'execution_log': execution_log,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        return summary
    
    async def handle_error_recovery(self, page_content: Dict[str, Any], error: str, 
                                   original_task: str) -> Dict[str, Any]:
        """Handle errors and suggest recovery actions"""
        try:
            prompt = self.prompt_templates.get_error_recovery_prompt(
                page_content, error, original_task
            )
            
            response = await self._generate_content(prompt)
            recovery_plan = self.response_parser.parse_action_plan(response.text)
            
            return recovery_plan
            
        except Exception as e:
            logger.error(f"Error in recovery planning: {e}")
            return {
                'success': False,
                'error': str(e),
                'actions': []
            }
    
    async def _generate_content(self, prompt: str) -> Any:
        """Generate content using Gemini API"""
        try:
            # Use async generation if available, otherwise use sync
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating content from Gemini: {e}")
            raise
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation history"""
        return {
            'total_interactions': len(self.conversation_history),
            'tasks_executed': len([h for h in self.conversation_history 
                                 if h['type'] == 'task_execution']),
            'pages_analyzed': len([h for h in self.conversation_history 
                                 if h['type'] == 'page_analysis']),
            'history': self.conversation_history[-5:]  # Last 5 interactions
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
