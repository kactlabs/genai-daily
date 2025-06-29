from pytube import Channel

channel_url = "https://www.youtube.com/@a2dchannel/UCaqgoG_VCMhjccHPUI"
channel = Channel(channel_url)

print("Trending videos:")
for video in channel.videos[:5]:
    print(video.title)
