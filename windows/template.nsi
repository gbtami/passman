[% extends "pyapp_installpy.nsi" %]

[% block install_shortcuts %]
    ; This is a complete overwrite of the install_shortcuts block,
    ; so there is no need to call super().
    SetOutPath "$INSTDIR"
    Var /GLOBAL passman_install_directory
    [% if single_shortcut %]
        StrCpy $passman_install_directory "$SMPROGRAMS"
    [% else %]
        StrCpy $passman_install_directory "$SMPROGRAMS\${PRODUCT_NAME}"
        ; Multiple shortcuts: create a directory for them
        CreateDirectory "$passman_install_directory"
    [% endif %]
    [% for scname, sc in ib.shortcuts.items() %]
        CreateShortCut "$passman_install_directory\[[scname]].lnk" \
                       "[[sc['target'] ]]" \
                       '[[ sc['parameters'] ]]' \
                       "$INSTDIR\[[ sc['icon'] ]]"
        [% if scname == "PassMan" %]
            CreateShortCut "$SMSTARTUP\[[scname]].lnk" \
                           "[[ sc['target'] ]]" \
                           '[[ sc['parameters'] ]] --autostart --hide' \
                           "$INSTDIR\[[ sc['icon'] ]]"
        [% endif %]
    [% endfor %]
[% endblock %]

