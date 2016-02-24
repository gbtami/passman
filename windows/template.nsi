[% extends "pyapp_installpy.nsi" %]

[% block install_shortcuts %]
    [[ super() ]]
    SetOutPath "%HOMEDRIVE%\%HOMEPATH%"
    [% for scname, sc in ib.shortcuts.items() %]
        [% if scname == "PassMan" %]
            CreateShortCut "$SMSTARTUP\[[scname]].lnk" \
                           "[[ sc['target'] ]]" \
                           '[[ sc['parameters'] ]] --hide' \
                           "$INSTDIR\[[ sc['icon'] ]]"
        [% endif %]
    [% endfor %]
    SetOutPath "$INSTDIR"
[% endblock %]

