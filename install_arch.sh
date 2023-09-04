#!/bin/bash -i

CPU_type='intel'
GPUs='intel nvidia'
ismount=`grep -qs '/mnt' /proc/mounts`
UserName='qs315490'
UserPasswd='Qs315490'
HostName='Qs315490-Laptop'

# 软件源
# reflector -p https -f 1 -c china --save /etc/pacman.d/mirrorlist
mirror='mirrors.tuna.tsinghua.edu.cn'
echo "Server = https://$mirror/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

if false;then
    mount -t btrfs -o compress=zstd /dev/nvme0n1p3 /mnt
    cd /mnt
    btrfs sub create @
    umount /mnt
fi

# mount
if ! $ismount;then
    mount -t btrfs -o compress=zstd,subvol=@ /dev/nvme0n1p3 /mnt
    mkdir -p /mnt/boot/efi
    mount /dev/nvme0n1p1 /mnt/boot/efi
    swapon /dev/nvme0n1p2
fi

GPU(){
    for arg in "$@";do
        case $arg in
            "intel") 
                echo {vulkan,xf86-video}-intel intel-media-driver;;
            'nvidia') 
                echo nvidia{,-{utils,prime,settings}};;
            'amd') 
                echo xf86-video-amdgpu vulkan-radeon libva-mesa-driver mesa-vdpau;;
            *) ;;
        esac
    done
}

packages=(
base-devel
# Shell
bash-completion zsh sudo reflector pkgfile
# 字体
noto-fonts-{cjk,emoji} ttf-cascadia-code
# 音频
sof-firmware alsa-utils pulseaudio-alsa
# 文件系统
btrfs-progs exfatprogs
# 网络
networkmanager
# CPU
${CPU_type}-ucode
# GPU
`GPU ${GPUs}`
# sddm
sddm sddm-kcm # kde 控制模块
# Kde
plasma-{desktop,pa,nm,systemmonitor} breeze-gtk kde-gtk-config powerdevil kscreen kgamma5 kinfocenter konsole fcitx5-im kcm-fcitx5 fcitx5-rime kate dolphin colord-kde gpm ark partitionmanager kwalletmanager kdeconnect sshfs
# bluetooth
bluez-utils bluedevil pulseaudio-bluetooth
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
run pacman -S paru timeshift oh-my-zsh-git pamac-aur rime-cloverpinyin plymouth --noconfirm|| exit 1

genfstab -U /mnt >> /mnt/etc/fstab

# 配置 sudo
run ln -s /usr/bin/vim /usr/bin/vi
run sed -i 's/# %wheel ALL=(ALL:ALL) N/%wheel ALL=(ALL:ALL) N/' /etc/sudoers

# 配置 time 设置
run ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
run hwclock --systohc

# locale
run sed -i 's/#zh_CN.U/zh_CN.U/' /etc/locale.gen
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
cat <<EOF > /mnt/etc/sddm.conf.d/numlock.conf
[General]
Numlock=on
EOF
cat <<EOF >/mnt/etc/sddm.conf.d/autologin.conf
[Autologin]
Relogin=false
Session=plasma
User=$UserName
EOF
for gpu in ${GPUs[@]};do
    case $gpu in
        intel)
            echo 'options i915 enable_fbc=1'>/mnt/etc/modprobe.d/i915.conf;;
    esac
done

cat <<EOF >> /mnt/etc/environment
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
SDL_IM_MODULE=fcitx
GLFW_IM_MODULE=ibus
EOF

# pacman config
run sed -i 's/#Color/Color/' /etc/pacman.conf
run sed -i 's/#BottomUp/BottomUp/' /etc/paru.conf

# 修复 dolphin ntfs报错
cat <<EOF >> /mnt/etc/udisks2/mount_options.conf
[defaults]
ntfs_defaults=uid=\$UID,gid=\$GID,noatime,prealloc
EOF

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
run grub-mkconfig -o /boot/grub/grub.cfg

run pkgfile --update
