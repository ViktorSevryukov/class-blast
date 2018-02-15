installing chrome driver

mkdir -p $HOME/bin
chmod +x chromedriver
mv src/drivers/chromedriver $HOME/bin

additional:
echo "export PATH=$PATH:$HOME/bin" >> $HOME/.bash_profile


OSX:
export PATH=$PATH:/{folder with driver}/