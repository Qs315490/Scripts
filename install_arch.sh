#!/bin/bash

# 错误即停止
set -e
# 管道中任何一个命令失败则失败
set -o pipefail
# 显示执行的命令
# set -x
# 开启 alias
shopt -s expand_aliases

CPU_type='intel'
GPUs=(intel nvidia)
UserName='qs315490'
UserPasswd='Qs315490'
HostName='Qs315490-Laptop'
# Desktop Type (gnome plasma plasma_wayland hyprland)
desktop_type='plasma_wayland'

disk_path='/dev/nvme0n1'
get_part_path() {
    # 通过分区序号获取分区路径
    # $1 分区号
    # return /dev/xxx
    if [ -z "$disk_path" ];then
        echo "Please provide disk path"
        exit 1
    fi
    if [ -z "$1" ];then
        echo "Please provide partition number"
        exit 1
    fi
    # 假定已经分区好了
    result=$(lsblk $disk_path -o NAME,PARTN -p -l | awk "\$2==$1 {print \$1}")
    if [ -z "$result" ];then
        echo "Partition $1 not found on $disk_path"
        exit 1
    fi
    echo $result
}
# 分区 内核路径 动态获取
part_root=$(get_part_path 3)
part_swap=$(get_part_path 2)
part_efi=$(get_part_path 1)

mount_dir='/mnt'
ismount=$(grep -qs $mount_dir /proc/mounts && echo "true" || echo "false")

network_check() {
    if ! ping -c 1 -W 1 8.8.8.8 &> /dev/null;then
        echo "Network is not available"
        return 1
    fi
}

# 软件源
# reflector -p https -f 1 -c china --save /etc/pacman.d/mirrorlist
mirror='mirrors.cernet.edu.cn'
echo "Server = https://$mirror/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

if [[ $1 == 'sel' ]];then
    PS3='CPU Type: ';select CPU_type in intel amd;break
    PS3='GPU Type: ';select GPUs in intel amd nvidia;break
fi

btrfs_create_subvol() {
    if [ "$ismount" = "true" ];then
        echo "$mount_dir is already mounted, skipping btrfs subvolume creation"
        return
    fi
    mount -t btrfs -o compress=zstd $part_root $mount_dir
    pushd "$mount_dir"
    btrfs sub c @
    btrfs sub c @home
    popd
    umount $mount_dir
}

# mount
mount_part() {
    if [ "$ismount" = "true" ];then
        echo "$mount_dir is already mounted, skipping mount"
        return
    fi
    # 检查变量是否设置
    if [ -z "$part_root" ];then
        echo "Please set part_root"
        return 1
    fi
    if [ -z "$part_efi" ];then
        echo "Please set part_efi"
        return 1
    fi
    # 判断分区是否存在
    if [ ! -b "$part_root" ];then
        echo "$part_root is not a block device"
        return 1
    fi
    if [ ! -b "$part_efi" ];then
        echo "$part_efi is not a block device"
        return 1
    fi

    echo mount rootfs and efi
    mount -t btrfs -o compress=zstd,subvol=@ $part_root $mount_dir
    mkdir -p $mount_dir/{boot/efi,home}
    mount -t btrfs -o compress=zstd,subvol=@home $part_root $mount_dir/home
    mount $part_efi $mount_dir/boot/efi

    if [ -n "$part_swap" ];then
        # 如果有交换分区就启用
        swapon $part_swap
    fi
}

intel_gpu=(vulkan-intel intel-media-driver)
amd_gpu=(vulkan-radeon libva-mesa-driver mesa-vdpau)
nvidia_gpu=(nvidia{,-prime})

plasma=(
# 显示器管理器
sddm sddm-kcm # kde 控制模块
# Kde 最小安装
plasma-{desktop,pa,nm,systemmonitor} powerdevil kscreen kgamma colord-kde
# 主题
breeze-gtk kde-gtk-config 
# 文件管理器
dolphin
# 终端
konsole
# 输入法
fcitx5-im kcm-fcitx5 fcitx5-chinese-addons
# 文本编辑器
kate
# 密钥管理器
kwalletmanager
# 蓝牙 托盘图标
bluedevil
# 屏幕跟随传感器旋转
#iio-sensor-proxy
# 系统信息查看器
kinfocenter
# 归档管理器
ark
# 分区工具
partitionmanager
# 手机连接
kdeconnect sshfs
)

