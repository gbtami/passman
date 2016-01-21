sudo rpm -e PassMan
python3 setup.py bdist_rpm --post-install post_install.sh
sudo rpm -i dist/PassMan-0.1.0-1.noarch.rpm
passman
