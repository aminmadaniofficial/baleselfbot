import os
import sys
import importlib
import logging
from typing import List, Dict

logger = logging.getLogger("PluginLoader")


def load_all_plugins(plugins_dir: str = "plugins") -> List[str]:
    """
    Dynamically discovers and imports all Python plugin files (.py) from the plugins directory.
    Fault-tolerant: if one plugin fails, others continue loading smoothly.
    """
    loaded_plugins = []

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        logger.info(f"Created plugins directory at: ./{plugins_dir}")

    abs_path = os.path.abspath(".")
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)

    for filename in sorted(os.listdir(plugins_dir)):
        if filename.endswith(".py") and not filename.startswith("_"):
            plugin_name = filename[:-3]
            module_path = f"{plugins_dir}.{plugin_name}"

            try:
                if module_path in sys.modules:
                    importlib.reload(sys.modules[module_path])
                else:
                    importlib.import_module(module_path)

                loaded_plugins.append(plugin_name)
                logger.info(f"🔌 [PLUGIN LOADED] Successfully loaded: {plugin_name}")
            except Exception as e:
                logger.error(f"❌ [PLUGIN ERROR] Failed to load plugin '{plugin_name}': {e}", exc_info=True)

    return loaded_plugins


def reload_all_plugins(plugins_dir: str = "plugins") -> List[str]:
    """
    Clears current command registry and reloads all active plugins cleanly.
    """
    import core.registry as registry

    registry.COMMANDS.clear()
    return load_all_plugins(plugins_dir)


def get_plugins_status(plugins_dir: str = "plugins") -> Dict[str, List[str]]:
    """
    Scans plugins directory and returns active (.py) and disabled (.py.disabled) plugins.
    """
    active = []
    disabled = []

    if os.path.exists(plugins_dir):
        for filename in sorted(os.listdir(plugins_dir)):
            if filename.startswith("_"):
                continue
            if filename.endswith(".py"):
                active.append(filename[:-3])
            elif filename.endswith(".py.disabled"):
                disabled.append(filename[:-12])

    return {"active": active, "disabled": disabled}


def disable_plugin(plugin_name: str, plugins_dir: str = "plugins") -> bool:
    """
    Disables an active plugin by renaming it to .py.disabled and reloading registry.
    """
    src = os.path.join(plugins_dir, f"{plugin_name}.py")
    dst = os.path.join(plugins_dir, f"{plugin_name}.py.disabled")

    if os.path.exists(src):
        os.rename(src, dst)
        reload_all_plugins(plugins_dir)
        return True
    return False


def enable_plugin(plugin_name: str, plugins_dir: str = "plugins") -> bool:
    """
    Enables a disabled plugin by renaming .py.disabled back to .py and reloading registry.
    """
    src = os.path.join(plugins_dir, f"{plugin_name}.py.disabled")
    dst = os.path.join(plugins_dir, f"{plugin_name}.py")

    if os.path.exists(src):
        os.rename(src, dst)
        reload_all_plugins(plugins_dir)
        return True
    return False