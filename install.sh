#!/usr/bin/env bash
automation_hat_url="https://get.pimoroni.com/automationhat"
repo_url="https://github.com/BramDriesen/rpi-jenkins-tower-light.git"
repo_dir="rpi-jenkins-tower-light"

if_rpi(){
    if grep "Raspbian" /etc/os-release >/dev/null; then
        :
    else
        $red
        "This script only works on Raspberry Pi's"
        $reset
        exit 1
    fi
}

is_root(){
    if [ "$(id -u)" = "0" ]; then
        :
    else
        echo
        $red
        echo "Must be root(sudo) to install packages..."
        $reset
        exit 1
    fi
}

if_pip(){
    if command -v pip3 --version >/dev/null; then
        :
    else
      $red
      echo "Pip3 not installed"
      $yellow
      echo "Installing pip3 ..."
      echo
      $reset
      apt-get update && apt-get install python3-pip
    fi
}

install_pip_libs(){
    $green
    echo "Installing 'jenkinsapi' Python library..."
    $reset
    if pip3 install jenkinsapi --upgrade; then
        :
    else
        $red
        echo "jenkinsapi library installation failed, Jenkins Tower Light will not work correctly."
        $reset
    fi
}

install_hat(){
    $green
    echo "Installing Automation Hat..."
    $reset
    sudo -u pi bash -c "$(curl -sL ${automation_hat_url})"
}

clone_repo(){
    if command -v git --version >/dev/null; then
        :
    else
      $red
      echo "GIT not installed"
      $yellow
      echo "Installing GIT ..."
      echo
      $reset
      apt-get update && apt-get install git
    fi
    $reset
    if test -d $repo_dir; then
        mv $repo_dir $repo_dir.bak
    fi
    git clone $repo_url
}

read_config_opts(){
    config=$repo_dir/config.py
    if test -d ./$repo_dir; then
        $green
        echo "Enter your Jenkins URL(http://localhost:8080/jenkins):"
        $yellow
        read url
        echo "jenkinsurl = \"${url}\"" > $config
        echo
        
        $green
        echo "Enter your Jenkins username:"
        $yellow
        read username
        echo "username = \"${username}\"" >> $config
        echo

        $green
        echo "Enter your Jenkins password:"
        $yellow
        read password
        echo "password = \"${password}\"" >> $config
        echo

        $green
        echo "Enter the job names you would like to monitor separated by commas"
        echo "Example: job1,job2,job3"
        echo
        $yellow
        read jobs

        IFS=','
        printf "jobs=[" >> $config
        for i in $jobs; 
            do printf \"$i\", >> $config
        done
        printf "]" >> $config
        unset IFS
        $green
        echo "Your config($(pwd)/${repo_dir}/config.py):"
        echo
        $yellow
        cat $(pwd)/${repo_dir}/config.py
        echo
        $reset
        chown -R pi:pi $(pwd)/${repo_dir}
    else
        $red
        echo "Cannot find ${repo_dir}"
        exit 1
    fi
}

show_gpio_config(){
    $green
    echo
    echo "######################"
    echo "# GPIO Configuration #"
    echo "######################"
    echo
    echo "To enable gpio pins, follow this config example and edit your config at ($(pwd)/${repo_dir}/config.py)"
    echo
    $blue
    cat $(pwd)/${repo_dir}/config.py
    echo
    echo "gpios = {"
    echo "'red': 18,"
    echo "'buzzer': 23,"
    echo "'yellow': 24,"
    echo "'green': 27,"
    echo "}"
    echo
    sleep 5
    $reset
}

enable_network_on_boot(){
$green
echo "Enabling wait for network on boot..."
$reset

mkdir -p /etc/systemd/system/dhcpcd.service.d/
cat > /etc/systemd/system/dhcpcd.service.d/wait.conf << EOF
[Service]
ExecStart=
ExecStart=/usr/lib/dhcpcd5/dhcpcd -q -w
EOF
}

enable_service(){
    $green
    if grep $repo_dir /etc/rc.local >/dev/null;then
        :
    else
    echo "Enabling Jenkins Tower Light to start at boot..."
        sed -e s/exit 0//g -i *
        echo "python3 /home/pi/${repo_dir}/jenkins_tower_light_hat.py &" >> /etc/rc.local
        echo "exit 0" >> /etc/rc.local
    fi
    $reset
}

reboot(){
    $green
    echo
    echo "#########################"
    echo "# Installation Complete #"
    echo "#########################"
    echo
    $yellow
    echo "Raspberry Pi rebooting in 60s..."
    $red
    echo "Ctrl+C to stop reboot"
    $reset
    sleep 60
    reboot
}

##############
# Begin Script
##############
red="tput setaf 1"
green="tput setaf 2"
yellow="tput setaf 3"
blue="tput setaf 4"
reset="tput sgr0"

$green
echo "#######################"
echo "# Jenkins Tower Light #"
echo "#######################"
echo

if_rpi
is_root
if_pip
install_pip_libs
install_hat
clone_repo
read_config_opts
show_gpio_config
enable_network_on_boot
enable_service
reboot

$reset
exit 0