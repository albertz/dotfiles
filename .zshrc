# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000
setopt appendhistory autocd extendedglob
unsetopt beep nomatch
bindkey -e
bindkey "^[[3~" delete-char
bindkey "^[[H" beginning-of-line
bindkey "^[[F" end-of-line

# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
zstyle :compinstall filename '/home/tom/.zshrc'

#autoload -Uz compinit
#compinit

# End of lines added by compinstall

# Colorful prompt
BLACK="%{"$'\033[01;30m'"%}"
GREEN="%{"$'\033[01;32m'"%}"
RED="%{"$'\033[01;31m'"%}"
YELLOW="%{"$'\033[01;33m'"%}"
BLUE="%{"$'\033[01;34m'"%}"
BOLD="%{"$'\033[01;39m'"%}"
NORM="%{"$'\033[00m'"%}"
export PS1="${RED}%n${NORM}@${BLUE}%m ${YELLOW}%! ${GREEN}(%1~) %#${NORM}"

#Some fun global aliases

alias ls='ls -G'
alias -g ...='../..'
alias -g ....='../../..'
alias -g .....='../../../..'
alias -g EL='|& less'
alias -g ETL='|& tail -20'
alias -g G='| egrep'
alias -g LL="2>&1 | less"
alias -g L="| less"
alias GO="gnome-open"

#Correction
setopt correctall
zstyle ':completion:*' completer _complete _match

#Title in xterm
chpwd() {
  [[ -t 1 ]] || return
  case $TERM in
    sun-cmd) print -Pn "\e]l%~\e\\"
      ;;
    *xterm*|rxvt|(dt|k|E)term) print -Pn "\e]2;%n@%m: %~\a"
      ;;
  esac
}

case $TERM in
  sun-cmd) print -Pn "\e]l%~\e\\"
    ;;
  *xterm*|rxvt|(dt|k|E)term) print -Pn "\e]2;%n@%m: %~\a"
    ;;
esac

source ~/.profile

# . /sw/bin/init.sh


source /Users/az/Library/Preferences/org.dystroy.broot/launcher/bash/br
