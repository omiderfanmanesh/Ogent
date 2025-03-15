"""Command DTOs for the controller service."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class CommandRequestDTO:
    """Command request data transfer object."""
    
    command: str
    agent_id: str
    execution_target: str = "auto"
    use_ai: bool = False
    system: str = "Linux"
    context: str = "Server administration"
    requester_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command request to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command request
        """
        return {
            "command": self.command,
            "agent_id": self.agent_id,
            "execution_target": self.execution_target,
            "use_ai": self.use_ai,
            "system": self.system,
            "context": self.context,
            "requester_id": self.requester_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandRequestDTO':
        """Create a command request from a dictionary.
        
        Args:
            data: Dictionary representation of the command request
            
        Returns:
            CommandRequestDTO: Command request instance
        """
        return cls(
            command=data.get("command", ""),
            agent_id=data.get("agent_id", ""),
            execution_target=data.get("execution_target", "auto"),
            use_ai=data.get("use_ai", False),
            system=data.get("system", "Linux"),
            context=data.get("context", "Server administration"),
            requester_id=data.get("requester_id")
        )


@dataclass
class CommandValidationDTO:
    """Command validation data transfer object."""
    
    safe: bool
    risk_level: str
    risks: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the validation
        """
        return {
            "safe": self.safe,
            "risk_level": self.risk_level,
            "risks": self.risks,
            "suggestions": self.suggestions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandValidationDTO':
        """Create a validation from a dictionary.
        
        Args:
            data: Dictionary representation of the validation
            
        Returns:
            CommandValidationDTO: Validation instance
        """
        return cls(
            safe=data.get("safe", True),
            risk_level=data.get("risk_level", "unknown"),
            risks=data.get("risks", []),
            suggestions=data.get("suggestions", [])
        )


@dataclass
class CommandOptimizationDTO:
    """Command optimization data transfer object."""
    
    optimized_command: str
    improvements: List[str] = field(default_factory=list)
    explanation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the optimization to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the optimization
        """
        return {
            "optimized_command": self.optimized_command,
            "improvements": self.improvements,
            "explanation": self.explanation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandOptimizationDTO':
        """Create an optimization from a dictionary.
        
        Args:
            data: Dictionary representation of the optimization
            
        Returns:
            CommandOptimizationDTO: Optimization instance
        """
        return cls(
            optimized_command=data.get("optimized_command", ""),
            improvements=data.get("improvements", []),
            explanation=data.get("explanation")
        )


@dataclass
class CommandComponentDTO:
    """Command component data transfer object."""
    
    component: str
    function: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the component
        """
        return {
            "component": self.component,
            "function": self.function
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandComponentDTO':
        """Create a component from a dictionary.
        
        Args:
            data: Dictionary representation of the component
            
        Returns:
            CommandComponentDTO: Component instance
        """
        return cls(
            component=data.get("component", ""),
            function=data.get("function", "")
        )


@dataclass
class CommandEnrichmentDTO:
    """Command enrichment data transfer object."""
    
    purpose: str
    components: List[CommandComponentDTO] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the enrichment to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the enrichment
        """
        return {
            "purpose": self.purpose,
            "components": [component.to_dict() for component in self.components],
            "side_effects": self.side_effects,
            "prerequisites": self.prerequisites,
            "related_commands": self.related_commands
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandEnrichmentDTO':
        """Create an enrichment from a dictionary.
        
        Args:
            data: Dictionary representation of the enrichment
            
        Returns:
            CommandEnrichmentDTO: Enrichment instance
        """
        components = [
            CommandComponentDTO.from_dict(component)
            for component in data.get("components", [])
        ]
        
        return cls(
            purpose=data.get("purpose", ""),
            components=components,
            side_effects=data.get("side_effects", []),
            prerequisites=data.get("prerequisites", []),
            related_commands=data.get("related_commands", [])
        )


@dataclass
class CommandAIProcessingDTO:
    """Command AI processing data transfer object."""
    
    original_command: str
    processed_command: str
    validation: CommandValidationDTO
    optimization: CommandOptimizationDTO
    enrichment: CommandEnrichmentDTO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AI processing to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the AI processing
        """
        return {
            "original_command": self.original_command,
            "processed_command": self.processed_command,
            "validation": self.validation.to_dict(),
            "optimization": self.optimization.to_dict(),
            "enrichment": self.enrichment.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandAIProcessingDTO':
        """Create an AI processing from a dictionary.
        
        Args:
            data: Dictionary representation of the AI processing
            
        Returns:
            CommandAIProcessingDTO: AI processing instance
        """
        return cls(
            original_command=data.get("original_command", ""),
            processed_command=data.get("processed_command", ""),
            validation=CommandValidationDTO.from_dict(data.get("validation", {})),
            optimization=CommandOptimizationDTO.from_dict(data.get("optimization", {})),
            enrichment=CommandEnrichmentDTO.from_dict(data.get("enrichment", {}))
        )


@dataclass
class CommandResponseDTO:
    """Command response data transfer object."""
    
    command: str
    command_id: str
    agent_id: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    status: str = "pending"
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    execution_type: Optional[str] = None
    target: Optional[str] = None
    ai_processing: Optional[CommandAIProcessingDTO] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command response to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command response
        """
        result = {
            "command": self.command,
            "command_id": self.command_id,
            "agent_id": self.agent_id,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "execution_type": self.execution_type,
            "target": self.target
        }
        
        if self.ai_processing:
            result["ai_processing"] = self.ai_processing.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandResponseDTO':
        """Create a command response from a dictionary.
        
        Args:
            data: Dictionary representation of the command response
            
        Returns:
            CommandResponseDTO: Command response instance
        """
        # Convert ISO format timestamp to datetime if it's a string
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        # Create AI processing if present
        ai_processing = None
        if "ai_processing" in data:
            ai_processing = CommandAIProcessingDTO.from_dict(data["ai_processing"])
        
        return cls(
            command=data.get("command", ""),
            command_id=data.get("command_id", ""),
            agent_id=data.get("agent_id", ""),
            exit_code=data.get("exit_code"),
            stdout=data.get("stdout"),
            stderr=data.get("stderr"),
            status=data.get("status", "pending"),
            timestamp=timestamp,
            execution_type=data.get("execution_type"),
            target=data.get("target"),
            ai_processing=ai_processing
        ) 