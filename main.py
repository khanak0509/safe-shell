import platform 
from langgraph.graph import StateGraph , START , END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import re 
import json 
import os 
import time 
from numpy import empty
from Schema_class import * 
from list_of_cmds import * 
from prompt import * 
from helper_function import * 
from initialize_llm import * 

def NormalizeCommandNode(state: State):
    raw_cmd = state.raw_command

    if not raw_cmd or not raw_cmd.strip():
        return {
            "normalized_command": "",
            "commands": []
        }

    raw_cmd = raw_cmd.strip()
    normalized_cmd = re.sub(r'\s+', ' ', raw_cmd)

    commands = []
    current = ""
    in_single_quote = False
    in_double_quote = False
    i = 0

    while i < len(normalized_cmd):
        char = normalized_cmd[i]

        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote

        if not in_single_quote and not in_double_quote:
            if normalized_cmd[i:i+2] in ("&&", "||"):
                if current.strip():
                    commands.append(current.strip())
                current = ""
                i += 2
                continue

            if char == ";":
                if current.strip():
                    commands.append(current.strip())
                current = ""
                i += 1
                continue

        current += char
        i += 1

    if current.strip():
        commands.append(current.strip())

    return {
        "normalized_command": normalized_cmd,
        "commands": commands
    }


def CollectContextNode(state : State):
    cwd = os.getcwd()
    is_root_dir = (cwd == "/")
    if (os.geteuid() == 0):
        is_root_user =True
    else:
        is_root_user = False
    os_name = platform.system().lower()
    if "linux" in os_name  :
        os_type = "linux"
    elif "darwin" in os_name:
        os_type = "darwin"
    elif "windows" in os_name:
        os_type = "windows"
    else:
        os_type = "unknown"

    return {
         "cwd": cwd,
        "is_root_dir": is_root_dir,
        "is_root_user": is_root_user,
        "os_type": os_type

    }

    

def RuleBasedRiskNode(state: State):
    max_risk = "NONE"

    for cmd in state.commands:
        c = cmd.lower()

        for pattern in CRITICAL_PATTERNS:
            if re.search(pattern, c):
                return {"rule_risk": "CRITICAL"}

        for pattern in HIGH_PATTERNS:
            if re.search(pattern, c):
                max_risk = "HIGH"

        for pattern in MEDIUM_PATTERNS:
            if re.search(pattern, c) and max_risk not in ("HIGH",):
                max_risk = "MEDIUM"

        for pattern in LOW_PATTERNS:
            if re.search(pattern, c) and max_risk == "NONE":
                max_risk = "LOW"

    return {"rule_risk": max_risk}



def ContextRiskAdjustmentNode(state : State):
    rule_risk = state.rule_risk
    final_risk = rule_risk 
    is_root_dir = state.is_root_dir
    is_root_user = state.is_root_user
    cmds = state.commands
    if final_risk  =="CRITICAL":
        return {
            'final_risk' : final_risk
        }
    step = 0

    if is_root_dir and rule_risk in ("MEDIUM", "HIGH"):
        steps += 1
    if is_root_user and rule_risk in ("MEDIUM", "HIGH"):
        steps += 1
    for cmd in cmds:
        if "rm -rf" in cmd.lower():
            for d in SENSITIVE_DIRS:
                if state.cwd.startswith(d):
                    steps += 1
                    break
    final_risk = escalate_risk(rule_risk, steps)
    return {"final_risk": final_risk}



def risk_branch(state: State):
    final_risk = state.final_risk
    if final_risk in ["MEDIUM", "HIGH", "CRITICAL"]:
        return "LLMExplanationNode"
    else:
        return "DecisionNode"

def LLMExplanationNode(state : State):
    commands = state.commands
    is_root_dir = state.is_root_dir
    is_root_user = state.is_root_user
    cwd = state.cwd
    rule_risk = state.rule_risk
    final_rist = state.final_risk
    
    llm_explain = llm.with_structured_output(explain)

    chain = prompt | llm_explain
    result = chain.invoke({
        "commands" : commands,
        'rule_risk' : rule_risk,
        "final_risk" : final_rist,
        "cwd": cwd,
          "is_root_user":is_root_user,
        "is_root_dir" : is_root_dir
    })
    print(result)
    return {
        "decision" : result.decision,
        "explanation" : result.explanation,
        "consequences" : result.consequences,
        "safer_alternative" : result.safer_alternative
    }


def DecisionNode(state : State):
    final_risk = state.final_risk
    return {
        "decision" : final_risk
    }
 



graph = StateGraph(State)

graph.add_node("NormalizeCommandNode", NormalizeCommandNode)
graph.add_node("CollectContextNode", CollectContextNode)
graph.add_node("RuleBasedRiskNode", RuleBasedRiskNode)
graph.add_node("ContextRiskAdjustmentNode", ContextRiskAdjustmentNode)
graph.add_node("LLMExplanationNode", LLMExplanationNode)
graph.add_node("DecisionNode", DecisionNode)

graph.add_edge(START, "NormalizeCommandNode")
graph.add_edge("NormalizeCommandNode", "CollectContextNode")
graph.add_edge("CollectContextNode", "RuleBasedRiskNode")
graph.add_edge("RuleBasedRiskNode", "ContextRiskAdjustmentNode")

graph.add_conditional_edges(
    "ContextRiskAdjustmentNode",
    risk_branch
)

graph.add_edge("LLMExplanationNode", "DecisionNode")
graph.add_edge("DecisionNode", END)

workflow = graph.compile()

result = workflow.invoke({
    "raw_command": "rm -rf / ; echo 'This is a test' && ls -la || mkdir new_folder",
    
})

print(result)
with open("final_result.json", "w") as f:
    json.dump(result, f, indent=4)  
