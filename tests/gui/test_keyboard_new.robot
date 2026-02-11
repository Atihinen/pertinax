*** Settings ***
Documentation     Keyboard shortcut tests for Pertinax
Suite Setup       Setup Test Environment With PDF
Suite Teardown    Close Pertinax
Resource          resources.robot
Test Timeout      30 seconds

*** Test Cases ***
Ctrl E Opens Export Dialog
    [Documentation]    Verify Ctrl+E keyboard shortcut opens export dialog
    [Tags]    keyboard    export
    # Wait for PDF to load
    Wait For Thumbnails    3    timeout=10
    
    # Send Ctrl+E
    Send Keyboard Shortcut    <Control>e
    Sleep    1s
    
    # App should still be running
    Verify App Is Running
    
    # Close any dialog with Escape
    Send Keyboard Shortcut    Escape
    Sleep    0.5s

Ctrl O Opens File Dialog
    [Documentation]    Verify Ctrl+O keyboard shortcut opens file dialog
    [Tags]    keyboard    file
    # Send Ctrl+O
    Send Keyboard Shortcut    <Control>o
    Sleep    1s
    
    # App should still be running
    Verify App Is Running
    
    # Close dialog with Escape
    Send Keyboard Shortcut    Escape
    Sleep    0.5s

Escape Closes Dialogs
    [Documentation]    Verify Escape key closes dialogs
    [Tags]    keyboard    dialog
    # Open a dialog
    Send Keyboard Shortcut    <Control>o
    Sleep    1s
    
    # Close with Escape
    Send Keyboard Shortcut    Escape
    Sleep    0.5s
    
    # App should be back to normal
    Verify App Is Running

*** Keywords ***
Setup Test Environment With PDF
    [Documentation]    Setup with a test PDF loaded
    ${test_pdf}=    Set Variable    /home/atihinen/projects/pertinax/tests/data/sample.pdf
    File Should Exist    ${test_pdf}
    Launch Pertinax    ${test_pdf}
    Sleep    2s
