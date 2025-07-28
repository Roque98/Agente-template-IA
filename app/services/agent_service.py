import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.models.agent import Agent
from app.models.execution import Execution
from app.models.cost import Cost
from app.models.user import User
from app.services.tool_service import ToolService
from app.services.cost_service import CostService
from app.core.config import settings

class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.tool_service = ToolService(db)
        self.cost_service = CostService(db)
    
    def execute_agent(
        self, 
        agent_id: int, 
        user: User, 
        input_message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Execution:
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent with id {agent_id} not found")
        
        if not agent.is_active:
            raise ValueError(f"Agent {agent.name} is not active")
        
        execution = Execution(
            agent_id=agent_id,
            user_id=user.id,
            input_data=input_message,
            status="running"
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        try:
            start_time = time.time()
            
            # Initialize OpenAI LLM with agent configuration
            llm = ChatOpenAI(
                model_name=agent.model_name,
                temperature=float(agent.temperature),
                max_tokens=agent.max_tokens,
                top_p=float(agent.top_p),
                frequency_penalty=float(agent.frequency_penalty),
                presence_penalty=float(agent.presence_penalty),
                openai_api_key=settings.openai_api_key
            )
            
            # Prepare messages
            messages = []
            
            # Add system prompt if available
            if agent.system_prompt:
                system_content = agent.system_prompt
                if agent.personality:
                    system_content += f"\n\nPersonality: {agent.personality}"
                messages.append(SystemMessage(content=system_content))
            
            # Add context if provided
            if context:
                context_message = f"Context: {json.dumps(context, indent=2)}"
                messages.append(SystemMessage(content=context_message))
            
            # Add user input
            messages.append(HumanMessage(content=input_message))
            
            # Execute the LLM call
            response = llm(messages)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Estimate cost (simplified - in production, use actual token counts)
            tokens_used = self._estimate_tokens(input_message + response.content)
            cost = self._calculate_cost(agent.model_name, tokens_used)
            
            # Update execution
            execution.output_data = response.content
            execution.status = "completed"
            execution.execution_time_ms = execution_time_ms
            execution.tokens_used = tokens_used
            execution.cost = cost
            execution.completed_at = time.time()
            
            # Record cost
            self.cost_service.record_cost(
                user_id=user.id,
                agent_id=agent_id,
                execution_id=execution.id,
                cost_type="llm_call",
                amount=cost,
                tokens_input=len(input_message.split()),  # Simplified
                tokens_output=len(response.content.split()),  # Simplified
                description=f"LLM call for agent {agent.name}"
            )
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = time.time()
        
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def _estimate_tokens(self, text: str) -> int:
        # Simplified token estimation - in production, use tiktoken
        return len(text.split()) * 1.3  # Rough approximation
    
    def _calculate_cost(self, model_name: str, tokens: int) -> float:
        # Simplified cost calculation - update with actual OpenAI pricing
        cost_per_1k_tokens = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "gpt-3.5-turbo-16k": 0.004
        }
        
        rate = cost_per_1k_tokens.get(model_name, 0.002)
        return (tokens / 1000) * rate
    
    def get_agent_tools(self, agent_id: int) -> List[Dict[str, Any]]:
        """Get all tools available to an agent"""
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return []
        
        tools = []
        for agent_tool in agent.agent_tools:
            if agent_tool.is_active and agent_tool.tool.is_active:
                tool_config = {
                    "id": agent_tool.tool.id,
                    "name": agent_tool.tool.name,
                    "description": agent_tool.tool.description,
                    "endpoint_template": agent_tool.tool.endpoint_template,
                    "configuration": json.loads(agent_tool.configuration or "{}")
                }
                tools.append(tool_config)
        
        return tools