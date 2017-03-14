#!/usr/bin/env python

import re
import os
import sys
import time
import subprocess

TARGET_DISK=sys.argv[1]


status_timestamps = {}
def Status(msg,status="New"):
	if status=='New':
		print "Beginning %s" % msg
		status_timestamps[msg] = time.time()
	else:
		print "%s %s... (%ss)" % (status,msg,int(time.time()-status_timestamps[msg]))


#
# System pre-reqs
Status("system package install")
subprocess.Popen("apt-get -y install lvm2 mdadm",shell=True).wait()
Status("system package install","Completed")


#
# Mount disk and begin customizations
#
Status("mounting image")
subprocess.Popen("partprobe %s" % TARGET_DISK,shell=True).wait() # system reload partition tables


#
# Build list of viable partitions
#
partitions_to_mount=[]
parted_out, parted_err = subprocess.Popen("parted -m %s -s print | tail -n +3" % TARGET_DISK,shell=True,stdout=subprocess.PIPE).communicate()
if len(parted_out)==0:  partitions_to_mount.append("mount %s /mnt" % TARGET_DISK)	# No partitions - using whole disk?
for parted_line in parted_out.split("\n"):
	cols = parted_line.split(":")
	if len(cols)<=1:  continue
	partition_num = cols[0]
	partition_type = cols[4]

	if re.search("lvm",parted_line):
		## TODO
		#dprobe dm-mod
		subprocess.Popen("vgchange -ay",shell=True)
		lvscan_out, lvscan_err = subprocess.Popen("lvscan | awk '{print $2}' | perl -p -e \"s/'//g\"",shell=True,stdout=subprocess.PIPE).communicate()
		for lv_part in lvscan_out.split("\n"):
			if not len(lv_part):  continue
			file_out, file_err = subprocess.Popen("file -sL %s" % lv_part,shell=True,stdout=subprocess.PIPE).communicate()
			if re.search("ext[234]|reiserfs",file_out):
				# direct mountable partitions
				partitions_to_mount.append("mount %s /mnt" % lv_part)
			elif partition_type in ("swap"):
				## Ignore these types
				pass
			else:
				sys.stderr.write("Unknown partition type '%s\\%s' on %s%s\n" % (partition_type,file_out,TARGET_DISK,partition_num))

	elif partition_type in ("ext2","ext3","ext4","reiserfs"):
		# direct mountable partitions
		partitions_to_mount.append("mount %s%s /mnt" % (TARGET_DISK,partition_num))
	elif partition_type in ("swap","fat16"):
		## Ignore these types
		pass
	else:
		sys.stderr.write("Unknown partition type '%s' on %s%s\n" % (partition_type,TARGET_DISK,partition_num))


#
# Proess each viable partition
#
configs_set = {
		'network': False,
		'ssh': False,
	}

