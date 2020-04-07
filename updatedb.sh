mysqldump --add-drop-table -h 127.0.0.1 --port=3307 -u root -p123 --databases _8caf1f8f708e356e > ~/_8caf1f8f708e356e.sql
mysql -h 127.0.0.1 --port=3307 -u root -p123 -e "drop schema _8caf1f8f708e356e;"
mysql -h 127.0.0.1 --port=3307 -u root -p123 < ./erpnext/assets/_8caf1f8f708e356e.sql