plasma_wayland=(
${plasma[@]}
plasma-wayland-protocols
krdp
)

# gnome 最小安装
gnome=(
# 显示器管理器
gdm
# 桌面环境
gnome-shell gnome-shell-extension-appindicator gnome-backgrounds adw-gtk-theme
# 设置
gnome-control-center gnome-tweaks dconf-editor
# 文件管理器
nautilus gvfs-smb
# 终端
gnome-console
# 文本编辑器
gnome-text-editor
# 任务管理器
gnome-system-monitor
# 密钥管理器
seahorse
# 输入法
ibus ibus-libpinyin
# 远程桌面服务器
gnome-remote-desktop
# 摄像头
#snapshot
)

# 未完成
hyprland=(
    # 管理器
    sddm
    # hyprland
    hyprland
    # 终端
    foot
    # 状态栏
    waybar
    # 启动器
    wofi
    # 音频
)

declare -n desktop="$desktop_type"

packages=(
base-devel
# Shell
bash-completion zsh sudo reflector pkgfile less vim
zsh-autocomplete zsh-syntax-highlighting
# 字体
noto-fonts-{cjk,emoji} ttf-cascadia-code
# 音频
sof-firmware alsa-utils pipewire-{alsa,audio,pulse}
# 文件系统
btrfs-progs exfatprogs
# 网络
networkmanager
# CPU
${CPU_type}-ucode
# 桌面环境
${desktop[@]}
# 蓝牙
bluez-utils
# 电源配置
power-profiles-daemon
# 线程优化
irqbalance
# zram
zram-generator
)
for GPU in "${GPUs[@]}"; do
    declare -n current_array="${GPU}_gpu"   # 创建一个 变量，其值是 ${GPU}_gpu 数组
    packages+=("${current_array[@]}")       # 把当前数组的内容追加到 packages 中
done

alias run='arch-chroot $mount_dir'
install_packages() {
    pacstrap $mount_dir base linux linux-firmware grub efibootmgr os-prober ${packages[@]}
    if ! grep -qs "archlinuxcn" $mount_dir/etc/pacman.conf;then
    cat <<EOF >>$mount_dir/etc/pacman.conf
[archlinuxcn]
Server = https://$mirror/archlinuxcn/\$arch

EOF
    fi
    run pacman -Sy archlinuxcn-keyring --noconfirm
    run pacman -S paru timeshift pamac-aur plymouth --noconfirm
}

config_user() {
    echo set root password as User Passwd
    run bash -c "echo root:$UserPasswd|chpasswd"

    echo add user $UserName
    run useradd -m -G wheel,lp -s '/usr/bin/zsh' $UserName || echo "User $UserName already exists"

    echo set $UserName password
    run bash -c "echo $UserName:$UserPasswd|chpasswd"

    echo install oh-my-zsh
    run su $UserName -c 'paru -S oh-my-zsh-git --noconfirm'

    echo config oh-my-zsh pulgin and theme
	run sed -i 's|#[[:space:]]*ZSH_CUSTOM=.*|ZSH_CUSTOM=/usr/share/zsh|' /usr/share/oh-my-zsh/zshrc
    run cp /usr/share/oh-my-zsh/zshrc /home/$UserName/.zshrc
    run chown $UserName:$UserName /home/$UserName/.zshrc
    run su $UserName -c 'source ~/.zshrc;omz theme set ys;omz plugin enable sudo safe-paste extract command-not-found zsh-autocomplete zsh-syntax-highlighting'

    echo copy oh-my-zsh config to root
    run cp /home/$UserName/.zshrc /root/.zshrc
    run chown root:root /root/.zshrc
}

