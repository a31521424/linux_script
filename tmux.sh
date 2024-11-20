#! /bin/bash

cd $HOME
git clone https://github.com/gpakosz/.tmux.git
ln -s -f .tmux/.tmux.conf
cp .tmux/.tmux.conf.local .


sudo apt install tmux -y

cat >> $HOME/.bashrc << 'EOF'
# Auto start tmux on SSH
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    if [ -z "$TMUX" ]; then
        if command -v tmux &> /dev/null; then
            tmux attach || tmux new
        fi
    fi
fi
EOF
