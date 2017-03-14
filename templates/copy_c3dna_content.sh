#Copy Startup Scripts
#etc_path="/mnt/etc/init.d"
etc_path="/etc/init.d"
config_filename=configure_controller.sh

echo "Copy $config_filename on $etc_path"
cp $config_filename $etc_path/
chmod 755 $etc_path/$config_filename
ln -s /etc/init.d/$config_filename /etc/rc1.d/S99$config_filename
ln -s /etc/init.d/$config_filename /etc/rc2.d/S99$config_filename
ln -s /etc/init.d/$config_filename /etc/rc3.d/S99$config_filename
