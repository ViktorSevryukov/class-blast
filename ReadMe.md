installing chrome driver

mkdir -p $HOME/bin
mv src/drivers/chromedriver $HOME/bin

additional:
echo "export PATH=$PATH:$HOME/bin" >> $HOME/.bash_profile