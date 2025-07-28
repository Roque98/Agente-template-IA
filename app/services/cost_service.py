from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.cost import Cost
from decimal import Decimal

class CostService:
    def __init__(self, db: Session):
        self.db = db
    
    def record_cost(
        self,
        user_id: int,
        cost_type: str,
        amount: Decimal,
        agent_id: Optional[int] = None,
        tool_id: Optional[int] = None,
        execution_id: Optional[int] = None,
        tokens_input: int = 0,
        tokens_output: int = 0,
        description: Optional[str] = None,
        currency: str = "USD"
    ) -> Cost:
        """Record a cost entry"""
        
        cost = Cost(
            user_id=user_id,
            agent_id=agent_id,
            tool_id=tool_id,
            execution_id=execution_id,
            cost_type=cost_type,
            amount=amount,
            currency=currency,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            description=description
        )
        
        self.db.add(cost)
        self.db.commit()
        self.db.refresh(cost)
        
        return cost
    
    def get_user_costs(
        self, 
        user_id: int, 
        cost_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> dict:
        """Get cost summary for a user"""
        
        query = self.db.query(Cost).filter(Cost.user_id == user_id)
        
        if cost_type:
            query = query.filter(Cost.cost_type == cost_type)
        
        if start_date:
            query = query.filter(Cost.created_at >= start_date)
        
        if end_date:
            query = query.filter(Cost.created_at <= end_date)
        
        costs = query.all()
        
        total_amount = sum(cost.amount for cost in costs)
        total_tokens_input = sum(cost.tokens_input for cost in costs)
        total_tokens_output = sum(cost.tokens_output for cost in costs)
        
        # Group by cost type
        by_type = {}
        for cost in costs:
            if cost.cost_type not in by_type:
                by_type[cost.cost_type] = {
                    "count": 0,
                    "total_amount": Decimal("0"),
                    "total_tokens_input": 0,
                    "total_tokens_output": 0
                }
            
            by_type[cost.cost_type]["count"] += 1
            by_type[cost.cost_type]["total_amount"] += cost.amount
            by_type[cost.cost_type]["total_tokens_input"] += cost.tokens_input
            by_type[cost.cost_type]["total_tokens_output"] += cost.tokens_output
        
        return {
            "total_amount": total_amount,
            "total_tokens_input": total_tokens_input,
            "total_tokens_output": total_tokens_output,
            "total_entries": len(costs),
            "by_type": by_type
        }
    
    def get_agent_costs(self, agent_id: int) -> dict:
        """Get cost summary for an agent"""
        
        costs = self.db.query(Cost).filter(Cost.agent_id == agent_id).all()
        
        total_amount = sum(cost.amount for cost in costs)
        total_tokens = sum(cost.tokens_input + cost.tokens_output for cost in costs)
        
        return {
            "agent_id": agent_id,
            "total_amount": total_amount,
            "total_tokens": total_tokens,
            "total_calls": len(costs)
        }