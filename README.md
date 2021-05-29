# pve-zfs-encryption-patch-py

Proxmox 6.4-6 не поддерживает шифрованные дасеты и тома.

Он не может их реплицировать, так как для их репликации требуется указание особого ключа и выполнение нескольких дополнительных шагов. Временное решение здесь:

https://bugzilla.proxmox.com/show_bug.cgi?id=2350#

Обсуждение проблемы здесь:

https://forum.proxmox.com/threads/replication-not-possible-on-encrypted-data-pool.78470/

Этот скрипт делает почти тоже самое что и:

https://github.com/igluko/pve-zfs-encryption-patch



Скрипт на Python 3.7. Это версия Python по умолчанию в Proxmox 6.4-6.

Параметр **-noemail** отключает отправку писем. 

По умолчанию, письма отправляются на email указанный при установке Proxmox (это email пользователя root@pam).


