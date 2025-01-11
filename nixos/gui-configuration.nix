{ config, lib, pkgs, ...}:
{
    imports = [];
    options.gui = {
        enable = lib.mkEnableOption "Enable GUI";
        type = lib.mkOption {
            type = lib.types.str;
            default = "kde";
            example = "kde";
            description = "install Desktop environment to use";
        };
        packages = lib.mkOption {
            type = lib.types.listOf lib.types.package;
            default = [];
            example = [ pkgs.microsoft-edge ];
            description = "install package if gui enable";
        };
    };
    config = lib.mkIf config.gui.enable (lib.mkMerge [
        (lib.mkIf (config.gui.type=="kde") {
            services = {
                displayManager.autoLogin = {
                    enable = true;
                    user = "qs315490";
                };
                displayManager.sddm = {
                    enable = true;
                    autoNumlock = true;
                };
                desktopManager.plasma6 = {
                    enable = true;
                };
            };
            i18n.inputMethod = {
                enable = true;
                type = "fcitx5";
                fcitx5 = {
                    waylandFrontend = true;
                    addons = with pkgs;[
                        fcitx5-rime
                    ];
                };
            };
            environment = {
                # plasma6自动安装软件包的排除列表
                plasma6.excludePackages = with pkgs.kdePackages;[
                    elisa okular gwenview
                ];
            };
        })
        {
            environment.systemPackages = config.gui.packages;
        }
        (lib.mkIf (config.i18n.defaultLocale == "zh_CN.UTF-8") {
            environment.systemPackages = with pkgs;[
                noto-fonts-cjk-serif
                noto-fonts-cjk-sans
            ];
        })
    ]);
}
