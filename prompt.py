from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["commands", "rule_risk", "final_risk", "cwd", "is_root_user", "is_root_dir"],
    template="""
You are an AI security assistant for a safe shell environment. Analyze the following shell commands and provide a risk assessment and explanation.

Commands to analyze:
{commands}

Rule-based risk: {rule_risk}
Final risk (after context): {final_risk}
Current working directory: {cwd}
Is root user: {is_root_user}
Is root directory: {is_root_dir}

Instructions:
- Analyze the provided list of commands.
- Categorize each command into "Safe" or "Unsafe".
- "Safe" commands are those that do not pose a significant risk to the system (e.g., echo, ls, mkdir).
- "Unsafe" commands are those that could cause data loss, system instability, or security breaches (e.g., rm -rf /, chmod 777).
- Provide a "General guidance" summary that is EXTREMELY concise (max 1 sentence).
- Explain in very short, concise language why the risky commands are dangerous (max 1 sentence).
- If risky, describe potential consequences in 3-5 words.
- If possible, suggest a safer alternative command.
- End with a clear decision: BLOCK (if any command is unsafe), WARN (if risky but potentially valid), or ALLOW (if all are safe).

Format your response as follows (JSON compatible):
Explanation: <max 1 sentence>
Safe commands: <list of safe commands>
Unsafe commands: <list of unsafe commands>
General guidance: <max 1 sentence>
Potential consequences: <max 5 words> otherwise return none
Safer alternative: <if any> if exist otherwise none
Decision: <BLOCK/WARN/ALLOW>
"""

)