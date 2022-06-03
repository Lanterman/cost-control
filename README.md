#README.md

# Сost-control

The project was created for informational purposes only.

Description

This GUI application performs the basic functions of managing your expenses, i.e. creating, editing, searching, deleting the records.
It also calculates the balance, the expenses, the income and displays the bar chart of expenses.

### Launch of the project

#### 1) clone the repository
```
https://github.com/Lanterman/cost-control.git
```
#### 2) Switch to for_buildozer branch
```
git checkout for_buildozer
```
#### 3) Install buildozer
```
git clone https://github.com/kivy/buildozer.git
cd buildozer
sudo python setup.py install
```
#### 4) Install buildozer’s dependencies
```
sudo apt update
sudo apt install -y git zip unzip openjdk-13-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.19 virtualenv  # the --user should be removed if you do this in a venv

# add the following line at the end of your ~/.bashrc file
export PATH=$PATH:~/.local/bin/
```
#### 5) Finally, plug in your android device and run:
```
buildozer android debug deploy run
```