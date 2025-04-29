set WORKSPACE=..\..
set LUBAN_DLL=%WORKSPACE%\LubanConfig\MiniTemplate\Luban\Luban.dll
set CONF_ROOT=.

dotnet %LUBAN_DLL% ^
    -t all ^
    -d json ^
    -c python-json ^
    --conf %CONF_ROOT%\luban.conf ^
    -x outputDataDir=%WORKSPACE%\GenData ^
    -x outputCodeDir=%WORKSPACE%\GenCode

pause