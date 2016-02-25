[% extends "pyapp_installpy.nsi" %]

[% block install_shortcuts %]
    ; This is a complete overwrite of the install_shortcuts block,
    ; so there is no need to call super(). It is also assumed
    ; SetOutPath points to $INSTDIR.
    Var install_directory
    [% if single_shortcut %]
        StrCpy $install_directory "$SMPROGRAMS"
    [% else %]
        StrCpy $install_directory "$SMPROGRAMS\${PRODUCT_NAME}"
        ; Multiple shortcuts: create a directory for them
        CreateDirectory "$install_directory"
    [% endif %]
    [% for scname, sc in ib.shortcuts.items() %]
        CreateShortCut "$install_directory\[[scname]].lnk" \
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

