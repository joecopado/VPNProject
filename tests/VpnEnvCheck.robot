*** Settings ***
Library    ../resources/vpn_env_check.py

*** Test Cases ***
Check VPN Tunnel Feasibility
    ${report}=    Run Full Env Check
    Log    ${report}    console=True
