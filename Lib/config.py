import os

if os.environ.get("xRun") is None:
    os.environ["xRun"] = ""   

    import sys

    current_folder = os.path.dirname(os.path.abspath(__file__))     # ../Main/Lib

    sys.path.append( os.path.join( current_folder, 'Common') )
    sys.path.append( os.path.join( current_folder, 'Exchange'))
    sys.path.append( os.path.join( current_folder, 'Telegram'))
    sys.path.append( os.path.join( current_folder, 'Parser'))

    main_folder = os.path.dirname( current_folder)  # ../Main)

    cfg_files = os.path.join( main_folder, "CfgFiles")
    out_files = os.path.join( main_folder, "OutFiles")

    tg_session = os.path.join( cfg_files, "App050325" )
    secrets    = os.path.join( cfg_files, "secrets.json" )

    print(" config is done")
