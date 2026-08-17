*** Settings ***
Library    ../resources/vpn_env_check.py
Suite Setup                     Setup Browser
Suite Teardown                  End suite
Resource                        ../resources/common.robot

*** Test Cases ***
Check VPN Tunnel Feasibility
    ${report}=    Run Full Env Check
    Log    ${report}    console=True
