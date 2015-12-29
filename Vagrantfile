# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provision "shell", path: "pg_config.sh"
  # config.vm.box = "hashicorp/precise32"
  config.vm.box = "ubuntu/trusty32"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 3001, host: 3001
  config.vm.network "forwarded_port", guest: 3002, host: 3002
  config.vm.network "forwarded_port", guest: 3003, host: 3003
  config.vm.network "forwarded_port", guest: 3004, host: 3004
end
