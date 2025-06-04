#!/bin/bash

# Verificar o limite atual
echo "Limite atual de inotify watches:"
cat /proc/sys/fs/inotify/max_user_watches

# Aumentar temporariamente o limite (válido até reiniciar)
echo "Aumentando o limite temporariamente..."
sudo sysctl fs.inotify.max_user_watches=524288

# Verificar o novo limite
echo "Novo limite de inotify watches:"
cat /proc/sys/fs/inotify/max_user_watches

# Instruções para tornar a alteração permanente
echo ""
echo "Para tornar esta alteração permanente, execute:"
echo "echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf"
echo "sudo sysctl -p"