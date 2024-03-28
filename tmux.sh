#! /bin/bash
git clone https://github.com/gpakosz/.tmux.git "/path/to/oh-my-tmux"
mkdir -p "~/.config/tmux"
ln -s "/path/to/oh-my-tmux/.tmux.conf" "~/.config/tmux/tmux.conf"
cp "/path/to/oh-my-tmux/.tmux.conf.local" "~/.config/tmux/tmux.conf.local"
