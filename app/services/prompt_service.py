import re
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.prompt_template import PromptTemplate

class PromptService:
    def __init__(self, db: Session):
        self.db = db
    
    def render_template(self, template_id: int, variables: Dict[str, Any]) -> str:
        """Render a prompt template with provided variables"""
        
        template = self.db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id,
            PromptTemplate.is_active == True
        ).first()
        
        if not template:
            raise ValueError(f"Template with id {template_id} not found or inactive")
        
        # Get template variables
        template_variables = []
        if template.variables:
            try:
                template_variables = json.loads(template.variables)
            except json.JSONDecodeError:
                pass
        
        # Validate that all required variables are provided
        missing_vars = []
        for var in template_variables:
            if var not in variables:
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Render template
        content = template.template_content
        
        # Replace variables in format {variable_name}
        for var_name, var_value in variables.items():
            pattern = f"{{{var_name}}}"
            content = content.replace(pattern, str(var_value))
        
        return content
    
    def extract_variables_from_template(self, template_content: str) -> List[str]:
        """Extract variable names from a template content"""
        
        # Find all {variable_name} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template_content)
        
        # Remove duplicates and return
        return list(set(matches))
    
    def validate_template(self, template_content: str) -> Dict[str, Any]:
        """Validate a template and return analysis"""
        
        variables = self.extract_variables_from_template(template_content)
        
        # Check for common issues
        issues = []
        
        # Check for unclosed braces
        open_braces = template_content.count('{')
        close_braces = template_content.count('}')
        if open_braces != close_braces:
            issues.append("Mismatched braces - check for unclosed variable declarations")
        
        # Check for empty variables
        if '{}' in template_content:
            issues.append("Empty variable declarations found")
        
        # Check for nested braces
        if '{{' in template_content or '}}' in template_content:
            issues.append("Nested braces detected - use single braces for variables")
        
        return {
            "is_valid": len(issues) == 0,
            "variables": variables,
            "variable_count": len(variables),
            "issues": issues
        }
    
    def create_template_version(
        self, 
        original_template_id: int, 
        new_content: str,
        description: str = None
    ) -> PromptTemplate:
        """Create a new version of an existing template"""
        
        original = self.db.query(PromptTemplate).filter(
            PromptTemplate.id == original_template_id
        ).first()
        
        if not original:
            raise ValueError(f"Original template with id {original_template_id} not found")
        
        # Get next version number
        max_version = self.db.query(func.max(PromptTemplate.version)).filter(
            PromptTemplate.name == original.name
        ).scalar() or 0
        
        # Extract variables from new content
        variables = self.extract_variables_from_template(new_content)
        
        # Create new version
        new_template = PromptTemplate(
            name=original.name,
            template_content=new_content,
            description=description or f"Version {max_version + 1} of {original.name}",
            variables=json.dumps(variables),
            version=max_version + 1,
            created_by=original.created_by
        )
        
        self.db.add(new_template)
        self.db.commit()
        self.db.refresh(new_template)
        
        return new_template