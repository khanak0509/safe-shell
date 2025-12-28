from typing import List , Dict , Literal
from pydantic import BaseModel 

class State(BaseModel):
    raw_command: str
    normalized_command: str
    commands: list[str]      
    cwd: str
    is_root_dir: bool
    is_root_user: bool
    os_type: str
    rule_risk: Literal["NONE" , "LOW" , "MEDIUM" , "HIGH" , "CRITICAL"]
    context_risk: Literal["NONE" , "LOW" , "MEDIUM" , "HIGH" , "CRITICAL"]
    final_risk: str
    decision: str
    explanation: str
    precautions: str
    safer_alternative: str


