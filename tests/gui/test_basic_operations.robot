*** Settings ***
Documentation     Basic operation tests for Pertinax PDF compositor GUI
Suite Setup       Setup Test Environment
Suite Teardown    Close Pertinax
Resource          resources.robot
Test Timeout      30 seconds

*** Test Cases ***
Application Launches Successfully
    [Documentation]    Verify the application can launch without errors
    [Tags]    smoke
    Verify App Is Running
    Verify Widget Visible    empty_state

Empty State Displays Correctly
    [Documentation]    Verify the empty state is shown when no PDF is loaded
    [Tags]    ui
    Verify Widget Visible    empty_state
    Verify Widget Not Visible    preview_pane
    ${count}=    Get Page Count From Status
    Should Be Equal As Integers    ${count}    0

Buttons Have Correct Initial State
    [Documentation]    Verify button states when no PDF is loaded
    [Tags]    ui
    ${open_state}=    Get Button State    Open PDF
    Should Be True    ${open_state}    Open button should be enabled
    
    ${export_state}=    Get Button State    Export PDF
    Should Not Be True    ${export_state}    Export button should be disabled
    
    ${insert_state}=    Get Button State    Insert Pages
    Should Not Be True    ${insert_state}    Insert button should be disabled
    
    ${delete_state}=    Get Button State    Delete Pages
    Should Not Be True    ${delete_state}    Delete button should be disabled

Open PDF Button Works
    [Documentation]    Verify the Open PDF button is clickable
    [Tags]    functional
    Click Button By Label    Open PDF
    Sleep    1s
    # Close any dialog with Escape
    Send Keyboard Shortcut    Escape
    Sleep    0.5s
    Verify App Is Running

*** Keywords ***
Setup Test Environment
    [Documentation]    Setup before running tests
    Launch Pertinax
