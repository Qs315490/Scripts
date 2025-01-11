{config, lib, pkgs, ...}:
let
    nvidiaGpu=false;
    amdGpu=false;
    intelGpu=false;
in
{
    imports = [];

    boot = {
        initrd = {
            availableKernelModules = ["ata_piix" "uhci_hcd" "ehci_pci" "ahci" "usb_storage" "sd_mod"];
            kernelModules = [];
        };
        kernelModules = [];
        extraModulePackages = [];
    };

    # open-vm-tools
    virtualisation.vmware.guest.enable = true;

    hardware.graphics = {
        extraPackages = with pkgs;lib.optional intelGpu [
            intel-media-sdk
            #vpl-gpu-rt
        ];
    };
    hardware.nvidia = lib.mkIf nvidiaGpu {
        modesetting.enable = true;
        powerManagement = {
            enable = false;
            finegrained = false;
        };
        # use open modules
        open = false;
        nvidiaSettings = true;
        # nvidia package version
        package = config.boot.kernelPackages.nvidiaPackages.stable;
    };
    hardware.amdgpu = lib.mkIf amdGpu {
        initrd.enable = true;
        opencl.enable = true;
        amdvlk = {
            enable = true;
        };
    };

    fileSystems = {
        "/" = {
            device = "/dev/disk/by-label/nix-root";
            fsType = "btrfs";
            options = ["compress=zstd" "subvol=@"];
        };
        "/home" = {
            device = "/dev/disk/by-label/nix-root";
            fsType = "btrfs";
            options = ["compress=zstd" "subvol=@home"];
        };
        "/nix" = {
            device = "/dev/disk/by-label/nix-root";
            fsType = "btrfs";
            options = ["compress=zstd" "subvol=@nix" "noatime"];
        };
        "/boot" = {
            device = "/dev/disk/by-label/ESP";
            fsType = "vfat";
        };
    };
    swapDevices = [{ device = "/dev/disk/by-label/nix-swap"; }];
}
