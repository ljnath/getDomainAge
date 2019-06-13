@echo off
@REM DRIVER SCRIPT FOR RUNNING getDomainAge in windows environment
@REM Author: Lakhya Jyoti Nath (ljnath) @ June 2019 
@REM
@REM Prerequisite : Python 3.5/3.6  and python binary path should be in the path variable


:INITIALIZE
    SET VIRTUAL_ENV=.venv
    IF NOT EXIST %VIRTUAL_ENV% GOTO CREATE_AND_RUN

:SWITCH_AND_RUN
    %VIRTUAL_ENV%\Scripts\activate && python app.py
    GOTO EXIT
    
:CREATE_AND_RUN
    python -m venv %VIRTUAL_ENV%
    %VIRTUAL_ENV%\Scripts\activate && pip install -r requirement.txt && cls && python app.py
    GOTO EXIT
	
:EXIT
    @REM Not in the mood of doing anything :)