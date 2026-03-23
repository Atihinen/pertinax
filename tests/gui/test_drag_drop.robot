*** Settings ***
Documentation     Drag and drop operation tests to verify UI stability
Suite Setup       Setup Test Environment With PDF
Suite Teardown    Close Pertinax
Resource          resources.robot
Test Timeout      60 seconds

*** Test Cases ***
Application Survives Basic Drag Drop
    [Documentation]    Critical test: Verify application doesn't crash on drag and drop
    [Tags]    critical    drag-drop
    # Wait for PDF to load
    Wait For Thumbnails    4    timeout=10
    
    # Perform drag and drop
    Drag And Drop Page    0    2
    
    # Verify app is still running (this was failing before)
    Verify App Is Running
    Sleep    1s
    
    # Verify we still have the same number of pages
    ${count}=    Get Page Count From Status
    Should Be Equal As Integers    ${count}    4

Drag Drop Updates UI
    [Documentation]    Verify drag and drop updates the thumbnail list
    [Tags]    drag-drop    ui
    # Perform another drag operation
    Drag And Drop Page    2    0
    
    # App should still be running
    Verify App Is Running
    
    # Count should remain the same
    ${count}=    Get Page Count From Status
    Should Be Equal As Integers    ${count}    4

Multiple Drag Operations
    [Documentation]    Verify multiple drag operations work correctly
    [Tags]    drag-drop    stress
    # Perform several drag operations
    Drag And Drop Page    1    2
    Sleep    0.5s
    Verify App Is Running
    
    Drag And Drop Page    0    1
    Sleep    0.5s
    Verify App Is Running
    
    Drag And Drop Page    2    1
    Sleep    0.5s
    Verify App Is Running
    
    # Verify page count is still correct
    ${count}=    Get Page Count From Status
    Should Be Equal As Integers    ${count}    4

*** Keywords ***
Setup Test Environment With PDF
    [Documentation]    Setup with a test PDF loaded
    File Should Exist    ${TEST_PDF_1}
    Launch Pertinax    ${TEST_PDF_1}
    Sleep    2s
