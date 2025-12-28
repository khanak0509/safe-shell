from langgraph.graph import StateGraph , START , END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json 
import os 
import time
from Schema_class import * 

def NormalizeCommandNode(state : State):
    raw_cmd = state.raw_command
    


def CollectContextNode(state : State):
    pass


def RuleBasedRiskNode(state : State):
    pass


def ContextRiskAdjustmentNode(state : State):
    pass

def risk_branch(state: State):
    risk = state.final_risk or state.context_risk or state.rule_risk
    if risk in ["MEDIUM", "HIGH", "CRITICAL"]:
        return "LLMExplanationNode"
    else:
        return "DecisionNode"

def LLMExplanationNode(state : State):
    pass


def DecisionNode(state : State):
    pass


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
    risk_branch,
    {"LLMExplanationNode": "LLMExplanationNode", "DecisionNode": "DecisionNode"}
)

graph.add_edge("LLMExplanationNode", "DecisionNode")
graph.add_edge("DecisionNode", END)

workflow = graph.compile()

