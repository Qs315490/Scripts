{ pkgs, lib, ...}:
{
    imports = [
        ./hardware-configuration.nix
        ./gui-configuration.nix
    ];
    boot.loader.efi = {
        canTouchEfiVariables = true;
        # EFI 分区位置
        efiSysMountPoint = "/boot";
    };
    boot.loader.grub = {
        enable = true;
        efiSupport = true;
        device = "nodev";
    };
    networking = {
        hostName = "nixos";
        networkmanager = {
            enable = true;
        };
    };
    time = {
        timeZone = "Asia/Shanghai";
        hardwareClockInLocalTime = true;
    };
    i18n.defaultLocale = "zh_CN.UTF-8";
    gui = {
        enable = true;
        type = "kde";
        packages = with pkgs;[
            nil # nix 语言服务器
            microsoft-edge
        ];
    };
    # 软件包
    environment.defaultPackages = with pkgs;[
        rsync strace
    ];
    # 系统软件包
    environment.systemPackages = with pkgs; [
        vim btop
    ];
    # 软件包配置
    programs = {
        zsh = {
            enable = true;
            enableBashCompletion = true;
            ohMyZsh = {
                enable = true;
                theme = "ys";
                plugins = ["extract" "safe-paste" "sudo" "nix"];
                customPkgs = with pkgs;[
                    nix-zsh-completions
                ];
            };
            syntaxHighlighting.enable = true;
            autosuggestions.enable = true;
        };
    };
    security.sudo = {
        # wheel 是否需要密码
        wheelNeedsPassword = false;
    };
    # 镜像源
    nix.settings.substituters = lib.mkForce [
        "https://mirrors.cernet.edu.cn/nix-channels/store"
    ];
    # 允许非自由软件包
    nixpkgs.config.allowUnfree = true;
    users = {
        defaultUserShell = pkgs.zsh;
        mutableUsers = true;
        users = {
            root = {
                initialPassword = "Qs315490";
            };
            qs315490 = {
                isNormalUser = true;
                initialPassword = "Qs315490";
                extraGroups = [ "networkmanager" "wheel" ];
            };
        };
    };
    system.stateVersion = "24.11";
}
