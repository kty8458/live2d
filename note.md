
gst-launch-1.0 -v \
udpsrc port=5005 caps="application/x-rtp, media=(string)audio, clock-rate=(int)48000, encoding-name=(string)OPUS" ! \
rtpjitterbuffer latency=25 ! \
rtpopusdepay ! \
opusdec ! \
audioconvert ! \
audioresample ! \
pulsesink

sudo apt install pulseaudio
pip install pyaudio numpy



sudo iptables -t nat -A POSTROUTING -o wlp2s0 -j MASQUERADE
sudo iptables -A FORWARD -i enx00e04c36ef90 -o wlp2s0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i enx00e04c36ef90 -o wlp2s0 -j ACCEPT

sudo ip addr add 192.168.123.19/24 dev eth1  # 临时分配
sudo ip link set eth1 up                      # 确保接口启用