config_system() {
    echo genfstab
    genfstab -U /mnt | run tee /etc/fstab

    echo link vi to vim
    run ln -s /usr/bin/vim /usr/bin/vi
    echo config sudo
    run sed -i 's/# %wheel ALL=(ALL:ALL) N/%wheel ALL=(ALL:ALL) N/' /etc/sudoers

    echo config timezone
    run ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
    # run hwclock --systohc
    # timedatectl 只能改变当前环境，chroot环境不影响最终环境
    # run timedatectl set-local-rtc true

    echo config locale
    run sed -i 's/#zh_CN.U/zh_CN.U/' /etc/locale.gen
    run locale-gen
    echo 'LANG=zh_CN.UTF-8' | run tee /etc/locale.conf

    echo config hostname
    echo $HostName | run tee /etc/hostname

    echo config zram
	cat <<EOF | run tee /etc/systemd/zram-generator.conf
[zram0]
zram-size = min(ram / 2, 4096)
compression-algorithm = zstd
EOF

    echo enable service
    enable="systemctl enable"
    cat <<EOF >> $mount_dir/usr/lib/systemd/system/systemd-zram-setup@.service
[Install]
WantedBy=multi-user.target

EOF
	run $enable systemd-zram-setup@zram0.service
    run $enable NetworkManager
    run $enable irqbalance
    if [[ "$desktop_type" =~ 'plasma' ]];then
        run $enable sddm
        balooctl=`run sh -c 'ls /usr/bin/balooctl*'`
        run $balooctl suspend
        run $balooctl disable
    fi
    run $enable bluetooth

    if [[ "$desktop_type" =~ 'plasma' ]];then
        echo config sddm
        run mkdir /etc/sddm.conf.d
        cat <<EOF | run tee /etc/sddm.conf.d/kde_settings.conf
[General]
Numlock=on
[Autologin]
Relogin=false
Session=plasma
User=$UserName
EOF
        if [[ "$desktop_type" == 'plasma_wayland' ]];then
            cat <<EOF | run tee /etc/sddm.conf.d/10-wayland.conf
[General]
DisplayServer=wayland
GreeterEnvironment=QT_WAYLAND_SHELL_INTEGRATION=layer-shell

[Wayland]
CompositorCommand=kwin_wayland --drm --no-lockscreen --no-global-shortcuts --locale1 --inputmethod maliit-keyboard
EOF
        fi
    fi


    for gpu in ${GPUs[@]};do
        case $gpu in
            intel)
                echo 'options i915 enable_fbc=1' | run tee /etc/modprobe.d/i915.conf;;
        esac
    done

    if [[ "$desktop_type" =~ 'plasma' ]];then
        echo config fcitx5
        cat <<EOF >> $mount_dir/etc/environment
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
SDL_IM_MODULE=fcitx
GLFW_IM_MODULE=ibus
EOF
    fi

    # pacman config
    run sed -i 's/#Color/Color/' /etc/pacman.conf
    run sed -i 's/#BottomUp/BottomUp/' /etc/paru.conf

    if [[ "$desktop_type" =~ 'plasma' ]];then
        echo fix dolphin ntfs error
        cat <<EOF >> $mount_dir/etc/udisks2/mount_options.conf
[defaults]
ntfs_defaults=uid=\$UID,gid=\$GID,noatime,prealloc
EOF
    fi

    echo config plymouth mkinitramfs.conf hooks
	run sed -i 's/^HOOKS=(\([^)]*\))/HOOKS=(\1 plymouth)/' /etc/mkinitcpio.conf
	run mkinitcpio -P

    echo update pkgfile database
    run pkgfile --update
}

grub_install() {
    run grub-install --target=x86_64-efi --efi-directory=/boot/efi
    run sed -i 's/#GRUB_DISABLE_OS/GRUB_DISABLE_OS/' /etc/default/grub
    run grub-mkconfig -o /boot/grub/grub.cfg
}

all(){
    network_check || return 1
    btrfs_create_subvol
    mount_part
    install_packages
    config_user
    config_system
    grub_install
}
all
