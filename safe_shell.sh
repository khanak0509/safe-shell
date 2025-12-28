#!/bin/zsh

SAFE_SHELL_DIR="$(dirname "${(%):-%N}")"

function _safe_shell_accept_line() {
    local cmd="$BUFFER"

    if [[ -z "$cmd" ]]; then
        zle .accept-line
        return
    fi
    
    if [[ "$cmd" == "clear" ]]; then
        zle .accept-line
        return
    fi

    echo ""
    echo -n "Analyzing..."

    local json_output=$(python3 "$SAFE_SHELL_DIR/main.py" "$cmd" 2>/dev/null)
    local exit_code=$?
    
    printf "\r\033[K" 

    if [[ $exit_code -ne 0 ]] || [[ -z "$json_output" ]]; then
         echo "⚠️  Safe Shell Error. Running cautiously..."
         zle .accept-line
         return
    fi

    local parsed_values=$(echo "$json_output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"{data.get('decision', '')}|{data.get('explanation', '')}|{data.get('general_guidance', '')}|{data.get('consequences', '')}\")
except Exception:
    print('|||')
")

    local decision="${parsed_values%%|*}"
    local remainder="${parsed_values#*|}"
    local explanation="${remainder%%|*}"
    local remainder="${remainder#*|}"
    local guidance="${remainder%%|*}"
    local consequences="${remainder#*|}"

    local RED='\033[0;31m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local NC='\033[0m'
    local BOLD='\033[1m'

    if [[ "$decision" == "BLOCK" || "$decision" == "CRITICAL" ]]; then
        echo "${RED}${BOLD}🚫 DANGER (${decision})${NC}"
        echo "${RED}$explanation${NC}"
        echo -n "${RED}${BOLD}Force Execute? [y/N] ${NC}"
        
        read -k 1 -r REPLY
        echo "" 
        
        if [[ "$REPLY" =~ ^[Yy]$ ]]; then
             zle .accept-line
        else
             zle .redisplay
        fi
        return
    fi

    if [[ "$decision" == "WARN" || "$decision" == "HIGH" || "$decision" == "MEDIUM" ]]; then
        echo "${YELLOW}${BOLD}⚠️  WARNING (${decision})${NC}"
        echo "${YELLOW}$explanation${NC}"
        if [[ -n "$consequences" ]]; then
            echo "${YELLOW}Consequences: $consequences${NC}"
        fi
        echo -n "${BOLD}Execute? [y/N] ${NC}"
        
        read -k 1 -r REPLY
        echo "" 
        
        if [[ "$REPLY" =~ ^[Yy]$ ]]; then
             zle .accept-line
        else
             echo "❌ Aborted."
             zle .redisplay
        fi
        return
    fi

    zle .accept-line
}

zle -N _safe_shell_accept_line
bindkey '^M' _safe_shell_accept_line
