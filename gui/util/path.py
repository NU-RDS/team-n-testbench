# path.py

import os
import sys

class PathUtil:
    @staticmethod
    def get_dirname(path : str, levels_up : int = 1):
        """
        Returns the directory name of the path, optionally moving up `levels_up` directories.
        """
        for _ in range(levels_up):
            path = os.path.dirname(path)
        return path 

    @staticmethod
    def get_gui_root():
        return PathUtil.get_dirname(__file__, 2)
    
    @staticmethod
    def get_asset_folder():
        return os.path.join(PathUtil.get_gui_root(), "assets")
    

    @staticmethod
    def asset_file_path(filename : str):
        return os.path.join(PathUtil.get_asset_folder(), filename)
    
    @staticmethod
    def asset_file_contents(filename : str):
        with open(PathUtil.asset_file_path(filename), "r") as f:
            return f.read()
        
    @staticmethod
    def file(path : str, make_dirs : bool = False):
        path = os.path.join(PathUtil.get_gui_root(), path)
        # make sure the directory exists
        if make_dirs:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path
    
    @staticmethod
    def file_exists(path : str):
        return os.path.exists(PathUtil.file(path, False))
    
    @staticmethod
    def read_file(path : str):
        with open(path, "r") as file:
            return file.read()