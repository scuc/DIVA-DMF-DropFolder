#! /usr/bin/env python3

import logging
import os
import re
import shutil

import config
import filepath_mods as fpmod


config = config.get_config()
archive_f = config['paths']['archive_dropfolder']
drop_f = config['paths']['mac_dropfolder']
divaname = config['paths']['DIVAName']

logger = logging.getLogger(__name__)


def create_mdf(): 
    """
    Check a watch folder for directory sets to archive. 
    Walk through each directory set and build a list
    of file/folder paths to archive. Use the path list
    to write a .mdf file that is used as the trigger for
    the DIVA archive job. 
    """

    dlist = [d for d in os.listdir(
        drop_f) if os.path.isdir(os.path.join(drop_f, d)) and 
        d != "_archiving"]

    dlist_msg = f"New directories for DMF archiving: {dlist}")
    logger.info(dlist_msg)

    movelist = []

    if len(dlist) != 0: 
        for d in dlist: 
            mdf_doc = d + '.mdf'
            count=0
            if os.path.exists(os.path.join(archive_f,mdf_doc)):
                dlist.remove(d)
                fileexist_msg = f"{mdf_doc} already exists in the archive folder, skipping"
                logger.info(fileexist_msg)
                continue
            else: 
                dpath = os.path.join(drop_f,d)
                fpath = fpmod.check_pathname(dpath)

                for root, dirs, files in os.walk(dpath): 
                    for name in files: 
                        fpath = os.path.join(root,name)
                        if fpath.endswith('.DS_Store'):
                            os.remove(fpath)
                            count += 1
                        else:
                            pass
                    rm_msg = f"{count} .DS_Store files removed from dir before archive."
                    logger.info(rm_msg)

                # paths_string = '\n'.join(map(str, pathslist))
                paths_string = f"{d}/*"

                os.chdir(drop_f)

                with open(mdf_doc, mode="w", encoding='utf-8-sig') as mdf_doc:

                    doc_body = (
                                f"#\n"
                                f"# Object configuration.\n"
                                f"#\n"
                                f"\n"
                                f"priority=50\n"
                                f"objectName={d}\n"
                                f"categoryName=AXF\n"
                                f"\n"
                                f"<comments>\n"
                                f"{d}\n"
                                f"</comments>\n"
                                f"\n"
                                f"#sourceDestinationDIVAName={divaname}\n"
                                f"#sourceDestinationDIVAPath={drop_f}\n"
                                f"\n"
                                f"<fileList>\n"
                                f"{paths_string}\n"
                                f"</fileList>"
                    )

                    mdf_doc.write(doc_body)
                    mdf_doc.close()
                    movelist.extend([dpath, os.path.join(drop_f, d + ".mdf")])
                    new_mdf_msg = f"New .mdf file created: {d + '.mdf'}"
                    logger.info(new_mdf_msg)
                    dir_delim_msg=f"\n 
                                {'-'*60} \n 
                                \n"
                    logger.info(dir_delim_msg)
    print(f"MOVE LIST: {movelist}")
    move_to_checkin(movelist)


def move_to_checkin(movelist):
    """
    Move files and dir in the movelist from the drop folder to the archive location.
    """
    
    for x in movelist:
        arch_check = os.path.basename(x)
        try:
            if os.path.exists(os.path.join(archive_f, arch_check)): 
                print(f"{arch_check} already exists in this location, skipping")
                pass
            else:
                shutil.move(x, archive_f)
        except Exception as e:
            move_excp_msg = f"\n\
            Exception raised on moving {x}.\n\
            Error Message:  {str(e)} \n\
            "

    return


if __name__ == '__main__':
    create_mdf()
