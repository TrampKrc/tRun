import os

if os.environ.get("xRun") is None:
    os.environ["xRun"] = ""   

    import sys

    current_folder = os.path.dirname(os.path.abspath(__file__))     # folder Lib

    sys.path.append( os.path.join( current_folder, 'Common') )
    sys.path.append( os.path.join( current_folder, 'Exchange'))
    sys.path.append( os.path.join( current_folder, 'Telegram'))
    sys.path.append( os.path.join( current_folder, 'Parser'))

    main_folder = os.path.dirname( current_folder)  # folder project root

    cfg_files = os.path.join( main_folder, "CfgFiles")
    out_files = os.path.join( main_folder, "OutFiles")

    #tg_session = os.path.join( cfg_files, "App050325" )
    #tg_session = os.path.join( cfg_files, "App081925" )
    tg_session = os.path.join( cfg_files, "App092425" )
    secrets    = os.path.join( cfg_files, "secrets.json" )

    bybit_key_demo = 'ByBitDemoAll-072125'

    print("<config is updated>")
