CRITICAL_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+--no-preserve-root",
    r"dd\s+if=",
    r"\bmkfs(\.\w+)?\b",
    r":\(\)\s*\{\s*:\|\:&\s*\}\s*;",
]

HIGH_PATTERNS = [
    r"chmod\s+-R\s+777\s+/",
    r"chown\s+-R\s+/",
    r"kill\s+-9\s+-1",
    r"\bshutdown\b",
    r"\breboot\b",
]

MEDIUM_PATTERNS = [
    r"rm\s+-rf\b",
    r"curl.+\|\s*(bash|sh|zsh)",
    r"wget.+\|\s*(bash|sh)",
    r"\bsudo\b",
    r"\bssh\b",
    r"\bscp\b",
    r"pip\s+install",
    r"npm\s+install",
    r"yarn\s+add",

]

LOW_PATTERNS = [
    r"pipx\s+install",
    r"brew\s+install",
    r"apt(-get)?\s+install",
]

SENSITIVE_DIRS = ["/", "/home", "/var", "/etc", "/usr"]

RISK_ORDER = ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
