*** Settings ***
Documentation     Common keywords and resources for Pertinax GUI tests

Library           PertinaxLibrary.py
Library           OperatingSystem

*** Variables ***
${APP_NAME}       pertinax_gui.py
${TEST_PDF}       ${CURDIR}/../data/sample.pdf
${TEST_DATA_DIR}    ${CURDIR}/../data
${TEST_PDF_1}       ${TEST_DATA_DIR}/data-1.pdf
${TEST_PDF_2}       ${TEST_DATA_DIR}/data-2.pdf
${TIMEOUT}          10s

*** Keywords ***
Launch Pertinax
    [Documentation]    Launch the Pertinax application
    [Arguments]        ${pdf_path}=${EMPTY}
    PertinaxLibrary.Launch Pertinax    ${pdf_path}

Close Pertinax
    [Documentation]    Close the Pertinax application
    PertinaxLibrary.Close Pertinax

Click Button By Label
    [Documentation]    Click a button by its accessibility label
    [Arguments]        ${label}
    PertinaxLibrary.Click Button By Label    ${label}

Wait For Thumbnails
    [Documentation]    Wait for thumbnails to be loaded
    [Arguments]        ${expected_count}    ${timeout}=10
    PertinaxLibrary.Wait For Thumbnails    ${expected_count}    ${timeout}

Get Page Count From Status
    [Documentation]    Get the page count from status label
    ${count}=    PertinaxLibrary.Get Page Count From Status
    RETURN    ${count}

Verify App Is Running
    [Documentation]    Verify the application is still running
    PertinaxLibrary.Verify App Is Running

Get Button State
    [Documentation]    Check if a button is enabled
    [Arguments]    ${label}
    ${state}=    PertinaxLibrary.Get Button Sensitive    ${label}
    RETURN    ${state}

Verify Widget Visible
    [Documentation]    Verify that a widget is visible
    [Arguments]    ${label}
    PertinaxLibrary.Verify Widget Visible    ${label}

Verify Widget Not Visible
    [Documentation]    Verify that a widget is not visible
    [Arguments]    ${label}
    PertinaxLibrary.Verify Widget Not Visible    ${label}

Open File Dialog
    [Documentation]    Open a PDF file using the file dialog
    [Arguments]    ${pdf_path}
    PertinaxLibrary.Open File Dialog    ${pdf_path}

Send Keyboard Shortcut
    [Documentation]    Send a keyboard shortcut to the application
    [Arguments]    ${shortcut}
    PertinaxLibrary.Send Keyboard Shortcut    ${shortcut}

Drag And Drop Page
    [Documentation]    Drag and drop a page from one position to another
    [Arguments]    ${from_index}    ${to_index}
    PertinaxLibrary.Drag And Drop Page    ${from_index}    ${to_index}