for mount_cmd in partitions_to_mount:
	subprocess.Popen("umount /mnt",shell=True).wait()

	print "Executing: %s" % mount_cmd

	p = subprocess.Popen(mount_cmd,shell=True)
	err = p.wait()
	if err>0:
		sys.stderr.write("Error mounting partition with command '%s'\n" % mount_cmd)

	# Proceed only if we have access to etc - assume this means a root partition
	if not os.path.exists("/mnt/etc"):  continue

	# Disable cloud-config
	subprocess.Popen("rm -f /mnt/etc/init/cloud-*",shell=True).wait()

	# Set DNS #
	subprocess.Popen("rm -f /mnt/etc/resolv.conf",shell=True).wait()
	subprocess.Popen("cp -Hf /etc/resolv.conf /mnt/etc/resolv.conf",shell=True).wait()

	# ADDED By C3DNA
	# Copy content and set init script
    #    subprocess.Popen("bash /root/clc_installer/copy_c3dna_content.sh",shell=True).wait()

	# Copy sysadmin scripts
	# TODO - only if we're within a specific set of operating systems?  And only
	#        if we are at the root partition level.
	subprocess.Popen("cp -Rp /sysadmin /mnt/",shell=True).wait()

	# Set hostname
	subprocess.Popen("rm -f /mnt/etc/hostname",shell=True).wait()
	subprocess.Popen("cp /etc/hostname /mnt/etc/hostname",shell=True).wait()

	# Get network variables
	nw_mac = subprocess.check_output("ifconfig eth0 | grep HWaddr | awk '{print $5}'",shell=True).strip()
	nw_ipaddr = subprocess.check_output("ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'",shell=True).strip()
	nw_netmask = subprocess.check_output("ifconfig eth0 | grep 'Mask:' | awk '{print $4}' | cut -d: -f2",shell=True).strip()
	nw_broadcast = subprocess.check_output("ifconfig eth0 | grep 'Bcast:' | awk '{print $3}' | cut -d: -f2",shell=True).strip()
	nw_gw = subprocess.check_output("netstat -nr | grep \"^0.0.0.0\" | awk '{print $2}'",shell=True).strip()
	nw_hostname = subprocess.check_output("hostname",shell=True).strip()
	nw_network = subprocess.check_output("route | tail -1 | awk '{print $1}'",shell=True).strip()

	# Copy network config
	# SuSe Type
	if os.path.exists("/mnt/etc/SuSE-release") or os.path.exists("/mnt/etc/sysconfig/network"):
		configs_set['network'] = True
		with open("/mnt/etc/sysconfig/network/ifcfg-lan0","w") as fh:
			fh.write("""STARTMODE=auto
BOOTPROTO=static
IPADDR=%s
NETMASK=%s
BROADCAST=%s
NETWORK=%s
""" % (nw_ipaddr,nw_netmask,nw_broadcast,nw_network))
		with open("/mnt/etc/sysconfig/network/ifroute-lan0","w") as fh:
			fh.write("""# Destination     Dummy/Gateway     Netmask      Device
#
default %s - lan0
""" % (nw_gw,))

	# RHEL Type
	elif os.path.exists("/mnt/etc/redhat-release") or os.path.exists("/mnt/etc/sysconfig/network-scripts/"):
		configs_set['network'] = True
		with open("/mnt/etc/sysconfig/network-scripts/ifcfg-eth0","w") as fh:
			fh.write("""DEVICE=eth0
TYPE=Ethernet
BOOTPROTO=none
ONBOOT=yes
HWADDR=%s
IPADDR=%s
NETMASK=%s
GATEWAY=%s
DNS1=172.17.1.26
DNS2=172.17.1.27
""" % (nw_mac,nw_ipaddr,nw_netmask,nw_gw))

	# DEB Type
	elif os.path.exists("/mnt/etc/debian_version") or os.path.exists("/mnt/etc/network/interfaces"):
		configs_set['network'] = True
		with open("/mnt/etc/network/interfaces","w") as fh:
			fh.write("""iface lo inet loopback
auto lo

auto eth0
iface eth0 inet static
address %s
netmask %s
up route add default gw %s
dns-search %s
dns-nameservers 172.17.1.26 172.17.1.27
""" % (nw_ipaddr,nw_netmask,nw_gw,nw_hostname))

	# Gentoo Type
	elif os.path.exists("/mnt/etc/gentoo-release"):
		configs_set['network'] = True
		with open("/mnt/etc/conf.d/net.eth0","w") as fh:
			fh.write("""config_eth0=( "%s netmask %s broadcast %s" )
routes_eth0=( "default via %s" )
dns_servers_eth0="172.17.1.26 172.17.1.27"
""" % (nw_ipaddr,nw_netmask,nw_broadcast,nw_gw))

	#else:
	#	sys.stderr.write("Unable to identify OS - unsure where to place network config.  Fatal Error\n")
	#	sys.exit(1)

	# Set root password
	subprocess.Popen("grep ^root /etc/shadow > /tmp/shadow",shell=True).wait()
	subprocess.Popen("grep -v ^root /mnt/etc/shadow >> /tmp/shadow",shell=True).wait()
	subprocess.Popen("mv -f /tmp/shadow /mnt/etc/shadow",shell=True).wait()

	# Enable ssh at boot - assumes default runlevel 3
	# TODO - does not catch SuSe Linux, they have a different structure
	if os.path.exists("/mnt/etc/rc3.d") and subprocess.Popen("ls -l /mnt/etc/rc3.d | grep ssh>/dev/null 2>&1",shell=True).wait():
		subprocess.Popen("cd /mnt/etc; ln -s ../`ls init.d/*ssh*|head -1` rc3.d/S75ssh",shell=True).wait()

	# Enable root ssh login
	if os.path.exists("/mnt/etc/ssh/sshd_config"):
		configs_set['ssh'] = True
		subprocess.Popen("perl -p -i -e 's/^Port.*/Port 22/gi' /mnt/etc/ssh/sshd_config",shell=True).wait()
		subprocess.Popen("perl -p -i -e 's/^PermitRootLogin.*/PermitRootLogin yes/gi' /mnt/etc/ssh/sshd_config",shell=True).wait()
		subprocess.Popen("perl -p -i -e 's/^\s*PasswordAuthentication.*/PasswordAuthentication yes/gi' /mnt/etc/ssh/sshd_config",shell=True).wait()

subprocess.Popen("umount /mnt",shell=True).wait()


# Alert if configs not set
error = False
for key,val in configs_set.iteritems():
	if val==False:
		error = True
		sys.stderr.write("Unable to configure %s\n" % key)

Status("mounting image","Complete")

if error:
	sys.stderr.write("Fatal error configuring disk\n")
	sys.exit(1)
