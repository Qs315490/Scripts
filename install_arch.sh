#!/bin/bash -i

CPU_type='intel'
GPUs=(intel nvidia)
ismount=`grep -qs '/mnt' /proc/mounts`
UserName='qs315490'
UserPasswd='Qs315490'
HostName='Qs315490-Laptop'

desktop_type='plasma_waylan'

part_root='/dev/nvme0n1p3'
part_swap='/dev/nvme0n1p2'
part_efi='/dev/nvme0n1p1'

# 软件源
# reflector -p https -f 1 -c china --save /etc/pacman.d/mirrorlist
mirror='mirrors.cernet.edu.cn'
echo "Server = https://$mirror/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

if [[ $1 == 'sel' ]];then
    echo 'WIP'
    PS3='CPU Type: ';select CPU_type in intel amd;break
    PS3='GPU Type: ';select GPUs in intel amd nvidia;break
fi

if false;then
    mount -t btrfs -o compress=zstd $part_root /mnt
    cd /mnt
    btrfs sub c @
    btrfs sub c @home
    cd ..
    umount /mnt
fi

# mount
if ! $ismount;then
    mount -t btrfs -o compress=zstd,subvol=@ $part_root /mnt
    mkdir -p /mnt/boot/efi /mnt/home
    mount -t btrfs -o compress=zstd,subvol=@home $part_root /mnt/home
    mount $part_efi /mnt/boot/efi
    swapon $part_swap
fi

GPU(){
    for arg in "$GPUs";do
        case $arg in
            'intel') 
                echo vulkan-intel intel-media-driver;;
            'nvidia') 
                echo nvidia{,-prime};;
            'amd') 
                echo vulkan-radeon libva-mesa-driver mesa-vdpau;;
            *) ;;
        esac
    done
}

plasma=(
# sddm
sddm sddm-kcm # kde 控制模块
# Kde 最小安装
plasma-{desktop,pa,nm,systemmonitor} breeze-gtk kde-gtk-config powerdevil kscreen kgamma kinfocenter konsole fcitx5-im kcm-fcitx5 fcitx5-chinese-addons kate dolphin colord-kde gpm ark partitionmanager kwalletmanager kdeconnect sshfs
# 蓝牙
bluedevil
# 屏幕跟随传感器旋转
# iio-sensor-proxy
)

# 未完成
plasma_wayland=(
${plasma[@]}
plasma-wayland-protocols
krdp
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

packages=(
base-devel
# Shell
bash-completion zsh sudo reflector pkgfile less
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
# GPU
`GPU`
# 桌面环境
${$desktop_type}
# 蓝牙
bluez-utils
)

# 开始安装
pacstrap /mnt base linux linux-firmware vim grub efibootmgr os-prober ${packages[@]} || exit 1
if ! grep -qs "archlinuxcn" /mnt/etc/pacman.conf;then
    cat <<EOF >>/mnt/etc/pacman.conf
[archlinuxcn]
Server = https://$mirror/archlinuxcn/\$arch

EOF
fi

alias run='arch-chroot /mnt'

# install packages
run pacman -Sy archlinuxcn-keyring --noconfirm|| exit 1
run pacman -S paru timeshift oh-my-zsh-git pamac-aur plymouth --noconfirm|| exit 1

genfstab -U /mnt >> /mnt/etc/fstab

# 配置 sudo
run ln -s /usr/bin/vim /usr/bin/vi
sed -i 's/# %wheel ALL=(ALL:ALL) N/%wheel ALL=(ALL:ALL) N/' /mnt/etc/sudoers

# 配置 time 设置
run ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
run hwclock --systohc
# timedatectl 只能改变当前环境，chroot环境不影响最终环境
# run timedatectl set-local-rtc true

# locale
sed -i 's/#zh_CN.U/zh_CN.U/' /mnt/etc/locale.gen
run locale-gen
echo 'LANG=zh_CN.UTF-8' > /mnt/etc/locale.conf

# hostname
echo $HostName > /mnt/etc/hostname

# service
run balooctl suspend
run balooctl disable
enable="systemctl enable"
run $enable NetworkManager
run $enable sddm
run $enable bluetooth

# config
mkdir /mnt/etc/sddm.conf.d
if [[ $desktop_type == 'plasma' ]];then
cat <<EOF > /mnt/etc/sddm.conf.d/kde_settings.conf
[General]
Numlock=on
[Autologin]
Relogin=false
Session=plasma
User=$UserName
EOF
fi

for gpu in ${GPUs[@]};do
    case $gpu in
        intel)
            echo 'options i915 enable_fbc=1'>/mnt/etc/modprobe.d/i915.conf;;
    esac
done

if [[ $desktop_type == 'plasma' ]];then
cat <<EOF >> /mnt/etc/environment
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
EOF
fi

cat <<EOF >> /mnt/etc/environment
XMODIFIERS=@im=fcitx
SDL_IM_MODULE=fcitx
GLFW_IM_MODULE=ibus
EOF

# pacman config
sed -i 's/#Color/Color/' /mnt/etc/pacman.conf
sed -i 's/#BottomUp/BottomUp/' /mnt/etc/paru.conf

# 修复 dolphin ntfs报错
if [[ $disktop_type == 'plasma' ]];then
cat <<EOF >> /mnt/etc/udisks2/mount_options.conf
[defaults]
ntfs_defaults=uid=\$UID,gid=\$GID,noatime,prealloc
EOF
fi

# add user
run useradd -m -G wheel,lp -s '/usr/bin/zsh' $UserName
run cp /usr/share/oh-my-zsh/zshrc /home/$UserName/.zshrc
run chown $UserName:$UserName /home/$UserName/.zshrc
run su $UserName -c 'source ~/.zshrc;omz theme set ys;omz plugin enable sudo safe-paste extract command-not-found'

# password
run bash -c "echo root:$UserPasswd|chpasswd"
run bash -c "echo $UserName:$UserPasswd|chpasswd"

# grub
run grub-install
run sed -i 's/#GRUB_DISABLE_OS/GRUB_DISABLE_OS/' /etc/default/grub
run grub-mkconfig -o /boot/grub/grub.cfg

run pkgfile --update
