from list_of_cmds import *
def escalate_risk(risk, steps=1):
    idx = RISK_ORDER.index(risk)
    return RISK_ORDER[min(idx + steps, len(RISK_ORDER) - 1)]

